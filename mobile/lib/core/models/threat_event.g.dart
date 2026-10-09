// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'threat_event.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ThreatEvent _$ThreatEventFromJson(Map<String, dynamic> json) => _ThreatEvent(
  threatId: json['threat_id'] as String,
  channel: json['channel'] as String,
  riskScore: (json['risk_score'] as num).toDouble(),
  primaryCategory: json['primary_category'] as String,
  signals:
      (json['signals'] as List<dynamic>?)
          ?.map((e) => ThreatSignal.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  requestedAmount: const NullableDecimalConverter().fromJson(
    json['requested_amount'] as String?,
  ),
  payeeIdentifier: json['payee_identifier'] as String?,
  detectedAt: DateTime.parse(json['detected_at'] as String),
  impact: json['impact'] == null
      ? null
      : ThreatImpact.fromJson(json['impact'] as Map<String, dynamic>),
);

Map<String, dynamic> _$ThreatEventToJson(_ThreatEvent instance) =>
    <String, dynamic>{
      'threat_id': instance.threatId,
      'channel': instance.channel,
      'risk_score': instance.riskScore,
      'primary_category': instance.primaryCategory,
      'signals': instance.signals,
      'requested_amount': const NullableDecimalConverter().toJson(
        instance.requestedAmount,
      ),
      'payee_identifier': instance.payeeIdentifier,
      'detected_at': instance.detectedAt.toIso8601String(),
      'impact': instance.impact,
    };

_ThreatEventSummary _$ThreatEventSummaryFromJson(Map<String, dynamic> json) =>
    _ThreatEventSummary(
      id: json['id'] as String,
      channel: json['channel'] as String,
      riskScore: (json['risk_score'] as num).toDouble(),
      primaryCategory: json['primary_category'] as String,
      detectedAt: DateTime.parse(json['detected_at'] as String),
    );

Map<String, dynamic> _$ThreatEventSummaryToJson(_ThreatEventSummary instance) =>
    <String, dynamic>{
      'id': instance.id,
      'channel': instance.channel,
      'risk_score': instance.riskScore,
      'primary_category': instance.primaryCategory,
      'detected_at': instance.detectedAt.toIso8601String(),
    };

_ThreatEventDetail _$ThreatEventDetailFromJson(Map<String, dynamic> json) =>
    _ThreatEventDetail(
      id: json['id'] as String,
      channel: json['channel'] as String,
      riskScore: (json['risk_score'] as num).toDouble(),
      primaryCategory: json['primary_category'] as String,
      signals:
          (json['signals'] as List<dynamic>?)
              ?.map((e) => ThreatSignal.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      requestedAmount: const NullableDecimalConverter().fromJson(
        json['requested_amount'] as String?,
      ),
      payeeIdentifier: json['payee_identifier'] as String?,
      rawReference: json['raw_reference'] as String?,
      transcriptExcerpt: json['transcript_excerpt'] as String?,
      dataSource: json['data_source'] as String,
      detectionConfidence: (json['detection_confidence'] as num).toDouble(),
      financialImpact: json['financial_impact'] == null
          ? null
          : ThreatImpact.fromJson(
              json['financial_impact'] as Map<String, dynamic>,
            ),
      detectedAt: DateTime.parse(json['detected_at'] as String),
    );

Map<String, dynamic> _$ThreatEventDetailToJson(_ThreatEventDetail instance) =>
    <String, dynamic>{
      'id': instance.id,
      'channel': instance.channel,
      'risk_score': instance.riskScore,
      'primary_category': instance.primaryCategory,
      'signals': instance.signals,
      'requested_amount': const NullableDecimalConverter().toJson(
        instance.requestedAmount,
      ),
      'payee_identifier': instance.payeeIdentifier,
      'raw_reference': instance.rawReference,
      'transcript_excerpt': instance.transcriptExcerpt,
      'data_source': instance.dataSource,
      'detection_confidence': instance.detectionConfidence,
      'financial_impact': instance.financialImpact,
      'detected_at': instance.detectedAt.toIso8601String(),
    };
