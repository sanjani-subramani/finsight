import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';
import 'goal.dart';
import 'income_forecast.dart';
import 'obligation.dart';
import 'shortfall_risk.dart';

part 'financial_state_snapshot.freezed.dart';
part 'financial_state_snapshot.g.dart';

/// Mirrors app.contracts.events.FinancialStateSnapshot exactly —
/// GET /twin/snapshot returns this shape directly.
@freezed
abstract class FinancialStateSnapshot with _$FinancialStateSnapshot {
  const FinancialStateSnapshot._();

  const factory FinancialStateSnapshot({
    @JsonKey(name: 'schema_version') @Default(1) int schemaVersion,
    @JsonKey(name: 'snapshot_id') required String snapshotId,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'generated_at') required DateTime generatedAt,
    @JsonKey(name: 'cash_available') @DecimalConverter() required Decimal cashAvailable,
    @JsonKey(name: 'emergency_fund') @DecimalConverter() required Decimal emergencyFund,
    @JsonKey(name: 'income_forecast') required IncomeForecast incomeForecast,
    @Default([]) List<Obligation> obligations,
    @Default([]) List<Goal> goals,
    // "stable" | "pressure" | "risk" | "critical"
    required String weather,
    @JsonKey(name: 'shortfall_risks') @Default([]) List<ShortfallRisk> shortfallRisks,
    @JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,
    @JsonKey(name: 'safe_to_spend') @DecimalConverter() required Decimal safeToSpend,
    @JsonKey(name: 'state_confidence') required double stateConfidence,
    @JsonKey(name: 'unconfirmed_event_count') @Default(0) int unconfirmedEventCount,
    @JsonKey(name: 'contains_simulated_data') @Default(false) bool containsSimulatedData,
    @JsonKey(name: 'last_event_id') String? lastEventId,
    @JsonKey(name: 'events_applied') @Default(0) int eventsApplied,
  }) = _FinancialStateSnapshot;

  factory FinancialStateSnapshot.fromJson(Map<String, dynamic> json) =>
      _$FinancialStateSnapshotFromJson(json);

  /// Mirrors the backend's total_fixed_obligations property — sum of
  /// unpaid, fixed obligations. Kept in lockstep with
  /// app.contracts.events.FinancialStateSnapshot.total_fixed_obligations.
  Decimal get totalFixedObligations => obligations
      .where((o) => o.isFixed && !o.isPaid)
      .fold(Decimal.zero, (sum, o) => sum + o.amount);
}
