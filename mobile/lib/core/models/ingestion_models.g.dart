// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingestion_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IngestionResult _$IngestionResultFromJson(Map<String, dynamic> json) =>
    _IngestionResult(
      eventId: json['event_id'] as String?,
      method: json['method'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      wasDuplicate: json['was_duplicate'] as bool,
      quarantined: json['quarantined'] as bool,
      reason: json['reason'] as String?,
    );

Map<String, dynamic> _$IngestionResultToJson(_IngestionResult instance) =>
    <String, dynamic>{
      'event_id': instance.eventId,
      'method': instance.method,
      'confidence': instance.confidence,
      'was_duplicate': instance.wasDuplicate,
      'quarantined': instance.quarantined,
      'reason': instance.reason,
    };
