import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../auth/token_store.dart';

/// Fired when the refresh token itself is no longer usable (expired,
/// revoked, or caught as a reuse/theft signal by the backend — see
/// AuthInterceptor's class doc) and the user must log in again.
class AuthExpiredEvent {
  const AuthExpiredEvent();
}

/// Base URL from --dart-define=API_BASE_URL=..., defaulting to the
/// Android emulator's host-loopback alias.
///
/// 10.0.2.2 is a special address the Android EMULATOR maps to the HOST
/// machine's own localhost. The emulator is a separate virtual device
/// with its own network stack, so "localhost" from inside it refers to
/// the emulator itself — a real backend running on the dev machine is
/// invisible at that address. On a real device, an iOS simulator, or a
/// remote backend, override this with `--dart-define=API_BASE_URL=<url>`
/// pointing at wherever the backend is actually reachable.
const String kDefaultBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

/// ============================================================================
/// AuthInterceptor — SINGLE-FLIGHT REFRESH.
/// This is the single most important piece of client code in the app.
/// Read this comment in full before changing anything here.
/// ============================================================================
///
/// Two responsibilities:
///   1. Attach `Authorization: Bearer <access_token>` to every outgoing
///      request (except the auth endpoints themselves).
///   2. On a 401, refresh the access token and retry the ORIGINAL
///      request exactly once.
///
/// THE HAZARD THIS CLASS EXISTS TO PREVENT:
///
/// The backend rotates refresh tokens — every successful call to
/// /auth/refresh issues a brand-new refresh token and immediately
/// invalidates the one that was just presented. If that same
/// already-used refresh token is EVER presented again, the backend
/// treats it as evidence of theft (an attacker replaying a captured
/// token, or — without this class — our own retry logic tripping over
/// itself) and revokes the ENTIRE refresh-token chain, logging the user
/// out.
///
/// Picture three requests firing at once (e.g. Home screen loading three
/// widgets in parallel) at the exact moment the access token has just
/// expired. All three get a 401 within milliseconds of each other. If
/// each one independently called /auth/refresh:
///   1. Request A's refresh call reaches the backend first, gets a new
///      token pair, and the OLD refresh token is now spent.
///   2. Request B's refresh call — which already read the OLD refresh
///      token from storage before A's response overwrote it — then
///      presents that same spent token to the backend.
///   3. The backend sees a reused refresh token, assumes theft, and
///      revokes everything. The user is logged out by our OWN retry
///      logic, having done nothing wrong.
///
/// THE FIX: at most one refresh call is ever in flight, no matter how
/// many requests 401 concurrently. This is tracked with a single
/// `Completer<String>? _refreshInFlight`:
///   - The FIRST 401 to arrive finds `_refreshInFlight == null`. It
///     creates the Completer, becomes the one responsible for actually
///     calling /auth/refresh, and completes the Completer with the new
///     access token when the call resolves (or completes it with the
///     error, on failure).
///   - Every OTHER 401 that arrives WHILE that refresh is still running
///     finds `_refreshInFlight != null` and simply `await`s that SAME
///     Completer's future instead of starting a second refresh call.
///     Every one of them receives the SAME new access token once the one
///     real network call finishes, and retries its own original request
///     with it.
///   - The Completer is cleared back to null in a `finally`-equivalent
///     (`whenComplete`), so the next time the token expires, a fresh
///     refresh cycle is free to start.
///
/// Net effect: N concurrent 401s collapse into exactly ONE call to
/// /auth/refresh — this is what the "3 concurrent 401s -> exactly one
/// refresh call" test in test/core/api/api_client_test.dart verifies.
///
/// A request is never retried more than once: the retried request is
/// tagged via `requestOptions.extra['fs_retried_after_refresh']`, so if
/// it somehow 401s again, onError sees the tag and gives up immediately
/// instead of looping.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required TokenStore tokenStore,
    required Dio dio,
    required VoidCallback onAuthExpired,
  })  : _tokenStore = tokenStore,
        _dio = dio,
        _onAuthExpired = onAuthExpired;

  final TokenStore _tokenStore;
  final Dio _dio;
  final VoidCallback _onAuthExpired;

  /// The in-flight refresh shared by every concurrent 401; null when no
  /// refresh is currently running. THIS is the single-flight mechanism —
  /// see the class doc above.
  Completer<String>? _refreshInFlight;

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (_isAuthEndpoint(options.path)) {
      // Never attach a (possibly stale) bearer token to the auth
      // endpoints themselves — register/login carry no token yet, and
      // refresh must present ONLY the refresh token in its body.
      return handler.next(options);
    }

    if (await _tokenStore.needsProactiveRefresh() && await _tokenStore.readRefreshToken() != null) {
      try {
        await _refresh();
      } catch (_) {
        // Swallow here — if proactive refresh failed, the request goes
        // out with whatever token is on hand (or none), and the 401
        // path below is the safety net that actually handles it.
      }
    }

    final accessToken = await _tokenStore.readAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final requestOptions = err.requestOptions;
    final isUnauthorized = err.response?.statusCode == 401;
    final isAuthEndpoint = _isAuthEndpoint(requestOptions.path);
    final alreadyRetried = requestOptions.extra['fs_retried_after_refresh'] == true;

    if (!isUnauthorized || isAuthEndpoint || alreadyRetried) {
      return handler.next(err);
    }

    try {
      final newAccessToken = await _refresh();
      // Mark BEFORE resending: never retry more than once per request,
      // even if this retried call itself somehow 401s again.
      requestOptions.extra['fs_retried_after_refresh'] = true;
      requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
      final retried = await _dio.fetch<dynamic>(requestOptions);
      return handler.resolve(retried);
    } catch (_) {
      // The refresh itself failed — the refresh token is dead (expired,
      // revoked, or flagged as reused). Nothing left to try.
      await _tokenStore.clear();
      _onAuthExpired();
      return handler.next(err);
    }
  }

  /// Runs (or joins) the single in-flight refresh. Returns the new
  /// access token; throws on failure.
  Future<String> _refresh() {
    final existing = _refreshInFlight;
    if (existing != null) {
      // A refresh is already running — piggyback on it. This branch is
      // the entire point of this class: it's what stops the second and
      // third concurrent 401 from making their own /auth/refresh call.
      return existing.future;
    }

    final completer = Completer<String>();
    _refreshInFlight = completer;
    unawaited(
      _doRefresh().then(completer.complete).catchError((Object e, StackTrace st) {
        completer.completeError(e, st);
      }).whenComplete(() {
        if (identical(_refreshInFlight, completer)) {
          _refreshInFlight = null;
        }
      }),
    );
    return completer.future;
  }

  Future<String> _doRefresh() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    if (refreshToken == null) {
      throw StateError('No refresh token available');
    }
    // Reuses the same Dio/interceptor chain deliberately: _isAuthEndpoint
    // already keeps onRequest from attaching a bearer token to this call
    // and keeps onError from trying to "refresh-and-retry" a 401 on the
    // refresh call itself, so this can't recurse. A second Dio instance
    // isn't needed, and using this one means the exact same mockable
    // HTTP adapter handles both the refresh call and every retried
    // request in tests.
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    final data = response.data!;
    final newAccessToken = data['access_token'] as String;
    final newRefreshToken = data['refresh_token'] as String;
    final expiresIn = data['expires_in'] as int;
    await _tokenStore.saveTokens(
      accessToken: newAccessToken,
      refreshToken: newRefreshToken,
      expiresInSeconds: expiresIn,
    );
    return newAccessToken;
  }

  bool _isAuthEndpoint(String path) {
    return path.contains('/auth/login') ||
        path.contains('/auth/register') ||
        path.contains('/auth/refresh');
  }
}

/// Reads X-Trace-ID off every response (success or error) and logs it,
/// so a user's bug report ("the app said X happened") can be matched to
/// the exact server-side request via app.platform.middleware.TraceIDMiddleware's
/// trace_id, without needing to reproduce the issue.
class TraceInterceptor extends Interceptor {
  @override
  void onResponse(Response<dynamic> response, ResponseInterceptorHandler handler) {
    _logTraceId(response.requestOptions, response.headers.value('x-trace-id'));
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    _logTraceId(err.requestOptions, err.response?.headers.value('x-trace-id'));
    handler.next(err);
  }

  void _logTraceId(RequestOptions options, String? traceId) {
    if (traceId == null) return;
    debugPrint('[trace ${options.method} ${options.path}] $traceId');
  }
}

/// The shared Dio-based HTTP client for the whole app: one instance, one
/// interceptor chain, one single-flight refresh mechanism.
class ApiClient {
  ApiClient({
    required TokenStore tokenStore,
    String? baseUrl,
    VoidCallback? onAuthExpired,
    Dio? dio,
  }) : dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: baseUrl ?? kDefaultBaseUrl,
                connectTimeout: const Duration(seconds: 15),
                receiveTimeout: const Duration(seconds: 20),
                contentType: 'application/json',
              ),
            ) {
    this.dio.interceptors.addAll([
      AuthInterceptor(
        tokenStore: tokenStore,
        dio: this.dio,
        onAuthExpired: () => onAuthExpired?.call(),
      ),
      TraceInterceptor(),
    ]);
  }

  final Dio dio;
}
