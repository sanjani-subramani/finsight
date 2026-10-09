// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recommended_action.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_RecommendedAction _$RecommendedActionFromJson(Map<String, dynamic> json) =>
    _RecommendedAction(
      actionType: json['action_type'] as String,
      label: json['label'] as String,
      amount: const NullableDecimalConverter().fromJson(
        json['amount'] as String?,
      ),
      expectedEffect: json['expected_effect'] as String?,
      projectedRiskAfter: (json['projected_risk_after'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$RecommendedActionToJson(_RecommendedAction instance) =>
    <String, dynamic>{
      'action_type': instance.actionType,
      'label': instance.label,
      'amount': const NullableDecimalConverter().toJson(instance.amount),
      'expected_effect': instance.expectedEffect,
      'projected_risk_after': instance.projectedRiskAfter,
    };
