import 'package:drift/drift.dart';

// Conditional import: the Dart compiler picks exactly ONE of these
// files depending on which platform libraries are available.
//
// • dart.library.io        → native (Android / iOS / desktop)
//   Uses NativeDatabase backed by dart:ffi — fast, file-backed SQLite.
//
// • dart.library.js_interop → web (Chrome / Edge)
//   Uses WasmDatabase — SQLite compiled to WebAssembly, stored in
//   IndexedDB.  Needs sqlite3.wasm + drift_worker.js served from the
//   web root (generate with `dart run drift_dev make_web`).
//
// • fallback               → unsupported platform (throws)
//
// This pattern is the standard Dart way to avoid importing dart:ffi on
// web (which would fail at compile time).
import 'open_connection_unsupported.dart'
    if (dart.library.io) 'open_connection_native.dart'
    if (dart.library.js_interop) 'open_connection_web.dart';

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
  AppDatabase([QueryExecutor? executor]) : super(executor ?? openConnection());

  @override
  int get schemaVersion => 1;
}
