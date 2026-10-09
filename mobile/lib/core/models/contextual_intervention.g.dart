// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'contextual_intervention.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_InterventionSummary _$InterventionSummaryFromJson(Map<String, dynamic> json) =>
    _InterventionSummary(
      id: json['id'] as String,
      severity: json['severity'] as String,
      severityRaw: (json['severity_raw'] as num).toDouble(),
      confidenceCeilingApplied: json['confidence_ceiling_applied'] as bool,
      headline: json['headline'] as String,
      body: json['body'] as String,
      probability: (json['probability'] as num).toDouble(),
      urgencyScore: (json['urgency_score'] as num).toDouble(),
      dataConfidence: (json['data_confidence'] as num).toDouble(),
      shadowMode: json['shadow_mode'] as bool,
      delivered: json['delivered'] as bool,
      userAcknowledged: json['user_acknowledged'] as bool,
      userActed: json['user_acted'] as bool,
      outcomeMaterialized: json['outcome_materialized'] as bool?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$InterventionSummaryToJson(
  _InterventionSummary instance,
) => <String, dynamic>{
  'id': instance.id,
  'severity': instance.severity,
  'severity_raw': instance.severityRaw,
  'confidence_ceiling_applied': instance.confidenceCeilingApplied,
  'headline': instance.headline,
  'body': instance.body,
  'probability': instance.probability,
  'urgency_score': instance.urgencyScore,
  'data_confidence': instance.dataConfidence,
  'shadow_mode': instance.shadowMode,
  'delivered': instance.delivered,
  'user_acknowledged': instance.userAcknowledged,
  'user_acted': instance.userActed,
  'outcome_materialized': instance.outcomeMaterialized,
  'created_at': instance.createdAt.toIso8601String(),
};

_ContextualIntervention _$ContextualInterventionFromJson(
  Map<String, dynamic> json,
) => _ContextualIntervention(
  id: json['id'] as String,
  severity: json['severity'] as String,
  severityRaw: (json['severity_raw'] as num).toDouble(),
  confidenceCeilingApplied: json['confidence_ceiling_applied'] as bool,
  headline: json['headline'] as String,
  body: json['body'] as String,
  probability: (json['probability'] as num).toDouble(),
  urgencyScore: (json['urgency_score'] as num).toDouble(),
  dataConfidence: (json['data_confidence'] as num).toDouble(),
  shadowMode: json['shadow_mode'] as bool,
  delivered: json['delivered'] as bool,
  userAcknowledged: json['user_acknowledged'] as bool,
  userActed: json['user_acted'] as bool,
  outcomeMaterialized: json['outcome_materialized'] as bool?,
  createdAt: DateTime.parse(json['created_at'] as String),
  triggeredByEventId: json['triggered_by_event_id'] as String?,
  triggeredByThreatId: json['triggered_by_threat_id'] as String?,
  snapshotId: json['snapshot_id'] as String?,
  simulationRunId: json['simulation_run_id'] as String?,
  outcomeCheckedAt: json['outcome_checked_at'] == null
      ? null
      : DateTime.parse(json['outcome_checked_at'] as String),
  decisionTrace:
      (json['decision_trace'] as List<dynamic>?)
          ?.map((e) => TraceStep.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  recommendedActions:
      (json['recommended_actions'] as List<dynamic>?)
          ?.map((e) => RecommendedAction.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$ContextualInterventionToJson(
  _ContextualIntervention instance,
) => <String, dynamic>{
  'id': instance.id,
  'severity': instance.severity,
  'severity_raw': instance.severityRaw,
  'confidence_ceiling_applied': instance.confidenceCeilingApplied,
  'headline': instance.headline,
  'body': instance.body,
  'probability': instance.probability,
  'urgency_score': instance.urgencyScore,
  'data_confidence': instance.dataConfidence,
  'shadow_mode': instance.shadowMode,
  'delivered': instance.delivered,
  'user_acknowledged': instance.userAcknowledged,
  'user_acted': instance.userActed,
  'outcome_materialized': instance.outcomeMaterialized,
  'created_at': instance.createdAt.toIso8601String(),
  'triggered_by_event_id': instance.triggeredByEventId,
  'triggered_by_threat_id': instance.triggeredByThreatId,
  'snapshot_id': instance.snapshotId,
  'simulation_run_id': instance.simulationRunId,
  'outcome_checked_at': instance.outcomeCheckedAt?.toIso8601String(),
  'decision_trace': instance.decisionTrace,
  'recommended_actions': instance.recommendedActions,
};
