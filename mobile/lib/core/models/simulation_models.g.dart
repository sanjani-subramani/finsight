// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'simulation_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_BalanceMatrixSummary _$BalanceMatrixSummaryFromJson(
  Map<String, dynamic> json,
) => _BalanceMatrixSummary(
  days:
      (json['days'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList() ??
      const [],
  p5:
      (json['p5'] as List<dynamic>?)
          ?.map((e) => (e as num).toDouble())
          .toList() ??
      const [],
  p25:
      (json['p25'] as List<dynamic>?)
          ?.map((e) => (e as num).toDouble())
          .toList() ??
      const [],
  p50:
      (json['p50'] as List<dynamic>?)
          ?.map((e) => (e as num).toDouble())
          .toList() ??
      const [],
  p75:
      (json['p75'] as List<dynamic>?)
          ?.map((e) => (e as num).toDouble())
          .toList() ??
      const [],
  p95:
      (json['p95'] as List<dynamic>?)
          ?.map((e) => (e as num).toDouble())
          .toList() ??
      const [],
);

Map<String, dynamic> _$BalanceMatrixSummaryToJson(
  _BalanceMatrixSummary instance,
) => <String, dynamic>{
  'days': instance.days,
  'p5': instance.p5,
  'p25': instance.p25,
  'p50': instance.p50,
  'p75': instance.p75,
  'p95': instance.p95,
};

_SensitivityFactor _$SensitivityFactorFromJson(Map<String, dynamic> json) =>
    _SensitivityFactor(
      name: json['name'] as String,
      description: json['description'] as String,
      probBefore: (json['prob_before'] as num).toDouble(),
      probAfter: (json['prob_after'] as num).toDouble(),
      delta: (json['delta'] as num).toDouble(),
      actionable: json['actionable'] as bool,
    );

Map<String, dynamic> _$SensitivityFactorToJson(_SensitivityFactor instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'prob_before': instance.probBefore,
      'prob_after': instance.probAfter,
      'delta': instance.delta,
      'actionable': instance.actionable,
    };

_SimulationRunResult _$SimulationRunResultFromJson(Map<String, dynamic> json) =>
    _SimulationRunResult(
      runId: json['run_id'] as String,
      scenariosRun: (json['scenarios_run'] as num).toInt(),
      horizonDays: (json['horizon_days'] as num).toInt(),
      seed: (json['seed'] as num).toInt(),
      shortfallProbabilityByHorizon:
          (json['shortfall_probability_by_horizon'] as Map<String, dynamic>?)
              ?.map((k, e) => MapEntry(k, (e as num).toDouble())) ??
          const {},
      minBalanceP5: const DecimalConverter().fromJson(
        json['min_balance_p5'] as String,
      ),
      minBalanceP50: const DecimalConverter().fromJson(
        json['min_balance_p50'] as String,
      ),
      timeToDangerDays: (json['time_to_danger_days'] as num?)?.toInt(),
      safeToSpend: const DecimalConverter().fromJson(
        json['safe_to_spend'] as String,
      ),
      durationMs: (json['duration_ms'] as num).toInt(),
      fromCache: json['from_cache'] as bool,
      balanceMatrixSummary: BalanceMatrixSummary.fromJson(
        json['balance_matrix_summary'] as Map<String, dynamic>,
      ),
      sensitivity:
          (json['sensitivity'] as List<dynamic>?)
              ?.map(
                (e) => SensitivityFactor.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const [],
    );

Map<String, dynamic> _$SimulationRunResultToJson(
  _SimulationRunResult instance,
) => <String, dynamic>{
  'run_id': instance.runId,
  'scenarios_run': instance.scenariosRun,
  'horizon_days': instance.horizonDays,
  'seed': instance.seed,
  'shortfall_probability_by_horizon': instance.shortfallProbabilityByHorizon,
  'min_balance_p5': const DecimalConverter().toJson(instance.minBalanceP5),
  'min_balance_p50': const DecimalConverter().toJson(instance.minBalanceP50),
  'time_to_danger_days': instance.timeToDangerDays,
  'safe_to_spend': const DecimalConverter().toJson(instance.safeToSpend),
  'duration_ms': instance.durationMs,
  'from_cache': instance.fromCache,
  'balance_matrix_summary': instance.balanceMatrixSummary,
  'sensitivity': instance.sensitivity,
};

_PurchaseVerdict _$PurchaseVerdictFromJson(Map<String, dynamic> json) =>
    _PurchaseVerdict(
      affordable: json['affordable'] as bool,
      probBefore: (json['prob_before'] as num).toDouble(),
      probAfter: (json['prob_after'] as num).toDouble(),
      waitDaysRecommended: (json['wait_days_recommended'] as num?)?.toInt(),
      reasoningValues:
          json['reasoning_values'] as Map<String, dynamic>? ?? const {},
    );

Map<String, dynamic> _$PurchaseVerdictToJson(_PurchaseVerdict instance) =>
    <String, dynamic>{
      'affordable': instance.affordable,
      'prob_before': instance.probBefore,
      'prob_after': instance.probAfter,
      'wait_days_recommended': instance.waitDaysRecommended,
      'reasoning_values': instance.reasoningValues,
    };
