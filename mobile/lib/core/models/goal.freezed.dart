// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'goal.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Goal {

@JsonKey(name: 'goal_id') String get goalId; String get label;@JsonKey(name: 'target_amount')@DecimalConverter() Decimal get targetAmount;@JsonKey(name: 'saved_amount')@DecimalConverter() Decimal get savedAmount;@JsonKey(name: 'target_date') DateTime? get targetDate; int get priority;@JsonKey(name: 'is_flexible') bool get isFlexible;
/// Create a copy of Goal
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GoalCopyWith<Goal> get copyWith => _$GoalCopyWithImpl<Goal>(this as Goal, _$identity);

  /// Serializes this Goal to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Goal;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Goal&&(identical(other.goalId, _this.goalId) || other.goalId == _this.goalId)&&(identical(other.label, _this.label) || other.label == _this.label)&&(identical(other.targetAmount, _this.targetAmount) || other.targetAmount == _this.targetAmount)&&(identical(other.savedAmount, _this.savedAmount) || other.savedAmount == _this.savedAmount)&&(identical(other.targetDate, _this.targetDate) || other.targetDate == _this.targetDate)&&(identical(other.priority, _this.priority) || other.priority == _this.priority)&&(identical(other.isFlexible, _this.isFlexible) || other.isFlexible == _this.isFlexible));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Goal;
  return Object.hash(runtimeType,_this.goalId,_this.label,_this.targetAmount,_this.savedAmount,_this.targetDate,_this.priority,_this.isFlexible);
}

@override
String toString() {
  final _this = this as Goal;
  return 'Goal(goalId: ${_this.goalId}, label: ${_this.label}, targetAmount: ${_this.targetAmount}, savedAmount: ${_this.savedAmount}, targetDate: ${_this.targetDate}, priority: ${_this.priority}, isFlexible: ${_this.isFlexible})';
}


}

/// @nodoc
abstract mixin class $GoalCopyWith<$Res>  {
  factory $GoalCopyWith(Goal value, $Res Function(Goal) _then) = _$GoalCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'goal_id') String goalId, String label,@JsonKey(name: 'target_amount')@DecimalConverter() Decimal targetAmount,@JsonKey(name: 'saved_amount')@DecimalConverter() Decimal savedAmount,@JsonKey(name: 'target_date') DateTime? targetDate, int priority,@JsonKey(name: 'is_flexible') bool isFlexible
});




}
/// @nodoc
class _$GoalCopyWithImpl<$Res>
    implements $GoalCopyWith<$Res> {
  _$GoalCopyWithImpl(this._self, this._then);

  final Goal _self;
  final $Res Function(Goal) _then;

/// Create a copy of Goal
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? goalId = null,Object? label = null,Object? targetAmount = null,Object? savedAmount = null,Object? targetDate = freezed,Object? priority = null,Object? isFlexible = null,}) {
  return _then(Goal(
goalId: null == goalId ? _self.goalId : goalId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,targetAmount: null == targetAmount ? _self.targetAmount : targetAmount // ignore: cast_nullable_to_non_nullable
as Decimal,savedAmount: null == savedAmount ? _self.savedAmount : savedAmount // ignore: cast_nullable_to_non_nullable
as Decimal,targetDate: freezed == targetDate ? _self.targetDate : targetDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priority: null == priority ? _self.priority : priority // ignore: cast_nullable_to_non_nullable
as int,isFlexible: null == isFlexible ? _self.isFlexible : isFlexible // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Goal].
extension GoalPatterns on Goal {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Goal value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Goal() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Goal value)  $default,){
final _that = this;
switch (_that) {
case _Goal():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Goal value)?  $default,){
final _that = this;
switch (_that) {
case _Goal() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'goal_id')  String goalId,  String label, @JsonKey(name: 'target_amount')@DecimalConverter()  Decimal targetAmount, @JsonKey(name: 'saved_amount')@DecimalConverter()  Decimal savedAmount, @JsonKey(name: 'target_date')  DateTime? targetDate,  int priority, @JsonKey(name: 'is_flexible')  bool isFlexible)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Goal() when $default != null:
return $default(_that.goalId,_that.label,_that.targetAmount,_that.savedAmount,_that.targetDate,_that.priority,_that.isFlexible);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'goal_id')  String goalId,  String label, @JsonKey(name: 'target_amount')@DecimalConverter()  Decimal targetAmount, @JsonKey(name: 'saved_amount')@DecimalConverter()  Decimal savedAmount, @JsonKey(name: 'target_date')  DateTime? targetDate,  int priority, @JsonKey(name: 'is_flexible')  bool isFlexible)  $default,) {final _that = this;
switch (_that) {
case _Goal():
return $default(_that.goalId,_that.label,_that.targetAmount,_that.savedAmount,_that.targetDate,_that.priority,_that.isFlexible);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'goal_id')  String goalId,  String label, @JsonKey(name: 'target_amount')@DecimalConverter()  Decimal targetAmount, @JsonKey(name: 'saved_amount')@DecimalConverter()  Decimal savedAmount, @JsonKey(name: 'target_date')  DateTime? targetDate,  int priority, @JsonKey(name: 'is_flexible')  bool isFlexible)?  $default,) {final _that = this;
switch (_that) {
case _Goal() when $default != null:
return $default(_that.goalId,_that.label,_that.targetAmount,_that.savedAmount,_that.targetDate,_that.priority,_that.isFlexible);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Goal implements Goal {
  const _Goal({@JsonKey(name: 'goal_id') required this.goalId, required this.label, @JsonKey(name: 'target_amount')@DecimalConverter() required this.targetAmount, @JsonKey(name: 'saved_amount')@DecimalConverter() required this.savedAmount, @JsonKey(name: 'target_date') this.targetDate, required this.priority, @JsonKey(name: 'is_flexible') required this.isFlexible});
  factory _Goal.fromJson(Map<String, dynamic> json) => _$GoalFromJson(json);

@override@JsonKey(name: 'goal_id') final  String goalId;
@override final  String label;
@override@JsonKey(name: 'target_amount')@DecimalConverter() final  Decimal targetAmount;
@override@JsonKey(name: 'saved_amount')@DecimalConverter() final  Decimal savedAmount;
@override@JsonKey(name: 'target_date') final  DateTime? targetDate;
@override final  int priority;
@override@JsonKey(name: 'is_flexible') final  bool isFlexible;

/// Create a copy of Goal
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GoalCopyWith<_Goal> get copyWith => __$GoalCopyWithImpl<_Goal>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GoalToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Goal&&(identical(other.goalId, goalId) || other.goalId == goalId)&&(identical(other.label, label) || other.label == label)&&(identical(other.targetAmount, targetAmount) || other.targetAmount == targetAmount)&&(identical(other.savedAmount, savedAmount) || other.savedAmount == savedAmount)&&(identical(other.targetDate, targetDate) || other.targetDate == targetDate)&&(identical(other.priority, priority) || other.priority == priority)&&(identical(other.isFlexible, isFlexible) || other.isFlexible == isFlexible));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,goalId,label,targetAmount,savedAmount,targetDate,priority,isFlexible);
}

@override
String toString() {
    return 'Goal(goalId: $goalId, label: $label, targetAmount: $targetAmount, savedAmount: $savedAmount, targetDate: $targetDate, priority: $priority, isFlexible: $isFlexible)';
}


}

/// @nodoc
abstract mixin class _$GoalCopyWith<$Res> implements $GoalCopyWith<$Res> {
  factory _$GoalCopyWith(_Goal value, $Res Function(_Goal) _then) = __$GoalCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'goal_id') String goalId, String label,@JsonKey(name: 'target_amount')@DecimalConverter() Decimal targetAmount,@JsonKey(name: 'saved_amount')@DecimalConverter() Decimal savedAmount,@JsonKey(name: 'target_date') DateTime? targetDate, int priority,@JsonKey(name: 'is_flexible') bool isFlexible
});




}
/// @nodoc
class __$GoalCopyWithImpl<$Res>
    implements _$GoalCopyWith<$Res> {
  __$GoalCopyWithImpl(this._self, this._then);

  final _Goal _self;
  final $Res Function(_Goal) _then;

/// Create a copy of Goal
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? goalId = null,Object? label = null,Object? targetAmount = null,Object? savedAmount = null,Object? targetDate = freezed,Object? priority = null,Object? isFlexible = null,}) {
  return _then(_Goal(
goalId: null == goalId ? _self.goalId : goalId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,targetAmount: null == targetAmount ? _self.targetAmount : targetAmount // ignore: cast_nullable_to_non_nullable
as Decimal,savedAmount: null == savedAmount ? _self.savedAmount : savedAmount // ignore: cast_nullable_to_non_nullable
as Decimal,targetDate: freezed == targetDate ? _self.targetDate : targetDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priority: null == priority ? _self.priority : priority // ignore: cast_nullable_to_non_nullable
as int,isFlexible: null == isFlexible ? _self.isFlexible : isFlexible // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
