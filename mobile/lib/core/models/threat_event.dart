import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';
import 'threat_impact.dart';
import 'threat_signal.dart';

part 'threat_event.freezed.dart';
part 'threat_event.g.dart';

/// Mirrors app.contracts.events.ThreatEvent as returned by
/// POST /threat/sms | /threat/url | /threat/qr (ThreatEventResponse on
/// the wire — the immediate analysis result, including impact when the
/// threat named a requested amount).
@freezed
abstract class ThreatEvent with _$ThreatEvent {
  const factory ThreatEvent({
    @JsonKey(name: 'threat_id') required String threatId,
    // "call" | "sms" | "qr" | "link"
    required String channel,
    @JsonKey(name: 'risk_score') required double riskScore,
    @JsonKey(name: 'primary_category') required String primaryCategory,
    @Default([]) List<ThreatSignal> signals,
    @JsonKey(name: 'requested_amount') @NullableDecimalConverter() Decimal? requestedAmount,
    @JsonKey(name: 'payee_identifier') String? payeeIdentifier,
    @JsonKey(name: 'detected_at') required DateTime detectedAt,
    ThreatImpact? impact,
  }) = _ThreatEvent;

  factory ThreatEvent.fromJson(Map<String, dynamic> json) => _$ThreatEventFromJson(json);
}

/// GET /threat/events — list item (ThreatEventSummaryResponse).
@freezed
abstract class ThreatEventSummary with _$ThreatEventSummary {
  const factory ThreatEventSummary({
    required String id,
    required String channel,
    @JsonKey(name: 'risk_score') required double riskScore,
    @JsonKey(name: 'primary_category') required String primaryCategory,
    @JsonKey(name: 'detected_at') required DateTime detectedAt,
  }) = _ThreatEventSummary;

  factory ThreatEventSummary.fromJson(Map<String, dynamic> json) =>
      _$ThreatEventSummaryFromJson(json);
}

/// GET /threat/events/{id} — full detail (ThreatEventDetailResponse).
@freezed
abstract class ThreatEventDetail with _$ThreatEventDetail {
  const factory ThreatEventDetail({
    required String id,
    required String channel,
    @JsonKey(name: 'risk_score') required double riskScore,
    @JsonKey(name: 'primary_category') required String primaryCategory,
    @Default([]) List<ThreatSignal> signals,
    @JsonKey(name: 'requested_amount') @NullableDecimalConverter() Decimal? requestedAmount,
    @JsonKey(name: 'payee_identifier') String? payeeIdentifier,
    @JsonKey(name: 'raw_reference') String? rawReference,
    @JsonKey(name: 'transcript_excerpt') String? transcriptExcerpt,
    @JsonKey(name: 'data_source') required String dataSource,
    @JsonKey(name: 'detection_confidence') required double detectionConfidence,
    @JsonKey(name: 'financial_impact') ThreatImpact? financialImpact,
    @JsonKey(name: 'detected_at') required DateTime detectedAt,
  }) = _ThreatEventDetail;

  factory ThreatEventDetail.fromJson(Map<String, dynamic> json) =>
      _$ThreatEventDetailFromJson(json);
}
