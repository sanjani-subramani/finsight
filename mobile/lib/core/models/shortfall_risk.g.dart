// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shortfall_risk.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ShortfallRisk _$ShortfallRiskFromJson(Map<String, dynamic> json) =>
    _ShortfallRisk(
      horizonDays: (json['horizon_days'] as num).toInt(),
      probability: (json['probability'] as num).toDouble(),
      firstBreachDate: json['first_breach_date'] == null
          ? null
          : DateTime.parse(json['first_breach_date'] as String),
      worstCaseBalance: const DecimalConverter().fromJson(
        json['worst_case_balance'] as String,
      ),
      scenariosRun: (json['scenarios_run'] as num).toInt(),
    );

Map<String, dynamic> _$ShortfallRiskToJson(_ShortfallRisk instance) =>
    <String, dynamic>{
      'horizon_days': instance.horizonDays,
      'probability': instance.probability,
      'first_breach_date': instance.firstBreachDate?.toIso8601String(),
      'worst_case_balance': const DecimalConverter().toJson(
        instance.worstCaseBalance,
      ),
      'scenarios_run': instance.scenariosRun,
    };
