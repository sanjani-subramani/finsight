// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'narration_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_NarrationResult _$NarrationResultFromJson(Map<String, dynamic> json) =>
    _NarrationResult(
      text: json['text'] as String,
      source: json['source'] as String,
      validationPassed: json['validation_passed'] as bool,
      violations:
          (json['violations'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      cached: json['cached'] as bool,
      durationMs: (json['duration_ms'] as num).toInt(),
    );

Map<String, dynamic> _$NarrationResultToJson(_NarrationResult instance) =>
    <String, dynamic>{
      'text': instance.text,
      'source': instance.source,
      'validation_passed': instance.validationPassed,
      'violations': instance.violations,
      'cached': instance.cached,
      'duration_ms': instance.durationMs,
    };
