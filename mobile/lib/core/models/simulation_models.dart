import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'simulation_models.freezed.dart';
part 'simulation_models.g.dart';

/// The percentile curves the Monte Carlo engine actually produces
/// (app.modules.simulation.engine — NOT a single line: p5/p25/p50/p75/p95
/// balance projections per day). The Insights forecast chart plots these
/// as BANDS, never collapses them to one line — a single line implies a
/// certainty the model does not have; the band IS the message.
@freezed
abstract class BalanceMatrixSummary with _$BalanceMatrixSummary {
  const factory BalanceMatrixSummary({
    @Default([]) List<int> days,
    @Default([]) List<double> p5,
    @Default([]) List<double> p25,
    @Default([]) List<double> p50,
    @Default([]) List<double> p75,
    @Default([]) List<double> p95,
  }) = _BalanceMatrixSummary;

  factory BalanceMatrixSummary.fromJson(Map<String, dynamic> json) =>
      _$BalanceMatrixSummaryFromJson(json);
}

/// SensitivityFactorResponse — "what would change this" on the
/// Affordability screen.
@freezed
abstract class SensitivityFactor with _$SensitivityFactor {
  const factory SensitivityFactor({
    required String name,
    required String description,
    @JsonKey(name: 'prob_before') required double probBefore,
    @JsonKey(name: 'prob_after') required double probAfter,
    required double delta,
    required bool actionable,
  }) = _SensitivityFactor;

  factory SensitivityFactor.fromJson(Map<String, dynamic> json) =>
      _$SensitivityFactorFromJson(json);
}

/// POST /simulation/run and GET /simulation/run (RunResponse).
@freezed
abstract class SimulationRunResult with _$SimulationRunResult {
  const factory SimulationRunResult({
    @JsonKey(name: 'run_id') required String runId,
    @JsonKey(name: 'scenarios_run') required int scenariosRun,
    @JsonKey(name: 'horizon_days') required int horizonDays,
    required int seed,
    @JsonKey(name: 'shortfall_probability_by_horizon') @Default({}) Map<String, double> shortfallProbabilityByHorizon,
    @JsonKey(name: 'min_balance_p5') @DecimalConverter() required Decimal minBalanceP5,
    @JsonKey(name: 'min_balance_p50') @DecimalConverter() required Decimal minBalanceP50,
    @JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,
    @JsonKey(name: 'safe_to_spend') @DecimalConverter() required Decimal safeToSpend,
    @JsonKey(name: 'duration_ms') required int durationMs,
    @JsonKey(name: 'from_cache') required bool fromCache,
    @JsonKey(name: 'balance_matrix_summary') required BalanceMatrixSummary balanceMatrixSummary,
    @Default([]) List<SensitivityFactor> sensitivity,
  }) = _SimulationRunResult;

  factory SimulationRunResult.fromJson(Map<String, dynamic> json) =>
      _$SimulationRunResultFromJson(json);
}

/// POST /simulation/afford (PurchaseVerdictResponse).
@freezed
abstract class PurchaseVerdict with _$PurchaseVerdict {
  const factory PurchaseVerdict({
    required bool affordable,
    @JsonKey(name: 'prob_before') required double probBefore,
    @JsonKey(name: 'prob_after') required double probAfter,
    @JsonKey(name: 'wait_days_recommended') int? waitDaysRecommended,
    @JsonKey(name: 'reasoning_values') @Default({}) Map<String, dynamic> reasoningValues,
  }) = _PurchaseVerdict;

  factory PurchaseVerdict.fromJson(Map<String, dynamic> json) => _$PurchaseVerdictFromJson(json);
}
