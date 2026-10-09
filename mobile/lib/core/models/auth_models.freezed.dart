// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'auth_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TokenResponse {

@JsonKey(name: 'access_token') String get accessToken;@JsonKey(name: 'refresh_token') String get refreshToken;@JsonKey(name: 'token_type') String get tokenType;@JsonKey(name: 'expires_in') int get expiresIn;
/// Create a copy of TokenResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TokenResponseCopyWith<TokenResponse> get copyWith => _$TokenResponseCopyWithImpl<TokenResponse>(this as TokenResponse, _$identity);

  /// Serializes this TokenResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as TokenResponse;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TokenResponse&&(identical(other.accessToken, _this.accessToken) || other.accessToken == _this.accessToken)&&(identical(other.refreshToken, _this.refreshToken) || other.refreshToken == _this.refreshToken)&&(identical(other.tokenType, _this.tokenType) || other.tokenType == _this.tokenType)&&(identical(other.expiresIn, _this.expiresIn) || other.expiresIn == _this.expiresIn));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as TokenResponse;
  return Object.hash(runtimeType,_this.accessToken,_this.refreshToken,_this.tokenType,_this.expiresIn);
}

@override
String toString() {
  final _this = this as TokenResponse;
  return 'TokenResponse(accessToken: ${_this.accessToken}, refreshToken: ${_this.refreshToken}, tokenType: ${_this.tokenType}, expiresIn: ${_this.expiresIn})';
}


}

/// @nodoc
abstract mixin class $TokenResponseCopyWith<$Res>  {
  factory $TokenResponseCopyWith(TokenResponse value, $Res Function(TokenResponse) _then) = _$TokenResponseCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'refresh_token') String refreshToken,@JsonKey(name: 'token_type') String tokenType,@JsonKey(name: 'expires_in') int expiresIn
});




}
/// @nodoc
class _$TokenResponseCopyWithImpl<$Res>
    implements $TokenResponseCopyWith<$Res> {
  _$TokenResponseCopyWithImpl(this._self, this._then);

  final TokenResponse _self;
  final $Res Function(TokenResponse) _then;

/// Create a copy of TokenResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? accessToken = null,Object? refreshToken = null,Object? tokenType = null,Object? expiresIn = null,}) {
  return _then(TokenResponse(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,refreshToken: null == refreshToken ? _self.refreshToken : refreshToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: null == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String,expiresIn: null == expiresIn ? _self.expiresIn : expiresIn // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [TokenResponse].
extension TokenResponsePatterns on TokenResponse {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TokenResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TokenResponse() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TokenResponse value)  $default,){
final _that = this;
switch (_that) {
case _TokenResponse():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TokenResponse value)?  $default,){
final _that = this;
switch (_that) {
case _TokenResponse() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in')  int expiresIn)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TokenResponse() when $default != null:
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.expiresIn);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in')  int expiresIn)  $default,) {final _that = this;
switch (_that) {
case _TokenResponse():
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.expiresIn);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'access_token')  String accessToken, @JsonKey(name: 'refresh_token')  String refreshToken, @JsonKey(name: 'token_type')  String tokenType, @JsonKey(name: 'expires_in')  int expiresIn)?  $default,) {final _that = this;
switch (_that) {
case _TokenResponse() when $default != null:
return $default(_that.accessToken,_that.refreshToken,_that.tokenType,_that.expiresIn);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TokenResponse implements TokenResponse {
  const _TokenResponse({@JsonKey(name: 'access_token') required this.accessToken, @JsonKey(name: 'refresh_token') required this.refreshToken, @JsonKey(name: 'token_type') this.tokenType = 'bearer', @JsonKey(name: 'expires_in') required this.expiresIn});
  factory _TokenResponse.fromJson(Map<String, dynamic> json) => _$TokenResponseFromJson(json);

@override@JsonKey(name: 'access_token') final  String accessToken;
@override@JsonKey(name: 'refresh_token') final  String refreshToken;
@override@JsonKey(name: 'token_type') final  String tokenType;
@override@JsonKey(name: 'expires_in') final  int expiresIn;

/// Create a copy of TokenResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TokenResponseCopyWith<_TokenResponse> get copyWith => __$TokenResponseCopyWithImpl<_TokenResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TokenResponseToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _TokenResponse&&(identical(other.accessToken, accessToken) || other.accessToken == accessToken)&&(identical(other.refreshToken, refreshToken) || other.refreshToken == refreshToken)&&(identical(other.tokenType, tokenType) || other.tokenType == tokenType)&&(identical(other.expiresIn, expiresIn) || other.expiresIn == expiresIn));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,accessToken,refreshToken,tokenType,expiresIn);
}

@override
String toString() {
    return 'TokenResponse(accessToken: $accessToken, refreshToken: $refreshToken, tokenType: $tokenType, expiresIn: $expiresIn)';
}


}

/// @nodoc
abstract mixin class _$TokenResponseCopyWith<$Res> implements $TokenResponseCopyWith<$Res> {
  factory _$TokenResponseCopyWith(_TokenResponse value, $Res Function(_TokenResponse) _then) = __$TokenResponseCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'access_token') String accessToken,@JsonKey(name: 'refresh_token') String refreshToken,@JsonKey(name: 'token_type') String tokenType,@JsonKey(name: 'expires_in') int expiresIn
});




}
/// @nodoc
class __$TokenResponseCopyWithImpl<$Res>
    implements _$TokenResponseCopyWith<$Res> {
  __$TokenResponseCopyWithImpl(this._self, this._then);

  final _TokenResponse _self;
  final $Res Function(_TokenResponse) _then;

/// Create a copy of TokenResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? accessToken = null,Object? refreshToken = null,Object? tokenType = null,Object? expiresIn = null,}) {
  return _then(_TokenResponse(
accessToken: null == accessToken ? _self.accessToken : accessToken // ignore: cast_nullable_to_non_nullable
as String,refreshToken: null == refreshToken ? _self.refreshToken : refreshToken // ignore: cast_nullable_to_non_nullable
as String,tokenType: null == tokenType ? _self.tokenType : tokenType // ignore: cast_nullable_to_non_nullable
as String,expiresIn: null == expiresIn ? _self.expiresIn : expiresIn // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$UserProfile {

 String get id; String get email;@JsonKey(name: 'display_name') String? get displayName; String? get phone;@JsonKey(name: 'account_type') String get accountType;@JsonKey(name: 'is_active') bool get isActive;@JsonKey(name: 'is_verified') bool get isVerified;@JsonKey(name: 'risk_tolerance') String get riskTolerance;@JsonKey(name: 'onboarding_stage') String get onboardingStage;
/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserProfileCopyWith<UserProfile> get copyWith => _$UserProfileCopyWithImpl<UserProfile>(this as UserProfile, _$identity);

  /// Serializes this UserProfile to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as UserProfile;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserProfile&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.email, _this.email) || other.email == _this.email)&&(identical(other.displayName, _this.displayName) || other.displayName == _this.displayName)&&(identical(other.phone, _this.phone) || other.phone == _this.phone)&&(identical(other.accountType, _this.accountType) || other.accountType == _this.accountType)&&(identical(other.isActive, _this.isActive) || other.isActive == _this.isActive)&&(identical(other.isVerified, _this.isVerified) || other.isVerified == _this.isVerified)&&(identical(other.riskTolerance, _this.riskTolerance) || other.riskTolerance == _this.riskTolerance)&&(identical(other.onboardingStage, _this.onboardingStage) || other.onboardingStage == _this.onboardingStage));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as UserProfile;
  return Object.hash(runtimeType,_this.id,_this.email,_this.displayName,_this.phone,_this.accountType,_this.isActive,_this.isVerified,_this.riskTolerance,_this.onboardingStage);
}

@override
String toString() {
  final _this = this as UserProfile;
  return 'UserProfile(id: ${_this.id}, email: ${_this.email}, displayName: ${_this.displayName}, phone: ${_this.phone}, accountType: ${_this.accountType}, isActive: ${_this.isActive}, isVerified: ${_this.isVerified}, riskTolerance: ${_this.riskTolerance}, onboardingStage: ${_this.onboardingStage})';
}


}

/// @nodoc
abstract mixin class $UserProfileCopyWith<$Res>  {
  factory $UserProfileCopyWith(UserProfile value, $Res Function(UserProfile) _then) = _$UserProfileCopyWithImpl;
@useResult
$Res call({
 String id, String email,@JsonKey(name: 'display_name') String? displayName, String? phone,@JsonKey(name: 'account_type') String accountType,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'is_verified') bool isVerified,@JsonKey(name: 'risk_tolerance') String riskTolerance,@JsonKey(name: 'onboarding_stage') String onboardingStage
});




}
/// @nodoc
class _$UserProfileCopyWithImpl<$Res>
    implements $UserProfileCopyWith<$Res> {
  _$UserProfileCopyWithImpl(this._self, this._then);

  final UserProfile _self;
  final $Res Function(UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? email = null,Object? displayName = freezed,Object? phone = freezed,Object? accountType = null,Object? isActive = null,Object? isVerified = null,Object? riskTolerance = null,Object? onboardingStage = null,}) {
  return _then(UserProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,phone: freezed == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String?,accountType: null == accountType ? _self.accountType : accountType // ignore: cast_nullable_to_non_nullable
as String,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,riskTolerance: null == riskTolerance ? _self.riskTolerance : riskTolerance // ignore: cast_nullable_to_non_nullable
as String,onboardingStage: null == onboardingStage ? _self.onboardingStage : onboardingStage // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [UserProfile].
extension UserProfilePatterns on UserProfile {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _UserProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _UserProfile value)  $default,){
final _that = this;
switch (_that) {
case _UserProfile():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _UserProfile value)?  $default,){
final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String email, @JsonKey(name: 'display_name')  String? displayName,  String? phone, @JsonKey(name: 'account_type')  String accountType, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'is_verified')  bool isVerified, @JsonKey(name: 'risk_tolerance')  String riskTolerance, @JsonKey(name: 'onboarding_stage')  String onboardingStage)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that.id,_that.email,_that.displayName,_that.phone,_that.accountType,_that.isActive,_that.isVerified,_that.riskTolerance,_that.onboardingStage);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String email, @JsonKey(name: 'display_name')  String? displayName,  String? phone, @JsonKey(name: 'account_type')  String accountType, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'is_verified')  bool isVerified, @JsonKey(name: 'risk_tolerance')  String riskTolerance, @JsonKey(name: 'onboarding_stage')  String onboardingStage)  $default,) {final _that = this;
switch (_that) {
case _UserProfile():
return $default(_that.id,_that.email,_that.displayName,_that.phone,_that.accountType,_that.isActive,_that.isVerified,_that.riskTolerance,_that.onboardingStage);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String email, @JsonKey(name: 'display_name')  String? displayName,  String? phone, @JsonKey(name: 'account_type')  String accountType, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'is_verified')  bool isVerified, @JsonKey(name: 'risk_tolerance')  String riskTolerance, @JsonKey(name: 'onboarding_stage')  String onboardingStage)?  $default,) {final _that = this;
switch (_that) {
case _UserProfile() when $default != null:
return $default(_that.id,_that.email,_that.displayName,_that.phone,_that.accountType,_that.isActive,_that.isVerified,_that.riskTolerance,_that.onboardingStage);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _UserProfile implements UserProfile {
  const _UserProfile({required this.id, required this.email, @JsonKey(name: 'display_name') this.displayName, this.phone, @JsonKey(name: 'account_type') required this.accountType, @JsonKey(name: 'is_active') required this.isActive, @JsonKey(name: 'is_verified') required this.isVerified, @JsonKey(name: 'risk_tolerance') required this.riskTolerance, @JsonKey(name: 'onboarding_stage') required this.onboardingStage});
  factory _UserProfile.fromJson(Map<String, dynamic> json) => _$UserProfileFromJson(json);

@override final  String id;
@override final  String email;
@override@JsonKey(name: 'display_name') final  String? displayName;
@override final  String? phone;
@override@JsonKey(name: 'account_type') final  String accountType;
@override@JsonKey(name: 'is_active') final  bool isActive;
@override@JsonKey(name: 'is_verified') final  bool isVerified;
@override@JsonKey(name: 'risk_tolerance') final  String riskTolerance;
@override@JsonKey(name: 'onboarding_stage') final  String onboardingStage;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserProfileCopyWith<_UserProfile> get copyWith => __$UserProfileCopyWithImpl<_UserProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserProfileToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserProfile&&(identical(other.id, id) || other.id == id)&&(identical(other.email, email) || other.email == email)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.phone, phone) || other.phone == phone)&&(identical(other.accountType, accountType) || other.accountType == accountType)&&(identical(other.isActive, isActive) || other.isActive == isActive)&&(identical(other.isVerified, isVerified) || other.isVerified == isVerified)&&(identical(other.riskTolerance, riskTolerance) || other.riskTolerance == riskTolerance)&&(identical(other.onboardingStage, onboardingStage) || other.onboardingStage == onboardingStage));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,email,displayName,phone,accountType,isActive,isVerified,riskTolerance,onboardingStage);
}

@override
String toString() {
    return 'UserProfile(id: $id, email: $email, displayName: $displayName, phone: $phone, accountType: $accountType, isActive: $isActive, isVerified: $isVerified, riskTolerance: $riskTolerance, onboardingStage: $onboardingStage)';
}


}

/// @nodoc
abstract mixin class _$UserProfileCopyWith<$Res> implements $UserProfileCopyWith<$Res> {
  factory _$UserProfileCopyWith(_UserProfile value, $Res Function(_UserProfile) _then) = __$UserProfileCopyWithImpl;
@override @useResult
$Res call({
 String id, String email,@JsonKey(name: 'display_name') String? displayName, String? phone,@JsonKey(name: 'account_type') String accountType,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'is_verified') bool isVerified,@JsonKey(name: 'risk_tolerance') String riskTolerance,@JsonKey(name: 'onboarding_stage') String onboardingStage
});




}
/// @nodoc
class __$UserProfileCopyWithImpl<$Res>
    implements _$UserProfileCopyWith<$Res> {
  __$UserProfileCopyWithImpl(this._self, this._then);

  final _UserProfile _self;
  final $Res Function(_UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? email = null,Object? displayName = freezed,Object? phone = freezed,Object? accountType = null,Object? isActive = null,Object? isVerified = null,Object? riskTolerance = null,Object? onboardingStage = null,}) {
  return _then(_UserProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,email: null == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,phone: freezed == phone ? _self.phone : phone // ignore: cast_nullable_to_non_nullable
as String?,accountType: null == accountType ? _self.accountType : accountType // ignore: cast_nullable_to_non_nullable
as String,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,riskTolerance: null == riskTolerance ? _self.riskTolerance : riskTolerance // ignore: cast_nullable_to_non_nullable
as String,onboardingStage: null == onboardingStage ? _self.onboardingStage : onboardingStage // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
