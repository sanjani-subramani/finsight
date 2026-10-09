// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'income_forecast.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$IncomeForecast {

@JsonKey(name: 'expected_min')@NullableDecimalConverter() Decimal? get expectedMin;@JsonKey(name: 'expected_max')@NullableDecimalConverter() Decimal? get expectedMax;@NullableDecimalConverter() Decimal? get p10;@NullableDecimalConverter() Decimal? get p50;@NullableDecimalConverter() Decimal? get p90;@JsonKey(name: 'expected_arrival') DateTime? get expectedArrival;@JsonKey(name: 'arrival_uncertainty_days') int? get arrivalUncertaintyDays; String get source;@JsonKey(name: 'sample_size') int get sampleSize;@JsonKey(name: 'confidence_score') double get confidenceScore;
/// Create a copy of IncomeForecast
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IncomeForecastCopyWith<IncomeForecast> get copyWith => _$IncomeForecastCopyWithImpl<IncomeForecast>(this as IncomeForecast, _$identity);

  /// Serializes this IncomeForecast to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as IncomeForecast;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IncomeForecast&&(identical(other.expectedMin, _this.expectedMin) || other.expectedMin == _this.expectedMin)&&(identical(other.expectedMax, _this.expectedMax) || other.expectedMax == _this.expectedMax)&&(identical(other.p10, _this.p10) || other.p10 == _this.p10)&&(identical(other.p50, _this.p50) || other.p50 == _this.p50)&&(identical(other.p90, _this.p90) || other.p90 == _this.p90)&&(identical(other.expectedArrival, _this.expectedArrival) || other.expectedArrival == _this.expectedArrival)&&(identical(other.arrivalUncertaintyDays, _this.arrivalUncertaintyDays) || other.arrivalUncertaintyDays == _this.arrivalUncertaintyDays)&&(identical(other.source, _this.source) || other.source == _this.source)&&(identical(other.sampleSize, _this.sampleSize) || other.sampleSize == _this.sampleSize)&&(identical(other.confidenceScore, _this.confidenceScore) || other.confidenceScore == _this.confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as IncomeForecast;
  return Object.hash(runtimeType,_this.expectedMin,_this.expectedMax,_this.p10,_this.p50,_this.p90,_this.expectedArrival,_this.arrivalUncertaintyDays,_this.source,_this.sampleSize,_this.confidenceScore);
}

@override
String toString() {
  final _this = this as IncomeForecast;
  return 'IncomeForecast(expectedMin: ${_this.expectedMin}, expectedMax: ${_this.expectedMax}, p10: ${_this.p10}, p50: ${_this.p50}, p90: ${_this.p90}, expectedArrival: ${_this.expectedArrival}, arrivalUncertaintyDays: ${_this.arrivalUncertaintyDays}, source: ${_this.source}, sampleSize: ${_this.sampleSize}, confidenceScore: ${_this.confidenceScore})';
}


}

/// @nodoc
abstract mixin class $IncomeForecastCopyWith<$Res>  {
  factory $IncomeForecastCopyWith(IncomeForecast value, $Res Function(IncomeForecast) _then) = _$IncomeForecastCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'expected_min')@NullableDecimalConverter() Decimal? expectedMin,@JsonKey(name: 'expected_max')@NullableDecimalConverter() Decimal? expectedMax,@NullableDecimalConverter() Decimal? p10,@NullableDecimalConverter() Decimal? p50,@NullableDecimalConverter() Decimal? p90,@JsonKey(name: 'expected_arrival') DateTime? expectedArrival,@JsonKey(name: 'arrival_uncertainty_days') int? arrivalUncertaintyDays, String source,@JsonKey(name: 'sample_size') int sampleSize,@JsonKey(name: 'confidence_score') double confidenceScore
});




}
/// @nodoc
class _$IncomeForecastCopyWithImpl<$Res>
    implements $IncomeForecastCopyWith<$Res> {
  _$IncomeForecastCopyWithImpl(this._self, this._then);

  final IncomeForecast _self;
  final $Res Function(IncomeForecast) _then;

/// Create a copy of IncomeForecast
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? expectedMin = freezed,Object? expectedMax = freezed,Object? p10 = freezed,Object? p50 = freezed,Object? p90 = freezed,Object? expectedArrival = freezed,Object? arrivalUncertaintyDays = freezed,Object? source = null,Object? sampleSize = null,Object? confidenceScore = null,}) {
  return _then(IncomeForecast(
expectedMin: freezed == expectedMin ? _self.expectedMin : expectedMin // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedMax: freezed == expectedMax ? _self.expectedMax : expectedMax // ignore: cast_nullable_to_non_nullable
as Decimal?,p10: freezed == p10 ? _self.p10 : p10 // ignore: cast_nullable_to_non_nullable
as Decimal?,p50: freezed == p50 ? _self.p50 : p50 // ignore: cast_nullable_to_non_nullable
as Decimal?,p90: freezed == p90 ? _self.p90 : p90 // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedArrival: freezed == expectedArrival ? _self.expectedArrival : expectedArrival // ignore: cast_nullable_to_non_nullable
as DateTime?,arrivalUncertaintyDays: freezed == arrivalUncertaintyDays ? _self.arrivalUncertaintyDays : arrivalUncertaintyDays // ignore: cast_nullable_to_non_nullable
as int?,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,sampleSize: null == sampleSize ? _self.sampleSize : sampleSize // ignore: cast_nullable_to_non_nullable
as int,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [IncomeForecast].
extension IncomeForecastPatterns on IncomeForecast {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IncomeForecast value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IncomeForecast() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IncomeForecast value)  $default,){
final _that = this;
switch (_that) {
case _IncomeForecast():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IncomeForecast value)?  $default,){
final _that = this;
switch (_that) {
case _IncomeForecast() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'expected_min')@NullableDecimalConverter()  Decimal? expectedMin, @JsonKey(name: 'expected_max')@NullableDecimalConverter()  Decimal? expectedMax, @NullableDecimalConverter()  Decimal? p10, @NullableDecimalConverter()  Decimal? p50, @NullableDecimalConverter()  Decimal? p90, @JsonKey(name: 'expected_arrival')  DateTime? expectedArrival, @JsonKey(name: 'arrival_uncertainty_days')  int? arrivalUncertaintyDays,  String source, @JsonKey(name: 'sample_size')  int sampleSize, @JsonKey(name: 'confidence_score')  double confidenceScore)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IncomeForecast() when $default != null:
return $default(_that.expectedMin,_that.expectedMax,_that.p10,_that.p50,_that.p90,_that.expectedArrival,_that.arrivalUncertaintyDays,_that.source,_that.sampleSize,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'expected_min')@NullableDecimalConverter()  Decimal? expectedMin, @JsonKey(name: 'expected_max')@NullableDecimalConverter()  Decimal? expectedMax, @NullableDecimalConverter()  Decimal? p10, @NullableDecimalConverter()  Decimal? p50, @NullableDecimalConverter()  Decimal? p90, @JsonKey(name: 'expected_arrival')  DateTime? expectedArrival, @JsonKey(name: 'arrival_uncertainty_days')  int? arrivalUncertaintyDays,  String source, @JsonKey(name: 'sample_size')  int sampleSize, @JsonKey(name: 'confidence_score')  double confidenceScore)  $default,) {final _that = this;
switch (_that) {
case _IncomeForecast():
return $default(_that.expectedMin,_that.expectedMax,_that.p10,_that.p50,_that.p90,_that.expectedArrival,_that.arrivalUncertaintyDays,_that.source,_that.sampleSize,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'expected_min')@NullableDecimalConverter()  Decimal? expectedMin, @JsonKey(name: 'expected_max')@NullableDecimalConverter()  Decimal? expectedMax, @NullableDecimalConverter()  Decimal? p10, @NullableDecimalConverter()  Decimal? p50, @NullableDecimalConverter()  Decimal? p90, @JsonKey(name: 'expected_arrival')  DateTime? expectedArrival, @JsonKey(name: 'arrival_uncertainty_days')  int? arrivalUncertaintyDays,  String source, @JsonKey(name: 'sample_size')  int sampleSize, @JsonKey(name: 'confidence_score')  double confidenceScore)?  $default,) {final _that = this;
switch (_that) {
case _IncomeForecast() when $default != null:
return $default(_that.expectedMin,_that.expectedMax,_that.p10,_that.p50,_that.p90,_that.expectedArrival,_that.arrivalUncertaintyDays,_that.source,_that.sampleSize,_that.confidenceScore);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IncomeForecast implements IncomeForecast {
  const _IncomeForecast({@JsonKey(name: 'expected_min')@NullableDecimalConverter() this.expectedMin, @JsonKey(name: 'expected_max')@NullableDecimalConverter() this.expectedMax, @NullableDecimalConverter() this.p10, @NullableDecimalConverter() this.p50, @NullableDecimalConverter() this.p90, @JsonKey(name: 'expected_arrival') this.expectedArrival, @JsonKey(name: 'arrival_uncertainty_days') this.arrivalUncertaintyDays, required this.source, @JsonKey(name: 'sample_size') this.sampleSize = 0, @JsonKey(name: 'confidence_score') required this.confidenceScore});
  factory _IncomeForecast.fromJson(Map<String, dynamic> json) => _$IncomeForecastFromJson(json);

@override@JsonKey(name: 'expected_min')@NullableDecimalConverter() final  Decimal? expectedMin;
@override@JsonKey(name: 'expected_max')@NullableDecimalConverter() final  Decimal? expectedMax;
@override@NullableDecimalConverter() final  Decimal? p10;
@override@NullableDecimalConverter() final  Decimal? p50;
@override@NullableDecimalConverter() final  Decimal? p90;
@override@JsonKey(name: 'expected_arrival') final  DateTime? expectedArrival;
@override@JsonKey(name: 'arrival_uncertainty_days') final  int? arrivalUncertaintyDays;
@override final  String source;
@override@JsonKey(name: 'sample_size') final  int sampleSize;
@override@JsonKey(name: 'confidence_score') final  double confidenceScore;

/// Create a copy of IncomeForecast
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IncomeForecastCopyWith<_IncomeForecast> get copyWith => __$IncomeForecastCopyWithImpl<_IncomeForecast>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IncomeForecastToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _IncomeForecast&&(identical(other.expectedMin, expectedMin) || other.expectedMin == expectedMin)&&(identical(other.expectedMax, expectedMax) || other.expectedMax == expectedMax)&&(identical(other.p10, p10) || other.p10 == p10)&&(identical(other.p50, p50) || other.p50 == p50)&&(identical(other.p90, p90) || other.p90 == p90)&&(identical(other.expectedArrival, expectedArrival) || other.expectedArrival == expectedArrival)&&(identical(other.arrivalUncertaintyDays, arrivalUncertaintyDays) || other.arrivalUncertaintyDays == arrivalUncertaintyDays)&&(identical(other.source, source) || other.source == source)&&(identical(other.sampleSize, sampleSize) || other.sampleSize == sampleSize)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,expectedMin,expectedMax,p10,p50,p90,expectedArrival,arrivalUncertaintyDays,source,sampleSize,confidenceScore);
}

@override
String toString() {
    return 'IncomeForecast(expectedMin: $expectedMin, expectedMax: $expectedMax, p10: $p10, p50: $p50, p90: $p90, expectedArrival: $expectedArrival, arrivalUncertaintyDays: $arrivalUncertaintyDays, source: $source, sampleSize: $sampleSize, confidenceScore: $confidenceScore)';
}


}

/// @nodoc
abstract mixin class _$IncomeForecastCopyWith<$Res> implements $IncomeForecastCopyWith<$Res> {
  factory _$IncomeForecastCopyWith(_IncomeForecast value, $Res Function(_IncomeForecast) _then) = __$IncomeForecastCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'expected_min')@NullableDecimalConverter() Decimal? expectedMin,@JsonKey(name: 'expected_max')@NullableDecimalConverter() Decimal? expectedMax,@NullableDecimalConverter() Decimal? p10,@NullableDecimalConverter() Decimal? p50,@NullableDecimalConverter() Decimal? p90,@JsonKey(name: 'expected_arrival') DateTime? expectedArrival,@JsonKey(name: 'arrival_uncertainty_days') int? arrivalUncertaintyDays, String source,@JsonKey(name: 'sample_size') int sampleSize,@JsonKey(name: 'confidence_score') double confidenceScore
});




}
/// @nodoc
class __$IncomeForecastCopyWithImpl<$Res>
    implements _$IncomeForecastCopyWith<$Res> {
  __$IncomeForecastCopyWithImpl(this._self, this._then);

  final _IncomeForecast _self;
  final $Res Function(_IncomeForecast) _then;

/// Create a copy of IncomeForecast
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? expectedMin = freezed,Object? expectedMax = freezed,Object? p10 = freezed,Object? p50 = freezed,Object? p90 = freezed,Object? expectedArrival = freezed,Object? arrivalUncertaintyDays = freezed,Object? source = null,Object? sampleSize = null,Object? confidenceScore = null,}) {
  return _then(_IncomeForecast(
expectedMin: freezed == expectedMin ? _self.expectedMin : expectedMin // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedMax: freezed == expectedMax ? _self.expectedMax : expectedMax // ignore: cast_nullable_to_non_nullable
as Decimal?,p10: freezed == p10 ? _self.p10 : p10 // ignore: cast_nullable_to_non_nullable
as Decimal?,p50: freezed == p50 ? _self.p50 : p50 // ignore: cast_nullable_to_non_nullable
as Decimal?,p90: freezed == p90 ? _self.p90 : p90 // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedArrival: freezed == expectedArrival ? _self.expectedArrival : expectedArrival // ignore: cast_nullable_to_non_nullable
as DateTime?,arrivalUncertaintyDays: freezed == arrivalUncertaintyDays ? _self.arrivalUncertaintyDays : arrivalUncertaintyDays // ignore: cast_nullable_to_non_nullable
as int?,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,sampleSize: null == sampleSize ? _self.sampleSize : sampleSize // ignore: cast_nullable_to_non_nullable
as int,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
