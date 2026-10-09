import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// A minimal storage seam TokenStore depends on, instead of the concrete
/// FlutterSecureStorage class directly. FlutterSecureStorage bridges to a
/// platform channel internally, which has no in-memory substitute for
/// tests without a full plugin-binding setup; depending on this small
/// interface instead lets tests supply a trivial in-memory fake (see
/// test/test_utils/fake_secure_storage.dart) while production code uses
/// [SecureStorageAdapter], a thin wrapper around the real thing.
abstract class SecureStorage {
  Future<void> write(String key, String value);
  Future<String?> read(String key);
  Future<void> delete(String key);
}

/// Production implementation: OS-level secure store (Android Keystore /
/// iOS Keychain) — NEVER SharedPreferences.
///
/// SharedPreferences (and its iOS counterpart via the same plugin API)
/// backs onto a PLAINTEXT file on disk. Anyone with filesystem access to
/// a rooted/jailbroken device, an adb backup, or a misconfigured cloud
/// backup can read it directly with no decryption needed at all. An
/// access/refresh token pair is a bearer credential for this user's
/// entire financial account — storing it anywhere that doesn't at
/// minimum encrypt at rest and gate access behind the platform's own
/// credential store is unacceptable for a finance app. flutter_secure_
/// storage (Keystore-backed on Android, Keychain-backed on iOS) is the
/// correct primitive for exactly this reason; nothing in this app ever
/// touches SharedPreferences, and it must stay that way.
class SecureStorageAdapter implements SecureStorage {
  SecureStorageAdapter([FlutterSecureStorage? storage])
      : _storage = storage ??
            // AndroidOptions() always uses AES-GCM + RSA-OAEP key wrapping
            // as of flutter_secure_storage 10+ — there is no longer a
            // toggle for it, encryption at rest is unconditional.
            const FlutterSecureStorage(aOptions: AndroidOptions());

  final FlutterSecureStorage _storage;

  @override
  Future<void> write(String key, String value) => _storage.write(key: key, value: value);

  @override
  Future<String?> read(String key) => _storage.read(key: key);

  @override
  Future<void> delete(String key) => _storage.delete(key: key);
}

/// Persists auth tokens via [SecureStorage].
class TokenStore {
  TokenStore({SecureStorage? storage}) : _storage = storage ?? SecureStorageAdapter();

  final SecureStorage _storage;

  static const _accessTokenKey = 'fs_access_token';
  static const _refreshTokenKey = 'fs_refresh_token';
  static const _expiresAtKey = 'fs_access_token_expires_at';

  /// If the access token expires within this window, ApiClient refreshes
  /// it proactively rather than waiting to be rejected with a 401 —
  /// saves a round trip for the common case, while the 401 path remains
  /// as a safety net for clock skew or a token that lapses early.
  static const proactiveRefreshWindow = Duration(seconds: 60);

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
    required int expiresInSeconds,
  }) async {
    final expiresAt = DateTime.now().toUtc().add(Duration(seconds: expiresInSeconds));
    await Future.wait([
      _storage.write(_accessTokenKey, accessToken),
      _storage.write(_refreshTokenKey, refreshToken),
      _storage.write(_expiresAtKey, expiresAt.toIso8601String()),
    ]);
  }

  Future<String?> readAccessToken() => _storage.read(_accessTokenKey);

  Future<String?> readRefreshToken() => _storage.read(_refreshTokenKey);

  Future<DateTime?> readExpiresAt() async {
    final raw = await _storage.read(_expiresAtKey);
    if (raw == null) return null;
    return DateTime.tryParse(raw);
  }

  /// True if there's no known expiry, the token already expired, or it
  /// will expire within [proactiveRefreshWindow].
  Future<bool> needsProactiveRefresh() async {
    final expiresAt = await readExpiresAt();
    if (expiresAt == null) return true;
    return DateTime.now().toUtc().add(proactiveRefreshWindow).isAfter(expiresAt);
  }

  Future<bool> hasTokens() async {
    final access = await readAccessToken();
    final refresh = await readRefreshToken();
    return access != null && refresh != null;
  }

  Future<void> clear() async {
    await Future.wait([
      _storage.delete(_accessTokenKey),
      _storage.delete(_refreshTokenKey),
      _storage.delete(_expiresAtKey),
    ]);
  }
}
