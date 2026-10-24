/// Web database connection.
///
/// Uses drift's WasmDatabase — a WebAssembly build of SQLite that runs
/// entirely inside the browser, storing data in IndexedDB.  This file is
/// only compiled for web targets (the conditional import in
/// app_database.dart picks it via `dart.library.js_interop`).
///
/// At runtime the database needs two files served from the web root:
///   • sqlite3.wasm   — the SQLite WASM binary
///   • drift_worker.js — the drift web-worker script
///
/// Generate them once with:
///   dart run drift_dev make_web
///
/// If those files are missing the database will fail lazily (when the
/// first query runs), but the UI will still render and navigate —
/// offline caching simply won't work, which is fine for initial testing.
import 'package:drift/drift.dart';
import 'package:drift/wasm.dart';

QueryExecutor openConnection() {
  return DatabaseConnection.delayed(Future(() async {
    final result = await WasmDatabase.open(
      databaseName: 'finsentinel',
      sqlite3Uri: Uri.parse('sqlite3.wasm'),
      driftWorkerUri: Uri.parse('drift_worker.js'),
    );
    return result.resolvedExecutor;
  }));
}
