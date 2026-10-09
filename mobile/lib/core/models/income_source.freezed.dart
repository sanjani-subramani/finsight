// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'income_source.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$IncomeSource {

 String get id; String get label; String? get counterparty;@JsonKey(name: 'declared_min')@NullableDecimalConverter() Decimal? get declaredMin;@JsonKey(name: 'declared_max')@NullableDecimalConverter() Decimal? get declaredMax;@JsonKey(name: 'declared_frequency_days') int? get declaredFrequencyDays;@JsonKey(name: 'observed_p10')@NullableDecimalConverter() Decimal? get observedP10;@JsonKey(name: 'observed_p50')@NullableDecimalConverter() Decimal? get observedP50;@JsonKey(name: 'observed_p90')@NullableDecimalConverter() Decimal? get observedP90;@JsonKey(name: 'observation_count') int get observationCount;@JsonKey(name: 'forecast_mode') String get forecastMode;@JsonKey(name: 'confidence_score')@DecimalConverter() Decimal get confidenceScore;
/// Create a copy of IncomeSource
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IncomeSourceCopyWith<IncomeSource> get copyWith => _$IncomeSourceCopyWithImpl<IncomeSource>(this as IncomeSource, _$identity);

  /// Serializes this IncomeSource to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as IncomeSource;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IncomeSource&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.label, _this.label) || other.label == _this.label)&&(identical(other.counterparty, _this.counterparty) || other.counterparty == _this.counterparty)&&(identical(other.declaredMin, _this.declaredMin) || other.declaredMin == _this.declaredMin)&&(identical(other.declaredMax, _this.declaredMax) || other.declaredMax == _this.declaredMax)&&(identical(other.declaredFrequencyDays, _this.declaredFrequencyDays) || other.declaredFrequencyDays == _this.declaredFrequencyDays)&&(identical(other.observedP10, _this.observedP10) || other.observedP10 == _this.observedP10)&&(identical(other.observedP50, _this.observedP50) || other.observedP50 == _this.observedP50)&&(identical(other.observedP90, _this.observedP90) || other.observedP90 == _this.observedP90)&&(identical(other.observationCount, _this.observationCount) || other.observationCount == _this.observationCount)&&(identical(other.forecastMode, _this.forecastMode) || other.forecastMode == _this.forecastMode)&&(identical(other.confidenceScore, _this.confidenceScore) || other.confidenceScore == _this.confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as IncomeSource;
  return Object.hash(runtimeType,_this.id,_this.label,_this.counterparty,_this.declaredMin,_this.declaredMax,_this.declaredFrequencyDays,_this.observedP10,_this.observedP50,_this.observedP90,_this.observationCount,_this.forecastMode,_this.confidenceScore);
}

@override
String toString() {
  final _this = this as IncomeSource;
  return 'IncomeSource(id: ${_this.id}, label: ${_this.label}, counterparty: ${_this.counterparty}, declaredMin: ${_this.declaredMin}, declaredMax: ${_this.declaredMax}, declaredFrequencyDays: ${_this.declaredFrequencyDays}, observedP10: ${_this.observedP10}, observedP50: ${_this.observedP50}, observedP90: ${_this.observedP90}, observationCount: ${_this.observationCount}, forecastMode: ${_this.forecastMode}, confidenceScore: ${_this.confidenceScore})';
}


}

/// @nodoc
abstract mixin class $IncomeSourceCopyWith<$Res>  {
  factory $IncomeSourceCopyWith(IncomeSource value, $Res Function(IncomeSource) _then) = _$IncomeSourceCopyWithImpl;
@useResult
$Res call({
 String id, String label, String? counterparty,@JsonKey(name: 'declared_min')@NullableDecimalConverter() Decimal? declaredMin,@JsonKey(name: 'declared_max')@NullableDecimalConverter() Decimal? declaredMax,@JsonKey(name: 'declared_frequency_days') int? declaredFrequencyDays,@JsonKey(name: 'observed_p10')@NullableDecimalConverter() Decimal? observedP10,@JsonKey(name: 'observed_p50')@NullableDecimalConverter() Decimal? observedP50,@JsonKey(name: 'observed_p90')@NullableDecimalConverter() Decimal? observedP90,@JsonKey(name: 'observation_count') int observationCount,@JsonKey(name: 'forecast_mode') String forecastMode,@JsonKey(name: 'confidence_score')@DecimalConverter() Decimal confidenceScore
});




}
/// @nodoc
class _$IncomeSourceCopyWithImpl<$Res>
    implements $IncomeSourceCopyWith<$Res> {
  _$IncomeSourceCopyWithImpl(this._self, this._then);

  final IncomeSource _self;
  final $Res Function(IncomeSource) _then;

/// Create a copy of IncomeSource
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? label = null,Object? counterparty = freezed,Object? declaredMin = freezed,Object? declaredMax = freezed,Object? declaredFrequencyDays = freezed,Object? observedP10 = freezed,Object? observedP50 = freezed,Object? observedP90 = freezed,Object? observationCount = null,Object? forecastMode = null,Object? confidenceScore = null,}) {
  return _then(IncomeSource(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,counterparty: freezed == counterparty ? _self.counterparty : counterparty // ignore: cast_nullable_to_non_nullable
as String?,declaredMin: freezed == declaredMin ? _self.declaredMin : declaredMin // ignore: cast_nullable_to_non_nullable
as Decimal?,declaredMax: freezed == declaredMax ? _self.declaredMax : declaredMax // ignore: cast_nullable_to_non_nullable
as Decimal?,declaredFrequencyDays: freezed == declaredFrequencyDays ? _self.declaredFrequencyDays : declaredFrequencyDays // ignore: cast_nullable_to_non_nullable
as int?,observedP10: freezed == observedP10 ? _self.observedP10 : observedP10 // ignore: cast_nullable_to_non_nullable
as Decimal?,observedP50: freezed == observedP50 ? _self.observedP50 : observedP50 // ignore: cast_nullable_to_non_nullable
as Decimal?,observedP90: freezed == observedP90 ? _self.observedP90 : observedP90 // ignore: cast_nullable_to_non_nullable
as Decimal?,observationCount: null == observationCount ? _self.observationCount : observationCount // ignore: cast_nullable_to_non_nullable
as int,forecastMode: null == forecastMode ? _self.forecastMode : forecastMode // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as Decimal,
  ));
}

}


/// Adds pattern-matching-related methods to [IncomeSource].
extension IncomeSourcePatterns on IncomeSource {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IncomeSource value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IncomeSource() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IncomeSource value)  $default,){
final _that = this;
switch (_that) {
case _IncomeSource():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IncomeSource value)?  $default,){
final _that = this;
switch (_that) {
case _IncomeSource() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String label,  String? counterparty, @JsonKey(name: 'declared_min')@NullableDecimalConverter()  Decimal? declaredMin, @JsonKey(name: 'declared_max')@NullableDecimalConverter()  Decimal? declaredMax, @JsonKey(name: 'declared_frequency_days')  int? declaredFrequencyDays, @JsonKey(name: 'observed_p10')@NullableDecimalConverter()  Decimal? observedP10, @JsonKey(name: 'observed_p50')@NullableDecimalConverter()  Decimal? observedP50, @JsonKey(name: 'observed_p90')@NullableDecimalConverter()  Decimal? observedP90, @JsonKey(name: 'observation_count')  int observationCount, @JsonKey(name: 'forecast_mode')  String forecastMode, @JsonKey(name: 'confidence_score')@DecimalConverter()  Decimal confidenceScore)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IncomeSource() when $default != null:
return $default(_that.id,_that.label,_that.counterparty,_that.declaredMin,_that.declaredMax,_that.declaredFrequencyDays,_that.observedP10,_that.observedP50,_that.observedP90,_that.observationCount,_that.forecastMode,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String label,  String? counterparty, @JsonKey(name: 'declared_min')@NullableDecimalConverter()  Decimal? declaredMin, @JsonKey(name: 'declared_max')@NullableDecimalConverter()  Decimal? declaredMax, @JsonKey(name: 'declared_frequency_days')  int? declaredFrequencyDays, @JsonKey(name: 'observed_p10')@NullableDecimalConverter()  Decimal? observedP10, @JsonKey(name: 'observed_p50')@NullableDecimalConverter()  Decimal? observedP50, @JsonKey(name: 'observed_p90')@NullableDecimalConverter()  Decimal? observedP90, @JsonKey(name: 'observation_count')  int observationCount, @JsonKey(name: 'forecast_mode')  String forecastMode, @JsonKey(name: 'confidence_score')@DecimalConverter()  Decimal confidenceScore)  $default,) {final _that = this;
switch (_that) {
case _IncomeSource():
return $default(_that.id,_that.label,_that.counterparty,_that.declaredMin,_that.declaredMax,_that.declaredFrequencyDays,_that.observedP10,_that.observedP50,_that.observedP90,_that.observationCount,_that.forecastMode,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String label,  String? counterparty, @JsonKey(name: 'declared_min')@NullableDecimalConverter()  Decimal? declaredMin, @JsonKey(name: 'declared_max')@NullableDecimalConverter()  Decimal? declaredMax, @JsonKey(name: 'declared_frequency_days')  int? declaredFrequencyDays, @JsonKey(name: 'observed_p10')@NullableDecimalConverter()  Decimal? observedP10, @JsonKey(name: 'observed_p50')@NullableDecimalConverter()  Decimal? observedP50, @JsonKey(name: 'observed_p90')@NullableDecimalConverter()  Decimal? observedP90, @JsonKey(name: 'observation_count')  int observationCount, @JsonKey(name: 'forecast_mode')  String forecastMode, @JsonKey(name: 'confidence_score')@DecimalConverter()  Decimal confidenceScore)?  $default,) {final _that = this;
switch (_that) {
case _IncomeSource() when $default != null:
return $default(_that.id,_that.label,_that.counterparty,_that.declaredMin,_that.declaredMax,_that.declaredFrequencyDays,_that.observedP10,_that.observedP50,_that.observedP90,_that.observationCount,_that.forecastMode,_that.confidenceScore);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IncomeSource implements IncomeSource {
  const _IncomeSource({required this.id, required this.label, this.counterparty, @JsonKey(name: 'declared_min')@NullableDecimalConverter() this.declaredMin, @JsonKey(name: 'declared_max')@NullableDecimalConverter() this.declaredMax, @JsonKey(name: 'declared_frequency_days') this.declaredFrequencyDays, @JsonKey(name: 'observed_p10')@NullableDecimalConverter() this.observedP10, @JsonKey(name: 'observed_p50')@NullableDecimalConverter() this.observedP50, @JsonKey(name: 'observed_p90')@NullableDecimalConverter() this.observedP90, @JsonKey(name: 'observation_count') required this.observationCount, @JsonKey(name: 'forecast_mode') required this.forecastMode, @JsonKey(name: 'confidence_score')@DecimalConverter() required this.confidenceScore});
  factory _IncomeSource.fromJson(Map<String, dynamic> json) => _$IncomeSourceFromJson(json);

@override final  String id;
@override final  String label;
@override final  String? counterparty;
@override@JsonKey(name: 'declared_min')@NullableDecimalConverter() final  Decimal? declaredMin;
@override@JsonKey(name: 'declared_max')@NullableDecimalConverter() final  Decimal? declaredMax;
@override@JsonKey(name: 'declared_frequency_days') final  int? declaredFrequencyDays;
@override@JsonKey(name: 'observed_p10')@NullableDecimalConverter() final  Decimal? observedP10;
@override@JsonKey(name: 'observed_p50')@NullableDecimalConverter() final  Decimal? observedP50;
@override@JsonKey(name: 'observed_p90')@NullableDecimalConverter() final  Decimal? observedP90;
@override@JsonKey(name: 'observation_count') final  int observationCount;
@override@JsonKey(name: 'forecast_mode') final  String forecastMode;
@override@JsonKey(name: 'confidence_score')@DecimalConverter() final  Decimal confidenceScore;

/// Create a copy of IncomeSource
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IncomeSourceCopyWith<_IncomeSource> get copyWith => __$IncomeSourceCopyWithImpl<_IncomeSource>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IncomeSourceToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _IncomeSource&&(identical(other.id, id) || other.id == id)&&(identical(other.label, label) || other.label == label)&&(identical(other.counterparty, counterparty) || other.counterparty == counterparty)&&(identical(other.declaredMin, declaredMin) || other.declaredMin == declaredMin)&&(identical(other.declaredMax, declaredMax) || other.declaredMax == declaredMax)&&(identical(other.declaredFrequencyDays, declaredFrequencyDays) || other.declaredFrequencyDays == declaredFrequencyDays)&&(identical(other.observedP10, observedP10) || other.observedP10 == observedP10)&&(identical(other.observedP50, observedP50) || other.observedP50 == observedP50)&&(identical(other.observedP90, observedP90) || other.observedP90 == observedP90)&&(identical(other.observationCount, observationCount) || other.observationCount == observationCount)&&(identical(other.forecastMode, forecastMode) || other.forecastMode == forecastMode)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,label,counterparty,declaredMin,declaredMax,declaredFrequencyDays,observedP10,observedP50,observedP90,observationCount,forecastMode,confidenceScore);
}

@override
String toString() {
    return 'IncomeSource(id: $id, label: $label, counterparty: $counterparty, declaredMin: $declaredMin, declaredMax: $declaredMax, declaredFrequencyDays: $declaredFrequencyDays, observedP10: $observedP10, observedP50: $observedP50, observedP90: $observedP90, observationCount: $observationCount, forecastMode: $forecastMode, confidenceScore: $confidenceScore)';
}


}

/// @nodoc
abstract mixin class _$IncomeSourceCopyWith<$Res> implements $IncomeSourceCopyWith<$Res> {
  factory _$IncomeSourceCopyWith(_IncomeSource value, $Res Function(_IncomeSource) _then) = __$IncomeSourceCopyWithImpl;
@override @useResult
$Res call({
 String id, String label, String? counterparty,@JsonKey(name: 'declared_min')@NullableDecimalConverter() Decimal? declaredMin,@JsonKey(name: 'declared_max')@NullableDecimalConverter() Decimal? declaredMax,@JsonKey(name: 'declared_frequency_days') int? declaredFrequencyDays,@JsonKey(name: 'observed_p10')@NullableDecimalConverter() Decimal? observedP10,@JsonKey(name: 'observed_p50')@NullableDecimalConverter() Decimal? observedP50,@JsonKey(name: 'observed_p90')@NullableDecimalConverter() Decimal? observedP90,@JsonKey(name: 'observation_count') int observationCount,@JsonKey(name: 'forecast_mode') String forecastMode,@JsonKey(name: 'confidence_score')@DecimalConverter() Decimal confidenceScore
});




}
/// @nodoc
class __$IncomeSourceCopyWithImpl<$Res>
    implements _$IncomeSourceCopyWith<$Res> {
  __$IncomeSourceCopyWithImpl(this._self, this._then);

  final _IncomeSource _self;
  final $Res Function(_IncomeSource) _then;

/// Create a copy of IncomeSource
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? label = null,Object? counterparty = freezed,Object? declaredMin = freezed,Object? declaredMax = freezed,Object? declaredFrequencyDays = freezed,Object? observedP10 = freezed,Object? observedP50 = freezed,Object? observedP90 = freezed,Object? observationCount = null,Object? forecastMode = null,Object? confidenceScore = null,}) {
  return _then(_IncomeSource(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,counterparty: freezed == counterparty ? _self.counterparty : counterparty // ignore: cast_nullable_to_non_nullable
as String?,declaredMin: freezed == declaredMin ? _self.declaredMin : declaredMin // ignore: cast_nullable_to_non_nullable
as Decimal?,declaredMax: freezed == declaredMax ? _self.declaredMax : declaredMax // ignore: cast_nullable_to_non_nullable
as Decimal?,declaredFrequencyDays: freezed == declaredFrequencyDays ? _self.declaredFrequencyDays : declaredFrequencyDays // ignore: cast_nullable_to_non_nullable
as int?,observedP10: freezed == observedP10 ? _self.observedP10 : observedP10 // ignore: cast_nullable_to_non_nullable
as Decimal?,observedP50: freezed == observedP50 ? _self.observedP50 : observedP50 // ignore: cast_nullable_to_non_nullable
as Decimal?,observedP90: freezed == observedP90 ? _self.observedP90 : observedP90 // ignore: cast_nullable_to_non_nullable
as Decimal?,observationCount: null == observationCount ? _self.observationCount : observationCount // ignore: cast_nullable_to_non_nullable
as int,forecastMode: null == forecastMode ? _self.forecastMode : forecastMode // ignore: cast_nullable_to_non_nullable
as String,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as Decimal,
  ));
}


}

// dart format on
