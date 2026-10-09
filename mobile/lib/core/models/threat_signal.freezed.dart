// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'threat_signal.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ThreatSignal {

 String get name; String get category; double get weight; String? get evidence; String get detector;
/// Create a copy of ThreatSignal
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ThreatSignalCopyWith<ThreatSignal> get copyWith => _$ThreatSignalCopyWithImpl<ThreatSignal>(this as ThreatSignal, _$identity);

  /// Serializes this ThreatSignal to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ThreatSignal;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ThreatSignal&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.category, _this.category) || other.category == _this.category)&&(identical(other.weight, _this.weight) || other.weight == _this.weight)&&(identical(other.evidence, _this.evidence) || other.evidence == _this.evidence)&&(identical(other.detector, _this.detector) || other.detector == _this.detector));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ThreatSignal;
  return Object.hash(runtimeType,_this.name,_this.category,_this.weight,_this.evidence,_this.detector);
}

@override
String toString() {
  final _this = this as ThreatSignal;
  return 'ThreatSignal(name: ${_this.name}, category: ${_this.category}, weight: ${_this.weight}, evidence: ${_this.evidence}, detector: ${_this.detector})';
}


}

/// @nodoc
abstract mixin class $ThreatSignalCopyWith<$Res>  {
  factory $ThreatSignalCopyWith(ThreatSignal value, $Res Function(ThreatSignal) _then) = _$ThreatSignalCopyWithImpl;
@useResult
$Res call({
 String name, String category, double weight, String? evidence, String detector
});




}
/// @nodoc
class _$ThreatSignalCopyWithImpl<$Res>
    implements $ThreatSignalCopyWith<$Res> {
  _$ThreatSignalCopyWithImpl(this._self, this._then);

  final ThreatSignal _self;
  final $Res Function(ThreatSignal) _then;

/// Create a copy of ThreatSignal
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? category = null,Object? weight = null,Object? evidence = freezed,Object? detector = null,}) {
  return _then(ThreatSignal(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,evidence: freezed == evidence ? _self.evidence : evidence // ignore: cast_nullable_to_non_nullable
as String?,detector: null == detector ? _self.detector : detector // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ThreatSignal].
extension ThreatSignalPatterns on ThreatSignal {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ThreatSignal value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ThreatSignal() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ThreatSignal value)  $default,){
final _that = this;
switch (_that) {
case _ThreatSignal():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ThreatSignal value)?  $default,){
final _that = this;
switch (_that) {
case _ThreatSignal() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String category,  double weight,  String? evidence,  String detector)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ThreatSignal() when $default != null:
return $default(_that.name,_that.category,_that.weight,_that.evidence,_that.detector);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String category,  double weight,  String? evidence,  String detector)  $default,) {final _that = this;
switch (_that) {
case _ThreatSignal():
return $default(_that.name,_that.category,_that.weight,_that.evidence,_that.detector);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String category,  double weight,  String? evidence,  String detector)?  $default,) {final _that = this;
switch (_that) {
case _ThreatSignal() when $default != null:
return $default(_that.name,_that.category,_that.weight,_that.evidence,_that.detector);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ThreatSignal implements ThreatSignal {
  const _ThreatSignal({required this.name, required this.category, required this.weight, this.evidence, required this.detector});
  factory _ThreatSignal.fromJson(Map<String, dynamic> json) => _$ThreatSignalFromJson(json);

@override final  String name;
@override final  String category;
@override final  double weight;
@override final  String? evidence;
@override final  String detector;

/// Create a copy of ThreatSignal
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ThreatSignalCopyWith<_ThreatSignal> get copyWith => __$ThreatSignalCopyWithImpl<_ThreatSignal>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ThreatSignalToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ThreatSignal&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.weight, weight) || other.weight == weight)&&(identical(other.evidence, evidence) || other.evidence == evidence)&&(identical(other.detector, detector) || other.detector == detector));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,name,category,weight,evidence,detector);
}

@override
String toString() {
    return 'ThreatSignal(name: $name, category: $category, weight: $weight, evidence: $evidence, detector: $detector)';
}


}

/// @nodoc
abstract mixin class _$ThreatSignalCopyWith<$Res> implements $ThreatSignalCopyWith<$Res> {
  factory _$ThreatSignalCopyWith(_ThreatSignal value, $Res Function(_ThreatSignal) _then) = __$ThreatSignalCopyWithImpl;
@override @useResult
$Res call({
 String name, String category, double weight, String? evidence, String detector
});




}
/// @nodoc
class __$ThreatSignalCopyWithImpl<$Res>
    implements _$ThreatSignalCopyWith<$Res> {
  __$ThreatSignalCopyWithImpl(this._self, this._then);

  final _ThreatSignal _self;
  final $Res Function(_ThreatSignal) _then;

/// Create a copy of ThreatSignal
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? category = null,Object? weight = null,Object? evidence = freezed,Object? detector = null,}) {
  return _then(_ThreatSignal(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,evidence: freezed == evidence ? _self.evidence : evidence // ignore: cast_nullable_to_non_nullable
as String?,detector: null == detector ? _self.detector : detector // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
