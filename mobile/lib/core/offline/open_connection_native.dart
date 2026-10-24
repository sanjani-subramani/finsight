/// Native (Android / iOS / desktop) database connection.
///
/// Uses dart:ffi via drift's NativeDatabase — a direct FFI binding to the
/// SQLite C library bundled by sqlite3_flutter_libs.  This file is NEVER
/// compiled for web targets thanks to the conditional import in
/// app_database.dart, so the dart:ffi import here doesn't break web builds.
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

QueryExecutor openConnection() {
  return LazyDatabase(() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File(p.join(dir.path, 'finsentinel.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
