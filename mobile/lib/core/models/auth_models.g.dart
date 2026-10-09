// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TokenResponse _$TokenResponseFromJson(Map<String, dynamic> json) =>
    _TokenResponse(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: (json['expires_in'] as num).toInt(),
    );

Map<String, dynamic> _$TokenResponseToJson(_TokenResponse instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
      'token_type': instance.tokenType,
      'expires_in': instance.expiresIn,
    };

_UserProfile _$UserProfileFromJson(Map<String, dynamic> json) => _UserProfile(
  id: json['id'] as String,
  email: json['email'] as String,
  displayName: json['display_name'] as String?,
  phone: json['phone'] as String?,
  accountType: json['account_type'] as String,
  isActive: json['is_active'] as bool,
  isVerified: json['is_verified'] as bool,
  riskTolerance: json['risk_tolerance'] as String,
  onboardingStage: json['onboarding_stage'] as String,
);

Map<String, dynamic> _$UserProfileToJson(_UserProfile instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'display_name': instance.displayName,
      'phone': instance.phone,
      'account_type': instance.accountType,
      'is_active': instance.isActive,
      'is_verified': instance.isVerified,
      'risk_tolerance': instance.riskTolerance,
      'onboarding_stage': instance.onboardingStage,
    };
