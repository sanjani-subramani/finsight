import 'package:dio/dio.dart';

import '../models/ingestion_models.dart';
import '../offline/outbox_service.dart';

class IngestionRepository {
  IngestionRepository({required Dio dio, required OutboxService outboxService})
      : _dio = dio,
        _outboxService = outboxService;

  final Dio _dio;
  final OutboxService _outboxService;

  /// Submits a manual financial event with an Idempotency-Key header. If
  /// the device is currently offline (a connection-level DioException,
  /// not a server-side rejection), the write is queued to the outbox
  /// instead of throwing, reusing the SAME idempotency key it would have
  /// sent over the network — so whenever it does replay, a server that
  /// happens to have already processed it (its response was simply lost)
  /// answers idempotently instead of double-creating the entry.
  ///
  /// Returns null when queued (nothing to confirm yet); returns the
  /// confirmed IngestionResult when it went through immediately.
  Future<IngestionResult?> addManualEntry({
    required String eventType,
    String? amount,
    required DateTime occurredAt,
    String? counterparty,
    String? category,
    String? description,
    String? idempotencyKey,
  }) async {
    final key = idempotencyKey ?? OutboxService.newIdempotencyKey();
    final body = <String, dynamic>{
      'event_type': eventType,
      if (amount != null) 'amount': amount,
      'occurred_at': occurredAt.toUtc().toIso8601String(),
      if (counterparty != null) 'counterparty': counterparty,
      if (category != null) 'category': category,
      if (description != null) 'description': description,
    };

    try {
      final response = await _dio.post<Map<String, dynamic>>(
        '/ingest/manual',
        data: body,
        options: Options(headers: {'Idempotency-Key': key}),
      );
      return IngestionResult.fromJson(response.data!);
    } on DioException catch (e) {
      final isOffline = e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout;
      if (!isOffline) rethrow;

      await _outboxService.queue(
        endpoint: '/ingest/manual',
        method: 'POST',
        body: body,
        idempotencyKey: key,
      );
      return null;
    }
  }
}
