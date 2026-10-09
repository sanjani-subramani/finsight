// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'trace_step.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TraceStep {

 int get order; String get stage; String get statement; Map<String, dynamic> get values;
/// Create a copy of TraceStep
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TraceStepCopyWith<TraceStep> get copyWith => _$TraceStepCopyWithImpl<TraceStep>(this as TraceStep, _$identity);

  /// Serializes this TraceStep to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as TraceStep;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TraceStep&&(identical(other.order, _this.order) || other.order == _this.order)&&(identical(other.stage, _this.stage) || other.stage == _this.stage)&&(identical(other.statement, _this.statement) || other.statement == _this.statement)&&const DeepCollectionEquality().equals(other.values, _this.values));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as TraceStep;
  return Object.hash(runtimeType,_this.order,_this.stage,_this.statement,const DeepCollectionEquality().hash(_this.values));
}

@override
String toString() {
  final _this = this as TraceStep;
  return 'TraceStep(order: ${_this.order}, stage: ${_this.stage}, statement: ${_this.statement}, values: ${_this.values})';
}


}

/// @nodoc
abstract mixin class $TraceStepCopyWith<$Res>  {
  factory $TraceStepCopyWith(TraceStep value, $Res Function(TraceStep) _then) = _$TraceStepCopyWithImpl;
@useResult
$Res call({
 int order, String stage, String statement, Map<String, dynamic> values
});




}
/// @nodoc
class _$TraceStepCopyWithImpl<$Res>
    implements $TraceStepCopyWith<$Res> {
  _$TraceStepCopyWithImpl(this._self, this._then);

  final TraceStep _self;
  final $Res Function(TraceStep) _then;

/// Create a copy of TraceStep
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? order = null,Object? stage = null,Object? statement = null,Object? values = null,}) {
  return _then(TraceStep(
order: null == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int,stage: null == stage ? _self.stage : stage // ignore: cast_nullable_to_non_nullable
as String,statement: null == statement ? _self.statement : statement // ignore: cast_nullable_to_non_nullable
as String,values: null == values ? _self.values : values // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [TraceStep].
extension TraceStepPatterns on TraceStep {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TraceStep value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TraceStep() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TraceStep value)  $default,){
final _that = this;
switch (_that) {
case _TraceStep():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TraceStep value)?  $default,){
final _that = this;
switch (_that) {
case _TraceStep() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int order,  String stage,  String statement,  Map<String, dynamic> values)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TraceStep() when $default != null:
return $default(_that.order,_that.stage,_that.statement,_that.values);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int order,  String stage,  String statement,  Map<String, dynamic> values)  $default,) {final _that = this;
switch (_that) {
case _TraceStep():
return $default(_that.order,_that.stage,_that.statement,_that.values);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int order,  String stage,  String statement,  Map<String, dynamic> values)?  $default,) {final _that = this;
switch (_that) {
case _TraceStep() when $default != null:
return $default(_that.order,_that.stage,_that.statement,_that.values);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TraceStep implements TraceStep {
  const _TraceStep({required this.order, required this.stage, required this.statement,  Map<String, dynamic> values = const {}}): _values = values;
  factory _TraceStep.fromJson(Map<String, dynamic> json) => _$TraceStepFromJson(json);

@override final  int order;
@override final  String stage;
@override final  String statement;
 final  Map<String, dynamic> _values;
@override@JsonKey() Map<String, dynamic> get values {
  if (_values is EqualUnmodifiableMapView) return _values;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_values);
}


/// Create a copy of TraceStep
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TraceStepCopyWith<_TraceStep> get copyWith => __$TraceStepCopyWithImpl<_TraceStep>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TraceStepToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _TraceStep&&(identical(other.order, order) || other.order == order)&&(identical(other.stage, stage) || other.stage == stage)&&(identical(other.statement, statement) || other.statement == statement)&&const DeepCollectionEquality().equals(other.values, _values));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,order,stage,statement,const DeepCollectionEquality().hash(_values));
}

@override
String toString() {
    return 'TraceStep(order: $order, stage: $stage, statement: $statement, values: $values)';
}


}

/// @nodoc
abstract mixin class _$TraceStepCopyWith<$Res> implements $TraceStepCopyWith<$Res> {
  factory _$TraceStepCopyWith(_TraceStep value, $Res Function(_TraceStep) _then) = __$TraceStepCopyWithImpl;
@override @useResult
$Res call({
 int order, String stage, String statement, Map<String, dynamic> values
});




}
/// @nodoc
class __$TraceStepCopyWithImpl<$Res>
    implements _$TraceStepCopyWith<$Res> {
  __$TraceStepCopyWithImpl(this._self, this._then);

  final _TraceStep _self;
  final $Res Function(_TraceStep) _then;

/// Create a copy of TraceStep
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? order = null,Object? stage = null,Object? statement = null,Object? values = null,}) {
  return _then(_TraceStep(
order: null == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int,stage: null == stage ? _self.stage : stage // ignore: cast_nullable_to_non_nullable
as String,statement: null == statement ? _self.statement : statement // ignore: cast_nullable_to_non_nullable
as String,values: null == values ? _self._values : values // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
