// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'financial_state_snapshot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$FinancialStateSnapshot {

@JsonKey(name: 'schema_version') int get schemaVersion;@JsonKey(name: 'snapshot_id') String get snapshotId;@JsonKey(name: 'user_id') String get userId;@JsonKey(name: 'generated_at') DateTime get generatedAt;@JsonKey(name: 'cash_available')@DecimalConverter() Decimal get cashAvailable;@JsonKey(name: 'emergency_fund')@DecimalConverter() Decimal get emergencyFund;@JsonKey(name: 'income_forecast') IncomeForecast get incomeForecast; List<Obligation> get obligations; List<Goal> get goals; String get weather;@JsonKey(name: 'shortfall_risks') List<ShortfallRisk> get shortfallRisks;@JsonKey(name: 'time_to_danger_days') int? get timeToDangerDays;@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal get safeToSpend;@JsonKey(name: 'state_confidence') double get stateConfidence;@JsonKey(name: 'unconfirmed_event_count') int get unconfirmedEventCount;@JsonKey(name: 'contains_simulated_data') bool get containsSimulatedData;@JsonKey(name: 'last_event_id') String? get lastEventId;@JsonKey(name: 'events_applied') int get eventsApplied;
/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FinancialStateSnapshotCopyWith<FinancialStateSnapshot> get copyWith => _$FinancialStateSnapshotCopyWithImpl<FinancialStateSnapshot>(this as FinancialStateSnapshot, _$identity);

  /// Serializes this FinancialStateSnapshot to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as FinancialStateSnapshot;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FinancialStateSnapshot&&(identical(other.schemaVersion, _this.schemaVersion) || other.schemaVersion == _this.schemaVersion)&&(identical(other.snapshotId, _this.snapshotId) || other.snapshotId == _this.snapshotId)&&(identical(other.userId, _this.userId) || other.userId == _this.userId)&&(identical(other.generatedAt, _this.generatedAt) || other.generatedAt == _this.generatedAt)&&(identical(other.cashAvailable, _this.cashAvailable) || other.cashAvailable == _this.cashAvailable)&&(identical(other.emergencyFund, _this.emergencyFund) || other.emergencyFund == _this.emergencyFund)&&(identical(other.incomeForecast, _this.incomeForecast) || other.incomeForecast == _this.incomeForecast)&&const DeepCollectionEquality().equals(other.obligations, _this.obligations)&&const DeepCollectionEquality().equals(other.goals, _this.goals)&&(identical(other.weather, _this.weather) || other.weather == _this.weather)&&const DeepCollectionEquality().equals(other.shortfallRisks, _this.shortfallRisks)&&(identical(other.timeToDangerDays, _this.timeToDangerDays) || other.timeToDangerDays == _this.timeToDangerDays)&&(identical(other.safeToSpend, _this.safeToSpend) || other.safeToSpend == _this.safeToSpend)&&(identical(other.stateConfidence, _this.stateConfidence) || other.stateConfidence == _this.stateConfidence)&&(identical(other.unconfirmedEventCount, _this.unconfirmedEventCount) || other.unconfirmedEventCount == _this.unconfirmedEventCount)&&(identical(other.containsSimulatedData, _this.containsSimulatedData) || other.containsSimulatedData == _this.containsSimulatedData)&&(identical(other.lastEventId, _this.lastEventId) || other.lastEventId == _this.lastEventId)&&(identical(other.eventsApplied, _this.eventsApplied) || other.eventsApplied == _this.eventsApplied));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as FinancialStateSnapshot;
  return Object.hash(runtimeType,_this.schemaVersion,_this.snapshotId,_this.userId,_this.generatedAt,_this.cashAvailable,_this.emergencyFund,_this.incomeForecast,const DeepCollectionEquality().hash(_this.obligations),const DeepCollectionEquality().hash(_this.goals),_this.weather,const DeepCollectionEquality().hash(_this.shortfallRisks),_this.timeToDangerDays,_this.safeToSpend,_this.stateConfidence,_this.unconfirmedEventCount,_this.containsSimulatedData,_this.lastEventId,_this.eventsApplied);
}

@override
String toString() {
  final _this = this as FinancialStateSnapshot;
  return 'FinancialStateSnapshot(schemaVersion: ${_this.schemaVersion}, snapshotId: ${_this.snapshotId}, userId: ${_this.userId}, generatedAt: ${_this.generatedAt}, cashAvailable: ${_this.cashAvailable}, emergencyFund: ${_this.emergencyFund}, incomeForecast: ${_this.incomeForecast}, obligations: ${_this.obligations}, goals: ${_this.goals}, weather: ${_this.weather}, shortfallRisks: ${_this.shortfallRisks}, timeToDangerDays: ${_this.timeToDangerDays}, safeToSpend: ${_this.safeToSpend}, stateConfidence: ${_this.stateConfidence}, unconfirmedEventCount: ${_this.unconfirmedEventCount}, containsSimulatedData: ${_this.containsSimulatedData}, lastEventId: ${_this.lastEventId}, eventsApplied: ${_this.eventsApplied})';
}


}

/// @nodoc
abstract mixin class $FinancialStateSnapshotCopyWith<$Res>  {
  factory $FinancialStateSnapshotCopyWith(FinancialStateSnapshot value, $Res Function(FinancialStateSnapshot) _then) = _$FinancialStateSnapshotCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'schema_version') int schemaVersion,@JsonKey(name: 'snapshot_id') String snapshotId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'generated_at') DateTime generatedAt,@JsonKey(name: 'cash_available')@DecimalConverter() Decimal cashAvailable,@JsonKey(name: 'emergency_fund')@DecimalConverter() Decimal emergencyFund,@JsonKey(name: 'income_forecast') IncomeForecast incomeForecast, List<Obligation> obligations, List<Goal> goals, String weather,@JsonKey(name: 'shortfall_risks') List<ShortfallRisk> shortfallRisks,@JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal safeToSpend,@JsonKey(name: 'state_confidence') double stateConfidence,@JsonKey(name: 'unconfirmed_event_count') int unconfirmedEventCount,@JsonKey(name: 'contains_simulated_data') bool containsSimulatedData,@JsonKey(name: 'last_event_id') String? lastEventId,@JsonKey(name: 'events_applied') int eventsApplied
});


$IncomeForecastCopyWith<$Res> get incomeForecast;

}
/// @nodoc
class _$FinancialStateSnapshotCopyWithImpl<$Res>
    implements $FinancialStateSnapshotCopyWith<$Res> {
  _$FinancialStateSnapshotCopyWithImpl(this._self, this._then);

  final FinancialStateSnapshot _self;
  final $Res Function(FinancialStateSnapshot) _then;

/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? schemaVersion = null,Object? snapshotId = null,Object? userId = null,Object? generatedAt = null,Object? cashAvailable = null,Object? emergencyFund = null,Object? incomeForecast = null,Object? obligations = null,Object? goals = null,Object? weather = null,Object? shortfallRisks = null,Object? timeToDangerDays = freezed,Object? safeToSpend = null,Object? stateConfidence = null,Object? unconfirmedEventCount = null,Object? containsSimulatedData = null,Object? lastEventId = freezed,Object? eventsApplied = null,}) {
  return _then(FinancialStateSnapshot(
schemaVersion: null == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as int,snapshotId: null == snapshotId ? _self.snapshotId : snapshotId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,generatedAt: null == generatedAt ? _self.generatedAt : generatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,cashAvailable: null == cashAvailable ? _self.cashAvailable : cashAvailable // ignore: cast_nullable_to_non_nullable
as Decimal,emergencyFund: null == emergencyFund ? _self.emergencyFund : emergencyFund // ignore: cast_nullable_to_non_nullable
as Decimal,incomeForecast: null == incomeForecast ? _self.incomeForecast : incomeForecast // ignore: cast_nullable_to_non_nullable
as IncomeForecast,obligations: null == obligations ? _self.obligations : obligations // ignore: cast_nullable_to_non_nullable
as List<Obligation>,goals: null == goals ? _self.goals : goals // ignore: cast_nullable_to_non_nullable
as List<Goal>,weather: null == weather ? _self.weather : weather // ignore: cast_nullable_to_non_nullable
as String,shortfallRisks: null == shortfallRisks ? _self.shortfallRisks : shortfallRisks // ignore: cast_nullable_to_non_nullable
as List<ShortfallRisk>,timeToDangerDays: freezed == timeToDangerDays ? _self.timeToDangerDays : timeToDangerDays // ignore: cast_nullable_to_non_nullable
as int?,safeToSpend: null == safeToSpend ? _self.safeToSpend : safeToSpend // ignore: cast_nullable_to_non_nullable
as Decimal,stateConfidence: null == stateConfidence ? _self.stateConfidence : stateConfidence // ignore: cast_nullable_to_non_nullable
as double,unconfirmedEventCount: null == unconfirmedEventCount ? _self.unconfirmedEventCount : unconfirmedEventCount // ignore: cast_nullable_to_non_nullable
as int,containsSimulatedData: null == containsSimulatedData ? _self.containsSimulatedData : containsSimulatedData // ignore: cast_nullable_to_non_nullable
as bool,lastEventId: freezed == lastEventId ? _self.lastEventId : lastEventId // ignore: cast_nullable_to_non_nullable
as String?,eventsApplied: null == eventsApplied ? _self.eventsApplied : eventsApplied // ignore: cast_nullable_to_non_nullable
as int,
  ));
}
/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IncomeForecastCopyWith<$Res> get incomeForecast {
  
  return $IncomeForecastCopyWith<$Res>(_self.incomeForecast, (value) {
    return _then(_self.copyWith(incomeForecast: value));
  });
}
}


/// Adds pattern-matching-related methods to [FinancialStateSnapshot].
extension FinancialStateSnapshotPatterns on FinancialStateSnapshot {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FinancialStateSnapshot value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FinancialStateSnapshot() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FinancialStateSnapshot value)  $default,){
final _that = this;
switch (_that) {
case _FinancialStateSnapshot():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FinancialStateSnapshot value)?  $default,){
final _that = this;
switch (_that) {
case _FinancialStateSnapshot() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'schema_version')  int schemaVersion, @JsonKey(name: 'snapshot_id')  String snapshotId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'generated_at')  DateTime generatedAt, @JsonKey(name: 'cash_available')@DecimalConverter()  Decimal cashAvailable, @JsonKey(name: 'emergency_fund')@DecimalConverter()  Decimal emergencyFund, @JsonKey(name: 'income_forecast')  IncomeForecast incomeForecast,  List<Obligation> obligations,  List<Goal> goals,  String weather, @JsonKey(name: 'shortfall_risks')  List<ShortfallRisk> shortfallRisks, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'state_confidence')  double stateConfidence, @JsonKey(name: 'unconfirmed_event_count')  int unconfirmedEventCount, @JsonKey(name: 'contains_simulated_data')  bool containsSimulatedData, @JsonKey(name: 'last_event_id')  String? lastEventId, @JsonKey(name: 'events_applied')  int eventsApplied)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FinancialStateSnapshot() when $default != null:
return $default(_that.schemaVersion,_that.snapshotId,_that.userId,_that.generatedAt,_that.cashAvailable,_that.emergencyFund,_that.incomeForecast,_that.obligations,_that.goals,_that.weather,_that.shortfallRisks,_that.timeToDangerDays,_that.safeToSpend,_that.stateConfidence,_that.unconfirmedEventCount,_that.containsSimulatedData,_that.lastEventId,_that.eventsApplied);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'schema_version')  int schemaVersion, @JsonKey(name: 'snapshot_id')  String snapshotId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'generated_at')  DateTime generatedAt, @JsonKey(name: 'cash_available')@DecimalConverter()  Decimal cashAvailable, @JsonKey(name: 'emergency_fund')@DecimalConverter()  Decimal emergencyFund, @JsonKey(name: 'income_forecast')  IncomeForecast incomeForecast,  List<Obligation> obligations,  List<Goal> goals,  String weather, @JsonKey(name: 'shortfall_risks')  List<ShortfallRisk> shortfallRisks, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'state_confidence')  double stateConfidence, @JsonKey(name: 'unconfirmed_event_count')  int unconfirmedEventCount, @JsonKey(name: 'contains_simulated_data')  bool containsSimulatedData, @JsonKey(name: 'last_event_id')  String? lastEventId, @JsonKey(name: 'events_applied')  int eventsApplied)  $default,) {final _that = this;
switch (_that) {
case _FinancialStateSnapshot():
return $default(_that.schemaVersion,_that.snapshotId,_that.userId,_that.generatedAt,_that.cashAvailable,_that.emergencyFund,_that.incomeForecast,_that.obligations,_that.goals,_that.weather,_that.shortfallRisks,_that.timeToDangerDays,_that.safeToSpend,_that.stateConfidence,_that.unconfirmedEventCount,_that.containsSimulatedData,_that.lastEventId,_that.eventsApplied);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'schema_version')  int schemaVersion, @JsonKey(name: 'snapshot_id')  String snapshotId, @JsonKey(name: 'user_id')  String userId, @JsonKey(name: 'generated_at')  DateTime generatedAt, @JsonKey(name: 'cash_available')@DecimalConverter()  Decimal cashAvailable, @JsonKey(name: 'emergency_fund')@DecimalConverter()  Decimal emergencyFund, @JsonKey(name: 'income_forecast')  IncomeForecast incomeForecast,  List<Obligation> obligations,  List<Goal> goals,  String weather, @JsonKey(name: 'shortfall_risks')  List<ShortfallRisk> shortfallRisks, @JsonKey(name: 'time_to_danger_days')  int? timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter()  Decimal safeToSpend, @JsonKey(name: 'state_confidence')  double stateConfidence, @JsonKey(name: 'unconfirmed_event_count')  int unconfirmedEventCount, @JsonKey(name: 'contains_simulated_data')  bool containsSimulatedData, @JsonKey(name: 'last_event_id')  String? lastEventId, @JsonKey(name: 'events_applied')  int eventsApplied)?  $default,) {final _that = this;
switch (_that) {
case _FinancialStateSnapshot() when $default != null:
return $default(_that.schemaVersion,_that.snapshotId,_that.userId,_that.generatedAt,_that.cashAvailable,_that.emergencyFund,_that.incomeForecast,_that.obligations,_that.goals,_that.weather,_that.shortfallRisks,_that.timeToDangerDays,_that.safeToSpend,_that.stateConfidence,_that.unconfirmedEventCount,_that.containsSimulatedData,_that.lastEventId,_that.eventsApplied);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FinancialStateSnapshot extends FinancialStateSnapshot {
  const _FinancialStateSnapshot({@JsonKey(name: 'schema_version') this.schemaVersion = 1, @JsonKey(name: 'snapshot_id') required this.snapshotId, @JsonKey(name: 'user_id') required this.userId, @JsonKey(name: 'generated_at') required this.generatedAt, @JsonKey(name: 'cash_available')@DecimalConverter() required this.cashAvailable, @JsonKey(name: 'emergency_fund')@DecimalConverter() required this.emergencyFund, @JsonKey(name: 'income_forecast') required this.incomeForecast,  List<Obligation> obligations = const [],  List<Goal> goals = const [], required this.weather, @JsonKey(name: 'shortfall_risks')  List<ShortfallRisk> shortfallRisks = const [], @JsonKey(name: 'time_to_danger_days') this.timeToDangerDays, @JsonKey(name: 'safe_to_spend')@DecimalConverter() required this.safeToSpend, @JsonKey(name: 'state_confidence') required this.stateConfidence, @JsonKey(name: 'unconfirmed_event_count') this.unconfirmedEventCount = 0, @JsonKey(name: 'contains_simulated_data') this.containsSimulatedData = false, @JsonKey(name: 'last_event_id') this.lastEventId, @JsonKey(name: 'events_applied') this.eventsApplied = 0}): _obligations = obligations,_goals = goals,_shortfallRisks = shortfallRisks,super._();
  factory _FinancialStateSnapshot.fromJson(Map<String, dynamic> json) => _$FinancialStateSnapshotFromJson(json);

@override@JsonKey(name: 'schema_version') final  int schemaVersion;
@override@JsonKey(name: 'snapshot_id') final  String snapshotId;
@override@JsonKey(name: 'user_id') final  String userId;
@override@JsonKey(name: 'generated_at') final  DateTime generatedAt;
@override@JsonKey(name: 'cash_available')@DecimalConverter() final  Decimal cashAvailable;
@override@JsonKey(name: 'emergency_fund')@DecimalConverter() final  Decimal emergencyFund;
@override@JsonKey(name: 'income_forecast') final  IncomeForecast incomeForecast;
 final  List<Obligation> _obligations;
@override@JsonKey() List<Obligation> get obligations {
  if (_obligations is EqualUnmodifiableListView) return _obligations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_obligations);
}

 final  List<Goal> _goals;
@override@JsonKey() List<Goal> get goals {
  if (_goals is EqualUnmodifiableListView) return _goals;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_goals);
}

@override final  String weather;
 final  List<ShortfallRisk> _shortfallRisks;
@override@JsonKey(name: 'shortfall_risks') List<ShortfallRisk> get shortfallRisks {
  if (_shortfallRisks is EqualUnmodifiableListView) return _shortfallRisks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortfallRisks);
}

@override@JsonKey(name: 'time_to_danger_days') final  int? timeToDangerDays;
@override@JsonKey(name: 'safe_to_spend')@DecimalConverter() final  Decimal safeToSpend;
@override@JsonKey(name: 'state_confidence') final  double stateConfidence;
@override@JsonKey(name: 'unconfirmed_event_count') final  int unconfirmedEventCount;
@override@JsonKey(name: 'contains_simulated_data') final  bool containsSimulatedData;
@override@JsonKey(name: 'last_event_id') final  String? lastEventId;
@override@JsonKey(name: 'events_applied') final  int eventsApplied;

/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FinancialStateSnapshotCopyWith<_FinancialStateSnapshot> get copyWith => __$FinancialStateSnapshotCopyWithImpl<_FinancialStateSnapshot>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FinancialStateSnapshotToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _FinancialStateSnapshot&&(identical(other.schemaVersion, schemaVersion) || other.schemaVersion == schemaVersion)&&(identical(other.snapshotId, snapshotId) || other.snapshotId == snapshotId)&&(identical(other.userId, userId) || other.userId == userId)&&(identical(other.generatedAt, generatedAt) || other.generatedAt == generatedAt)&&(identical(other.cashAvailable, cashAvailable) || other.cashAvailable == cashAvailable)&&(identical(other.emergencyFund, emergencyFund) || other.emergencyFund == emergencyFund)&&(identical(other.incomeForecast, incomeForecast) || other.incomeForecast == incomeForecast)&&const DeepCollectionEquality().equals(other.obligations, _obligations)&&const DeepCollectionEquality().equals(other.goals, _goals)&&(identical(other.weather, weather) || other.weather == weather)&&const DeepCollectionEquality().equals(other.shortfallRisks, _shortfallRisks)&&(identical(other.timeToDangerDays, timeToDangerDays) || other.timeToDangerDays == timeToDangerDays)&&(identical(other.safeToSpend, safeToSpend) || other.safeToSpend == safeToSpend)&&(identical(other.stateConfidence, stateConfidence) || other.stateConfidence == stateConfidence)&&(identical(other.unconfirmedEventCount, unconfirmedEventCount) || other.unconfirmedEventCount == unconfirmedEventCount)&&(identical(other.containsSimulatedData, containsSimulatedData) || other.containsSimulatedData == containsSimulatedData)&&(identical(other.lastEventId, lastEventId) || other.lastEventId == lastEventId)&&(identical(other.eventsApplied, eventsApplied) || other.eventsApplied == eventsApplied));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,schemaVersion,snapshotId,userId,generatedAt,cashAvailable,emergencyFund,incomeForecast,const DeepCollectionEquality().hash(_obligations),const DeepCollectionEquality().hash(_goals),weather,const DeepCollectionEquality().hash(_shortfallRisks),timeToDangerDays,safeToSpend,stateConfidence,unconfirmedEventCount,containsSimulatedData,lastEventId,eventsApplied);
}

@override
String toString() {
    return 'FinancialStateSnapshot(schemaVersion: $schemaVersion, snapshotId: $snapshotId, userId: $userId, generatedAt: $generatedAt, cashAvailable: $cashAvailable, emergencyFund: $emergencyFund, incomeForecast: $incomeForecast, obligations: $obligations, goals: $goals, weather: $weather, shortfallRisks: $shortfallRisks, timeToDangerDays: $timeToDangerDays, safeToSpend: $safeToSpend, stateConfidence: $stateConfidence, unconfirmedEventCount: $unconfirmedEventCount, containsSimulatedData: $containsSimulatedData, lastEventId: $lastEventId, eventsApplied: $eventsApplied)';
}


}

/// @nodoc
abstract mixin class _$FinancialStateSnapshotCopyWith<$Res> implements $FinancialStateSnapshotCopyWith<$Res> {
  factory _$FinancialStateSnapshotCopyWith(_FinancialStateSnapshot value, $Res Function(_FinancialStateSnapshot) _then) = __$FinancialStateSnapshotCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'schema_version') int schemaVersion,@JsonKey(name: 'snapshot_id') String snapshotId,@JsonKey(name: 'user_id') String userId,@JsonKey(name: 'generated_at') DateTime generatedAt,@JsonKey(name: 'cash_available')@DecimalConverter() Decimal cashAvailable,@JsonKey(name: 'emergency_fund')@DecimalConverter() Decimal emergencyFund,@JsonKey(name: 'income_forecast') IncomeForecast incomeForecast, List<Obligation> obligations, List<Goal> goals, String weather,@JsonKey(name: 'shortfall_risks') List<ShortfallRisk> shortfallRisks,@JsonKey(name: 'time_to_danger_days') int? timeToDangerDays,@JsonKey(name: 'safe_to_spend')@DecimalConverter() Decimal safeToSpend,@JsonKey(name: 'state_confidence') double stateConfidence,@JsonKey(name: 'unconfirmed_event_count') int unconfirmedEventCount,@JsonKey(name: 'contains_simulated_data') bool containsSimulatedData,@JsonKey(name: 'last_event_id') String? lastEventId,@JsonKey(name: 'events_applied') int eventsApplied
});


@override $IncomeForecastCopyWith<$Res> get incomeForecast;

}
/// @nodoc
class __$FinancialStateSnapshotCopyWithImpl<$Res>
    implements _$FinancialStateSnapshotCopyWith<$Res> {
  __$FinancialStateSnapshotCopyWithImpl(this._self, this._then);

  final _FinancialStateSnapshot _self;
  final $Res Function(_FinancialStateSnapshot) _then;

/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? schemaVersion = null,Object? snapshotId = null,Object? userId = null,Object? generatedAt = null,Object? cashAvailable = null,Object? emergencyFund = null,Object? incomeForecast = null,Object? obligations = null,Object? goals = null,Object? weather = null,Object? shortfallRisks = null,Object? timeToDangerDays = freezed,Object? safeToSpend = null,Object? stateConfidence = null,Object? unconfirmedEventCount = null,Object? containsSimulatedData = null,Object? lastEventId = freezed,Object? eventsApplied = null,}) {
  return _then(_FinancialStateSnapshot(
schemaVersion: null == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as int,snapshotId: null == snapshotId ? _self.snapshotId : snapshotId // ignore: cast_nullable_to_non_nullable
as String,userId: null == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String,generatedAt: null == generatedAt ? _self.generatedAt : generatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,cashAvailable: null == cashAvailable ? _self.cashAvailable : cashAvailable // ignore: cast_nullable_to_non_nullable
as Decimal,emergencyFund: null == emergencyFund ? _self.emergencyFund : emergencyFund // ignore: cast_nullable_to_non_nullable
as Decimal,incomeForecast: null == incomeForecast ? _self.incomeForecast : incomeForecast // ignore: cast_nullable_to_non_nullable
as IncomeForecast,obligations: null == obligations ? _self._obligations : obligations // ignore: cast_nullable_to_non_nullable
as List<Obligation>,goals: null == goals ? _self._goals : goals // ignore: cast_nullable_to_non_nullable
as List<Goal>,weather: null == weather ? _self.weather : weather // ignore: cast_nullable_to_non_nullable
as String,shortfallRisks: null == shortfallRisks ? _self._shortfallRisks : shortfallRisks // ignore: cast_nullable_to_non_nullable
as List<ShortfallRisk>,timeToDangerDays: freezed == timeToDangerDays ? _self.timeToDangerDays : timeToDangerDays // ignore: cast_nullable_to_non_nullable
as int?,safeToSpend: null == safeToSpend ? _self.safeToSpend : safeToSpend // ignore: cast_nullable_to_non_nullable
as Decimal,stateConfidence: null == stateConfidence ? _self.stateConfidence : stateConfidence // ignore: cast_nullable_to_non_nullable
as double,unconfirmedEventCount: null == unconfirmedEventCount ? _self.unconfirmedEventCount : unconfirmedEventCount // ignore: cast_nullable_to_non_nullable
as int,containsSimulatedData: null == containsSimulatedData ? _self.containsSimulatedData : containsSimulatedData // ignore: cast_nullable_to_non_nullable
as bool,lastEventId: freezed == lastEventId ? _self.lastEventId : lastEventId // ignore: cast_nullable_to_non_nullable
as String?,eventsApplied: null == eventsApplied ? _self.eventsApplied : eventsApplied // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

/// Create a copy of FinancialStateSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IncomeForecastCopyWith<$Res> get incomeForecast {
  
  return $IncomeForecastCopyWith<$Res>(_self.incomeForecast, (value) {
    return _then(_self.copyWith(incomeForecast: value));
  });
}
}

// dart format on
