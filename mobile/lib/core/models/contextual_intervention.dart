import 'package:freezed_annotation/freezed_annotation.dart';

import 'recommended_action.dart';
import 'trace_step.dart';

part 'contextual_intervention.freezed.dart';
part 'contextual_intervention.g.dart';

/// GET /decisions and GET /decisions/shadow list item
/// (InterventionSummaryResponse).
@freezed
abstract class InterventionSummary with _$InterventionSummary {
  const factory InterventionSummary({
    required String id,
    // "ignore" | "monitor" | "notify" | "critical"
    required String severity,
    @JsonKey(name: 'severity_raw') required double severityRaw,
    @JsonKey(name: 'confidence_ceiling_applied') required bool confidenceCeilingApplied,
    required String headline,
    required String body,
    required double probability,
    @JsonKey(name: 'urgency_score') required double urgencyScore,
    @JsonKey(name: 'data_confidence') required double dataConfidence,
    @JsonKey(name: 'shadow_mode') required bool shadowMode,
    required bool delivered,
    @JsonKey(name: 'user_acknowledged') required bool userAcknowledged,
    @JsonKey(name: 'user_acted') required bool userActed,
    @JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _InterventionSummary;

  factory InterventionSummary.fromJson(Map<String, dynamic> json) =>
      _$InterventionSummaryFromJson(json);
}

/// GET /decisions/{id} — mirrors app.contracts.events.ContextualIntervention
/// as returned on the wire (InterventionDetailResponse): the full decision
/// trace and recommended actions, ready for the explainability view.
@freezed
abstract class ContextualIntervention with _$ContextualIntervention {
  const factory ContextualIntervention({
    required String id,
    required String severity,
    @JsonKey(name: 'severity_raw') required double severityRaw,
    @JsonKey(name: 'confidence_ceiling_applied') required bool confidenceCeilingApplied,
    required String headline,
    required String body,
    required double probability,
    @JsonKey(name: 'urgency_score') required double urgencyScore,
    @JsonKey(name: 'data_confidence') required double dataConfidence,
    @JsonKey(name: 'shadow_mode') required bool shadowMode,
    required bool delivered,
    @JsonKey(name: 'user_acknowledged') required bool userAcknowledged,
    @JsonKey(name: 'user_acted') required bool userActed,
    @JsonKey(name: 'outcome_materialized') bool? outcomeMaterialized,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'triggered_by_event_id') String? triggeredByEventId,
    @JsonKey(name: 'triggered_by_threat_id') String? triggeredByThreatId,
    @JsonKey(name: 'snapshot_id') String? snapshotId,
    @JsonKey(name: 'simulation_run_id') String? simulationRunId,
    @JsonKey(name: 'outcome_checked_at') DateTime? outcomeCheckedAt,
    @JsonKey(name: 'decision_trace') @Default([]) List<TraceStep> decisionTrace,
    @JsonKey(name: 'recommended_actions') @Default([]) List<RecommendedAction> recommendedActions,
  }) = _ContextualIntervention;

  factory ContextualIntervention.fromJson(Map<String, dynamic> json) =>
      _$ContextualInterventionFromJson(json);
}
