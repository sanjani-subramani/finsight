// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'threat_signal.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ThreatSignal _$ThreatSignalFromJson(Map<String, dynamic> json) =>
    _ThreatSignal(
      name: json['name'] as String,
      category: json['category'] as String,
      weight: (json['weight'] as num).toDouble(),
      evidence: json['evidence'] as String?,
      detector: json['detector'] as String,
    );

Map<String, dynamic> _$ThreatSignalToJson(_ThreatSignal instance) =>
    <String, dynamic>{
      'name': instance.name,
      'category': instance.category,
      'weight': instance.weight,
      'evidence': instance.evidence,
      'detector': instance.detector,
    };
