import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'income_source.freezed.dart';
part 'income_source.g.dart';

/// GET /twin/income-sources (IncomeSourceResponse).
///
/// forecast_mode + observation_count together let the Profile screen show
/// the user how their cold-start income model is progressing toward the
/// next mode (declared -> hybrid -> observed) — making the system's
/// learning legible instead of mysterious.
@freezed
abstract class IncomeSource with _$IncomeSource {
  const factory IncomeSource({
    required String id,
    required String label,
    String? counterparty,
    @JsonKey(name: 'declared_min') @NullableDecimalConverter() Decimal? declaredMin,
    @JsonKey(name: 'declared_max') @NullableDecimalConverter() Decimal? declaredMax,
    @JsonKey(name: 'declared_frequency_days') int? declaredFrequencyDays,
    @JsonKey(name: 'observed_p10') @NullableDecimalConverter() Decimal? observedP10,
    @JsonKey(name: 'observed_p50') @NullableDecimalConverter() Decimal? observedP50,
    @JsonKey(name: 'observed_p90') @NullableDecimalConverter() Decimal? observedP90,
    @JsonKey(name: 'observation_count') required int observationCount,
    // "declared" | "hybrid" | "observed"
    @JsonKey(name: 'forecast_mode') required String forecastMode,
    @JsonKey(name: 'confidence_score') @DecimalConverter() required Decimal confidenceScore,
  }) = _IncomeSource;

  factory IncomeSource.fromJson(Map<String, dynamic> json) => _$IncomeSourceFromJson(json);
}
