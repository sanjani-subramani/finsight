import 'package:dio/dio.dart';
import 'package:drift/native.dart';
import 'package:finsentinel/core/offline/app_database.dart';
import 'package:finsentinel/core/repositories/cache_status.dart';
import 'package:finsentinel/core/repositories/twin_repository.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../test_utils/fake_adapter.dart';

Map<String, dynamic> _snapshotJson() => {
      'schema_version': 1,
      'snapshot_id': 'snap-1',
      'user_id': 'user-1',
      'generated_at': DateTime.now().toUtc().toIso8601String(),
      'cash_available': '10000',
      'emergency_fund': '5000',
      'income_forecast': {'source': 'declared', 'confidence_score': 0.7, 'sample_size': 0},
      'obligations': <dynamic>[],
      'goals': <dynamic>[],
      'weather': 'stable',
      'shortfall_risks': <dynamic>[],
      'safe_to_spend': '1000',
      'state_confidence': 0.8,
      'unconfirmed_event_count': 0,
      'contains_simulated_data': false,
      'events_applied': 0,
    };

void main() {
  late AppDatabase db;
  late FakeHttpClientAdapter adapter;
  late Dio dio;
  late TwinRepository repo;

  setUp(() {
    db = AppDatabase(NativeDatabase.memory());
    adapter = FakeHttpClientAdapter();
    dio = Dio(BaseOptions(baseUrl: 'http://test'))..httpClientAdapter = adapter;
    repo = TwinRepository(dio: dio, database: db);
  });

  tearDown(() async {
    await db.close();
  });

  test('a successful fetch is marked fresh', () async {
    adapter.on('GET', '/twin/snapshot', (options) => jsonResponse(_snapshotJson(), 200));
    final result = await repo.fetchSnapshot('user-1');
    expect(result.status, CacheStatus.fresh);
  });

  test('a failed fetch with a cache hit falls back and is marked stale', () async {
    var callCount = 0;
    adapter.on('GET', '/twin/snapshot', (options) {
      callCount++;
      if (callCount == 1) return jsonResponse(_snapshotJson(), 200);
      throw DioException(
        requestOptions: options,
        type: DioExceptionType.badResponse,
        response: Response<dynamic>(requestOptions: options, statusCode: 500),
      );
    });

    final first = await repo.fetchSnapshot('user-1');
    expect(first.status, CacheStatus.fresh);

    final second = await repo.fetchSnapshot('user-1');
    expect(second.status, CacheStatus.stale, reason: 'never show cached data without marking it stale');
    expect(second.data.snapshotId, first.data.snapshotId);
    expect(second.fetchedAt, isNotNull);
  });

  test('a connection-level failure with a cache hit is marked offline', () async {
    var callCount = 0;
    adapter.on('GET', '/twin/snapshot', (options) {
      callCount++;
      if (callCount == 1) return jsonResponse(_snapshotJson(), 200);
      throw DioException(requestOptions: options, type: DioExceptionType.connectionError);
    });

    await repo.fetchSnapshot('user-1');
    final second = await repo.fetchSnapshot('user-1');
    expect(second.status, CacheStatus.offline);
  });

  test('a failed fetch with NO cache at all rethrows rather than fabricating data', () async {
    adapter.on(
      'GET',
      '/twin/snapshot',
      (options) => throw DioException(requestOptions: options, type: DioExceptionType.connectionError),
    );

    await expectLater(repo.fetchSnapshot('user-1'), throwsA(isA<DioException>()));
  });
}
