import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'shortfall_risk.freezed.dart';
part 'shortfall_risk.g.dart';

/// Mirrors app.contracts.events.ShortfallRisk exactly.
@freezed
abstract class ShortfallRisk with _$ShortfallRisk {
  const factory ShortfallRisk({
    @JsonKey(name: 'horizon_days') required int horizonDays,
    required double probability,
    @JsonKey(name: 'first_breach_date') DateTime? firstBreachDate,
    @JsonKey(name: 'worst_case_balance') @DecimalConverter() required Decimal worstCaseBalance,
    @JsonKey(name: 'scenarios_run') required int scenariosRun,
  }) = _ShortfallRisk;

  factory ShortfallRisk.fromJson(Map<String, dynamic> json) => _$ShortfallRiskFromJson(json);
}
