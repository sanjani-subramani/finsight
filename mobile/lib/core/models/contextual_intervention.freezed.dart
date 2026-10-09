// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'contextual_intervention.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$InterventionSummary {

 String get id; String get severity;@JsonKey(name: 'severity_raw') double get severityRaw;@JsonKey(name: 'confidence_ceiling_applied') bool get confidenceCeilingApplied; String get headline; String get body; double get probability;@JsonKey(name: 'urgency_score') double get urgencyScore;@JsonKey(name: 'data_confidence') double get dataConfidence;@JsonKey(name: 'shadow_mode') bool get shadowMode; bool get delivered;@JsonKey(name: 'user_acknowledged') bool get userAcknowledged;@JsonKey(name: 'user_acted') bool get userActed;@JsonKey(name: 'outcome_materialized') bool? get outcomeMaterialized;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of InterventionSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InterventionSummaryCopyWith<InterventionSummary> get copyWith => _$InterventionSummaryCopyWithImpl<InterventionSummary>(this as InterventionSummary, _$identity);

  /// Serializes this InterventionSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as InterventionSummary;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InterventionSummary&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.severity, _this.severity) || other.severity == _this.severity)&&(identical(other.severityRaw, _this.severityRaw) || other.severityRaw == _this.severityRaw)&&(identical(other.confidenceCeilingApplied, _this.confidenceCeilingApplied) || other.confidenceCeilingApplied == _this.confidenceCeilingApplied)&&(identical(other.headline, _this.headline) || other.headline == _this.headline)&&(identical(other.body, _this.body) || other.body == _this.body)&&(identical(other.probability, _this.probability) || other.probability == _this.probability)&&(identical(other.urgencyScore, _this.urgencyScore) || other.urgencyScore == _this.urgencyScore)&&(identical(other.dataConfidence, _this.dataConfidence) || other.dataConfidence == _this.dataConfidence)&&(identical(other.shadowMode, _this.shadowMode) || other.shadowMode == _this.shadowMode)&&(identical(other.delivered, _this.delivered) || other.delivered == _this.delivered)&&(identical(other.userAcknowledged, _this.userAcknowledged) || other.userAcknowledged == _this.userAcknowledged)&&(identical(other.userActed, _this.userActed) || other.userActed == _this.userActed)&&(identical(other.outcomeMaterialized, _this.outcomeMaterialized) || other.outcomeMaterialized == _this.outcomeMaterialized)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as InterventionSummary;
  return Object.hash(runtimeType,_this.id,_this.severity,_this.severityRaw,_this.confidenceCeilingApplied,_this.headline,_this.body,_this.probability,_this.urgencyScore,_this.dataConfidence,_this.shadowMode,_this.delivered,_this.userAcknowledged,_this.userActed,_this.outcomeMaterialized,_this.createdAt);
}

@override
String toString() {
  final _this = this as InterventionSummary;
  return 'InterventionSummary(id: ${_this.id}, severity: ${_this.severity}, severityRaw: ${_this.severityRaw}, confidenceCeilingApplied: ${_this.confidenceCeilingApplied}, headline: ${_this.headline}, body: ${_this.body}, probability: ${_this.probability}, urgencyScore: ${_this.urgencyScore}, dataConfidence: ${_this.dataConfidence}, shadowMode: ${_this.shadowMode}, delivered: ${_this.delivered}, userAcknowledged: ${_this.userAcknowledged}, userActed: ${_this.userActed}, outcomeMaterialized: ${_this.outcomeMaterialized}, createdAt: ${_this.createdAt})';
}


}

/// @nodoc
abstract mixin class $InterventionSummaryCopyWith<$Res>  {
  factory $InterventionSummaryCopyWith(InterventionSummary value, $Res Function(InterventionSummary) _then) = _$InterventionSummaryCopyWithImpl;
@useResult
$Res call({
 String id, String severity,@JsonKey(name: 'severity_raw') double severityRaw,@JsonKey(name: 'confidence_ceiling_applied') bool confidenceCeilingApplied, String headline, String body, double probability,@JsonKey(name: 'urgency_score') double urgencyScore,@JsonKey(name: 'data_confidence') double dataConfidence,@JsonKey(name: 'shadow_mode') bool shadowMode, bool delivered,@JsonKey(name: 'user_acknowledged') bool userAcknowledged,@JsonKey(name: 'user_acted') bool userActed,@JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class _$InterventionSummaryCopyWithImpl<$Res>
    implements $InterventionSummaryCopyWith<$Res> {
  _$InterventionSummaryCopyWithImpl(this._self, this._then);

  final InterventionSummary _self;
  final $Res Function(InterventionSummary) _then;

/// Create a copy of InterventionSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? severity = null,Object? severityRaw = null,Object? confidenceCeilingApplied = null,Object? headline = null,Object? body = null,Object? probability = null,Object? urgencyScore = null,Object? dataConfidence = null,Object? shadowMode = null,Object? delivered = null,Object? userAcknowledged = null,Object? userActed = null,Object? outcomeMaterialized = freezed,Object? createdAt = null,}) {
  return _then(InterventionSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,severityRaw: null == severityRaw ? _self.severityRaw : severityRaw // ignore: cast_nullable_to_non_nullable
as double,confidenceCeilingApplied: null == confidenceCeilingApplied ? _self.confidenceCeilingApplied : confidenceCeilingApplied // ignore: cast_nullable_to_non_nullable
as bool,headline: null == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String,body: null == body ? _self.body : body // ignore: cast_nullable_to_non_nullable
as String,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,urgencyScore: null == urgencyScore ? _self.urgencyScore : urgencyScore // ignore: cast_nullable_to_non_nullable
as double,dataConfidence: null == dataConfidence ? _self.dataConfidence : dataConfidence // ignore: cast_nullable_to_non_nullable
as double,shadowMode: null == shadowMode ? _self.shadowMode : shadowMode // ignore: cast_nullable_to_non_nullable
as bool,delivered: null == delivered ? _self.delivered : delivered // ignore: cast_nullable_to_non_nullable
as bool,userAcknowledged: null == userAcknowledged ? _self.userAcknowledged : userAcknowledged // ignore: cast_nullable_to_non_nullable
as bool,userActed: null == userActed ? _self.userActed : userActed // ignore: cast_nullable_to_non_nullable
as bool,outcomeMaterialized: freezed == outcomeMaterialized ? _self.outcomeMaterialized : outcomeMaterialized // ignore: cast_nullable_to_non_nullable
as bool?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [InterventionSummary].
extension InterventionSummaryPatterns on InterventionSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InterventionSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InterventionSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InterventionSummary value)  $default,){
final _that = this;
switch (_that) {
case _InterventionSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InterventionSummary value)?  $default,){
final _that = this;
switch (_that) {
case _InterventionSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InterventionSummary() when $default != null:
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _InterventionSummary():
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _InterventionSummary() when $default != null:
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _InterventionSummary implements InterventionSummary {
  const _InterventionSummary({required this.id, required this.severity, @JsonKey(name: 'severity_raw') required this.severityRaw, @JsonKey(name: 'confidence_ceiling_applied') required this.confidenceCeilingApplied, required this.headline, required this.body, required this.probability, @JsonKey(name: 'urgency_score') required this.urgencyScore, @JsonKey(name: 'data_confidence') required this.dataConfidence, @JsonKey(name: 'shadow_mode') required this.shadowMode, required this.delivered, @JsonKey(name: 'user_acknowledged') required this.userAcknowledged, @JsonKey(name: 'user_acted') required this.userActed, @JsonKey(name: 'outcome_materialized') this.outcomeMaterialized, @JsonKey(name: 'created_at') required this.createdAt});
  factory _InterventionSummary.fromJson(Map<String, dynamic> json) => _$InterventionSummaryFromJson(json);

@override final  String id;
@override final  String severity;
@override@JsonKey(name: 'severity_raw') final  double severityRaw;
@override@JsonKey(name: 'confidence_ceiling_applied') final  bool confidenceCeilingApplied;
@override final  String headline;
@override final  String body;
@override final  double probability;
@override@JsonKey(name: 'urgency_score') final  double urgencyScore;
@override@JsonKey(name: 'data_confidence') final  double dataConfidence;
@override@JsonKey(name: 'shadow_mode') final  bool shadowMode;
@override final  bool delivered;
@override@JsonKey(name: 'user_acknowledged') final  bool userAcknowledged;
@override@JsonKey(name: 'user_acted') final  bool userActed;
@override@JsonKey(name: 'outcome_materialized') final  bool? outcomeMaterialized;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

/// Create a copy of InterventionSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InterventionSummaryCopyWith<_InterventionSummary> get copyWith => __$InterventionSummaryCopyWithImpl<_InterventionSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InterventionSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _InterventionSummary&&(identical(other.id, id) || other.id == id)&&(identical(other.severity, severity) || other.severity == severity)&&(identical(other.severityRaw, severityRaw) || other.severityRaw == severityRaw)&&(identical(other.confidenceCeilingApplied, confidenceCeilingApplied) || other.confidenceCeilingApplied == confidenceCeilingApplied)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.body, body) || other.body == body)&&(identical(other.probability, probability) || other.probability == probability)&&(identical(other.urgencyScore, urgencyScore) || other.urgencyScore == urgencyScore)&&(identical(other.dataConfidence, dataConfidence) || other.dataConfidence == dataConfidence)&&(identical(other.shadowMode, shadowMode) || other.shadowMode == shadowMode)&&(identical(other.delivered, delivered) || other.delivered == delivered)&&(identical(other.userAcknowledged, userAcknowledged) || other.userAcknowledged == userAcknowledged)&&(identical(other.userActed, userActed) || other.userActed == userActed)&&(identical(other.outcomeMaterialized, outcomeMaterialized) || other.outcomeMaterialized == outcomeMaterialized)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,severity,severityRaw,confidenceCeilingApplied,headline,body,probability,urgencyScore,dataConfidence,shadowMode,delivered,userAcknowledged,userActed,outcomeMaterialized,createdAt);
}

@override
String toString() {
    return 'InterventionSummary(id: $id, severity: $severity, severityRaw: $severityRaw, confidenceCeilingApplied: $confidenceCeilingApplied, headline: $headline, body: $body, probability: $probability, urgencyScore: $urgencyScore, dataConfidence: $dataConfidence, shadowMode: $shadowMode, delivered: $delivered, userAcknowledged: $userAcknowledged, userActed: $userActed, outcomeMaterialized: $outcomeMaterialized, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$InterventionSummaryCopyWith<$Res> implements $InterventionSummaryCopyWith<$Res> {
  factory _$InterventionSummaryCopyWith(_InterventionSummary value, $Res Function(_InterventionSummary) _then) = __$InterventionSummaryCopyWithImpl;
@override @useResult
$Res call({
 String id, String severity,@JsonKey(name: 'severity_raw') double severityRaw,@JsonKey(name: 'confidence_ceiling_applied') bool confidenceCeilingApplied, String headline, String body, double probability,@JsonKey(name: 'urgency_score') double urgencyScore,@JsonKey(name: 'data_confidence') double dataConfidence,@JsonKey(name: 'shadow_mode') bool shadowMode, bool delivered,@JsonKey(name: 'user_acknowledged') bool userAcknowledged,@JsonKey(name: 'user_acted') bool userActed,@JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class __$InterventionSummaryCopyWithImpl<$Res>
    implements _$InterventionSummaryCopyWith<$Res> {
  __$InterventionSummaryCopyWithImpl(this._self, this._then);

  final _InterventionSummary _self;
  final $Res Function(_InterventionSummary) _then;

/// Create a copy of InterventionSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? severity = null,Object? severityRaw = null,Object? confidenceCeilingApplied = null,Object? headline = null,Object? body = null,Object? probability = null,Object? urgencyScore = null,Object? dataConfidence = null,Object? shadowMode = null,Object? delivered = null,Object? userAcknowledged = null,Object? userActed = null,Object? outcomeMaterialized = freezed,Object? createdAt = null,}) {
  return _then(_InterventionSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,severityRaw: null == severityRaw ? _self.severityRaw : severityRaw // ignore: cast_nullable_to_non_nullable
as double,confidenceCeilingApplied: null == confidenceCeilingApplied ? _self.confidenceCeilingApplied : confidenceCeilingApplied // ignore: cast_nullable_to_non_nullable
as bool,headline: null == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String,body: null == body ? _self.body : body // ignore: cast_nullable_to_non_nullable
as String,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,urgencyScore: null == urgencyScore ? _self.urgencyScore : urgencyScore // ignore: cast_nullable_to_non_nullable
as double,dataConfidence: null == dataConfidence ? _self.dataConfidence : dataConfidence // ignore: cast_nullable_to_non_nullable
as double,shadowMode: null == shadowMode ? _self.shadowMode : shadowMode // ignore: cast_nullable_to_non_nullable
as bool,delivered: null == delivered ? _self.delivered : delivered // ignore: cast_nullable_to_non_nullable
as bool,userAcknowledged: null == userAcknowledged ? _self.userAcknowledged : userAcknowledged // ignore: cast_nullable_to_non_nullable
as bool,userActed: null == userActed ? _self.userActed : userActed // ignore: cast_nullable_to_non_nullable
as bool,outcomeMaterialized: freezed == outcomeMaterialized ? _self.outcomeMaterialized : outcomeMaterialized // ignore: cast_nullable_to_non_nullable
as bool?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$ContextualIntervention {

 String get id; String get severity;@JsonKey(name: 'severity_raw') double get severityRaw;@JsonKey(name: 'confidence_ceiling_applied') bool get confidenceCeilingApplied; String get headline; String get body; double get probability;@JsonKey(name: 'urgency_score') double get urgencyScore;@JsonKey(name: 'data_confidence') double get dataConfidence;@JsonKey(name: 'shadow_mode') bool get shadowMode; bool get delivered;@JsonKey(name: 'user_acknowledged') bool get userAcknowledged;@JsonKey(name: 'user_acted') bool get userActed;@JsonKey(name: 'outcome_materialized') bool? get outcomeMaterialized;@JsonKey(name: 'created_at') DateTime get createdAt;@JsonKey(name: 'triggered_by_event_id') String? get triggeredByEventId;@JsonKey(name: 'triggered_by_threat_id') String? get triggeredByThreatId;@JsonKey(name: 'snapshot_id') String? get snapshotId;@JsonKey(name: 'simulation_run_id') String? get simulationRunId;@JsonKey(name: 'outcome_checked_at') DateTime? get outcomeCheckedAt;@JsonKey(name: 'decision_trace') List<TraceStep> get decisionTrace;@JsonKey(name: 'recommended_actions') List<RecommendedAction> get recommendedActions;
/// Create a copy of ContextualIntervention
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ContextualInterventionCopyWith<ContextualIntervention> get copyWith => _$ContextualInterventionCopyWithImpl<ContextualIntervention>(this as ContextualIntervention, _$identity);

  /// Serializes this ContextualIntervention to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ContextualIntervention;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ContextualIntervention&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.severity, _this.severity) || other.severity == _this.severity)&&(identical(other.severityRaw, _this.severityRaw) || other.severityRaw == _this.severityRaw)&&(identical(other.confidenceCeilingApplied, _this.confidenceCeilingApplied) || other.confidenceCeilingApplied == _this.confidenceCeilingApplied)&&(identical(other.headline, _this.headline) || other.headline == _this.headline)&&(identical(other.body, _this.body) || other.body == _this.body)&&(identical(other.probability, _this.probability) || other.probability == _this.probability)&&(identical(other.urgencyScore, _this.urgencyScore) || other.urgencyScore == _this.urgencyScore)&&(identical(other.dataConfidence, _this.dataConfidence) || other.dataConfidence == _this.dataConfidence)&&(identical(other.shadowMode, _this.shadowMode) || other.shadowMode == _this.shadowMode)&&(identical(other.delivered, _this.delivered) || other.delivered == _this.delivered)&&(identical(other.userAcknowledged, _this.userAcknowledged) || other.userAcknowledged == _this.userAcknowledged)&&(identical(other.userActed, _this.userActed) || other.userActed == _this.userActed)&&(identical(other.outcomeMaterialized, _this.outcomeMaterialized) || other.outcomeMaterialized == _this.outcomeMaterialized)&&(identical(other.createdAt, _this.createdAt) || other.createdAt == _this.createdAt)&&(identical(other.triggeredByEventId, _this.triggeredByEventId) || other.triggeredByEventId == _this.triggeredByEventId)&&(identical(other.triggeredByThreatId, _this.triggeredByThreatId) || other.triggeredByThreatId == _this.triggeredByThreatId)&&(identical(other.snapshotId, _this.snapshotId) || other.snapshotId == _this.snapshotId)&&(identical(other.simulationRunId, _this.simulationRunId) || other.simulationRunId == _this.simulationRunId)&&(identical(other.outcomeCheckedAt, _this.outcomeCheckedAt) || other.outcomeCheckedAt == _this.outcomeCheckedAt)&&const DeepCollectionEquality().equals(other.decisionTrace, _this.decisionTrace)&&const DeepCollectionEquality().equals(other.recommendedActions, _this.recommendedActions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ContextualIntervention;
  return Object.hashAll([runtimeType,_this.id,_this.severity,_this.severityRaw,_this.confidenceCeilingApplied,_this.headline,_this.body,_this.probability,_this.urgencyScore,_this.dataConfidence,_this.shadowMode,_this.delivered,_this.userAcknowledged,_this.userActed,_this.outcomeMaterialized,_this.createdAt,_this.triggeredByEventId,_this.triggeredByThreatId,_this.snapshotId,_this.simulationRunId,_this.outcomeCheckedAt,const DeepCollectionEquality().hash(_this.decisionTrace),const DeepCollectionEquality().hash(_this.recommendedActions)]);
}

@override
String toString() {
  final _this = this as ContextualIntervention;
  return 'ContextualIntervention(id: ${_this.id}, severity: ${_this.severity}, severityRaw: ${_this.severityRaw}, confidenceCeilingApplied: ${_this.confidenceCeilingApplied}, headline: ${_this.headline}, body: ${_this.body}, probability: ${_this.probability}, urgencyScore: ${_this.urgencyScore}, dataConfidence: ${_this.dataConfidence}, shadowMode: ${_this.shadowMode}, delivered: ${_this.delivered}, userAcknowledged: ${_this.userAcknowledged}, userActed: ${_this.userActed}, outcomeMaterialized: ${_this.outcomeMaterialized}, createdAt: ${_this.createdAt}, triggeredByEventId: ${_this.triggeredByEventId}, triggeredByThreatId: ${_this.triggeredByThreatId}, snapshotId: ${_this.snapshotId}, simulationRunId: ${_this.simulationRunId}, outcomeCheckedAt: ${_this.outcomeCheckedAt}, decisionTrace: ${_this.decisionTrace}, recommendedActions: ${_this.recommendedActions})';
}


}

/// @nodoc
abstract mixin class $ContextualInterventionCopyWith<$Res>  {
  factory $ContextualInterventionCopyWith(ContextualIntervention value, $Res Function(ContextualIntervention) _then) = _$ContextualInterventionCopyWithImpl;
@useResult
$Res call({
 String id, String severity,@JsonKey(name: 'severity_raw') double severityRaw,@JsonKey(name: 'confidence_ceiling_applied') bool confidenceCeilingApplied, String headline, String body, double probability,@JsonKey(name: 'urgency_score') double urgencyScore,@JsonKey(name: 'data_confidence') double dataConfidence,@JsonKey(name: 'shadow_mode') bool shadowMode, bool delivered,@JsonKey(name: 'user_acknowledged') bool userAcknowledged,@JsonKey(name: 'user_acted') bool userActed,@JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'triggered_by_event_id') String? triggeredByEventId,@JsonKey(name: 'triggered_by_threat_id') String? triggeredByThreatId,@JsonKey(name: 'snapshot_id') String? snapshotId,@JsonKey(name: 'simulation_run_id') String? simulationRunId,@JsonKey(name: 'outcome_checked_at') DateTime? outcomeCheckedAt,@JsonKey(name: 'decision_trace') List<TraceStep> decisionTrace,@JsonKey(name: 'recommended_actions') List<RecommendedAction> recommendedActions
});




}
/// @nodoc
class _$ContextualInterventionCopyWithImpl<$Res>
    implements $ContextualInterventionCopyWith<$Res> {
  _$ContextualInterventionCopyWithImpl(this._self, this._then);

  final ContextualIntervention _self;
  final $Res Function(ContextualIntervention) _then;

/// Create a copy of ContextualIntervention
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? severity = null,Object? severityRaw = null,Object? confidenceCeilingApplied = null,Object? headline = null,Object? body = null,Object? probability = null,Object? urgencyScore = null,Object? dataConfidence = null,Object? shadowMode = null,Object? delivered = null,Object? userAcknowledged = null,Object? userActed = null,Object? outcomeMaterialized = freezed,Object? createdAt = null,Object? triggeredByEventId = freezed,Object? triggeredByThreatId = freezed,Object? snapshotId = freezed,Object? simulationRunId = freezed,Object? outcomeCheckedAt = freezed,Object? decisionTrace = null,Object? recommendedActions = null,}) {
  return _then(ContextualIntervention(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,severityRaw: null == severityRaw ? _self.severityRaw : severityRaw // ignore: cast_nullable_to_non_nullable
as double,confidenceCeilingApplied: null == confidenceCeilingApplied ? _self.confidenceCeilingApplied : confidenceCeilingApplied // ignore: cast_nullable_to_non_nullable
as bool,headline: null == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String,body: null == body ? _self.body : body // ignore: cast_nullable_to_non_nullable
as String,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,urgencyScore: null == urgencyScore ? _self.urgencyScore : urgencyScore // ignore: cast_nullable_to_non_nullable
as double,dataConfidence: null == dataConfidence ? _self.dataConfidence : dataConfidence // ignore: cast_nullable_to_non_nullable
as double,shadowMode: null == shadowMode ? _self.shadowMode : shadowMode // ignore: cast_nullable_to_non_nullable
as bool,delivered: null == delivered ? _self.delivered : delivered // ignore: cast_nullable_to_non_nullable
as bool,userAcknowledged: null == userAcknowledged ? _self.userAcknowledged : userAcknowledged // ignore: cast_nullable_to_non_nullable
as bool,userActed: null == userActed ? _self.userActed : userActed // ignore: cast_nullable_to_non_nullable
as bool,outcomeMaterialized: freezed == outcomeMaterialized ? _self.outcomeMaterialized : outcomeMaterialized // ignore: cast_nullable_to_non_nullable
as bool?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,triggeredByEventId: freezed == triggeredByEventId ? _self.triggeredByEventId : triggeredByEventId // ignore: cast_nullable_to_non_nullable
as String?,triggeredByThreatId: freezed == triggeredByThreatId ? _self.triggeredByThreatId : triggeredByThreatId // ignore: cast_nullable_to_non_nullable
as String?,snapshotId: freezed == snapshotId ? _self.snapshotId : snapshotId // ignore: cast_nullable_to_non_nullable
as String?,simulationRunId: freezed == simulationRunId ? _self.simulationRunId : simulationRunId // ignore: cast_nullable_to_non_nullable
as String?,outcomeCheckedAt: freezed == outcomeCheckedAt ? _self.outcomeCheckedAt : outcomeCheckedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,decisionTrace: null == decisionTrace ? _self.decisionTrace : decisionTrace // ignore: cast_nullable_to_non_nullable
as List<TraceStep>,recommendedActions: null == recommendedActions ? _self.recommendedActions : recommendedActions // ignore: cast_nullable_to_non_nullable
as List<RecommendedAction>,
  ));
}

}


/// Adds pattern-matching-related methods to [ContextualIntervention].
extension ContextualInterventionPatterns on ContextualIntervention {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ContextualIntervention value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ContextualIntervention() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ContextualIntervention value)  $default,){
final _that = this;
switch (_that) {
case _ContextualIntervention():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ContextualIntervention value)?  $default,){
final _that = this;
switch (_that) {
case _ContextualIntervention() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'triggered_by_event_id')  String? triggeredByEventId, @JsonKey(name: 'triggered_by_threat_id')  String? triggeredByThreatId, @JsonKey(name: 'snapshot_id')  String? snapshotId, @JsonKey(name: 'simulation_run_id')  String? simulationRunId, @JsonKey(name: 'outcome_checked_at')  DateTime? outcomeCheckedAt, @JsonKey(name: 'decision_trace')  List<TraceStep> decisionTrace, @JsonKey(name: 'recommended_actions')  List<RecommendedAction> recommendedActions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ContextualIntervention() when $default != null:
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt,_that.triggeredByEventId,_that.triggeredByThreatId,_that.snapshotId,_that.simulationRunId,_that.outcomeCheckedAt,_that.decisionTrace,_that.recommendedActions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'triggered_by_event_id')  String? triggeredByEventId, @JsonKey(name: 'triggered_by_threat_id')  String? triggeredByThreatId, @JsonKey(name: 'snapshot_id')  String? snapshotId, @JsonKey(name: 'simulation_run_id')  String? simulationRunId, @JsonKey(name: 'outcome_checked_at')  DateTime? outcomeCheckedAt, @JsonKey(name: 'decision_trace')  List<TraceStep> decisionTrace, @JsonKey(name: 'recommended_actions')  List<RecommendedAction> recommendedActions)  $default,) {final _that = this;
switch (_that) {
case _ContextualIntervention():
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt,_that.triggeredByEventId,_that.triggeredByThreatId,_that.snapshotId,_that.simulationRunId,_that.outcomeCheckedAt,_that.decisionTrace,_that.recommendedActions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String severity, @JsonKey(name: 'severity_raw')  double severityRaw, @JsonKey(name: 'confidence_ceiling_applied')  bool confidenceCeilingApplied,  String headline,  String body,  double probability, @JsonKey(name: 'urgency_score')  double urgencyScore, @JsonKey(name: 'data_confidence')  double dataConfidence, @JsonKey(name: 'shadow_mode')  bool shadowMode,  bool delivered, @JsonKey(name: 'user_acknowledged')  bool userAcknowledged, @JsonKey(name: 'user_acted')  bool userActed, @JsonKey(name: 'outcome_materialized')  bool? outcomeMaterialized, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'triggered_by_event_id')  String? triggeredByEventId, @JsonKey(name: 'triggered_by_threat_id')  String? triggeredByThreatId, @JsonKey(name: 'snapshot_id')  String? snapshotId, @JsonKey(name: 'simulation_run_id')  String? simulationRunId, @JsonKey(name: 'outcome_checked_at')  DateTime? outcomeCheckedAt, @JsonKey(name: 'decision_trace')  List<TraceStep> decisionTrace, @JsonKey(name: 'recommended_actions')  List<RecommendedAction> recommendedActions)?  $default,) {final _that = this;
switch (_that) {
case _ContextualIntervention() when $default != null:
return $default(_that.id,_that.severity,_that.severityRaw,_that.confidenceCeilingApplied,_that.headline,_that.body,_that.probability,_that.urgencyScore,_that.dataConfidence,_that.shadowMode,_that.delivered,_that.userAcknowledged,_that.userActed,_that.outcomeMaterialized,_that.createdAt,_that.triggeredByEventId,_that.triggeredByThreatId,_that.snapshotId,_that.simulationRunId,_that.outcomeCheckedAt,_that.decisionTrace,_that.recommendedActions);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ContextualIntervention implements ContextualIntervention {
  const _ContextualIntervention({required this.id, required this.severity, @JsonKey(name: 'severity_raw') required this.severityRaw, @JsonKey(name: 'confidence_ceiling_applied') required this.confidenceCeilingApplied, required this.headline, required this.body, required this.probability, @JsonKey(name: 'urgency_score') required this.urgencyScore, @JsonKey(name: 'data_confidence') required this.dataConfidence, @JsonKey(name: 'shadow_mode') required this.shadowMode, required this.delivered, @JsonKey(name: 'user_acknowledged') required this.userAcknowledged, @JsonKey(name: 'user_acted') required this.userActed, @JsonKey(name: 'outcome_materialized') this.outcomeMaterialized, @JsonKey(name: 'created_at') required this.createdAt, @JsonKey(name: 'triggered_by_event_id') this.triggeredByEventId, @JsonKey(name: 'triggered_by_threat_id') this.triggeredByThreatId, @JsonKey(name: 'snapshot_id') this.snapshotId, @JsonKey(name: 'simulation_run_id') this.simulationRunId, @JsonKey(name: 'outcome_checked_at') this.outcomeCheckedAt, @JsonKey(name: 'decision_trace')  List<TraceStep> decisionTrace = const [], @JsonKey(name: 'recommended_actions')  List<RecommendedAction> recommendedActions = const []}): _decisionTrace = decisionTrace,_recommendedActions = recommendedActions;
  factory _ContextualIntervention.fromJson(Map<String, dynamic> json) => _$ContextualInterventionFromJson(json);

@override final  String id;
@override final  String severity;
@override@JsonKey(name: 'severity_raw') final  double severityRaw;
@override@JsonKey(name: 'confidence_ceiling_applied') final  bool confidenceCeilingApplied;
@override final  String headline;
@override final  String body;
@override final  double probability;
@override@JsonKey(name: 'urgency_score') final  double urgencyScore;
@override@JsonKey(name: 'data_confidence') final  double dataConfidence;
@override@JsonKey(name: 'shadow_mode') final  bool shadowMode;
@override final  bool delivered;
@override@JsonKey(name: 'user_acknowledged') final  bool userAcknowledged;
@override@JsonKey(name: 'user_acted') final  bool userActed;
@override@JsonKey(name: 'outcome_materialized') final  bool? outcomeMaterialized;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;
@override@JsonKey(name: 'triggered_by_event_id') final  String? triggeredByEventId;
@override@JsonKey(name: 'triggered_by_threat_id') final  String? triggeredByThreatId;
@override@JsonKey(name: 'snapshot_id') final  String? snapshotId;
@override@JsonKey(name: 'simulation_run_id') final  String? simulationRunId;
@override@JsonKey(name: 'outcome_checked_at') final  DateTime? outcomeCheckedAt;
 final  List<TraceStep> _decisionTrace;
@override@JsonKey(name: 'decision_trace') List<TraceStep> get decisionTrace {
  if (_decisionTrace is EqualUnmodifiableListView) return _decisionTrace;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_decisionTrace);
}

 final  List<RecommendedAction> _recommendedActions;
@override@JsonKey(name: 'recommended_actions') List<RecommendedAction> get recommendedActions {
  if (_recommendedActions is EqualUnmodifiableListView) return _recommendedActions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recommendedActions);
}


/// Create a copy of ContextualIntervention
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ContextualInterventionCopyWith<_ContextualIntervention> get copyWith => __$ContextualInterventionCopyWithImpl<_ContextualIntervention>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ContextualInterventionToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ContextualIntervention&&(identical(other.id, id) || other.id == id)&&(identical(other.severity, severity) || other.severity == severity)&&(identical(other.severityRaw, severityRaw) || other.severityRaw == severityRaw)&&(identical(other.confidenceCeilingApplied, confidenceCeilingApplied) || other.confidenceCeilingApplied == confidenceCeilingApplied)&&(identical(other.headline, headline) || other.headline == headline)&&(identical(other.body, body) || other.body == body)&&(identical(other.probability, probability) || other.probability == probability)&&(identical(other.urgencyScore, urgencyScore) || other.urgencyScore == urgencyScore)&&(identical(other.dataConfidence, dataConfidence) || other.dataConfidence == dataConfidence)&&(identical(other.shadowMode, shadowMode) || other.shadowMode == shadowMode)&&(identical(other.delivered, delivered) || other.delivered == delivered)&&(identical(other.userAcknowledged, userAcknowledged) || other.userAcknowledged == userAcknowledged)&&(identical(other.userActed, userActed) || other.userActed == userActed)&&(identical(other.outcomeMaterialized, outcomeMaterialized) || other.outcomeMaterialized == outcomeMaterialized)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.triggeredByEventId, triggeredByEventId) || other.triggeredByEventId == triggeredByEventId)&&(identical(other.triggeredByThreatId, triggeredByThreatId) || other.triggeredByThreatId == triggeredByThreatId)&&(identical(other.snapshotId, snapshotId) || other.snapshotId == snapshotId)&&(identical(other.simulationRunId, simulationRunId) || other.simulationRunId == simulationRunId)&&(identical(other.outcomeCheckedAt, outcomeCheckedAt) || other.outcomeCheckedAt == outcomeCheckedAt)&&const DeepCollectionEquality().equals(other.decisionTrace, _decisionTrace)&&const DeepCollectionEquality().equals(other.recommendedActions, _recommendedActions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hashAll([runtimeType,id,severity,severityRaw,confidenceCeilingApplied,headline,body,probability,urgencyScore,dataConfidence,shadowMode,delivered,userAcknowledged,userActed,outcomeMaterialized,createdAt,triggeredByEventId,triggeredByThreatId,snapshotId,simulationRunId,outcomeCheckedAt,const DeepCollectionEquality().hash(_decisionTrace),const DeepCollectionEquality().hash(_recommendedActions)]);
}

@override
String toString() {
    return 'ContextualIntervention(id: $id, severity: $severity, severityRaw: $severityRaw, confidenceCeilingApplied: $confidenceCeilingApplied, headline: $headline, body: $body, probability: $probability, urgencyScore: $urgencyScore, dataConfidence: $dataConfidence, shadowMode: $shadowMode, delivered: $delivered, userAcknowledged: $userAcknowledged, userActed: $userActed, outcomeMaterialized: $outcomeMaterialized, createdAt: $createdAt, triggeredByEventId: $triggeredByEventId, triggeredByThreatId: $triggeredByThreatId, snapshotId: $snapshotId, simulationRunId: $simulationRunId, outcomeCheckedAt: $outcomeCheckedAt, decisionTrace: $decisionTrace, recommendedActions: $recommendedActions)';
}


}

/// @nodoc
abstract mixin class _$ContextualInterventionCopyWith<$Res> implements $ContextualInterventionCopyWith<$Res> {
  factory _$ContextualInterventionCopyWith(_ContextualIntervention value, $Res Function(_ContextualIntervention) _then) = __$ContextualInterventionCopyWithImpl;
@override @useResult
$Res call({
 String id, String severity,@JsonKey(name: 'severity_raw') double severityRaw,@JsonKey(name: 'confidence_ceiling_applied') bool confidenceCeilingApplied, String headline, String body, double probability,@JsonKey(name: 'urgency_score') double urgencyScore,@JsonKey(name: 'data_confidence') double dataConfidence,@JsonKey(name: 'shadow_mode') bool shadowMode, bool delivered,@JsonKey(name: 'user_acknowledged') bool userAcknowledged,@JsonKey(name: 'user_acted') bool userActed,@JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'triggered_by_event_id') String? triggeredByEventId,@JsonKey(name: 'triggered_by_threat_id') String? triggeredByThreatId,@JsonKey(name: 'snapshot_id') String? snapshotId,@JsonKey(name: 'simulation_run_id') String? simulationRunId,@JsonKey(name: 'outcome_checked_at') DateTime? outcomeCheckedAt,@JsonKey(name: 'decision_trace') List<TraceStep> decisionTrace,@JsonKey(name: 'recommended_actions') List<RecommendedAction> recommendedActions
});




}
/// @nodoc
class __$ContextualInterventionCopyWithImpl<$Res>
    implements _$ContextualInterventionCopyWith<$Res> {
  __$ContextualInterventionCopyWithImpl(this._self, this._then);

  final _ContextualIntervention _self;
  final $Res Function(_ContextualIntervention) _then;

/// Create a copy of ContextualIntervention
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? severity = null,Object? severityRaw = null,Object? confidenceCeilingApplied = null,Object? headline = null,Object? body = null,Object? probability = null,Object? urgencyScore = null,Object? dataConfidence = null,Object? shadowMode = null,Object? delivered = null,Object? userAcknowledged = null,Object? userActed = null,Object? outcomeMaterialized = freezed,Object? createdAt = null,Object? triggeredByEventId = freezed,Object? triggeredByThreatId = freezed,Object? snapshotId = freezed,Object? simulationRunId = freezed,Object? outcomeCheckedAt = freezed,Object? decisionTrace = null,Object? recommendedActions = null,}) {
  return _then(_ContextualIntervention(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,severityRaw: null == severityRaw ? _self.severityRaw : severityRaw // ignore: cast_nullable_to_non_nullable
as double,confidenceCeilingApplied: null == confidenceCeilingApplied ? _self.confidenceCeilingApplied : confidenceCeilingApplied // ignore: cast_nullable_to_non_nullable
as bool,headline: null == headline ? _self.headline : headline // ignore: cast_nullable_to_non_nullable
as String,body: null == body ? _self.body : body // ignore: cast_nullable_to_non_nullable
as String,probability: null == probability ? _self.probability : probability // ignore: cast_nullable_to_non_nullable
as double,urgencyScore: null == urgencyScore ? _self.urgencyScore : urgencyScore // ignore: cast_nullable_to_non_nullable
as double,dataConfidence: null == dataConfidence ? _self.dataConfidence : dataConfidence // ignore: cast_nullable_to_non_nullable
as double,shadowMode: null == shadowMode ? _self.shadowMode : shadowMode // ignore: cast_nullable_to_non_nullable
as bool,delivered: null == delivered ? _self.delivered : delivered // ignore: cast_nullable_to_non_nullable
as bool,userAcknowledged: null == userAcknowledged ? _self.userAcknowledged : userAcknowledged // ignore: cast_nullable_to_non_nullable
as bool,userActed: null == userActed ? _self.userActed : userActed // ignore: cast_nullable_to_non_nullable
as bool,outcomeMaterialized: freezed == outcomeMaterialized ? _self.outcomeMaterialized : outcomeMaterialized // ignore: cast_nullable_to_non_nullable
as bool?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,triggeredByEventId: freezed == triggeredByEventId ? _self.triggeredByEventId : triggeredByEventId // ignore: cast_nullable_to_non_nullable
as String?,triggeredByThreatId: freezed == triggeredByThreatId ? _self.triggeredByThreatId : triggeredByThreatId // ignore: cast_nullable_to_non_nullable
as String?,snapshotId: freezed == snapshotId ? _self.snapshotId : snapshotId // ignore: cast_nullable_to_non_nullable
as String?,simulationRunId: freezed == simulationRunId ? _self.simulationRunId : simulationRunId // ignore: cast_nullable_to_non_nullable
as String?,outcomeCheckedAt: freezed == outcomeCheckedAt ? _self.outcomeCheckedAt : outcomeCheckedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,decisionTrace: null == decisionTrace ? _self._decisionTrace : decisionTrace // ignore: cast_nullable_to_non_nullable
as List<TraceStep>,recommendedActions: null == recommendedActions ? _self._recommendedActions : recommendedActions // ignore: cast_nullable_to_non_nullable
as List<RecommendedAction>,
  ));
}


}

// dart format on
