import 'package:freezed_annotation/freezed_annotation.dart';

part 'threat_impact.freezed.dart';
part 'threat_impact.g.dart';

/// Mirrors app.modules.threat.impact.ThreatImpact (ThreatImpactResponse
/// on the wire) — the differentiator: what a threat would actually cost.
@freezed
abstract class ThreatImpact with _$ThreatImpact {
  const factory ThreatImpact({
    @JsonKey(name: 'would_cause_shortfall') required bool wouldCauseShortfall,
    @JsonKey(name: 'prob_before') required double probBefore,
    @JsonKey(name: 'prob_after') required double probAfter,
    @JsonKey(name: 'obligations_at_risk') @Default([]) List<String> obligationsAtRisk,
    @JsonKey(name: 'days_until_first_impact') int? daysUntilFirstImpact,
    @JsonKey(name: 'human_statement') required String humanStatement,
  }) = _ThreatImpact;

  factory ThreatImpact.fromJson(Map<String, dynamic> json) => _$ThreatImpactFromJson(json);
}
