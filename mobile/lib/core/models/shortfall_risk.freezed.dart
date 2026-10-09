// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'shortfall_risk.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ShortfallRisk {

@JsonKey(name: 'horizon_days') int get horizonDays; double get probability;@JsonKey(name: 'first_breach_date') DateTime? get firstBreachDate;@JsonKey(name: 'worst_case_balance')@DecimalConverter() Decimal get worstCaseBalance;@JsonKey(name: 'scenarios_run') int get scenariosRun;
/// Create a copy of ShortfallRisk
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShortfallRiskCopyWith<ShortfallRisk> get copyWith => _$ShortfallRiskCopyWithImpl<ShortfallRisk>(this as ShortfallRisk, _$identity);

  /// Serializes this ShortfallRisk to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ShortfallRisk;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShortfallRisk&&(identical(other.horizonDays, _this.horizonDays) || other.horizonDays == _this.horizonDays)&&(identical(other.probability, _this.probability) || other.probability == _this.probability)&&(identical(other.firstBreachDate, _this.firstBreachDate) || other.firstBreachDate == _this.firstBreachDate)&&(identical(other.worstCaseBalance, _this.worstCaseBalance) || other.worstCaseBalance == _this.worstCaseBalance)&&(identical(other.scenariosRun, _this.scenariosRun) || other.scenariosRun == _this.scenariosRun));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ShortfallRisk;
  return Object.hash(runtimeType,_this.horizonDays,_this.probability,_this.firstBreachDate,_this.worstCaseBalance,_this.scenariosRun);
}

@override
String toString() {
  final _this = this as ShortfallRisk;
  return 'ShortfallRisk(horizonDays: ${_this.horizonDays}, probability: ${_this.probability}, firstBreachDate: ${_this.firstBreachDate}, worstCaseBalance: ${_this.worstCaseBalance}, scenariosRun: ${_this.scenariosRun})';
}


}

/// @nodoc
abstract mixin class $ShortfallRiskCopyWith<$Res>  {
  factory $ShortfallRiskCopyWith(ShortfallRisk value, $Res Function(ShortfallRisk) _then) = _$ShortfallRiskCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'horizon_days') int horizonDays, double probability,@JsonKey(name: 'first_breach_date') DateTime? firstBreachDate,@JsonKey(name: 'worst_case_balance')@DecimalConverter() Decimal worstCaseBalance,@JsonKey(name: 'scenarios_run') int scenariosRun
});




}
/// @nodoc
class _$ShortfallRiskCopyWithImpl<$Res>
    implements $ShortfallRiskCopyWith<$Res> {
  _$ShortfallRiskCopyWithImpl(this._self, this._then);

  final ShortfallRisk _self;
  final $Res Function(ShortfallRisk) _then;

/// Create a copy of ShortfallRisk
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? horizonDays = null,Object? probability = null,Object? firstBreachDate = freezed,Object? worstCaseBalance = null,Object? scenariosRun = null,}) {
  return _then(ShortfallRisk(
horizonDays: null == horizonDays ? _self.horizonDays : horizonDays // ignore: cast_nullable_to_non_nullable
as int,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,firstBreachDate: freezed == firstBreachDate ? _self.firstBreachDate : firstBreachDate // ignore: cast_nullable_to_non_nullable
as DateTime?,worstCaseBalance: null == worstCaseBalance ? _self.worstCaseBalance : worstCaseBalance // ignore: cast_nullable_to_non_nullable
as Decimal,scenariosRun: null == scenariosRun ? _self.scenariosRun : scenariosRun // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ShortfallRisk].
extension ShortfallRiskPatterns on ShortfallRisk {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShortfallRisk value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShortfallRisk() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShortfallRisk value)  $default,){
final _that = this;
switch (_that) {
case _ShortfallRisk():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShortfallRisk value)?  $default,){
final _that = this;
switch (_that) {
case _ShortfallRisk() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'horizon_days')  int horizonDays,  double probability, @JsonKey(name: 'first_breach_date')  DateTime? firstBreachDate, @JsonKey(name: 'worst_case_balance')@DecimalConverter()  Decimal worstCaseBalance, @JsonKey(name: 'scenarios_run')  int scenariosRun)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShortfallRisk() when $default != null:
return $default(_that.horizonDays,_that.probability,_that.firstBreachDate,_that.worstCaseBalance,_that.scenariosRun);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'horizon_days')  int horizonDays,  double probability, @JsonKey(name: 'first_breach_date')  DateTime? firstBreachDate, @JsonKey(name: 'worst_case_balance')@DecimalConverter()  Decimal worstCaseBalance, @JsonKey(name: 'scenarios_run')  int scenariosRun)  $default,) {final _that = this;
switch (_that) {
case _ShortfallRisk():
return $default(_that.horizonDays,_that.probability,_that.firstBreachDate,_that.worstCaseBalance,_that.scenariosRun);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'horizon_days')  int horizonDays,  double probability, @JsonKey(name: 'first_breach_date')  DateTime? firstBreachDate, @JsonKey(name: 'worst_case_balance')@DecimalConverter()  Decimal worstCaseBalance, @JsonKey(name: 'scenarios_run')  int scenariosRun)?  $default,) {final _that = this;
switch (_that) {
case _ShortfallRisk() when $default != null:
return $default(_that.horizonDays,_that.probability,_that.firstBreachDate,_that.worstCaseBalance,_that.scenariosRun);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShortfallRisk implements ShortfallRisk {
  const _ShortfallRisk({@JsonKey(name: 'horizon_days') required this.horizonDays, required this.probability, @JsonKey(name: 'first_breach_date') this.firstBreachDate, @JsonKey(name: 'worst_case_balance')@DecimalConverter() required this.worstCaseBalance, @JsonKey(name: 'scenarios_run') required this.scenariosRun});
  factory _ShortfallRisk.fromJson(Map<String, dynamic> json) => _$ShortfallRiskFromJson(json);

@override@JsonKey(name: 'horizon_days') final  int horizonDays;
@override final  double probability;
@override@JsonKey(name: 'first_breach_date') final  DateTime? firstBreachDate;
@override@JsonKey(name: 'worst_case_balance')@DecimalConverter() final  Decimal worstCaseBalance;
@override@JsonKey(name: 'scenarios_run') final  int scenariosRun;

/// Create a copy of ShortfallRisk
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShortfallRiskCopyWith<_ShortfallRisk> get copyWith => __$ShortfallRiskCopyWithImpl<_ShortfallRisk>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShortfallRiskToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShortfallRisk&&(identical(other.horizonDays, horizonDays) || other.horizonDays == horizonDays)&&(identical(other.probability, probability) || other.probability == probability)&&(identical(other.firstBreachDate, firstBreachDate) || other.firstBreachDate == firstBreachDate)&&(identical(other.worstCaseBalance, worstCaseBalance) || other.worstCaseBalance == worstCaseBalance)&&(identical(other.scenariosRun, scenariosRun) || other.scenariosRun == scenariosRun));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,horizonDays,probability,firstBreachDate,worstCaseBalance,scenariosRun);
}

@override
String toString() {
    return 'ShortfallRisk(horizonDays: $horizonDays, probability: $probability, firstBreachDate: $firstBreachDate, worstCaseBalance: $worstCaseBalance, scenariosRun: $scenariosRun)';
}


}

/// @nodoc
abstract mixin class _$ShortfallRiskCopyWith<$Res> implements $ShortfallRiskCopyWith<$Res> {
  factory _$ShortfallRiskCopyWith(_ShortfallRisk value, $Res Function(_ShortfallRisk) _then) = __$ShortfallRiskCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'horizon_days') int horizonDays, double probability,@JsonKey(name: 'first_breach_date') DateTime? firstBreachDate,@JsonKey(name: 'worst_case_balance')@DecimalConverter() Decimal worstCaseBalance,@JsonKey(name: 'scenarios_run') int scenariosRun
});




}
/// @nodoc
class __$ShortfallRiskCopyWithImpl<$Res>
    implements _$ShortfallRiskCopyWith<$Res> {
  __$ShortfallRiskCopyWithImpl(this._self, this._then);

  final _ShortfallRisk _self;
  final $Res Function(_ShortfallRisk) _then;

/// Create a copy of ShortfallRisk
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? horizonDays = null,Object? probability = null,Object? firstBreachDate = freezed,Object? worstCaseBalance = null,Object? scenariosRun = null,}) {
  return _then(_ShortfallRisk(
horizonDays: null == horizonDays ? _self.horizonDays : horizonDays // ignore: cast_nullable_to_non_nullable
as int,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,firstBreachDate: freezed == firstBreachDate ? _self.firstBreachDate : firstBreachDate // ignore: cast_nullable_to_non_nullable
as DateTime?,worstCaseBalance: null == worstCaseBalance ? _self.worstCaseBalance : worstCaseBalance // ignore: cast_nullable_to_non_nullable
as Decimal,scenariosRun: null == scenariosRun ? _self.scenariosRun : scenariosRun // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
