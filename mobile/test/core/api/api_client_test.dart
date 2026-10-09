import 'package:dio/dio.dart';
import 'package:finsentinel/core/api/api_client.dart';
import 'package:finsentinel/core/auth/token_store.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../test_utils/fake_adapter.dart';
import '../../test_utils/fake_secure_storage.dart';

void main() {
  late FakeHttpClientAdapter adapter;
  late Dio dio;
  late TokenStore tokenStore;

  setUp(() {
    adapter = FakeHttpClientAdapter();
    dio = Dio(BaseOptions(baseUrl: 'http://test'))..httpClientAdapter = adapter;
    tokenStore = TokenStore(storage: FakeSecureStorage());
  });

  // THE most important test in this step (per the task spec): if the
  // single-flight mechanism in AuthInterceptor regresses, concurrent
  // 401s each trigger their own refresh call, present an already-used
  // refresh token to the backend, and the backend's reuse-detection logs
  // the user out — a security feature turned into a self-inflicted bug.
  test('3 concurrent 401s trigger exactly ONE refresh call', () async {
    await tokenStore.saveTokens(accessToken: 'stale-token', refreshToken: 'refresh-v0', expiresInSeconds: 3600);

    var refreshCallCount = 0;
    var currentValidToken = 'token-v1';

    adapter.on('GET', '/protected', (options) {
      final auth = options.headers['Authorization'] as String?;
      if (auth == 'Bearer $currentValidToken') {
        return jsonResponse({'ok': true}, 200);
      }
      return jsonResponse({'detail': 'unauthorized'}, 401);
    });

    adapter.on('POST', '/auth/refresh', (options) {
      refreshCallCount++;
      currentValidToken = 'token-v${refreshCallCount + 1}';
      return jsonResponse(
        {'access_token': currentValidToken, 'refresh_token': 'refresh-v$refreshCallCount', 'expires_in': 3600},
        200,
      );
    });

    final apiClient = ApiClient(tokenStore: tokenStore, dio: dio);

    final results = await Future.wait([
      apiClient.dio.get<dynamic>('/protected'),
      apiClient.dio.get<dynamic>('/protected'),
      apiClient.dio.get<dynamic>('/protected'),
    ]);

    expect(refreshCallCount, 1, reason: 'exactly one refresh call, no matter how many requests 401 concurrently');
    for (final r in results) {
      expect(r.statusCode, 200);
    }
    // Every request that 401'd ended up authorized with the token the
    // single refresh call produced.
    expect(await tokenStore.readAccessToken(), 'token-v2');
  });

  test('refresh failure clears tokens and emits auth-expired', () async {
    await tokenStore.saveTokens(accessToken: 'stale-token', refreshToken: 'dead-refresh', expiresInSeconds: 3600);

    adapter.on('GET', '/protected', (options) => jsonResponse({'detail': 'unauthorized'}, 401));
    adapter.on('POST', '/auth/refresh', (options) => jsonResponse({'detail': 'refresh token invalid'}, 401));

    var authExpiredFired = false;
    final apiClient = ApiClient(tokenStore: tokenStore, dio: dio, onAuthExpired: () => authExpiredFired = true);

    await expectLater(apiClient.dio.get<dynamic>('/protected'), throwsA(isA<DioException>()));

    expect(authExpiredFired, isTrue);
    expect(await tokenStore.hasTokens(), isFalse);
  });

  test('a request is never retried more than once', () async {
    await tokenStore.saveTokens(accessToken: 'stale-token', refreshToken: 'refresh-v0', expiresInSeconds: 3600);

    var protectedCallCount = 0;
    adapter.on('GET', '/protected', (options) {
      protectedCallCount++;
      return jsonResponse({'detail': 'unauthorized'}, 401); // ALWAYS unauthorized, even after "refresh"
    });

    var refreshCallCount = 0;
    adapter.on('POST', '/auth/refresh', (options) {
      refreshCallCount++;
      return jsonResponse({'access_token': 'new-token', 'refresh_token': 'new-refresh', 'expires_in': 3600}, 200);
    });

    final apiClient = ApiClient(tokenStore: tokenStore, dio: dio);
    await expectLater(apiClient.dio.get<dynamic>('/protected'), throwsA(isA<DioException>()));

    expect(protectedCallCount, 2, reason: 'the original attempt plus exactly one retry, never more');
    expect(refreshCallCount, 1);
  });

  test('auth endpoints never trigger the refresh dance on their own 401', () async {
    await tokenStore.saveTokens(accessToken: 'stale-token', refreshToken: 'refresh-v0', expiresInSeconds: 3600);

    var refreshCallCount = 0;
    adapter.on('POST', '/auth/login', (options) => jsonResponse({'detail': 'bad credentials'}, 401));
    adapter.on('POST', '/auth/refresh', (options) {
      refreshCallCount++;
      return jsonResponse({'access_token': 'x', 'refresh_token': 'y', 'expires_in': 3600}, 200);
    });

    final apiClient = ApiClient(tokenStore: tokenStore, dio: dio);
    await expectLater(
      apiClient.dio.post<dynamic>('/auth/login', data: {'email': 'a@b.com', 'password': 'x'}),
      throwsA(isA<DioException>()),
    );

    expect(refreshCallCount, 0);
  });
}
