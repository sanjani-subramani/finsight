// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'financial_state_snapshot.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_FinancialStateSnapshot _$FinancialStateSnapshotFromJson(
  Map<String, dynamic> json,
) => _FinancialStateSnapshot(
  schemaVersion: (json['schema_version'] as num?)?.toInt() ?? 1,
  snapshotId: json['snapshot_id'] as String,
  userId: json['user_id'] as String,
  generatedAt: DateTime.parse(json['generated_at'] as String),
  cashAvailable: const DecimalConverter().fromJson(
    json['cash_available'] as String,
  ),
  emergencyFund: const DecimalConverter().fromJson(
    json['emergency_fund'] as String,
  ),
  incomeForecast: IncomeForecast.fromJson(
    json['income_forecast'] as Map<String, dynamic>,
  ),
  obligations:
      (json['obligations'] as List<dynamic>?)
          ?.map((e) => Obligation.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  goals:
      (json['goals'] as List<dynamic>?)
          ?.map((e) => Goal.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  weather: json['weather'] as String,
  shortfallRisks:
      (json['shortfall_risks'] as List<dynamic>?)
          ?.map((e) => ShortfallRisk.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  timeToDangerDays: (json['time_to_danger_days'] as num?)?.toInt(),
  safeToSpend: const DecimalConverter().fromJson(
    json['safe_to_spend'] as String,
  ),
  stateConfidence: (json['state_confidence'] as num).toDouble(),
  unconfirmedEventCount:
      (json['unconfirmed_event_count'] as num?)?.toInt() ?? 0,
  containsSimulatedData: json['contains_simulated_data'] as bool? ?? false,
  lastEventId: json['last_event_id'] as String?,
  eventsApplied: (json['events_applied'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$FinancialStateSnapshotToJson(
  _FinancialStateSnapshot instance,
) => <String, dynamic>{
  'schema_version': instance.schemaVersion,
  'snapshot_id': instance.snapshotId,
  'user_id': instance.userId,
  'generated_at': instance.generatedAt.toIso8601String(),
  'cash_available': const DecimalConverter().toJson(instance.cashAvailable),
  'emergency_fund': const DecimalConverter().toJson(instance.emergencyFund),
  'income_forecast': instance.incomeForecast,
  'obligations': instance.obligations,
  'goals': instance.goals,
  'weather': instance.weather,
  'shortfall_risks': instance.shortfallRisks,
  'time_to_danger_days': instance.timeToDangerDays,
  'safe_to_spend': const DecimalConverter().toJson(instance.safeToSpend),
  'state_confidence': instance.stateConfidence,
  'unconfirmed_event_count': instance.unconfirmedEventCount,
  'contains_simulated_data': instance.containsSimulatedData,
  'last_event_id': instance.lastEventId,
  'events_applied': instance.eventsApplied,
};
