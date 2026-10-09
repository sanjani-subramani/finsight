import 'package:dio/dio.dart';

import '../auth/token_store.dart';
import '../models/auth_models.dart';

/// No caching here — tokens have their own dedicated secure store, and
/// /auth/me is cheap and always worth a fresh call when it's used.
class AuthRepository {
  AuthRepository({required Dio dio, required TokenStore tokenStore})
      : _dio = dio,
        _tokenStore = tokenStore;

  final Dio _dio;
  final TokenStore _tokenStore;

  Future<void> register({
    required String email,
    required String password,
    String? displayName,
    String riskTolerance = 'balanced',
  }) async {
    await _dio.post<Map<String, dynamic>>(
      '/auth/register',
      data: {
        'email': email,
        'password': password,
        if (displayName != null) 'display_name': displayName,
        'risk_tolerance': riskTolerance,
      },
    );
  }

  Future<void> login({required String email, required String password}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    final token = TokenResponse.fromJson(response.data!);
    await _tokenStore.saveTokens(
      accessToken: token.accessToken,
      refreshToken: token.refreshToken,
      expiresInSeconds: token.expiresIn,
    );
  }

  Future<void> logout() async {
    final refreshToken = await _tokenStore.readRefreshToken();
    try {
      if (refreshToken != null) {
        await _dio.post<void>('/auth/logout', data: {'refresh_token': refreshToken});
      }
    } finally {
      // Tokens are cleared locally even if the network call fails — the
      // user asked to log out; we don't make that conditional on
      // connectivity.
      await _tokenStore.clear();
    }
  }

  Future<UserProfile> me() async {
    final response = await _dio.get<Map<String, dynamic>>('/auth/me');
    return UserProfile.fromJson(response.data!);
  }

  /// PATCH /auth/me — "conservative" | "balanced" | "aggressive". Feeds
  /// directly into the Gate's tolerance adjustment and arbitration's
  /// reduction ordering on every future decision.
  Future<UserProfile> updateRiskTolerance(String riskTolerance) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/auth/me',
      data: {'risk_tolerance': riskTolerance},
    );
    return UserProfile.fromJson(response.data!);
  }

  Future<void> changePassword({required String oldPassword, required String newPassword}) async {
    await _dio.post<void>(
      '/auth/change-password',
      data: {'old_password': oldPassword, 'new_password': newPassword},
    );
  }

  Future<bool> isAuthenticated() => _tokenStore.hasTokens();
}
