import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'income_forecast.freezed.dart';
part 'income_forecast.g.dart';

/// Mirrors app.contracts.events.IncomeForecast exactly.
@freezed
abstract class IncomeForecast with _$IncomeForecast {
  const factory IncomeForecast({
    @JsonKey(name: 'expected_min') @NullableDecimalConverter() Decimal? expectedMin,
    @JsonKey(name: 'expected_max') @NullableDecimalConverter() Decimal? expectedMax,
    @NullableDecimalConverter() Decimal? p10,
    @NullableDecimalConverter() Decimal? p50,
    @NullableDecimalConverter() Decimal? p90,
    @JsonKey(name: 'expected_arrival') DateTime? expectedArrival,
    @JsonKey(name: 'arrival_uncertainty_days') int? arrivalUncertaintyDays,
    // "declared" | "observed" | "hybrid"
    required String source,
    @JsonKey(name: 'sample_size') @Default(0) int sampleSize,
    @JsonKey(name: 'confidence_score') required double confidenceScore,
  }) = _IncomeForecast;

  factory IncomeForecast.fromJson(Map<String, dynamic> json) => _$IncomeForecastFromJson(json);
}
