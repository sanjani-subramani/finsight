// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'recommended_action.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$RecommendedAction {

@JsonKey(name: 'action_type') String get actionType; String get label;@NullableDecimalConverter() Decimal? get amount;@JsonKey(name: 'expected_effect') String? get expectedEffect;@JsonKey(name: 'projected_risk_after') double? get projectedRiskAfter;
/// Create a copy of RecommendedAction
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecommendedActionCopyWith<RecommendedAction> get copyWith => _$RecommendedActionCopyWithImpl<RecommendedAction>(this as RecommendedAction, _$identity);

  /// Serializes this RecommendedAction to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as RecommendedAction;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecommendedAction&&(identical(other.actionType, _this.actionType) || other.actionType == _this.actionType)&&(identical(other.label, _this.label) || other.label == _this.label)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.expectedEffect, _this.expectedEffect) || other.expectedEffect == _this.expectedEffect)&&(identical(other.projectedRiskAfter, _this.projectedRiskAfter) || other.projectedRiskAfter == _this.projectedRiskAfter));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as RecommendedAction;
  return Object.hash(runtimeType,_this.actionType,_this.label,_this.amount,_this.expectedEffect,_this.projectedRiskAfter);
}

@override
String toString() {
  final _this = this as RecommendedAction;
  return 'RecommendedAction(actionType: ${_this.actionType}, label: ${_this.label}, amount: ${_this.amount}, expectedEffect: ${_this.expectedEffect}, projectedRiskAfter: ${_this.projectedRiskAfter})';
}


}

/// @nodoc
abstract mixin class $RecommendedActionCopyWith<$Res>  {
  factory $RecommendedActionCopyWith(RecommendedAction value, $Res Function(RecommendedAction) _then) = _$RecommendedActionCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'action_type') String actionType, String label,@NullableDecimalConverter() Decimal? amount,@JsonKey(name: 'expected_effect') String? expectedEffect,@JsonKey(name: 'projected_risk_after') double? projectedRiskAfter
});




}
/// @nodoc
class _$RecommendedActionCopyWithImpl<$Res>
    implements $RecommendedActionCopyWith<$Res> {
  _$RecommendedActionCopyWithImpl(this._self, this._then);

  final RecommendedAction _self;
  final $Res Function(RecommendedAction) _then;

/// Create a copy of RecommendedAction
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? actionType = null,Object? label = null,Object? amount = freezed,Object? expectedEffect = freezed,Object? projectedRiskAfter = freezed,}) {
  return _then(RecommendedAction(
actionType: null == actionType ? _self.actionType : actionType // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,amount: freezed == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedEffect: freezed == expectedEffect ? _self.expectedEffect : expectedEffect // ignore: cast_nullable_to_non_nullable
as String?,projectedRiskAfter: freezed == projectedRiskAfter ? _self.projectedRiskAfter : projectedRiskAfter // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [RecommendedAction].
extension RecommendedActionPatterns on RecommendedAction {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecommendedAction value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecommendedAction() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecommendedAction value)  $default,){
final _that = this;
switch (_that) {
case _RecommendedAction():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecommendedAction value)?  $default,){
final _that = this;
switch (_that) {
case _RecommendedAction() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'action_type')  String actionType,  String label, @NullableDecimalConverter()  Decimal? amount, @JsonKey(name: 'expected_effect')  String? expectedEffect, @JsonKey(name: 'projected_risk_after')  double? projectedRiskAfter)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecommendedAction() when $default != null:
return $default(_that.actionType,_that.label,_that.amount,_that.expectedEffect,_that.projectedRiskAfter);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'action_type')  String actionType,  String label, @NullableDecimalConverter()  Decimal? amount, @JsonKey(name: 'expected_effect')  String? expectedEffect, @JsonKey(name: 'projected_risk_after')  double? projectedRiskAfter)  $default,) {final _that = this;
switch (_that) {
case _RecommendedAction():
return $default(_that.actionType,_that.label,_that.amount,_that.expectedEffect,_that.projectedRiskAfter);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'action_type')  String actionType,  String label, @NullableDecimalConverter()  Decimal? amount, @JsonKey(name: 'expected_effect')  String? expectedEffect, @JsonKey(name: 'projected_risk_after')  double? projectedRiskAfter)?  $default,) {final _that = this;
switch (_that) {
case _RecommendedAction() when $default != null:
return $default(_that.actionType,_that.label,_that.amount,_that.expectedEffect,_that.projectedRiskAfter);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecommendedAction implements RecommendedAction {
  const _RecommendedAction({@JsonKey(name: 'action_type') required this.actionType, required this.label, @NullableDecimalConverter() this.amount, @JsonKey(name: 'expected_effect') this.expectedEffect, @JsonKey(name: 'projected_risk_after') this.projectedRiskAfter});
  factory _RecommendedAction.fromJson(Map<String, dynamic> json) => _$RecommendedActionFromJson(json);

@override@JsonKey(name: 'action_type') final  String actionType;
@override final  String label;
@override@NullableDecimalConverter() final  Decimal? amount;
@override@JsonKey(name: 'expected_effect') final  String? expectedEffect;
@override@JsonKey(name: 'projected_risk_after') final  double? projectedRiskAfter;

/// Create a copy of RecommendedAction
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecommendedActionCopyWith<_RecommendedAction> get copyWith => __$RecommendedActionCopyWithImpl<_RecommendedAction>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecommendedActionToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecommendedAction&&(identical(other.actionType, actionType) || other.actionType == actionType)&&(identical(other.label, label) || other.label == label)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.expectedEffect, expectedEffect) || other.expectedEffect == expectedEffect)&&(identical(other.projectedRiskAfter, projectedRiskAfter) || other.projectedRiskAfter == projectedRiskAfter));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,actionType,label,amount,expectedEffect,projectedRiskAfter);
}

@override
String toString() {
    return 'RecommendedAction(actionType: $actionType, label: $label, amount: $amount, expectedEffect: $expectedEffect, projectedRiskAfter: $projectedRiskAfter)';
}


}

/// @nodoc
abstract mixin class _$RecommendedActionCopyWith<$Res> implements $RecommendedActionCopyWith<$Res> {
  factory _$RecommendedActionCopyWith(_RecommendedAction value, $Res Function(_RecommendedAction) _then) = __$RecommendedActionCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'action_type') String actionType, String label,@NullableDecimalConverter() Decimal? amount,@JsonKey(name: 'expected_effect') String? expectedEffect,@JsonKey(name: 'projected_risk_after') double? projectedRiskAfter
});




}
/// @nodoc
class __$RecommendedActionCopyWithImpl<$Res>
    implements _$RecommendedActionCopyWith<$Res> {
  __$RecommendedActionCopyWithImpl(this._self, this._then);

  final _RecommendedAction _self;
  final $Res Function(_RecommendedAction) _then;

/// Create a copy of RecommendedAction
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? actionType = null,Object? label = null,Object? amount = freezed,Object? expectedEffect = freezed,Object? projectedRiskAfter = freezed,}) {
  return _then(_RecommendedAction(
actionType: null == actionType ? _self.actionType : actionType // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,amount: freezed == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as Decimal?,expectedEffect: freezed == expectedEffect ? _self.expectedEffect : expectedEffect // ignore: cast_nullable_to_non_nullable
as String?,projectedRiskAfter: freezed == projectedRiskAfter ? _self.projectedRiskAfter : projectedRiskAfter // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}

// dart format on
