import 'dart:async';
import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import 'app_database.dart';

enum _ReplayOutcome { success, retryableFailure, permanentFailure }

/// A small seam OutboxService depends on instead of the concrete
/// [Connectivity] class directly — the same reasoning as
/// [SecureStorage] for TokenStore: the real plugin bridges to a platform
/// channel, which has no in-memory substitute for plain `flutter_test`
/// unit tests. Production code uses [ConnectivityPlusChecker]; tests
/// supply a fake that never touches a platform channel at all.
abstract class ConnectivityChecker {
  Stream<bool> get onlineStatusChanges;
}

class ConnectivityPlusChecker implements ConnectivityChecker {
  ConnectivityPlusChecker([Connectivity? connectivity]) : _connectivity = connectivity ?? Connectivity();
  final Connectivity _connectivity;

  @override
  Stream<bool> get onlineStatusChanges =>
      _connectivity.onConnectivityChanged.map((results) => results.any((r) => r != ConnectivityResult.none));
}

/// Queues writes made while offline and replays them, in creation order,
/// once connectivity returns.
class OutboxService {
  OutboxService({
    required AppDatabase database,
    required Dio dio,
    ConnectivityChecker? connectivity,
  })  : _db = database,
        _dio = dio,
        _connectivity = connectivity ?? ConnectivityPlusChecker() {
    _connectivitySubscription = _connectivity.onlineStatusChanges.listen((isOnline) {
      if (isOnline) {
        unawaited(replayAll());
      }
    });
  }

  final AppDatabase _db;
  final Dio _dio;
  final ConnectivityChecker _connectivity;
  late final StreamSubscription<bool> _connectivitySubscription;

  static const _uuid = Uuid();

  /// A fresh idempotency key for a NEW queued write. A UI-level retry of
  /// the same logical write must reuse the key already stored on its
  /// outbox row, never call this again — a new key per attempt would
  /// defeat the entire point of the header.
  static String newIdempotencyKey() => _uuid.v4();

  Future<int> queue({
    required String endpoint,
    required String method,
    required Map<String, dynamic> body,
    required String idempotencyKey,
  }) {
    return _db.into(_db.outbox).insert(
          OutboxCompanion.insert(
            endpoint: endpoint,
            method: method,
            body: jsonEncode(body),
            idempotencyKey: idempotencyKey,
            createdAt: DateTime.now().toUtc(),
          ),
        );
  }

  Future<List<OutboxData>> pending() {
    return (_db.select(_db.outbox)
          ..where((t) => t.status.equals('pending'))
          ..orderBy([(t) => OrderingTerm.asc(t.createdAt)]))
        .get();
  }

  Future<List<OutboxData>> failed() {
    return (_db.select(_db.outbox)..where((t) => t.status.equals('failed'))).get();
  }

  /// Replays every pending entry in creation order. Each replay reuses
  /// the SAME idempotency key it was queued with, so a write the server
  /// may already have processed (its response was simply lost to a
  /// dropped connection) is recognised as a duplicate and answered
  /// idempotently rather than double-created.
  ///
  /// Stops at the first RETRYABLE failure (network error, 401, 408, 429)
  /// so later writes never jump ahead of an earlier one that's still
  /// stuck — but skips past a PERMANENT failure (a genuine 4xx) and
  /// continues with the rest of the queue, since that entry will never
  /// succeed by itself and must not block everything behind it forever.
  Future<void> replayAll() async {
    final entries = await pending();
    for (final entry in entries) {
      final outcome = await _replayOne(entry);
      if (outcome == _ReplayOutcome.retryableFailure) {
        break;
      }
    }
  }

  Future<_ReplayOutcome> _replayOne(OutboxData entry) async {
    try {
      await _dio.request<dynamic>(
        entry.endpoint,
        data: jsonDecode(entry.body),
        options: Options(
          method: entry.method,
          headers: {'Idempotency-Key': entry.idempotencyKey},
        ),
      );
      await (_db.delete(_db.outbox)..where((t) => t.id.equals(entry.id))).go();
      return _ReplayOutcome.success;
    } on DioException catch (e) {
      final statusCode = e.response?.statusCode;
      final isRetryable = statusCode == null || // network-level failure, no response at all
          statusCode == 401 ||
          statusCode == 408 ||
          statusCode == 429 ||
          statusCode >= 500;

      await (_db.update(_db.outbox)..where((t) => t.id.equals(entry.id))).write(
        OutboxCompanion(
          status: Value(isRetryable ? 'pending' : 'failed'),
          attempts: Value(entry.attempts + 1),
          lastError: Value(e.message ?? e.toString()),
        ),
      );
      return isRetryable ? _ReplayOutcome.retryableFailure : _ReplayOutcome.permanentFailure;
    }
  }

  void dispose() {
    _connectivitySubscription.cancel();
  }
}
