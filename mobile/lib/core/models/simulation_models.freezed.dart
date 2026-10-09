// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'simulation_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$BalanceMatrixSummary {

 List<int> get days; List<double> get p5; List<double> get p25; List<double> get p50; List<double> get p75; List<double> get p95;
/// Create a copy of BalanceMatrixSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$BalanceMatrixSummaryCopyWith<BalanceMatrixSummary> get copyWith => _$BalanceMatrixSummaryCopyWithImpl<BalanceMatrixSummary>(this as BalanceMatrixSummary, _$identity);

  /// Serializes this BalanceMatrixSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as BalanceMatrixSummary;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is BalanceMatrixSummary&&const DeepCollectionEquality().equals(other.days, _this.days)&&const DeepCollectionEquality().equals(other.p5, _this.p5)&&const DeepCollectionEquality().equals(other.p25, _this.p25)&&const DeepCollectionEquality().equals(other.p50, _this.p50)&&const DeepCollectionEquality().equals(other.p75, _this.p75)&&const DeepCollectionEquality().equals(other.p95, _this.p95));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as BalanceMatrixSummary;
  return Object.hash(runtimeType,const DeepCollectionEquality().hash(_this.days),const DeepCollectionEquality().hash(_this.p5),const DeepCollectionEquality().hash(_this.p25),const DeepCollectionEquality().hash(_this.p50),const DeepCollectionEquality().hash(_this.p75),const DeepCollectionEquality().hash(_this.p95));
}

@override
String toString() {
  final _this = this as BalanceMatrixSummary;
  return 'BalanceMatrixSummary(days: ${_this.days}, p5: ${_this.p5}, p25: ${_this.p25}, p50: ${_this.p50}, p75: ${_this.p75}, p95: ${_this.p95})';
}


}

/// @nodoc
abstract mixin class $BalanceMatrixSummaryCopyWith<$Res>  {
  factory $BalanceMatrixSummaryCopyWith(BalanceMatrixSummary value, $Res Function(BalanceMatrixSummary) _then) = _$BalanceMatrixSummaryCopyWithImpl;
@useResult
$Res call({
 List<int> days, List<double> p5, List<double> p25, List<double> p50, List<double> p75, List<double> p95
});




}
/// @nodoc
class _$BalanceMatrixSummaryCopyWithImpl<$Res>
    implements $BalanceMatrixSummaryCopyWith<$Res> {
  _$BalanceMatrixSummaryCopyWithImpl(this._self, this._then);

  final BalanceMatrixSummary _self;
  final $Res Function(BalanceMatrixSummary) _then;

/// Create a copy of BalanceMatrixSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? days = null,Object? p5 = null,Object? p25 = null,Object? p50 = null,Object? p75 = null,Object? p95 = null,}) {
  return _then(BalanceMatrixSummary(
days: null == days ? _self.days : days // ignore: cast_nullable_to_non_nullable
as List<int>,p5: null == p5 ? _self.p5 : p5 // ignore: cast_nullable_to_non_nullable
as List<double>,p25: null == p25 ? _self.p25 : p25 // ignore: cast_nullable_to_non_nullable
as List<double>,p50: null == p50 ? _self.p50 : p50 // ignore: cast_nullable_to_non_nullable
as List<double>,p75: null == p75 ? _self.p75 : p75 // ignore: cast_nullable_to_non_nullable
as List<double>,p95: null == p95 ? _self.p95 : p95 // ignore: cast_nullable_to_non_nullable
as List<double>,
  ));
}

}


/// Adds pattern-matching-related methods to [BalanceMatrixSummary].
extension BalanceMatrixSummaryPatterns on BalanceMatrixSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _BalanceMatrixSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _BalanceMatrixSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _BalanceMatrixSummary value)  $default,){
final _that = this;
switch (_that) {
case _BalanceMatrixSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _BalanceMatrixSummary value)?  $default,){
final _that = this;
switch (_that) {
case _BalanceMatrixSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<int> days,  List<double> p5,  List<double> p25,  List<double> p50,  List<double> p75,  List<double> p95)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _BalanceMatrixSummary() when $default != null:
return $default(_that.days,_that.p5,_that.p25,_that.p50,_that.p75,_that.p95);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<int> days,  List<double> p5,  List<double> p25,  List<double> p50,  List<double> p75,  List<double> p95)  $default,) {final _that = this;
switch (_that) {
case _BalanceMatrixSummary():
return $default(_that.days,_that.p5,_that.p25,_that.p50,_that.p75,_that.p95);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<int> days,  List<double> p5,  List<double> p25,  List<double> p50,  List<double> p75,  List<double> p95)?  $default,) {final _that = this;
switch (_that) {
case _BalanceMatrixSummary() when $default != null:
return $default(_that.days,_that.p5,_that.p25,_that.p50,_that.p75,_that.p95);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _BalanceMatrixSummary implements BalanceMatrixSummary {
  const _BalanceMatrixSummary({ List<int> days = const [],  List<double> p5 = const [],  List<double> p25 = const [],  List<double> p50 = const [],  List<double> p75 = const [],  List<double> p95 = const []}): _days = days,_p5 = p5,_p25 = p25,_p50 = p50,_p75 = p75,_p95 = p95;
  factory _BalanceMatrixSummary.fromJson(Map<String, dynamic> json) => _$BalanceMatrixSummaryFromJson(json);

 final  List<int> _days;
@override@JsonKey() List<int> get days {
  if (_days is EqualUnmodifiableListView) return _days;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_days);
}

 final  List<double> _p5;
@override@JsonKey() List<double> get p5 {
  if (_p5 is EqualUnmodifiableListView) return _p5;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_p5);
}

 final  List<double> _p25;
@override@JsonKey() List<double> get p25 {
  if (_p25 is EqualUnmodifiableListView) return _p25;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_p25);
}

 final  List<double> _p50;
@override@JsonKey() List<double> get p50 {
  if (_p50 is EqualUnmodifiableListView) return _p50;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_p50);
}

 final  List<double> _p75;
@override@JsonKey() List<double> get p75 {
  if (_p75 is EqualUnmodifiableListView) return _p75;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_p75);
}

 final  List<double> _p95;
@override@JsonKey() List<double> get p95 {
  if (_p95 is EqualUnmodifiableListView) return _p95;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_p95);
}


/// Create a copy of BalanceMatrixSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$BalanceMatrixSummaryCopyWith<_BalanceMatrixSummary> get copyWith => __$BalanceMatrixSummaryCopyWithImpl<_BalanceMatrixSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$BalanceMatrixSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _BalanceMatrixSummary&&const DeepCollectionEquality().equals(other.days, _days)&&const DeepCollectionEquality().equals(other.p5, _p5)&&const DeepCollectionEquality().equals(other.p25, _p25)&&const DeepCollectionEquality().equals(other.p50, _p50)&&const DeepCollectionEquality().equals(other.p75, _p75)&&const DeepCollectionEquality().equals(other.p95, _p95));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,const DeepCollectionEquality().hash(_days),const DeepCollectionEquality().hash(_p5),const DeepCollectionEquality().hash(_p25),const DeepCollectionEquality().hash(_p50),const DeepCollectionEquality().hash(_p75),const DeepCollectionEquality().hash(_p95));
}

@override
String toString() {
    return 'BalanceMatrixSummary(days: $days, p5: $p5, p25: $p25, p50: $p50, p75: $p75, p95: $p95)';
}


}

/// @nodoc
abstract mixin class _$BalanceMatrixSummaryCopyWith<$Res> implements $BalanceMatrixSummaryCopyWith<$Res> {
  factory _$BalanceMatrixSummaryCopyWith(_BalanceMatrixSummary value, $Res Function(_BalanceMatrixSummary) _then) = __$BalanceMatrixSummaryCopyWithImpl;
@override @useResult
$Res call({
 List<int> days, List<double> p5, List<double> p25, List<double> p50, List<double> p75, List<double> p95
});




}
/// @nodoc
class __$BalanceMatrixSummaryCopyWithImpl<$Res>
    implements _$BalanceMatrixSummaryCopyWith<$Res> {
  __$BalanceMatrixSummaryCopyWithImpl(this._self, this._then);

  final _BalanceMatrixSummary _self;
  final $Res Function(_BalanceMatrixSummary) _then;

/// Create a copy of BalanceMatrixSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? days = null,Object? p5 = null,Object? p25 = null,Object? p50 = null,Object? p75 = null,Object? p95 = null,}) {
  return _then(_BalanceMatrixSummary(
days: null == days ? _self._days : days // ignore: cast_nullable_to_non_nullable
as List<int>,p5: null == p5 ? _self._p5 : p5 // ignore: cast_nullable_to_non_nullable
as List<double>,p25: null == p25 ? _self._p25 : p25 // ignore: cast_nullable_to_non_nullable
as List<double>,p50: null == p50 ? _self._p50 : p50 // ignore: cast_nullable_to_non_nullable
as List<double>,p75: null == p75 ? _self._p75 : p75 // ignore: cast_nullable_to_non_nullable
as List<double>,p95: null == p95 ? _self._p95 : p95 // ignore: cast_nullable_to_non_nullable
as List<double>,
  ));
}


}


/// @nodoc
mixin _$SensitivityFactor {

 String get name; String get description;@JsonKey(name: 'prob_before') double get probBefore;@JsonKey(name: 'prob_after') double get probAfter; double get delta; bool get actionable;
/// Create a copy of SensitivityFactor
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SensitivityFactorCopyWith<SensitivityFactor> get copyWith => _$SensitivityFactorCopyWithImpl<SensitivityFactor>(this as SensitivityFactor, _$identity);

  /// Serializes this SensitivityFactor to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SensitivityFactor;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SensitivityFactor&&(identical(other.name, _this.name) || other.name == _this.name)&&(identical(other.description, _this.description) || other.description == _this.description)&&(identical(other.probBefore, _this.probBefore) || other.probBefore == _this.probBefore)&&(identical(other.probAfter, _this.probAfter) || other.probAfter == _this.probAfter)&&(identical(other.delta, _this.delta) || other.delta == _this.delta)&&(identical(other.actionable, _this.actionable) || other.actionable == _this.actionable));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SensitivityFactor;
  return Object.hash(runtimeType,_this.name,_this.description,_this.probBefore,_this.probAfter,_this.delta,_this.actionable);
}

@override
String toString() {
  final _this = this as SensitivityFactor;
  return 'SensitivityFactor(name: ${_this.name}, description: ${_this.description}, probBefore: ${_this.probBefore}, probAfter: ${_this.probAfter}, delta: ${_this.delta}, actionable: ${_this.actionable})';
}


}

/// @nodoc
abstract mixin class $SensitivityFactorCopyWith<$Res>  {
  factory $SensitivityFactorCopyWith(SensitivityFactor value, $Res Function(SensitivityFactor) _then) = _$SensitivityFactorCopyWithImpl;
@useResult
$Res call({
 String name, String description,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter, double delta, bool actionable
});




}
/// @nodoc
class _$SensitivityFactorCopyWithImpl<$Res>
    implements $SensitivityFactorCopyWith<$Res> {
  _$SensitivityFactorCopyWithImpl(this._self, this._then);

  final SensitivityFactor _self;
  final $Res Function(SensitivityFactor) _then;

/// Create a copy of SensitivityFactor
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? description = null,Object? probBefore = null,Object? probAfter = null,Object? delta = null,Object? actionable = null,}) {
  return _then(SensitivityFactor(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,delta: null == delta ? _self.delta : delta // ignore: cast_nullable_to_non_nullable
as double,actionable: null == actionable ? _self.actionable : actionable // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [SensitivityFactor].
extension SensitivityFactorPatterns on SensitivityFactor {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SensitivityFactor value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SensitivityFactor() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SensitivityFactor value)  $default,){
final _that = this;
switch (_that) {
case _SensitivityFactor():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SensitivityFactor value)?  $default,){
final _that = this;
switch (_that) {
case _SensitivityFactor() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String description, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter,  double delta,  bool actionable)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SensitivityFactor() when $default != null:
return $default(_that.name,_that.description,_that.probBefore,_that.probAfter,_that.delta,_that.actionable);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String description, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter,  double delta,  bool actionable)  $default,) {final _that = this;
switch (_that) {
case _SensitivityFactor():
return $default(_that.name,_that.description,_that.probBefore,_that.probAfter,_that.delta,_that.actionable);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String description, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter,  double delta,  bool actionable)?  $default,) {final _that = this;
switch (_that) {
case _SensitivityFactor() when $default != null:
return $default(_that.name,_that.description,_that.probBefore,_that.probAfter,_that.delta,_that.actionable);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SensitivityFactor implements SensitivityFactor {
  const _SensitivityFactor({required this.name, required this.description, @JsonKey(name: 'prob_before') required this.probBefore, @JsonKey(name: 'prob_after') required this.probAfter, required this.delta, required this.actionable});
  factory _SensitivityFactor.fromJson(Map<String, dynamic> json) => _$SensitivityFactorFromJson(json);

@override final  String name;
@override final  String description;
@override@JsonKey(name: 'prob_before') final  double probBefore;
@override@JsonKey(name: 'prob_after') final  double probAfter;
@override final  double delta;
@override final  bool actionable;

/// Create a copy of SensitivityFactor
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SensitivityFactorCopyWith<_SensitivityFactor> get copyWith => __$SensitivityFactorCopyWithImpl<_SensitivityFactor>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SensitivityFactorToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SensitivityFactor&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.probBefore, probBefore) || other.probBefore == probBefore)&&(identical(other.probAfter, probAfter) || other.probAfter == probAfter)&&(identical(other.delta, delta) || other.delta == delta)&&(identical(other.actionable, actionable) || other.actionable == actionable));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,name,description,probBefore,probAfter,delta,actionable);
}

@override
String toString() {
    return 'SensitivityFactor(name: $name, description: $description, probBefore: $probBefore, probAfter: $probAfter, delta: $delta, actionable: $actionable)';
}


}

/// @nodoc
abstract mixin class _$SensitivityFactorCopyWith<$Res> implements $SensitivityFactorCopyWith<$Res> {
  factory _$SensitivityFactorCopyWith(_SensitivityFactor value, $Res Function(_SensitivityFactor) _then) = __$SensitivityFactorCopyWithImpl;
@override @useResult
$Res call({
 String name, String description,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter, double delta, bool actionable
});




}
/// @nodoc
class __$SensitivityFactorCopyWithImpl<$Res>
    implements _$SensitivityFactorCopyWith<$Res> {
  __$SensitivityFactorCopyWithImpl(this._self, this._then);

  final _SensitivityFactor _self;
  final $Res Function(_SensitivityFactor) _then;

/// Create a copy of SensitivityFactor
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? description = null,Object? probBefore = null,Object? probAfter = null,Object? delta = null,Object? actionable = null,}) {
  return _then(_SensitivityFactor(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,delta: null == delta ? _self.delta : delta // ignore: cast_nullable_to_non_nullable
as double,actionable: null == actionable ? _self.actionable : actionable // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$SimulationRunResult {

@JsonKey(name: 'run_id') String get runId;@JsonKey(name: 'scenarios_run') int get scenariosRun;@JsonKey(name: 'horizon_days') int get horizonDays; int get seed;@JsonKey(name: 'shortfall_probability_by_horizon') Map<String, double> get shortfallProbabilityByHorizon;@JsonKey(name: 'min_balance_p5')@DecimalConverter() Decimal get minBalanceP5;@JsonKey(name: 'min_balance_p50')@DecimalConverter() Decimal get minBalanceP50;@JsonKey(name: 'time_to_danger_days') int? get timeToDangerDays;@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal get safeToSpend;@JsonKey(name: 'duration_ms') int get durationMs;@JsonKey(name: 'from_cache') bool get fromCache;@JsonKey(name: 'balance_matrix_summary') BalanceMatrixSummary get balanceMatrixSummary; List<SensitivityFactor> get sensitivity;
/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SimulationRunResultCopyWith<SimulationRunResult> get copyWith => _$SimulationRunResultCopyWithImpl<SimulationRunResult>(this as SimulationRunResult, _$identity);

  /// Serializes this SimulationRunResult to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as SimulationRunResult;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SimulationRunResult&&(identical(other.runId, _this.runId) || other.runId == _this.runId)&&(identical(other.scenariosRun, _this.scenariosRun) || other.scenariosRun == _this.scenariosRun)&&(identical(other.horizonDays, _this.horizonDays) || other.horizonDays == _this.horizonDays)&&(identical(other.seed, _this.seed) || other.seed == _this.seed)&&const DeepCollectionEquality().equals(other.shortfallProbabilityByHorizon, _this.shortfallProbabilityByHorizon)&&(identical(other.minBalanceP5, _this.minBalanceP5) || other.minBalanceP5 == _this.minBalanceP5)&&(identical(other.minBalanceP50, _this.minBalanceP50) || other.minBalanceP50 == _this.minBalanceP50)&&(identical(other.timeToDangerDays, _this.timeToDangerDays) || other.timeToDangerDays == _this.timeToDangerDays)&&(identical(other.safeToSpend, _this.safeToSpend) || other.safeToSpend == _this.safeToSpend)&&(identical(other.durationMs, _this.durationMs) || other.durationMs == _this.durationMs)&&(identical(other.fromCache, _this.fromCache) || other.fromCache == _this.fromCache)&&(identical(other.balanceMatrixSummary, _this.balanceMatrixSummary) || other.balanceMatrixSummary == _this.balanceMatrixSummary)&&const DeepCollectionEquality().equals(other.sensitivity, _this.sensitivity));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as SimulationRunResult;
  return Object.hash(runtimeType,_this.runId,_this.scenariosRun,_this.horizonDays,_this.seed,const DeepCollectionEquality().hash(_this.shortfallProbabilityByHorizon),_this.minBalanceP5,_this.minBalanceP50,_this.timeToDangerDays,_this.safeToSpend,_this.durationMs,_this.fromCache,_this.balanceMatrixSummary,const DeepCollectionEquality().hash(_this.sensitivity));
}

@override
String toString() {
  final _this = this as SimulationRunResult;
  return 'SimulationRunResult(runId: ${_this.runId}, scenariosRun: ${_this.scenariosRun}, horizonDays: ${_this.horizonDays}, seed: ${_this.seed}, shortfallProbabilityByHorizon: ${_this.shortfallProbabilityByHorizon}, minBalanceP5: ${_this.minBalanceP5}, minBalanceP50: ${_this.minBalanceP50}, timeToDangerDays: ${_this.timeToDangerDays}, safeToSpend: ${_this.safeToSpend}, durationMs: ${_this.durationMs}, fromCache: ${_this.fromCache}, balanceMatrixSummary: ${_this.balanceMatrixSummary}, sensitivity: ${_this.sensitivity})';
}


}

/// @nodoc
abstract mixin class $SimulationRunResultCopyWith<$Res>  {
  factory $SimulationRunResultCopyWith(SimulationRunResult value, $Res Function(SimulationRunResult) _then) = _$SimulationRunResultCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'run_id') String runId,@JsonKey(name: 'scenarios_run') int scenariosRun,@JsonKey(name: 'horizon_days') int horizonDays, int seed,@JsonKey(name: 'shortfall_probability_by_horizon') Map<String, double> shortfallProbabilityByHorizon,@JsonKey(name: 'min_balance_p5')@DecimalConverter() Decimal minBalanceP5,@JsonKey(name: 'min_balance_p50')@DecimalConverter() Decimal minBalanceP50,@JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal safeToSpend,@JsonKey(name: 'duration_ms') int durationMs,@JsonKey(name: 'from_cache') bool fromCache,@JsonKey(name: 'balance_matrix_summary') BalanceMatrixSummary balanceMatrixSummary, List<SensitivityFactor> sensitivity
});


$BalanceMatrixSummaryCopyWith<$Res> get balanceMatrixSummary;

}
/// @nodoc
class _$SimulationRunResultCopyWithImpl<$Res>
    implements $SimulationRunResultCopyWith<$Res> {
  _$SimulationRunResultCopyWithImpl(this._self, this._then);

  final SimulationRunResult _self;
  final $Res Function(SimulationRunResult) _then;

/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? runId = null,Object? scenariosRun = null,Object? horizonDays = null,Object? seed = null,Object? shortfallProbabilityByHorizon = null,Object? minBalanceP5 = null,Object? minBalanceP50 = null,Object? timeToDangerDays = freezed,Object? safeToSpend = null,Object? durationMs = null,Object? fromCache = null,Object? balanceMatrixSummary = null,Object? sensitivity = null,}) {
  return _then(SimulationRunResult(
runId: null == runId ? _self.runId : runId // ignore: cast_nullable_to_non_nullable
as String,scenariosRun: null == scenariosRun ? _self.scenariosRun : scenariosRun // ignore: cast_nullable_to_non_nullable
as int,horizonDays: null == horizonDays ? _self.horizonDays : horizonDays // ignore: cast_nullable_to_non_nullable
as int,seed: null == seed ? _self.seed : seed // ignore: cast_nullable_to_non_nullable
as int,shortfallProbabilityByHorizon: null == shortfallProbabilityByHorizon ? _self.shortfallProbabilityByHorizon : shortfallProbabilityByHorizon // ignore: cast_nullable_to_non_nullable
as Map<String, double>,minBalanceP5: null == minBalanceP5 ? _self.minBalanceP5 : minBalanceP5 // ignore: cast_nullable_to_non_nullable
as Decimal,minBalanceP50: null == minBalanceP50 ? _self.minBalanceP50 : minBalanceP50 // ignore: cast_nullable_to_non_nullable
as Decimal,timeToDangerDays: freezed == timeToDangerDays ? _self.timeToDangerDays : timeToDangerDays // ignore: cast_nullable_to_non_nullable
as int?,safeToSpend: null == safeToSpend ? _self.safeToSpend : safeToSpend // ignore: cast_nullable_to_non_nullable
as Decimal,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,fromCache: null == fromCache ? _self.fromCache : fromCache // ignore: cast_nullable_to_non_nullable
as bool,balanceMatrixSummary: null == balanceMatrixSummary ? _self.balanceMatrixSummary : balanceMatrixSummary // ignore: cast_nullable_to_non_nullable
as BalanceMatrixSummary,sensitivity: null == sensitivity ? _self.sensitivity : sensitivity // ignore: cast_nullable_to_non_nullable
as List<SensitivityFactor>,
  ));
}
/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$BalanceMatrixSummaryCopyWith<$Res> get balanceMatrixSummary {
  
  return $BalanceMatrixSummaryCopyWith<$Res>(_self.balanceMatrixSummary, (value) {
    return _then(_self.copyWith(balanceMatrixSummary: value));
  });
}
}


/// Adds pattern-matching-related methods to [SimulationRunResult].
extension SimulationRunResultPatterns on SimulationRunResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SimulationRunResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SimulationRunResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SimulationRunResult value)  $default,){
final _that = this;
switch (_that) {
case _SimulationRunResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SimulationRunResult value)?  $default,){
final _that = this;
switch (_that) {
case _SimulationRunResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'run_id')  String runId, @JsonKey(name: 'scenarios_run')  int scenariosRun, @JsonKey(name: 'horizon_days')  int horizonDays,  int seed, @JsonKey(name: 'shortfall_probability_by_horizon')  Map<String, double> shortfallProbabilityByHorizon, @JsonKey(name: 'min_balance_p5')@DecimalConverter()  Decimal minBalanceP5, @JsonKey(name: 'min_balance_p50')@DecimalConverter()  Decimal minBalanceP50, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'from_cache')  bool fromCache, @JsonKey(name: 'balance_matrix_summary')  BalanceMatrixSummary balanceMatrixSummary,  List<SensitivityFactor> sensitivity)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SimulationRunResult() when $default != null:
return $default(_that.runId,_that.scenariosRun,_that.horizonDays,_that.seed,_that.shortfallProbabilityByHorizon,_that.minBalanceP5,_that.minBalanceP50,_that.timeToDangerDays,_that.safeToSpend,_that.durationMs,_that.fromCache,_that.balanceMatrixSummary,_that.sensitivity);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'run_id')  String runId, @JsonKey(name: 'scenarios_run')  int scenariosRun, @JsonKey(name: 'horizon_days')  int horizonDays,  int seed, @JsonKey(name: 'shortfall_probability_by_horizon')  Map<String, double> shortfallProbabilityByHorizon, @JsonKey(name: 'min_balance_p5')@DecimalConverter()  Decimal minBalanceP5, @JsonKey(name: 'min_balance_p50')@DecimalConverter()  Decimal minBalanceP50, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'from_cache')  bool fromCache, @JsonKey(name: 'balance_matrix_summary')  BalanceMatrixSummary balanceMatrixSummary,  List<SensitivityFactor> sensitivity)  $default,) {final _that = this;
switch (_that) {
case _SimulationRunResult():
return $default(_that.runId,_that.scenariosRun,_that.horizonDays,_that.seed,_that.shortfallProbabilityByHorizon,_that.minBalanceP5,_that.minBalanceP50,_that.timeToDangerDays,_that.safeToSpend,_that.durationMs,_that.fromCache,_that.balanceMatrixSummary,_that.sensitivity);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'run_id')  String runId, @JsonKey(name: 'scenarios_run')  int scenariosRun, @JsonKey(name: 'horizon_days')  int horizonDays,  int seed, @JsonKey(name: 'shortfall_probability_by_horizon')  Map<String, double> shortfallProbabilityByHorizon, @JsonKey(name: 'min_balance_p5')@DecimalConverter()  Decimal minBalanceP5, @JsonKey(name: 'min_balance_p50')@DecimalConverter()  Decimal minBalanceP50, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'duration_ms')  int durationMs, @JsonKey(name: 'from_cache')  bool fromCache, @JsonKey(name: 'balance_matrix_summary')  BalanceMatrixSummary balanceMatrixSummary,  List<SensitivityFactor> sensitivity)?  $default,) {final _that = this;
switch (_that) {
case _SimulationRunResult() when $default != null:
return $default(_that.runId,_that.scenariosRun,_that.horizonDays,_that.seed,_that.shortfallProbabilityByHorizon,_that.minBalanceP5,_that.minBalanceP50,_that.timeToDangerDays,_that.safeToSpend,_that.durationMs,_that.fromCache,_that.balanceMatrixSummary,_that.sensitivity);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SimulationRunResult implements SimulationRunResult {
  const _SimulationRunResult({@JsonKey(name: 'run_id') required this.runId, @JsonKey(name: 'scenarios_run') required this.scenariosRun, @JsonKey(name: 'horizon_days') required this.horizonDays, required this.seed, @JsonKey(name: 'shortfall_probability_by_horizon')  Map<String, double> shortfallProbabilityByHorizon = const {}, @JsonKey(name: 'min_balance_p5')@DecimalConverter() required this.minBalanceP5, @JsonKey(name: 'min_balance_p50')@DecimalConverter() required this.minBalanceP50, @JsonKey(name: 'time_to_danger_days') this.timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter() required this.safeToSpend, @JsonKey(name: 'duration_ms') required this.durationMs, @JsonKey(name: 'from_cache') required this.fromCache, @JsonKey(name: 'balance_matrix_summary') required this.balanceMatrixSummary,  List<SensitivityFactor> sensitivity = const []}): _shortfallProbabilityByHorizon = shortfallProbabilityByHorizon,_sensitivity = sensitivity;
  factory _SimulationRunResult.fromJson(Map<String, dynamic> json) => _$SimulationRunResultFromJson(json);

@override@JsonKey(name: 'run_id') final  String runId;
@override@JsonKey(name: 'scenarios_run') final  int scenariosRun;
@override@JsonKey(name: 'horizon_days') final  int horizonDays;
@override final  int seed;
 final  Map<String, double> _shortfallProbabilityByHorizon;
@override@JsonKey(name: 'shortfall_probability_by_horizon') Map<String, double> get shortfallProbabilityByHorizon {
  if (_shortfallProbabilityByHorizon is EqualUnmodifiableMapView) return _shortfallProbabilityByHorizon;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_shortfallProbabilityByHorizon);
}

@override@JsonKey(name: 'min_balance_p5')@DecimalConverter() final  Decimal minBalanceP5;
@override@JsonKey(name: 'min_balance_p50')@DecimalConverter() final  Decimal minBalanceP50;
@override@JsonKey(name: 'time_to_danger_days') final  int? timeToDangerDays;
@override@JsonKey(name: 'safe_to_spend')@DecimalConverter() final  Decimal safeToSpend;
@override@JsonKey(name: 'duration_ms') final  int durationMs;
@override@JsonKey(name: 'from_cache') final  bool fromCache;
@override@JsonKey(name: 'balance_matrix_summary') final  BalanceMatrixSummary balanceMatrixSummary;
 final  List<SensitivityFactor> _sensitivity;
@override@JsonKey() List<SensitivityFactor> get sensitivity {
  if (_sensitivity is EqualUnmodifiableListView) return _sensitivity;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sensitivity);
}


/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SimulationRunResultCopyWith<_SimulationRunResult> get copyWith => __$SimulationRunResultCopyWithImpl<_SimulationRunResult>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SimulationRunResultToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _SimulationRunResult&&(identical(other.runId, runId) || other.runId == runId)&&(identical(other.scenariosRun, scenariosRun) || other.scenariosRun == scenariosRun)&&(identical(other.horizonDays, horizonDays) || other.horizonDays == horizonDays)&&(identical(other.seed, seed) || other.seed == seed)&&const DeepCollectionEquality().equals(other.shortfallProbabilityByHorizon, _shortfallProbabilityByHorizon)&&(identical(other.minBalanceP5, minBalanceP5) || other.minBalanceP5 == minBalanceP5)&&(identical(other.minBalanceP50, minBalanceP50) || other.minBalanceP50 == minBalanceP50)&&(identical(other.timeToDangerDays, timeToDangerDays) || other.timeToDangerDays == timeToDangerDays)&&(identical(other.safeToSpend, safeToSpend) || other.safeToSpend == safeToSpend)&&(identical(other.durationMs, durationMs) || other.durationMs == durationMs)&&(identical(other.fromCache, fromCache) || other.fromCache == fromCache)&&(identical(other.balanceMatrixSummary, balanceMatrixSummary) || other.balanceMatrixSummary == balanceMatrixSummary)&&const DeepCollectionEquality().equals(other.sensitivity, _sensitivity));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,runId,scenariosRun,horizonDays,seed,const DeepCollectionEquality().hash(_shortfallProbabilityByHorizon),minBalanceP5,minBalanceP50,timeToDangerDays,safeToSpend,durationMs,fromCache,balanceMatrixSummary,const DeepCollectionEquality().hash(_sensitivity));
}

@override
String toString() {
    return 'SimulationRunResult(runId: $runId, scenariosRun: $scenariosRun, horizonDays: $horizonDays, seed: $seed, shortfallProbabilityByHorizon: $shortfallProbabilityByHorizon, minBalanceP5: $minBalanceP5, minBalanceP50: $minBalanceP50, timeToDangerDays: $timeToDangerDays, safeToSpend: $safeToSpend, durationMs: $durationMs, fromCache: $fromCache, balanceMatrixSummary: $balanceMatrixSummary, sensitivity: $sensitivity)';
}


}

/// @nodoc
abstract mixin class _$SimulationRunResultCopyWith<$Res> implements $SimulationRunResultCopyWith<$Res> {
  factory _$SimulationRunResultCopyWith(_SimulationRunResult value, $Res Function(_SimulationRunResult) _then) = __$SimulationRunResultCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'run_id') String runId,@JsonKey(name: 'scenarios_run') int scenariosRun,@JsonKey(name: 'horizon_days') int horizonDays, int seed,@JsonKey(name: 'shortfall_probability_by_horizon') Map<String, double> shortfallProbabilityByHorizon,@JsonKey(name: 'min_balance_p5')@DecimalConverter() Decimal minBalanceP5,@JsonKey(name: 'min_balance_p50')@DecimalConverter() Decimal minBalanceP50,@JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal safeToSpend,@JsonKey(name: 'duration_ms') int durationMs,@JsonKey(name: 'from_cache') bool fromCache,@JsonKey(name: 'balance_matrix_summary') BalanceMatrixSummary balanceMatrixSummary, List<SensitivityFactor> sensitivity
});


@override $BalanceMatrixSummaryCopyWith<$Res> get balanceMatrixSummary;

}
/// @nodoc
class __$SimulationRunResultCopyWithImpl<$Res>
    implements _$SimulationRunResultCopyWith<$Res> {
  __$SimulationRunResultCopyWithImpl(this._self, this._then);

  final _SimulationRunResult _self;
  final $Res Function(_SimulationRunResult) _then;

/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? runId = null,Object? scenariosRun = null,Object? horizonDays = null,Object? seed = null,Object? shortfallProbabilityByHorizon = null,Object? minBalanceP5 = null,Object? minBalanceP50 = null,Object? timeToDangerDays = freezed,Object? safeToSpend = null,Object? durationMs = null,Object? fromCache = null,Object? balanceMatrixSummary = null,Object? sensitivity = null,}) {
  return _then(_SimulationRunResult(
runId: null == runId ? _self.runId : runId // ignore: cast_nullable_to_non_nullable
as String,scenariosRun: null == scenariosRun ? _self.scenariosRun : scenariosRun // ignore: cast_nullable_to_non_nullable
as int,horizonDays: null == horizonDays ? _self.horizonDays : horizonDays // ignore: cast_nullable_to_non_nullable
as int,seed: null == seed ? _self.seed : seed // ignore: cast_nullable_to_non_nullable
as int,shortfallProbabilityByHorizon: null == shortfallProbabilityByHorizon ? _self._shortfallProbabilityByHorizon : shortfallProbabilityByHorizon // ignore: cast_nullable_to_non_nullable
as Map<String, double>,minBalanceP5: null == minBalanceP5 ? _self.minBalanceP5 : minBalanceP5 // ignore: cast_nullable_to_non_nullable
as Decimal,minBalanceP50: null == minBalanceP50 ? _self.minBalanceP50 : minBalanceP50 // ignore: cast_nullable_to_non_nullable
as Decimal,timeToDangerDays: freezed == timeToDangerDays ? _self.timeToDangerDays : timeToDangerDays // ignore: cast_nullable_to_non_nullable
as int?,safeToSpend: null == safeToSpend ? _self.safeToSpend : safeToSpend // ignore: cast_nullable_to_non_nullable
as Decimal,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,fromCache: null == fromCache ? _self.fromCache : fromCache // ignore: cast_nullable_to_non_nullable
as bool,balanceMatrixSummary: null == balanceMatrixSummary ? _self.balanceMatrixSummary : balanceMatrixSummary // ignore: cast_nullable_to_non_nullable
as BalanceMatrixSummary,sensitivity: null == sensitivity ? _self._sensitivity : sensitivity // ignore: cast_nullable_to_non_nullable
as List<SensitivityFactor>,
  ));
}

/// Create a copy of SimulationRunResult
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$BalanceMatrixSummaryCopyWith<$Res> get balanceMatrixSummary {
  
  return $BalanceMatrixSummaryCopyWith<$Res>(_self.balanceMatrixSummary, (value) {
    return _then(_self.copyWith(balanceMatrixSummary: value));
  });
}
}


/// @nodoc
mixin _$PurchaseVerdict {

 bool get affordable;@JsonKey(name: 'prob_before') double get probBefore;@JsonKey(name: 'prob_after') double get probAfter;@JsonKey(name: 'wait_days_recommended') int? get waitDaysRecommended;@JsonKey(name: 'reasoning_values') Map<String, dynamic> get reasoningValues;
/// Create a copy of PurchaseVerdict
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PurchaseVerdictCopyWith<PurchaseVerdict> get copyWith => _$PurchaseVerdictCopyWithImpl<PurchaseVerdict>(this as PurchaseVerdict, _$identity);

  /// Serializes this PurchaseVerdict to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as PurchaseVerdict;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PurchaseVerdict&&(identical(other.affordable, _this.affordable) || other.affordable == _this.affordable)&&(identical(other.probBefore, _this.probBefore) || other.probBefore == _this.probBefore)&&(identical(other.probAfter, _this.probAfter) || other.probAfter == _this.probAfter)&&(identical(other.waitDaysRecommended, _this.waitDaysRecommended) || other.waitDaysRecommended == _this.waitDaysRecommended)&&const DeepCollectionEquality().equals(other.reasoningValues, _this.reasoningValues));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as PurchaseVerdict;
  return Object.hash(runtimeType,_this.affordable,_this.probBefore,_this.probAfter,_this.waitDaysRecommended,const DeepCollectionEquality().hash(_this.reasoningValues));
}

@override
String toString() {
  final _this = this as PurchaseVerdict;
  return 'PurchaseVerdict(affordable: ${_this.affordable}, probBefore: ${_this.probBefore}, probAfter: ${_this.probAfter}, waitDaysRecommended: ${_this.waitDaysRecommended}, reasoningValues: ${_this.reasoningValues})';
}


}

/// @nodoc
abstract mixin class $PurchaseVerdictCopyWith<$Res>  {
  factory $PurchaseVerdictCopyWith(PurchaseVerdict value, $Res Function(PurchaseVerdict) _then) = _$PurchaseVerdictCopyWithImpl;
@useResult
$Res call({
 bool affordable,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter,@JsonKey(name: 'wait_days_recommended') int? waitDaysRecommended,@JsonKey(name: 'reasoning_values') Map<String, dynamic> reasoningValues
});




}
/// @nodoc
class _$PurchaseVerdictCopyWithImpl<$Res>
    implements $PurchaseVerdictCopyWith<$Res> {
  _$PurchaseVerdictCopyWithImpl(this._self, this._then);

  final PurchaseVerdict _self;
  final $Res Function(PurchaseVerdict) _then;

/// Create a copy of PurchaseVerdict
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? affordable = null,Object? probBefore = null,Object? probAfter = null,Object? waitDaysRecommended = freezed,Object? reasoningValues = null,}) {
  return _then(PurchaseVerdict(
affordable: null == affordable ? _self.affordable : affordable // ignore: cast_nullable_to_non_nullable
as bool,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,waitDaysRecommended: freezed == waitDaysRecommended ? _self.waitDaysRecommended : waitDaysRecommended // ignore: cast_nullable_to_non_nullable
as int?,reasoningValues: null == reasoningValues ? _self.reasoningValues : reasoningValues // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [PurchaseVerdict].
extension PurchaseVerdictPatterns on PurchaseVerdict {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PurchaseVerdict value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PurchaseVerdict() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PurchaseVerdict value)  $default,){
final _that = this;
switch (_that) {
case _PurchaseVerdict():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PurchaseVerdict value)?  $default,){
final _that = this;
switch (_that) {
case _PurchaseVerdict() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool affordable, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'wait_days_recommended')  int? waitDaysRecommended, @JsonKey(name: 'reasoning_values')  Map<String, dynamic> reasoningValues)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PurchaseVerdict() when $default != null:
return $default(_that.affordable,_that.probBefore,_that.probAfter,_that.waitDaysRecommended,_that.reasoningValues);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool affordable, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'wait_days_recommended')  int? waitDaysRecommended, @JsonKey(name: 'reasoning_values')  Map<String, dynamic> reasoningValues)  $default,) {final _that = this;
switch (_that) {
case _PurchaseVerdict():
return $default(_that.affordable,_that.probBefore,_that.probAfter,_that.waitDaysRecommended,_that.reasoningValues);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool affordable, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'wait_days_recommended')  int? waitDaysRecommended, @JsonKey(name: 'reasoning_values')  Map<String, dynamic> reasoningValues)?  $default,) {final _that = this;
switch (_that) {
case _PurchaseVerdict() when $default != null:
return $default(_that.affordable,_that.probBefore,_that.probAfter,_that.waitDaysRecommended,_that.reasoningValues);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PurchaseVerdict implements PurchaseVerdict {
  const _PurchaseVerdict({required this.affordable, @JsonKey(name: 'prob_before') required this.probBefore, @JsonKey(name: 'prob_after') required this.probAfter, @JsonKey(name: 'wait_days_recommended') this.waitDaysRecommended, @JsonKey(name: 'reasoning_values')  Map<String, dynamic> reasoningValues = const {}}): _reasoningValues = reasoningValues;
  factory _PurchaseVerdict.fromJson(Map<String, dynamic> json) => _$PurchaseVerdictFromJson(json);

@override final  bool affordable;
@override@JsonKey(name: 'prob_before') final  double probBefore;
@override@JsonKey(name: 'prob_after') final  double probAfter;
@override@JsonKey(name: 'wait_days_recommended') final  int? waitDaysRecommended;
 final  Map<String, dynamic> _reasoningValues;
@override@JsonKey(name: 'reasoning_values') Map<String, dynamic> get reasoningValues {
  if (_reasoningValues is EqualUnmodifiableMapView) return _reasoningValues;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_reasoningValues);
}


/// Create a copy of PurchaseVerdict
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PurchaseVerdictCopyWith<_PurchaseVerdict> get copyWith => __$PurchaseVerdictCopyWithImpl<_PurchaseVerdict>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PurchaseVerdictToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _PurchaseVerdict&&(identical(other.affordable, affordable) || other.affordable == affordable)&&(identical(other.probBefore, probBefore) || other.probBefore == probBefore)&&(identical(other.probAfter, probAfter) || other.probAfter == probAfter)&&(identical(other.waitDaysRecommended, waitDaysRecommended) || other.waitDaysRecommended == waitDaysRecommended)&&const DeepCollectionEquality().equals(other.reasoningValues, _reasoningValues));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,affordable,probBefore,probAfter,waitDaysRecommended,const DeepCollectionEquality().hash(_reasoningValues));
}

@override
String toString() {
    return 'PurchaseVerdict(affordable: $affordable, probBefore: $probBefore, probAfter: $probAfter, waitDaysRecommended: $waitDaysRecommended, reasoningValues: $reasoningValues)';
}


}

/// @nodoc
abstract mixin class _$PurchaseVerdictCopyWith<$Res> implements $PurchaseVerdictCopyWith<$Res> {
  factory _$PurchaseVerdictCopyWith(_PurchaseVerdict value, $Res Function(_PurchaseVerdict) _then) = __$PurchaseVerdictCopyWithImpl;
@override @useResult
$Res call({
 bool affordable,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter,@JsonKey(name: 'wait_days_recommended') int? waitDaysRecommended,@JsonKey(name: 'reasoning_values') Map<String, dynamic> reasoningValues
});




}
/// @nodoc
class __$PurchaseVerdictCopyWithImpl<$Res>
    implements _$PurchaseVerdictCopyWith<$Res> {
  __$PurchaseVerdictCopyWithImpl(this._self, this._then);

  final _PurchaseVerdict _self;
  final $Res Function(_PurchaseVerdict) _then;

/// Create a copy of PurchaseVerdict
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? affordable = null,Object? probBefore = null,Object? probAfter = null,Object? waitDaysRecommended = freezed,Object? reasoningValues = null,}) {
  return _then(_PurchaseVerdict(
affordable: null == affordable ? _self.affordable : affordable // ignore: cast_nullable_to_non_nullable
as bool,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,waitDaysRecommended: freezed == waitDaysRecommended ? _self.waitDaysRecommended : waitDaysRecommended // ignore: cast_nullable_to_non_nullable
as int?,reasoningValues: null == reasoningValues ? _self._reasoningValues : reasoningValues // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
