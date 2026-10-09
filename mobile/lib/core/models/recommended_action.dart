import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'recommended_action.freezed.dart';
part 'recommended_action.g.dart';

/// Mirrors app.contracts.events.RecommendedAction exactly.
///
/// projected_risk_after is ALWAYS the backend's actually re-simulated,
/// verified value (see app.modules.decision.arbitration) — never an
/// estimate computed on the client. Display it as-is; never recompute it.
@freezed
abstract class RecommendedAction with _$RecommendedAction {
  const factory RecommendedAction({
    @JsonKey(name: 'action_type') required String actionType,
    required String label,
    @NullableDecimalConverter() Decimal? amount,
    @JsonKey(name: 'expected_effect') String? expectedEffect,
    @JsonKey(name: 'projected_risk_after') double? projectedRiskAfter,
  }) = _RecommendedAction;

  factory RecommendedAction.fromJson(Map<String, dynamic> json) =>
      _$RecommendedActionFromJson(json);
}
