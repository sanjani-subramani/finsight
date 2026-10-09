// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'obligation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Obligation {

@JsonKey(name: 'obligation_id') String get obligationId; String get label;@DecimalConverter() Decimal get amount;@JsonKey(name: 'due_date') DateTime get dueDate; String? get category;@JsonKey(name: 'is_fixed') bool get isFixed;@JsonKey(name: 'is_paid') bool get isPaid;@JsonKey(name: 'confidence_score') double get confidenceScore;
/// Create a copy of Obligation
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ObligationCopyWith<Obligation> get copyWith => _$ObligationCopyWithImpl<Obligation>(this as Obligation, _$identity);

  /// Serializes this Obligation to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as Obligation;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Obligation&&(identical(other.obligationId, _this.obligationId) || other.obligationId == _this.obligationId)&&(identical(other.label, _this.label) || other.label == _this.label)&&(identical(other.amount, _this.amount) || other.amount == _this.amount)&&(identical(other.dueDate, _this.dueDate) || other.dueDate == _this.dueDate)&&(identical(other.category, _this.category) || other.category == _this.category)&&(identical(other.isFixed, _this.isFixed) || other.isFixed == _this.isFixed)&&(identical(other.isPaid, _this.isPaid) || other.isPaid == _this.isPaid)&&(identical(other.confidenceScore, _this.confidenceScore) || other.confidenceScore == _this.confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as Obligation;
  return Object.hash(runtimeType,_this.obligationId,_this.label,_this.amount,_this.dueDate,_this.category,_this.isFixed,_this.isPaid,_this.confidenceScore);
}

@override
String toString() {
  final _this = this as Obligation;
  return 'Obligation(obligationId: ${_this.obligationId}, label: ${_this.label}, amount: ${_this.amount}, dueDate: ${_this.dueDate}, category: ${_this.category}, isFixed: ${_this.isFixed}, isPaid: ${_this.isPaid}, confidenceScore: ${_this.confidenceScore})';
}


}

/// @nodoc
abstract mixin class $ObligationCopyWith<$Res>  {
  factory $ObligationCopyWith(Obligation value, $Res Function(Obligation) _then) = _$ObligationCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'obligation_id') String obligationId, String label,@DecimalConverter() Decimal amount,@JsonKey(name: 'due_date') DateTime dueDate, String? category,@JsonKey(name: 'is_fixed') bool isFixed,@JsonKey(name: 'is_paid') bool isPaid,@JsonKey(name: 'confidence_score') double confidenceScore
});




}
/// @nodoc
class _$ObligationCopyWithImpl<$Res>
    implements $ObligationCopyWith<$Res> {
  _$ObligationCopyWithImpl(this._self, this._then);

  final Obligation _self;
  final $Res Function(Obligation) _then;

/// Create a copy of Obligation
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? obligationId = null,Object? label = null,Object? amount = null,Object? dueDate = null,Object? category = freezed,Object? isFixed = null,Object? isPaid = null,Object? confidenceScore = null,}) {
  return _then(Obligation(
obligationId: null == obligationId ? _self.obligationId : obligationId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as Decimal,dueDate: null == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as DateTime,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,isFixed: null == isFixed ? _self.isFixed : isFixed // ignore: cast_nullable_to_non_nullable
as bool,isPaid: null == isPaid ? _self.isPaid : isPaid // ignore: cast_nullable_to_non_nullable
as bool,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [Obligation].
extension ObligationPatterns on Obligation {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Obligation value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Obligation() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Obligation value)  $default,){
final _that = this;
switch (_that) {
case _Obligation():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Obligation value)?  $default,){
final _that = this;
switch (_that) {
case _Obligation() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'obligation_id')  String obligationId,  String label, @DecimalConverter()  Decimal amount, @JsonKey(name: 'due_date')  DateTime dueDate,  String? category, @JsonKey(name: 'is_fixed')  bool isFixed, @JsonKey(name: 'is_paid')  bool isPaid, @JsonKey(name: 'confidence_score')  double confidenceScore)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Obligation() when $default != null:
return $default(_that.obligationId,_that.label,_that.amount,_that.dueDate,_that.category,_that.isFixed,_that.isPaid,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'obligation_id')  String obligationId,  String label, @DecimalConverter()  Decimal amount, @JsonKey(name: 'due_date')  DateTime dueDate,  String? category, @JsonKey(name: 'is_fixed')  bool isFixed, @JsonKey(name: 'is_paid')  bool isPaid, @JsonKey(name: 'confidence_score')  double confidenceScore)  $default,) {final _that = this;
switch (_that) {
case _Obligation():
return $default(_that.obligationId,_that.label,_that.amount,_that.dueDate,_that.category,_that.isFixed,_that.isPaid,_that.confidenceScore);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'obligation_id')  String obligationId,  String label, @DecimalConverter()  Decimal amount, @JsonKey(name: 'due_date')  DateTime dueDate,  String? category, @JsonKey(name: 'is_fixed')  bool isFixed, @JsonKey(name: 'is_paid')  bool isPaid, @JsonKey(name: 'confidence_score')  double confidenceScore)?  $default,) {final _that = this;
switch (_that) {
case _Obligation() when $default != null:
return $default(_that.obligationId,_that.label,_that.amount,_that.dueDate,_that.category,_that.isFixed,_that.isPaid,_that.confidenceScore);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Obligation implements Obligation {
  const _Obligation({@JsonKey(name: 'obligation_id') required this.obligationId, required this.label, @DecimalConverter() required this.amount, @JsonKey(name: 'due_date') required this.dueDate, this.category, @JsonKey(name: 'is_fixed') required this.isFixed, @JsonKey(name: 'is_paid') required this.isPaid, @JsonKey(name: 'confidence_score') required this.confidenceScore});
  factory _Obligation.fromJson(Map<String, dynamic> json) => _$ObligationFromJson(json);

@override@JsonKey(name: 'obligation_id') final  String obligationId;
@override final  String label;
@override@DecimalConverter() final  Decimal amount;
@override@JsonKey(name: 'due_date') final  DateTime dueDate;
@override final  String? category;
@override@JsonKey(name: 'is_fixed') final  bool isFixed;
@override@JsonKey(name: 'is_paid') final  bool isPaid;
@override@JsonKey(name: 'confidence_score') final  double confidenceScore;

/// Create a copy of Obligation
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ObligationCopyWith<_Obligation> get copyWith => __$ObligationCopyWithImpl<_Obligation>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ObligationToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _Obligation&&(identical(other.obligationId, obligationId) || other.obligationId == obligationId)&&(identical(other.label, label) || other.label == label)&&(identical(other.amount, amount) || other.amount == amount)&&(identical(other.dueDate, dueDate) || other.dueDate == dueDate)&&(identical(other.category, category) || other.category == category)&&(identical(other.isFixed, isFixed) || other.isFixed == isFixed)&&(identical(other.isPaid, isPaid) || other.isPaid == isPaid)&&(identical(other.confidenceScore, confidenceScore) || other.confidenceScore == confidenceScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,obligationId,label,amount,dueDate,category,isFixed,isPaid,confidenceScore);
}

@override
String toString() {
    return 'Obligation(obligationId: $obligationId, label: $label, amount: $amount, dueDate: $dueDate, category: $category, isFixed: $isFixed, isPaid: $isPaid, confidenceScore: $confidenceScore)';
}


}

/// @nodoc
abstract mixin class _$ObligationCopyWith<$Res> implements $ObligationCopyWith<$Res> {
  factory _$ObligationCopyWith(_Obligation value, $Res Function(_Obligation) _then) = __$ObligationCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'obligation_id') String obligationId, String label,@DecimalConverter() Decimal amount,@JsonKey(name: 'due_date') DateTime dueDate, String? category,@JsonKey(name: 'is_fixed') bool isFixed,@JsonKey(name: 'is_paid') bool isPaid,@JsonKey(name: 'confidence_score') double confidenceScore
});




}
/// @nodoc
class __$ObligationCopyWithImpl<$Res>
    implements _$ObligationCopyWith<$Res> {
  __$ObligationCopyWithImpl(this._self, this._then);

  final _Obligation _self;
  final $Res Function(_Obligation) _then;

/// Create a copy of Obligation
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? obligationId = null,Object? label = null,Object? amount = null,Object? dueDate = null,Object? category = freezed,Object? isFixed = null,Object? isPaid = null,Object? confidenceScore = null,}) {
  return _then(_Obligation(
obligationId: null == obligationId ? _self.obligationId : obligationId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,amount: null == amount ? _self.amount : amount // ignore: cast_nullable_to_non_nullable
as Decimal,dueDate: null == dueDate ? _self.dueDate : dueDate // ignore: cast_nullable_to_non_nullable
as DateTime,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,isFixed: null == isFixed ? _self.isFixed : isFixed // ignore: cast_nullable_to_non_nullable
as bool,isPaid: null == isPaid ? _self.isPaid : isPaid // ignore: cast_nullable_to_non_nullable
as bool,confidenceScore: null == confidenceScore ? _self.confidenceScore : confidenceScore // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

// dart format on
