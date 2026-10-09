// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'trace_step.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TraceStep _$TraceStepFromJson(Map<String, dynamic> json) => _TraceStep(
  order: (json['order'] as num).toInt(),
  stage: json['stage'] as String,
  statement: json['statement'] as String,
  values: json['values'] as Map<String, dynamic>? ?? const {},
);

Map<String, dynamic> _$TraceStepToJson(_TraceStep instance) =>
    <String, dynamic>{
      'order': instance.order,
      'stage': instance.stage,
      'statement': instance.statement,
      'values': instance.values,
    };
