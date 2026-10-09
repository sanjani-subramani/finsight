// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'obligation.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Obligation _$ObligationFromJson(Map<String, dynamic> json) => _Obligation(
  obligationId: json['obligation_id'] as String,
  label: json['label'] as String,
  amount: const DecimalConverter().fromJson(json['amount'] as String),
  dueDate: DateTime.parse(json['due_date'] as String),
  category: json['category'] as String?,
  isFixed: json['is_fixed'] as bool,
  isPaid: json['is_paid'] as bool,
  confidenceScore: (json['confidence_score'] as num).toDouble(),
);

Map<String, dynamic> _$ObligationToJson(_Obligation instance) =>
    <String, dynamic>{
      'obligation_id': instance.obligationId,
      'label': instance.label,
      'amount': const DecimalConverter().toJson(instance.amount),
      'due_date': instance.dueDate.toIso8601String(),
      'category': instance.category,
      'is_fixed': instance.isFixed,
      'is_paid': instance.isPaid,
      'confidence_score': instance.confidenceScore,
    };
