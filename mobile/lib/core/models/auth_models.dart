import 'package:freezed_annotation/freezed_annotation.dart';

part 'auth_models.freezed.dart';
part 'auth_models.g.dart';

/// POST /auth/login and /auth/refresh (TokenResponse).
@freezed
abstract class TokenResponse with _$TokenResponse {
  const factory TokenResponse({
    @JsonKey(name: 'access_token') required String accessToken,
    @JsonKey(name: 'refresh_token') required String refreshToken,
    @JsonKey(name: 'token_type') @Default('bearer') String tokenType,
    @JsonKey(name: 'expires_in') required int expiresIn,
  }) = _TokenResponse;

  factory TokenResponse.fromJson(Map<String, dynamic> json) => _$TokenResponseFromJson(json);
}

/// GET /auth/me (UserResponse).
@freezed
abstract class UserProfile with _$UserProfile {
  const factory UserProfile({
    required String id,
    required String email,
    @JsonKey(name: 'display_name') String? displayName,
    String? phone,
    @JsonKey(name: 'account_type') required String accountType,
    @JsonKey(name: 'is_active') required bool isActive,
    @JsonKey(name: 'is_verified') required bool isVerified,
    // "conservative" | "balanced" | "aggressive"
    @JsonKey(name: 'risk_tolerance') required String riskTolerance,
    @JsonKey(name: 'onboarding_stage') required String onboardingStage,
  }) = _UserProfile;

  factory UserProfile.fromJson(Map<String, dynamic> json) => _$UserProfileFromJson(json);
}
