import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

part 'app_database.g.dart';

/// One row per cached payload (keyed by a caller-chosen cache key, e.g.
/// "twin_snapshot:`<user_id>`") — the fallback shown when the network is
/// unavailable, ALWAYS paired with a visible staleness marker (see
/// CacheStatus in lib/core/repositories/cache_status.dart). Showing
/// cached financial data with no indication it might be stale is the
/// worst failure mode in a finance app: the user makes a decision on a
/// number that is no longer true.
class CachedSnapshots extends Table {
  TextColumn get cacheKey => text()();
  TextColumn get userId => text()();
  TextColumn get payload => text()(); // raw JSON
  DateTimeColumn get fetchedAt => dateTime()();

  @override
  Set<Column<Object>> get primaryKey => {cacheKey};
}

/// A queued write made while offline (or that failed transiently),
/// replayed in creation order once connectivity returns.
///
/// Every queued write carries a client-generated idempotency key that is
/// reused verbatim on every replay attempt — this is exactly why
/// POST /ingest/manual REQUIRES an Idempotency-Key header
/// (app/platform/idempotency.py on the backend): if the app queues a
/// write, goes offline before confirming success, and later replays it,
/// the server must be able to tell "this is the same request I may have
/// already processed" from "this is a genuinely new one." Without a
/// stable key reused across retries, a flaky connection could silently
/// double-create the same expense entry.
class Outbox extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get endpoint => text()();
  TextColumn get method => text()();
  TextColumn get body => text()(); // raw JSON
  TextColumn get idempotencyKey => text()();
  DateTimeColumn get createdAt => dateTime()();
  IntColumn get attempts => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
  // "pending" | "failed" — a permanently failed entry (a genuine 4xx
  // that isn't 401/408/429) is surfaced to the user rather than retried
  // forever.
  TextColumn get status => text().withDefault(const Constant('pending'))();
}

@DriftDatabase(tables: [CachedSnapshots, Outbox])
class AppDatabase extends _$AppDatabase {
  AppDatabase([QueryExecutor? executor]) : super(executor ?? _openConnection());

  @override
  int get schemaVersion => 1;

  static QueryExecutor _openConnection() {
    return LazyDatabase(() async {
      final dir = await getApplicationDocumentsDirectory();
      final file = File(p.join(dir.path, 'finsentinel.sqlite'));
      return NativeDatabase.createInBackground(file);
    });
  }
}
