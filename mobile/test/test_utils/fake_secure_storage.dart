import 'package:finsentinel/core/auth/token_store.dart';

/// A trivial in-memory [SecureStorage] for tests — no platform channel,
/// fully synchronous under the hood, fully deterministic.
class FakeSecureStorage implements SecureStorage {
  final Map<String, String> _values = {};

  @override
  Future<void> write(String key, String value) async {
    _values[key] = value;
  }

  @override
  Future<String?> read(String key) async => _values[key];

  @override
  Future<void> delete(String key) async {
    _values.remove(key);
  }
}
