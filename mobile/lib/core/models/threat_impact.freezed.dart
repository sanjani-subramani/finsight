// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'threat_impact.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ThreatImpact {

@JsonKey(name: 'would_cause_shortfall') bool get wouldCauseShortfall;@JsonKey(name: 'prob_before') double get probBefore;@JsonKey(name: 'prob_after') double get probAfter;@JsonKey(name: 'obligations_at_risk') List<String> get obligationsAtRisk;@JsonKey(name: 'days_until_first_impact') int? get daysUntilFirstImpact;@JsonKey(name: 'human_statement') String get humanStatement;
/// Create a copy of ThreatImpact
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ThreatImpactCopyWith<ThreatImpact> get copyWith => _$ThreatImpactCopyWithImpl<ThreatImpact>(this as ThreatImpact, _$identity);

  /// Serializes this ThreatImpact to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ThreatImpact;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ThreatImpact&&(identical(other.wouldCauseShortfall, _this.wouldCauseShortfall) || other.wouldCauseShortfall == _this.wouldCauseShortfall)&&(identical(other.probBefore, _this.probBefore) || other.probBefore == _this.probBefore)&&(identical(other.probAfter, _this.probAfter) || other.probAfter == _this.probAfter)&&const DeepCollectionEquality().equals(other.obligationsAtRisk, _this.obligationsAtRisk)&&(identical(other.daysUntilFirstImpact, _this.daysUntilFirstImpact) || other.daysUntilFirstImpact == _this.daysUntilFirstImpact)&&(identical(other.humanStatement, _this.humanStatement) || other.humanStatement == _this.humanStatement));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ThreatImpact;
  return Object.hash(runtimeType,_this.wouldCauseShortfall,_this.probBefore,_this.probAfter,const DeepCollectionEquality().hash(_this.obligationsAtRisk),_this.daysUntilFirstImpact,_this.humanStatement);
}

@override
String toString() {
  final _this = this as ThreatImpact;
  return 'ThreatImpact(wouldCauseShortfall: ${_this.wouldCauseShortfall}, probBefore: ${_this.probBefore}, probAfter: ${_this.probAfter}, obligationsAtRisk: ${_this.obligationsAtRisk}, daysUntilFirstImpact: ${_this.daysUntilFirstImpact}, humanStatement: ${_this.humanStatement})';
}


}

/// @nodoc
abstract mixin class $ThreatImpactCopyWith<$Res>  {
  factory $ThreatImpactCopyWith(ThreatImpact value, $Res Function(ThreatImpact) _then) = _$ThreatImpactCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'would_cause_shortfall') bool wouldCauseShortfall,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter,@JsonKey(name: 'obligations_at_risk') List<String> obligationsAtRisk,@JsonKey(name: 'days_until_first_impact') int? daysUntilFirstImpact,@JsonKey(name: 'human_statement') String humanStatement
});




}
/// @nodoc
class _$ThreatImpactCopyWithImpl<$Res>
    implements $ThreatImpactCopyWith<$Res> {
  _$ThreatImpactCopyWithImpl(this._self, this._then);

  final ThreatImpact _self;
  final $Res Function(ThreatImpact) _then;

/// Create a copy of ThreatImpact
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? wouldCauseShortfall = null,Object? probBefore = null,Object? probAfter = null,Object? obligationsAtRisk = null,Object? daysUntilFirstImpact = freezed,Object? humanStatement = null,}) {
  return _then(ThreatImpact(
wouldCauseShortfall: null == wouldCauseShortfall ? _self.wouldCauseShortfall : wouldCauseShortfall // ignore: cast_nullable_to_non_nullable
as bool,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,obligationsAtRisk: null == obligationsAtRisk ? _self.obligationsAtRisk : obligationsAtRisk // ignore: cast_nullable_to_non_nullable
as List<String>,daysUntilFirstImpact: freezed == daysUntilFirstImpact ? _self.daysUntilFirstImpact : daysUntilFirstImpact // ignore: cast_nullable_to_non_nullable
as int?,humanStatement: null == humanStatement ? _self.humanStatement : humanStatement // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ThreatImpact].
extension ThreatImpactPatterns on ThreatImpact {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ThreatImpact value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ThreatImpact() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ThreatImpact value)  $default,){
final _that = this;
switch (_that) {
case _ThreatImpact():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ThreatImpact value)?  $default,){
final _that = this;
switch (_that) {
case _ThreatImpact() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'would_cause_shortfall')  bool wouldCauseShortfall, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'obligations_at_risk')  List<String> obligationsAtRisk, @JsonKey(name: 'days_until_first_impact')  int? daysUntilFirstImpact, @JsonKey(name: 'human_statement')  String humanStatement)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ThreatImpact() when $default != null:
return $default(_that.wouldCauseShortfall,_that.probBefore,_that.probAfter,_that.obligationsAtRisk,_that.daysUntilFirstImpact,_that.humanStatement);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'would_cause_shortfall')  bool wouldCauseShortfall, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'obligations_at_risk')  List<String> obligationsAtRisk, @JsonKey(name: 'days_until_first_impact')  int? daysUntilFirstImpact, @JsonKey(name: 'human_statement')  String humanStatement)  $default,) {final _that = this;
switch (_that) {
case _ThreatImpact():
return $default(_that.wouldCauseShortfall,_that.probBefore,_that.probAfter,_that.obligationsAtRisk,_that.daysUntilFirstImpact,_that.humanStatement);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'would_cause_shortfall')  bool wouldCauseShortfall, @JsonKey(name: 'prob_before')  double probBefore, @JsonKey(name: 'prob_after')  double probAfter, @JsonKey(name: 'obligations_at_risk')  List<String> obligationsAtRisk, @JsonKey(name: 'days_until_first_impact')  int? daysUntilFirstImpact, @JsonKey(name: 'human_statement')  String humanStatement)?  $default,) {final _that = this;
switch (_that) {
case _ThreatImpact() when $default != null:
return $default(_that.wouldCauseShortfall,_that.probBefore,_that.probAfter,_that.obligationsAtRisk,_that.daysUntilFirstImpact,_that.humanStatement);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ThreatImpact implements ThreatImpact {
  const _ThreatImpact({@JsonKey(name: 'would_cause_shortfall') required this.wouldCauseShortfall, @JsonKey(name: 'prob_before') required this.probBefore, @JsonKey(name: 'prob_after') required this.probAfter, @JsonKey(name: 'obligations_at_risk')  List<String> obligationsAtRisk = const [], @JsonKey(name: 'days_until_first_impact') this.daysUntilFirstImpact, @JsonKey(name: 'human_statement') required this.humanStatement}): _obligationsAtRisk = obligationsAtRisk;
  factory _ThreatImpact.fromJson(Map<String, dynamic> json) => _$ThreatImpactFromJson(json);

@override@JsonKey(name: 'would_cause_shortfall') final  bool wouldCauseShortfall;
@override@JsonKey(name: 'prob_before') final  double probBefore;
@override@JsonKey(name: 'prob_after') final  double probAfter;
 final  List<String> _obligationsAtRisk;
@override@JsonKey(name: 'obligations_at_risk') List<String> get obligationsAtRisk {
  if (_obligationsAtRisk is EqualUnmodifiableListView) return _obligationsAtRisk;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_obligationsAtRisk);
}

@override@JsonKey(name: 'days_until_first_impact') final  int? daysUntilFirstImpact;
@override@JsonKey(name: 'human_statement') final  String humanStatement;

/// Create a copy of ThreatImpact
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ThreatImpactCopyWith<_ThreatImpact> get copyWith => __$ThreatImpactCopyWithImpl<_ThreatImpact>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ThreatImpactToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ThreatImpact&&(identical(other.wouldCauseShortfall, wouldCauseShortfall) || other.wouldCauseShortfall == wouldCauseShortfall)&&(identical(other.probBefore, probBefore) || other.probBefore == probBefore)&&(identical(other.probAfter, probAfter) || other.probAfter == probAfter)&&const DeepCollectionEquality().equals(other.obligationsAtRisk, _obligationsAtRisk)&&(identical(other.daysUntilFirstImpact, daysUntilFirstImpact) || other.daysUntilFirstImpact == daysUntilFirstImpact)&&(identical(other.humanStatement, humanStatement) || other.humanStatement == humanStatement));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,wouldCauseShortfall,probBefore,probAfter,const DeepCollectionEquality().hash(_obligationsAtRisk),daysUntilFirstImpact,humanStatement);
}

@override
String toString() {
    return 'ThreatImpact(wouldCauseShortfall: $wouldCauseShortfall, probBefore: $probBefore, probAfter: $probAfter, obligationsAtRisk: $obligationsAtRisk, daysUntilFirstImpact: $daysUntilFirstImpact, humanStatement: $humanStatement)';
}


}

/// @nodoc
abstract mixin class _$ThreatImpactCopyWith<$Res> implements $ThreatImpactCopyWith<$Res> {
  factory _$ThreatImpactCopyWith(_ThreatImpact value, $Res Function(_ThreatImpact) _then) = __$ThreatImpactCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'would_cause_shortfall') bool wouldCauseShortfall,@JsonKey(name: 'prob_before') double probBefore,@JsonKey(name: 'prob_after') double probAfter,@JsonKey(name: 'obligations_at_risk') List<String> obligationsAtRisk,@JsonKey(name: 'days_until_first_impact') int? daysUntilFirstImpact,@JsonKey(name: 'human_statement') String humanStatement
});




}
/// @nodoc
class __$ThreatImpactCopyWithImpl<$Res>
    implements _$ThreatImpactCopyWith<$Res> {
  __$ThreatImpactCopyWithImpl(this._self, this._then);

  final _ThreatImpact _self;
  final $Res Function(_ThreatImpact) _then;

/// Create a copy of ThreatImpact
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? wouldCauseShortfall = null,Object? probBefore = null,Object? probAfter = null,Object? obligationsAtRisk = null,Object? daysUntilFirstImpact = freezed,Object? humanStatement = null,}) {
  return _then(_ThreatImpact(
wouldCauseShortfall: null == wouldCauseShortfall ? _self.wouldCauseShortfall : wouldCauseShortfall // ignore: cast_nullable_to_non_nullable
as bool,probBefore: null == probBefore ? _self.probBefore : probBefore // ignore: cast_nullable_to_non_nullable
as double,probAfter: null == probAfter ? _self.probAfter : probAfter // ignore: cast_nullable_to_non_nullable
as double,obligationsAtRisk: null == obligationsAtRisk ? _self._obligationsAtRisk : obligationsAtRisk // ignore: cast_nullable_to_non_nullable
as List<String>,daysUntilFirstImpact: freezed == daysUntilFirstImpact ? _self.daysUntilFirstImpact : daysUntilFirstImpact // ignore: cast_nullable_to_non_nullable
as int?,humanStatement: null == humanStatement ? _self.humanStatement : humanStatement // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
