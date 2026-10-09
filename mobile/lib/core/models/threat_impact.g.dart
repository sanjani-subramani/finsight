// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'threat_impact.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ThreatImpact _$ThreatImpactFromJson(Map<String, dynamic> json) =>
    _ThreatImpact(
      wouldCauseShortfall: json['would_cause_shortfall'] as bool,
      probBefore: (json['prob_before'] as num).toDouble(),
      probAfter: (json['prob_after'] as num).toDouble(),
      obligationsAtRisk:
          (json['obligations_at_risk'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      daysUntilFirstImpact: (json['days_until_first_impact'] as num?)?.toInt(),
      humanStatement: json['human_statement'] as String,
    );

Map<String, dynamic> _$ThreatImpactToJson(_ThreatImpact instance) =>
    <String, dynamic>{
      'would_cause_shortfall': instance.wouldCauseShortfall,
      'prob_before': instance.probBefore,
      'prob_after': instance.probAfter,
      'obligations_at_risk': instance.obligationsAtRisk,
      'days_until_first_impact': instance.daysUntilFirstImpact,
      'human_statement': instance.humanStatement,
    };
