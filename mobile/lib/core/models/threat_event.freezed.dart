// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'threat_event.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ThreatEvent {

@JsonKey(name: 'threat_id') String get threatId; String get channel;@JsonKey(name: 'risk_score') double get riskScore;@JsonKey(name: 'primary_category') String get primaryCategory; List<ThreatSignal> get signals;@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? get requestedAmount;@JsonKey(name: 'payee_identifier') String? get payeeIdentifier;@JsonKey(name: 'detected_at') DateTime get detectedAt; ThreatImpact? get impact;
/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ThreatEventCopyWith<ThreatEvent> get copyWith => _$ThreatEventCopyWithImpl<ThreatEvent>(this as ThreatEvent, _$identity);

  /// Serializes this ThreatEvent to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ThreatEvent;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ThreatEvent&&(identical(other.threatId, _this.threatId) || other.threatId == _this.threatId)&&(identical(other.channel, _this.channel) || other.channel == _this.channel)&&(identical(other.riskScore, _this.riskScore) || other.riskScore == _this.riskScore)&&(identical(other.primaryCategory, _this.primaryCategory) || other.primaryCategory == _this.primaryCategory)&&const DeepCollectionEquality().equals(other.signals, _this.signals)&&(identical(other.requestedAmount, _this.requestedAmount) || other.requestedAmount == _this.requestedAmount)&&(identical(other.payeeIdentifier, _this.payeeIdentifier) || other.payeeIdentifier == _this.payeeIdentifier)&&(identical(other.detectedAt, _this.detectedAt) || other.detectedAt == _this.detectedAt)&&(identical(other.impact, _this.impact) || other.impact == _this.impact));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ThreatEvent;
  return Object.hash(runtimeType,_this.threatId,_this.channel,_this.riskScore,_this.primaryCategory,const DeepCollectionEquality().hash(_this.signals),_this.requestedAmount,_this.payeeIdentifier,_this.detectedAt,_this.impact);
}

@override
String toString() {
  final _this = this as ThreatEvent;
  return 'ThreatEvent(threatId: ${_this.threatId}, channel: ${_this.channel}, riskScore: ${_this.riskScore}, primaryCategory: ${_this.primaryCategory}, signals: ${_this.signals}, requestedAmount: ${_this.requestedAmount}, payeeIdentifier: ${_this.payeeIdentifier}, detectedAt: ${_this.detectedAt}, impact: ${_this.impact})';
}


}

/// @nodoc
abstract mixin class $ThreatEventCopyWith<$Res>  {
  factory $ThreatEventCopyWith(ThreatEvent value, $Res Function(ThreatEvent) _then) = _$ThreatEventCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'threat_id') String threatId, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory, List<ThreatSignal> signals,@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? requestedAmount,@JsonKey(name: 'payee_identifier') String? payeeIdentifier,@JsonKey(name: 'detected_at') DateTime detectedAt, ThreatImpact? impact
});


$ThreatImpactCopyWith<$Res>? get impact;

}
/// @nodoc
class _$ThreatEventCopyWithImpl<$Res>
    implements $ThreatEventCopyWith<$Res> {
  _$ThreatEventCopyWithImpl(this._self, this._then);

  final ThreatEvent _self;
  final $Res Function(ThreatEvent) _then;

/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? threatId = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? signals = null,Object? requestedAmount = freezed,Object? payeeIdentifier = freezed,Object? detectedAt = null,Object? impact = freezed,}) {
  return _then(ThreatEvent(
threatId: null == threatId ? _self.threatId : threatId // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,signals: null == signals ? _self.signals : signals // ignore: cast_nullable_to_non_nullable
as List<ThreatSignal>,requestedAmount: freezed == requestedAmount ? _self.requestedAmount : requestedAmount // ignore: cast_nullable_to_non_nullable
as Decimal?,payeeIdentifier: freezed == payeeIdentifier ? _self.payeeIdentifier : payeeIdentifier // ignore: cast_nullable_to_non_nullable
as String?,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,impact: freezed == impact ? _self.impact : impact // ignore: cast_nullable_to_non_nullable
as ThreatImpact?,
  ));
}
/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ThreatImpactCopyWith<$Res>? get impact {
    if (_self.impact == null) {
    return null;
  }

  return $ThreatImpactCopyWith<$Res>(_self.impact!, (value) {
    return _then(_self.copyWith(impact: value));
  });
}
}


/// Adds pattern-matching-related methods to [ThreatEvent].
extension ThreatEventPatterns on ThreatEvent {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ThreatEvent value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ThreatEvent() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ThreatEvent value)  $default,){
final _that = this;
switch (_that) {
case _ThreatEvent():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ThreatEvent value)?  $default,){
final _that = this;
switch (_that) {
case _ThreatEvent() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'threat_id')  String threatId,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'detected_at')  DateTime detectedAt,  ThreatImpact? impact)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ThreatEvent() when $default != null:
return $default(_that.threatId,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.detectedAt,_that.impact);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'threat_id')  String threatId,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'detected_at')  DateTime detectedAt,  ThreatImpact? impact)  $default,) {final _that = this;
switch (_that) {
case _ThreatEvent():
return $default(_that.threatId,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.detectedAt,_that.impact);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'threat_id')  String threatId,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'detected_at')  DateTime detectedAt,  ThreatImpact? impact)?  $default,) {final _that = this;
switch (_that) {
case _ThreatEvent() when $default != null:
return $default(_that.threatId,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.detectedAt,_that.impact);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ThreatEvent implements ThreatEvent {
  const _ThreatEvent({@JsonKey(name: 'threat_id') required this.threatId, required this.channel, @JsonKey(name: 'risk_score') required this.riskScore, @JsonKey(name: 'primary_category') required this.primaryCategory,  List<ThreatSignal> signals = const [], @JsonKey(name: 'requested_amount')@NullableDecimalConverter() this.requestedAmount, @JsonKey(name: 'payee_identifier') this.payeeIdentifier, @JsonKey(name: 'detected_at') required this.detectedAt, this.impact}): _signals = signals;
  factory _ThreatEvent.fromJson(Map<String, dynamic> json) => _$ThreatEventFromJson(json);

@override@JsonKey(name: 'threat_id') final  String threatId;
@override final  String channel;
@override@JsonKey(name: 'risk_score') final  double riskScore;
@override@JsonKey(name: 'primary_category') final  String primaryCategory;
 final  List<ThreatSignal> _signals;
@override@JsonKey() List<ThreatSignal> get signals {
  if (_signals is EqualUnmodifiableListView) return _signals;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_signals);
}

@override@JsonKey(name: 'requested_amount')@NullableDecimalConverter() final  Decimal? requestedAmount;
@override@JsonKey(name: 'payee_identifier') final  String? payeeIdentifier;
@override@JsonKey(name: 'detected_at') final  DateTime detectedAt;
@override final  ThreatImpact? impact;

/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ThreatEventCopyWith<_ThreatEvent> get copyWith => __$ThreatEventCopyWithImpl<_ThreatEvent>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ThreatEventToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ThreatEvent&&(identical(other.threatId, threatId) || other.threatId == threatId)&&(identical(other.channel, channel) || other.channel == channel)&&(identical(other.riskScore, riskScore) || other.riskScore == riskScore)&&(identical(other.primaryCategory, primaryCategory) || other.primaryCategory == primaryCategory)&&const DeepCollectionEquality().equals(other.signals, _signals)&&(identical(other.requestedAmount, requestedAmount) || other.requestedAmount == requestedAmount)&&(identical(other.payeeIdentifier, payeeIdentifier) || other.payeeIdentifier == payeeIdentifier)&&(identical(other.detectedAt, detectedAt) || other.detectedAt == detectedAt)&&(identical(other.impact, impact) || other.impact == impact));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,threatId,channel,riskScore,primaryCategory,const DeepCollectionEquality().hash(_signals),requestedAmount,payeeIdentifier,detectedAt,impact);
}

@override
String toString() {
    return 'ThreatEvent(threatId: $threatId, channel: $channel, riskScore: $riskScore, primaryCategory: $primaryCategory, signals: $signals, requestedAmount: $requestedAmount, payeeIdentifier: $payeeIdentifier, detectedAt: $detectedAt, impact: $impact)';
}


}

/// @nodoc
abstract mixin class _$ThreatEventCopyWith<$Res> implements $ThreatEventCopyWith<$Res> {
  factory _$ThreatEventCopyWith(_ThreatEvent value, $Res Function(_ThreatEvent) _then) = __$ThreatEventCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'threat_id') String threatId, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory, List<ThreatSignal> signals,@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? requestedAmount,@JsonKey(name: 'payee_identifier') String? payeeIdentifier,@JsonKey(name: 'detected_at') DateTime detectedAt, ThreatImpact? impact
});


@override $ThreatImpactCopyWith<$Res>? get impact;

}
/// @nodoc
class __$ThreatEventCopyWithImpl<$Res>
    implements _$ThreatEventCopyWith<$Res> {
  __$ThreatEventCopyWithImpl(this._self, this._then);

  final _ThreatEvent _self;
  final $Res Function(_ThreatEvent) _then;

/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? threatId = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? signals = null,Object? requestedAmount = freezed,Object? payeeIdentifier = freezed,Object? detectedAt = null,Object? impact = freezed,}) {
  return _then(_ThreatEvent(
threatId: null == threatId ? _self.threatId : threatId // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,signals: null == signals ? _self._signals : signals // ignore: cast_nullable_to_non_nullable
as List<ThreatSignal>,requestedAmount: freezed == requestedAmount ? _self.requestedAmount : requestedAmount // ignore: cast_nullable_to_non_nullable
as Decimal?,payeeIdentifier: freezed == payeeIdentifier ? _self.payeeIdentifier : payeeIdentifier // ignore: cast_nullable_to_non_nullable
as String?,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,impact: freezed == impact ? _self.impact : impact // ignore: cast_nullable_to_non_nullable
as ThreatImpact?,
  ));
}

/// Create a copy of ThreatEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ThreatImpactCopyWith<$Res>? get impact {
    if (_self.impact == null) {
    return null;
  }

  return $ThreatImpactCopyWith<$Res>(_self.impact!, (value) {
    return _then(_self.copyWith(impact: value));
  });
}
}


/// @nodoc
mixin _$ThreatEventSummary {

 String get id; String get channel;@JsonKey(name: 'risk_score') double get riskScore;@JsonKey(name: 'primary_category') String get primaryCategory;@JsonKey(name: 'detected_at') DateTime get detectedAt;
/// Create a copy of ThreatEventSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ThreatEventSummaryCopyWith<ThreatEventSummary> get copyWith => _$ThreatEventSummaryCopyWithImpl<ThreatEventSummary>(this as ThreatEventSummary, _$identity);

  /// Serializes this ThreatEventSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ThreatEventSummary;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ThreatEventSummary&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.channel, _this.channel) || other.channel == _this.channel)&&(identical(other.riskScore, _this.riskScore) || other.riskScore == _this.riskScore)&&(identical(other.primaryCategory, _this.primaryCategory) || other.primaryCategory == _this.primaryCategory)&&(identical(other.detectedAt, _this.detectedAt) || other.detectedAt == _this.detectedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ThreatEventSummary;
  return Object.hash(runtimeType,_this.id,_this.channel,_this.riskScore,_this.primaryCategory,_this.detectedAt);
}

@override
String toString() {
  final _this = this as ThreatEventSummary;
  return 'ThreatEventSummary(id: ${_this.id}, channel: ${_this.channel}, riskScore: ${_this.riskScore}, primaryCategory: ${_this.primaryCategory}, detectedAt: ${_this.detectedAt})';
}


}

/// @nodoc
abstract mixin class $ThreatEventSummaryCopyWith<$Res>  {
  factory $ThreatEventSummaryCopyWith(ThreatEventSummary value, $Res Function(ThreatEventSummary) _then) = _$ThreatEventSummaryCopyWithImpl;
@useResult
$Res call({
 String id, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory,@JsonKey(name: 'detected_at') DateTime detectedAt
});




}
/// @nodoc
class _$ThreatEventSummaryCopyWithImpl<$Res>
    implements $ThreatEventSummaryCopyWith<$Res> {
  _$ThreatEventSummaryCopyWithImpl(this._self, this._then);

  final ThreatEventSummary _self;
  final $Res Function(ThreatEventSummary) _then;

/// Create a copy of ThreatEventSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? detectedAt = null,}) {
  return _then(ThreatEventSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [ThreatEventSummary].
extension ThreatEventSummaryPatterns on ThreatEventSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ThreatEventSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ThreatEventSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ThreatEventSummary value)  $default,){
final _that = this;
switch (_that) {
case _ThreatEventSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ThreatEventSummary value)?  $default,){
final _that = this;
switch (_that) {
case _ThreatEventSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory, @JsonKey(name: 'detected_at')  DateTime detectedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ThreatEventSummary() when $default != null:
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.detectedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory, @JsonKey(name: 'detected_at')  DateTime detectedAt)  $default,) {final _that = this;
switch (_that) {
case _ThreatEventSummary():
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.detectedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory, @JsonKey(name: 'detected_at')  DateTime detectedAt)?  $default,) {final _that = this;
switch (_that) {
case _ThreatEventSummary() when $default != null:
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.detectedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ThreatEventSummary implements ThreatEventSummary {
  const _ThreatEventSummary({required this.id, required this.channel, @JsonKey(name: 'risk_score') required this.riskScore, @JsonKey(name: 'primary_category') required this.primaryCategory, @JsonKey(name: 'detected_at') required this.detectedAt});
  factory _ThreatEventSummary.fromJson(Map<String, dynamic> json) => _$ThreatEventSummaryFromJson(json);

@override final  String id;
@override final  String channel;
@override@JsonKey(name: 'risk_score') final  double riskScore;
@override@JsonKey(name: 'primary_category') final  String primaryCategory;
@override@JsonKey(name: 'detected_at') final  DateTime detectedAt;

/// Create a copy of ThreatEventSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ThreatEventSummaryCopyWith<_ThreatEventSummary> get copyWith => __$ThreatEventSummaryCopyWithImpl<_ThreatEventSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ThreatEventSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ThreatEventSummary&&(identical(other.id, id) || other.id == id)&&(identical(other.channel, channel) || other.channel == channel)&&(identical(other.riskScore, riskScore) || other.riskScore == riskScore)&&(identical(other.primaryCategory, primaryCategory) || other.primaryCategory == primaryCategory)&&(identical(other.detectedAt, detectedAt) || other.detectedAt == detectedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,channel,riskScore,primaryCategory,detectedAt);
}

@override
String toString() {
    return 'ThreatEventSummary(id: $id, channel: $channel, riskScore: $riskScore, primaryCategory: $primaryCategory, detectedAt: $detectedAt)';
}


}

/// @nodoc
abstract mixin class _$ThreatEventSummaryCopyWith<$Res> implements $ThreatEventSummaryCopyWith<$Res> {
  factory _$ThreatEventSummaryCopyWith(_ThreatEventSummary value, $Res Function(_ThreatEventSummary) _then) = __$ThreatEventSummaryCopyWithImpl;
@override @useResult
$Res call({
 String id, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory,@JsonKey(name: 'detected_at') DateTime detectedAt
});




}
/// @nodoc
class __$ThreatEventSummaryCopyWithImpl<$Res>
    implements _$ThreatEventSummaryCopyWith<$Res> {
  __$ThreatEventSummaryCopyWithImpl(this._self, this._then);

  final _ThreatEventSummary _self;
  final $Res Function(_ThreatEventSummary) _then;

/// Create a copy of ThreatEventSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? detectedAt = null,}) {
  return _then(_ThreatEventSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$ThreatEventDetail {

 String get id; String get channel;@JsonKey(name: 'risk_score') double get riskScore;@JsonKey(name: 'primary_category') String get primaryCategory; List<ThreatSignal> get signals;@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? get requestedAmount;@JsonKey(name: 'payee_identifier') String? get payeeIdentifier;@JsonKey(name: 'raw_reference') String? get rawReference;@JsonKey(name: 'transcript_excerpt') String? get transcriptExcerpt;@JsonKey(name: 'data_source') String get dataSource;@JsonKey(name: 'detection_confidence') double get detectionConfidence;@JsonKey(name: 'financial_impact') ThreatImpact? get financialImpact;@JsonKey(name: 'detected_at') DateTime get detectedAt;
/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ThreatEventDetailCopyWith<ThreatEventDetail> get copyWith => _$ThreatEventDetailCopyWithImpl<ThreatEventDetail>(this as ThreatEventDetail, _$identity);

  /// Serializes this ThreatEventDetail to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as ThreatEventDetail;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ThreatEventDetail&&(identical(other.id, _this.id) || other.id == _this.id)&&(identical(other.channel, _this.channel) || other.channel == _this.channel)&&(identical(other.riskScore, _this.riskScore) || other.riskScore == _this.riskScore)&&(identical(other.primaryCategory, _this.primaryCategory) || other.primaryCategory == _this.primaryCategory)&&const DeepCollectionEquality().equals(other.signals, _this.signals)&&(identical(other.requestedAmount, _this.requestedAmount) || other.requestedAmount == _this.requestedAmount)&&(identical(other.payeeIdentifier, _this.payeeIdentifier) || other.payeeIdentifier == _this.payeeIdentifier)&&(identical(other.rawReference, _this.rawReference) || other.rawReference == _this.rawReference)&&(identical(other.transcriptExcerpt, _this.transcriptExcerpt) || other.transcriptExcerpt == _this.transcriptExcerpt)&&(identical(other.dataSource, _this.dataSource) || other.dataSource == _this.dataSource)&&(identical(other.detectionConfidence, _this.detectionConfidence) || other.detectionConfidence == _this.detectionConfidence)&&(identical(other.financialImpact, _this.financialImpact) || other.financialImpact == _this.financialImpact)&&(identical(other.detectedAt, _this.detectedAt) || other.detectedAt == _this.detectedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as ThreatEventDetail;
  return Object.hash(runtimeType,_this.id,_this.channel,_this.riskScore,_this.primaryCategory,const DeepCollectionEquality().hash(_this.signals),_this.requestedAmount,_this.payeeIdentifier,_this.rawReference,_this.transcriptExcerpt,_this.dataSource,_this.detectionConfidence,_this.financialImpact,_this.detectedAt);
}

@override
String toString() {
  final _this = this as ThreatEventDetail;
  return 'ThreatEventDetail(id: ${_this.id}, channel: ${_this.channel}, riskScore: ${_this.riskScore}, primaryCategory: ${_this.primaryCategory}, signals: ${_this.signals}, requestedAmount: ${_this.requestedAmount}, payeeIdentifier: ${_this.payeeIdentifier}, rawReference: ${_this.rawReference}, transcriptExcerpt: ${_this.transcriptExcerpt}, dataSource: ${_this.dataSource}, detectionConfidence: ${_this.detectionConfidence}, financialImpact: ${_this.financialImpact}, detectedAt: ${_this.detectedAt})';
}


}

/// @nodoc
abstract mixin class $ThreatEventDetailCopyWith<$Res>  {
  factory $ThreatEventDetailCopyWith(ThreatEventDetail value, $Res Function(ThreatEventDetail) _then) = _$ThreatEventDetailCopyWithImpl;
@useResult
$Res call({
 String id, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory, List<ThreatSignal> signals,@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? requestedAmount,@JsonKey(name: 'payee_identifier') String? payeeIdentifier,@JsonKey(name: 'raw_reference') String? rawReference,@JsonKey(name: 'transcript_excerpt') String? transcriptExcerpt,@JsonKey(name: 'data_source') String dataSource,@JsonKey(name: 'detection_confidence') double detectionConfidence,@JsonKey(name: 'financial_impact') ThreatImpact? financialImpact,@JsonKey(name: 'detected_at') DateTime detectedAt
});


$ThreatImpactCopyWith<$Res>? get financialImpact;

}
/// @nodoc
class _$ThreatEventDetailCopyWithImpl<$Res>
    implements $ThreatEventDetailCopyWith<$Res> {
  _$ThreatEventDetailCopyWithImpl(this._self, this._then);

  final ThreatEventDetail _self;
  final $Res Function(ThreatEventDetail) _then;

/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? signals = null,Object? requestedAmount = freezed,Object? payeeIdentifier = freezed,Object? rawReference = freezed,Object? transcriptExcerpt = freezed,Object? dataSource = null,Object? detectionConfidence = null,Object? financialImpact = freezed,Object? detectedAt = null,}) {
  return _then(ThreatEventDetail(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,signals: null == signals ? _self.signals : signals // ignore: cast_nullable_to_non_nullable
as List<ThreatSignal>,requestedAmount: freezed == requestedAmount ? _self.requestedAmount : requestedAmount // ignore: cast_nullable_to_non_nullable
as Decimal?,payeeIdentifier: freezed == payeeIdentifier ? _self.payeeIdentifier : payeeIdentifier // ignore: cast_nullable_to_non_nullable
as String?,rawReference: freezed == rawReference ? _self.rawReference : rawReference // ignore: cast_nullable_to_non_nullable
as String?,transcriptExcerpt: freezed == transcriptExcerpt ? _self.transcriptExcerpt : transcriptExcerpt // ignore: cast_nullable_to_non_nullable
as String?,dataSource: null == dataSource ? _self.dataSource : dataSource // ignore: cast_nullable_to_non_nullable
as String,detectionConfidence: null == detectionConfidence ? _self.detectionConfidence : detectionConfidence // ignore: cast_nullable_to_non_nullable
as double,financialImpact: freezed == financialImpact ? _self.financialImpact : financialImpact // ignore: cast_nullable_to_non_nullable
as ThreatImpact?,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}
/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ThreatImpactCopyWith<$Res>? get financialImpact {
    if (_self.financialImpact == null) {
    return null;
  }

  return $ThreatImpactCopyWith<$Res>(_self.financialImpact!, (value) {
    return _then(_self.copyWith(financialImpact: value));
  });
}
}


/// Adds pattern-matching-related methods to [ThreatEventDetail].
extension ThreatEventDetailPatterns on ThreatEventDetail {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ThreatEventDetail value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ThreatEventDetail() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ThreatEventDetail value)  $default,){
final _that = this;
switch (_that) {
case _ThreatEventDetail():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ThreatEventDetail value)?  $default,){
final _that = this;
switch (_that) {
case _ThreatEventDetail() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'raw_reference')  String? rawReference, @JsonKey(name: 'transcript_excerpt')  String? transcriptExcerpt, @JsonKey(name: 'data_source')  String dataSource, @JsonKey(name: 'detection_confidence')  double detectionConfidence, @JsonKey(name: 'financial_impact')  ThreatImpact? financialImpact, @JsonKey(name: 'detected_at')  DateTime detectedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ThreatEventDetail() when $default != null:
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.rawReference,_that.transcriptExcerpt,_that.dataSource,_that.detectionConfidence,_that.financialImpact,_that.detectedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'raw_reference')  String? rawReference, @JsonKey(name: 'transcript_excerpt')  String? transcriptExcerpt, @JsonKey(name: 'data_source')  String dataSource, @JsonKey(name: 'detection_confidence')  double detectionConfidence, @JsonKey(name: 'financial_impact')  ThreatImpact? financialImpact, @JsonKey(name: 'detected_at')  DateTime detectedAt)  $default,) {final _that = this;
switch (_that) {
case _ThreatEventDetail():
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.rawReference,_that.transcriptExcerpt,_that.dataSource,_that.detectionConfidence,_that.financialImpact,_that.detectedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String channel, @JsonKey(name: 'risk_score')  double riskScore, @JsonKey(name: 'primary_category')  String primaryCategory,  List<ThreatSignal> signals, @JsonKey(name: 'requested_amount')@NullableDecimalConverter()  Decimal? requestedAmount, @JsonKey(name: 'payee_identifier')  String? payeeIdentifier, @JsonKey(name: 'raw_reference')  String? rawReference, @JsonKey(name: 'transcript_excerpt')  String? transcriptExcerpt, @JsonKey(name: 'data_source')  String dataSource, @JsonKey(name: 'detection_confidence')  double detectionConfidence, @JsonKey(name: 'financial_impact')  ThreatImpact? financialImpact, @JsonKey(name: 'detected_at')  DateTime detectedAt)?  $default,) {final _that = this;
switch (_that) {
case _ThreatEventDetail() when $default != null:
return $default(_that.id,_that.channel,_that.riskScore,_that.primaryCategory,_that.signals,_that.requestedAmount,_that.payeeIdentifier,_that.rawReference,_that.transcriptExcerpt,_that.dataSource,_that.detectionConfidence,_that.financialImpact,_that.detectedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ThreatEventDetail implements ThreatEventDetail {
  const _ThreatEventDetail({required this.id, required this.channel, @JsonKey(name: 'risk_score') required this.riskScore, @JsonKey(name: 'primary_category') required this.primaryCategory,  List<ThreatSignal> signals = const [], @JsonKey(name: 'requested_amount')@NullableDecimalConverter() this.requestedAmount, @JsonKey(name: 'payee_identifier') this.payeeIdentifier, @JsonKey(name: 'raw_reference') this.rawReference, @JsonKey(name: 'transcript_excerpt') this.transcriptExcerpt, @JsonKey(name: 'data_source') required this.dataSource, @JsonKey(name: 'detection_confidence') required this.detectionConfidence, @JsonKey(name: 'financial_impact') this.financialImpact, @JsonKey(name: 'detected_at') required this.detectedAt}): _signals = signals;
  factory _ThreatEventDetail.fromJson(Map<String, dynamic> json) => _$ThreatEventDetailFromJson(json);

@override final  String id;
@override final  String channel;
@override@JsonKey(name: 'risk_score') final  double riskScore;
@override@JsonKey(name: 'primary_category') final  String primaryCategory;
 final  List<ThreatSignal> _signals;
@override@JsonKey() List<ThreatSignal> get signals {
  if (_signals is EqualUnmodifiableListView) return _signals;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_signals);
}

@override@JsonKey(name: 'requested_amount')@NullableDecimalConverter() final  Decimal? requestedAmount;
@override@JsonKey(name: 'payee_identifier') final  String? payeeIdentifier;
@override@JsonKey(name: 'raw_reference') final  String? rawReference;
@override@JsonKey(name: 'transcript_excerpt') final  String? transcriptExcerpt;
@override@JsonKey(name: 'data_source') final  String dataSource;
@override@JsonKey(name: 'detection_confidence') final  double detectionConfidence;
@override@JsonKey(name: 'financial_impact') final  ThreatImpact? financialImpact;
@override@JsonKey(name: 'detected_at') final  DateTime detectedAt;

/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ThreatEventDetailCopyWith<_ThreatEventDetail> get copyWith => __$ThreatEventDetailCopyWithImpl<_ThreatEventDetail>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ThreatEventDetailToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _ThreatEventDetail&&(identical(other.id, id) || other.id == id)&&(identical(other.channel, channel) || other.channel == channel)&&(identical(other.riskScore, riskScore) || other.riskScore == riskScore)&&(identical(other.primaryCategory, primaryCategory) || other.primaryCategory == primaryCategory)&&const DeepCollectionEquality().equals(other.signals, _signals)&&(identical(other.requestedAmount, requestedAmount) || other.requestedAmount == requestedAmount)&&(identical(other.payeeIdentifier, payeeIdentifier) || other.payeeIdentifier == payeeIdentifier)&&(identical(other.rawReference, rawReference) || other.rawReference == rawReference)&&(identical(other.transcriptExcerpt, transcriptExcerpt) || other.transcriptExcerpt == transcriptExcerpt)&&(identical(other.dataSource, dataSource) || other.dataSource == dataSource)&&(identical(other.detectionConfidence, detectionConfidence) || other.detectionConfidence == detectionConfidence)&&(identical(other.financialImpact, financialImpact) || other.financialImpact == financialImpact)&&(identical(other.detectedAt, detectedAt) || other.detectedAt == detectedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,id,channel,riskScore,primaryCategory,const DeepCollectionEquality().hash(_signals),requestedAmount,payeeIdentifier,rawReference,transcriptExcerpt,dataSource,detectionConfidence,financialImpact,detectedAt);
}

@override
String toString() {
    return 'ThreatEventDetail(id: $id, channel: $channel, riskScore: $riskScore, primaryCategory: $primaryCategory, signals: $signals, requestedAmount: $requestedAmount, payeeIdentifier: $payeeIdentifier, rawReference: $rawReference, transcriptExcerpt: $transcriptExcerpt, dataSource: $dataSource, detectionConfidence: $detectionConfidence, financialImpact: $financialImpact, detectedAt: $detectedAt)';
}


}

/// @nodoc
abstract mixin class _$ThreatEventDetailCopyWith<$Res> implements $ThreatEventDetailCopyWith<$Res> {
  factory _$ThreatEventDetailCopyWith(_ThreatEventDetail value, $Res Function(_ThreatEventDetail) _then) = __$ThreatEventDetailCopyWithImpl;
@override @useResult
$Res call({
 String id, String channel,@JsonKey(name: 'risk_score') double riskScore,@JsonKey(name: 'primary_category') String primaryCategory, List<ThreatSignal> signals,@JsonKey(name: 'requested_amount')@NullableDecimalConverter() Decimal? requestedAmount,@JsonKey(name: 'payee_identifier') String? payeeIdentifier,@JsonKey(name: 'raw_reference') String? rawReference,@JsonKey(name: 'transcript_excerpt') String? transcriptExcerpt,@JsonKey(name: 'data_source') String dataSource,@JsonKey(name: 'detection_confidence') double detectionConfidence,@JsonKey(name: 'financial_impact') ThreatImpact? financialImpact,@JsonKey(name: 'detected_at') DateTime detectedAt
});


@override $ThreatImpactCopyWith<$Res>? get financialImpact;

}
/// @nodoc
class __$ThreatEventDetailCopyWithImpl<$Res>
    implements _$ThreatEventDetailCopyWith<$Res> {
  __$ThreatEventDetailCopyWithImpl(this._self, this._then);

  final _ThreatEventDetail _self;
  final $Res Function(_ThreatEventDetail) _then;

/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? channel = null,Object? riskScore = null,Object? primaryCategory = null,Object? signals = null,Object? requestedAmount = freezed,Object? payeeIdentifier = freezed,Object? rawReference = freezed,Object? transcriptExcerpt = freezed,Object? dataSource = null,Object? detectionConfidence = null,Object? financialImpact = freezed,Object? detectedAt = null,}) {
  return _then(_ThreatEventDetail(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,channel: null == channel ? _self.channel : channel // ignore: cast_nullable_to_non_nullable
as String,riskScore: null == riskScore ? _self.riskScore : riskScore // ignore: cast_nullable_to_non_nullable
as double,primaryCategory: null == primaryCategory ? _self.primaryCategory : primaryCategory // ignore: cast_nullable_to_non_nullable
as String,signals: null == signals ? _self._signals : signals // ignore: cast_nullable_to_non_nullable
as List<ThreatSignal>,requestedAmount: freezed == requestedAmount ? _self.requestedAmount : requestedAmount // ignore: cast_nullable_to_non_nullable
as Decimal?,payeeIdentifier: freezed == payeeIdentifier ? _self.payeeIdentifier : payeeIdentifier // ignore: cast_nullable_to_non_nullable
as String?,rawReference: freezed == rawReference ? _self.rawReference : rawReference // ignore: cast_nullable_to_non_nullable
as String?,transcriptExcerpt: freezed == transcriptExcerpt ? _self.transcriptExcerpt : transcriptExcerpt // ignore: cast_nullable_to_non_nullable
as String?,dataSource: null == dataSource ? _self.dataSource : dataSource // ignore: cast_nullable_to_non_nullable
as String,detectionConfidence: null == detectionConfidence ? _self.detectionConfidence : detectionConfidence // ignore: cast_nullable_to_non_nullable
as double,financialImpact: freezed == financialImpact ? _self.financialImpact : financialImpact // ignore: cast_nullable_to_non_nullable
as ThreatImpact?,detectedAt: null == detectedAt ? _self.detectedAt : detectedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

/// Create a copy of ThreatEventDetail
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ThreatImpactCopyWith<$Res>? get financialImpact {
    if (_self.financialImpact == null) {
    return null;
  }

  return $ThreatImpactCopyWith<$Res>(_self.financialImpact!, (value) {
    return _then(_self.copyWith(financialImpact: value));
  });
}
}

// dart format on
