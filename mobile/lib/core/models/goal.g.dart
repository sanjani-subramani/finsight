// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'goal.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Goal _$GoalFromJson(Map<String, dynamic> json) => _Goal(
  goalId: json['goal_id'] as String,
  label: json['label'] as String,
  targetAmount: const DecimalConverter().fromJson(
    json['target_amount'] as String,
  ),
  savedAmount: const DecimalConverter().fromJson(
    json['saved_amount'] as String,
  ),
  targetDate: json['target_date'] == null
      ? null
      : DateTime.parse(json['target_date'] as String),
  priority: (json['priority'] as num).toInt(),
  isFlexible: json['is_flexible'] as bool,
);

Map<String, dynamic> _$GoalToJson(_Goal instance) => <String, dynamic>{
  'goal_id': instance.goalId,
  'label': instance.label,
  'target_amount': const DecimalConverter().toJson(instance.targetAmount),
  'saved_amount': const DecimalConverter().toJson(instance.savedAmount),
  'target_date': instance.targetDate?.toIso8601String(),
  'priority': instance.priority,
  'is_flexible': instance.isFlexible,
};
