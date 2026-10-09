// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'income_forecast.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IncomeForecast _$IncomeForecastFromJson(Map<String, dynamic> json) =>
    _IncomeForecast(
      expectedMin: const NullableDecimalConverter().fromJson(
        json['expected_min'] as String?,
      ),
      expectedMax: const NullableDecimalConverter().fromJson(
        json['expected_max'] as String?,
      ),
      p10: const NullableDecimalConverter().fromJson(json['p10'] as String?),
      p50: const NullableDecimalConverter().fromJson(json['p50'] as String?),
      p90: const NullableDecimalConverter().fromJson(json['p90'] as String?),
      expectedArrival: json['expected_arrival'] == null
          ? null
          : DateTime.parse(json['expected_arrival'] as String),
      arrivalUncertaintyDays: (json['arrival_uncertainty_days'] as num?)
          ?.toInt(),
      source: json['source'] as String,
      sampleSize: (json['sample_size'] as num?)?.toInt() ?? 0,
      confidenceScore: (json['confidence_score'] as num).toDouble(),
    );

Map<String, dynamic> _$IncomeForecastToJson(
  _IncomeForecast instance,
) => <String, dynamic>{
  'expected_min': const NullableDecimalConverter().toJson(instance.expectedMin),
  'expected_max': const NullableDecimalConverter().toJson(instance.expectedMax),
  'p10': const NullableDecimalConverter().toJson(instance.p10),
  'p50': const NullableDecimalConverter().toJson(instance.p50),
  'p90': const NullableDecimalConverter().toJson(instance.p90),
  'expected_arrival': instance.expectedArrival?.toIso8601String(),
  'arrival_uncertainty_days': instance.arrivalUncertaintyDays,
  'source': instance.source,
  'sample_size': instance.sampleSize,
  'confidence_score': instance.confidenceScore,
};
