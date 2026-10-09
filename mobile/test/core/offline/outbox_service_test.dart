import 'package:dio/dio.dart';
import 'package:drift/native.dart';
import 'package:finsentinel/core/offline/app_database.dart';
import 'package:finsentinel/core/offline/outbox_service.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../test_utils/fake_adapter.dart';
import '../../test_utils/fake_connectivity.dart';

void main() {
  late AppDatabase db;
  late FakeHttpClientAdapter adapter;
  late Dio dio;
  late FakeConnectivityChecker connectivity;

  setUp(() {
    db = AppDatabase(NativeDatabase.memory());
    adapter = FakeHttpClientAdapter();
    dio = Dio(BaseOptions(baseUrl: 'http://test'))..httpClientAdapter = adapter;
    connectivity = FakeConnectivityChecker();
  });

  tearDown(() async {
    connectivity.dispose();
    await db.close();
  });

  test('a write goes to the outbox and replays on reconnect', () async {
    final service = OutboxService(database: db, dio: dio, connectivity: connectivity);
    var callCount = 0;
    String? seenIdempotencyKey;
    adapter.on('POST', '/ingest/manual', (options) {
      callCount++;
      seenIdempotencyKey = options.headers['Idempotency-Key'] as String?;
      return jsonResponse(
        {'event_id': 'evt-1', 'method': 'manual', 'confidence': 0.9, 'was_duplicate': false, 'quarantined': false},
        201,
      );
    });

    final key = OutboxService.newIdempotencyKey();
    await service.queue(endpoint: '/ingest/manual', method: 'POST', body: {'amount': '100'}, idempotencyKey: key);

    expect(await service.pending(), hasLength(1));
    expect(callCount, 0, reason: 'queued, not yet replayed');

    connectivity.goOnline();
    await pumpEventQueue();

    expect(callCount, 1);
    expect(seenIdempotencyKey, key);
    expect(await service.pending(), isEmpty);

    service.dispose();
  });

  test('replay reuses the same idempotency key on every attempt', () async {
    final service = OutboxService(database: db, dio: dio, connectivity: connectivity);
    final seenKeys = <String>[];
    var attempt = 0;
    adapter.on('POST', '/ingest/manual', (options) {
      attempt++;
      seenKeys.add(options.headers['Idempotency-Key'] as String);
      if (attempt == 1) {
        throw DioException(requestOptions: options, type: DioExceptionType.connectionError);
      }
      return jsonResponse(
        {'event_id': 'evt-2', 'method': 'manual', 'confidence': 0.9, 'was_duplicate': false, 'quarantined': false},
        201,
      );
    });

    final key = OutboxService.newIdempotencyKey();
    await service.queue(endpoint: '/ingest/manual', method: 'POST', body: {'amount': '100'}, idempotencyKey: key);

    await service.replayAll(); // fails (connection error), stays pending
    expect(await service.pending(), hasLength(1));

    await service.replayAll(); // succeeds on retry
    expect(await service.pending(), isEmpty);

    expect(seenKeys, [key, key], reason: 'the SAME key must be reused on every attempt, never regenerated');

    service.dispose();
  });

  test('a permanent failure (422) is marked failed and not retried forever', () async {
    final service = OutboxService(database: db, dio: dio, connectivity: connectivity);
    var callCount = 0;
    adapter.on('POST', '/ingest/manual', (options) {
      callCount++;
      throw DioException(
        requestOptions: options,
        response: Response<dynamic>(requestOptions: options, statusCode: 422),
        type: DioExceptionType.badResponse,
      );
    });

    final key = OutboxService.newIdempotencyKey();
    await service.queue(endpoint: '/ingest/manual', method: 'POST', body: {}, idempotencyKey: key);

    await service.replayAll();

    expect(await service.pending(), isEmpty);
    expect(await service.failed(), hasLength(1));
    expect(callCount, 1);

    await service.replayAll(); // must not retry a permanently-failed entry
    expect(callCount, 1);

    service.dispose();
  });
}
