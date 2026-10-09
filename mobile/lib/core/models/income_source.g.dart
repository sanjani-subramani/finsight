// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'income_source.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IncomeSource _$IncomeSourceFromJson(Map<String, dynamic> json) =>
    _IncomeSource(
      id: json['id'] as String,
      label: json['label'] as String,
      counterparty: json['counterparty'] as String?,
      declaredMin: const NullableDecimalConverter().fromJson(
        json['declared_min'] as String?,
      ),
      declaredMax: const NullableDecimalConverter().fromJson(
        json['declared_max'] as String?,
      ),
      declaredFrequencyDays: (json['declared_frequency_days'] as num?)?.toInt(),
      observedP10: const NullableDecimalConverter().fromJson(
        json['observed_p10'] as String?,
      ),
      observedP50: const NullableDecimalConverter().fromJson(
        json['observed_p50'] as String?,
      ),
      observedP90: const NullableDecimalConverter().fromJson(
        json['observed_p90'] as String?,
      ),
      observationCount: (json['observation_count'] as num).toInt(),
      forecastMode: json['forecast_mode'] as String,
      confidenceScore: const DecimalConverter().fromJson(
        json['confidence_score'] as String,
      ),
    );

Map<String, dynamic> _$IncomeSourceToJson(
  _IncomeSource instance,
) => <String, dynamic>{
  'id': instance.id,
  'label': instance.label,
  'counterparty': instance.counterparty,
  'declared_min': const NullableDecimalConverter().toJson(instance.declaredMin),
  'declared_max': const NullableDecimalConverter().toJson(instance.declaredMax),
  'declared_frequency_days': instance.declaredFrequencyDays,
  'observed_p10': const NullableDecimalConverter().toJson(instance.observedP10),
  'observed_p50': const NullableDecimalConverter().toJson(instance.observedP50),
  'observed_p90': const NullableDecimalConverter().toJson(instance.observedP90),
  'observation_count': instance.observationCount,
  'forecast_mode': instance.forecastMode,
  'confidence_score': const DecimalConverter().toJson(instance.confidenceScore),
};
