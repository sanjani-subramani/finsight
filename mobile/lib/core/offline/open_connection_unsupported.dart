/// Fallback stub — compiled only when neither dart:io (native) nor
/// dart:js_interop (web) is available, which shouldn't happen in
/// practice with Flutter's supported targets.
import 'package:drift/drift.dart';

QueryExecutor openConnection() {
  throw UnsupportedError(
    'No drift database implementation for this platform. '
    'Supported: Android, iOS, desktop (via dart:ffi) and web (via WASM).',
  );
}
