// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ingestion_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$IngestionResult {

@JsonKey(name: 'event_id') String? get eventId; String get method; double get confidence;@JsonKey(name: 'was_duplicate') bool get wasDuplicate; bool get quarantined; String? get reason;
/// Create a copy of IngestionResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngestionResultCopyWith<IngestionResult> get copyWith => _$IngestionResultCopyWithImpl<IngestionResult>(this as IngestionResult, _$identity);

  /// Serializes this IngestionResult to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as IngestionResult;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngestionResult&&(identical(other.eventId, _this.eventId) || other.eventId == _this.eventId)&&(identical(other.method, _this.method) || other.method == _this.method)&&(identical(other.confidence, _this.confidence) || other.confidence == _this.confidence)&&(identical(other.wasDuplicate, _this.wasDuplicate) || other.wasDuplicate == _this.wasDuplicate)&&(identical(other.quarantined, _this.quarantined) || other.quarantined == _this.quarantined)&&(identical(other.reason, _this.reason) || other.reason == _this.reason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as IngestionResult;
  return Object.hash(runtimeType,_this.eventId,_this.method,_this.confidence,_this.wasDuplicate,_this.quarantined,_this.reason);
}

@override
String toString() {
  final _this = this as IngestionResult;
  return 'IngestionResult(eventId: ${_this.eventId}, method: ${_this.method}, confidence: ${_this.confidence}, wasDuplicate: ${_this.wasDuplicate}, quarantined: ${_this.quarantined}, reason: ${_this.reason})';
}


}

/// @nodoc
abstract mixin class $IngestionResultCopyWith<$Res>  {
  factory $IngestionResultCopyWith(IngestionResult value, $Res Function(IngestionResult) _then) = _$IngestionResultCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'event_id') String? eventId, String method, double confidence,@JsonKey(name: 'was_duplicate') bool wasDuplicate, bool quarantined, String? reason
});




}
/// @nodoc
class _$IngestionResultCopyWithImpl<$Res>
    implements $IngestionResultCopyWith<$Res> {
  _$IngestionResultCopyWithImpl(this._self, this._then);

  final IngestionResult _self;
  final $Res Function(IngestionResult) _then;

/// Create a copy of IngestionResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? eventId = freezed,Object? method = null,Object? confidence = null,Object? wasDuplicate = null,Object? quarantined = null,Object? reason = freezed,}) {
  return _then(IngestionResult(
eventId: freezed == eventId ? _self.eventId : eventId // ignore: cast_nullable_to_non_nullable
as String?,method: null == method ? _self.method : method // ignore: cast_nullable_to_non_nullable
as String,confidence: null == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double,wasDuplicate: null == wasDuplicate ? _self.wasDuplicate : wasDuplicate // ignore: cast_nullable_to_non_nullable
as bool,quarantined: null == quarantined ? _self.quarantined : quarantined // ignore: cast_nullable_to_non_nullable
as bool,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [IngestionResult].
extension IngestionResultPatterns on IngestionResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngestionResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngestionResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngestionResult value)  $default,){
final _that = this;
switch (_that) {
case _IngestionResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngestionResult value)?  $default,){
final _that = this;
switch (_that) {
case _IngestionResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'event_id')  String? eventId,  String method,  double confidence, @JsonKey(name: 'was_duplicate')  bool wasDuplicate,  bool quarantined,  String? reason)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngestionResult() when $default != null:
return $default(_that.eventId,_that.method,_that.confidence,_that.wasDuplicate,_that.quarantined,_that.reason);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'event_id')  String? eventId,  String method,  double confidence, @JsonKey(name: 'was_duplicate')  bool wasDuplicate,  bool quarantined,  String? reason)  $default,) {final _that = this;
switch (_that) {
case _IngestionResult():
return $default(_that.eventId,_that.method,_that.confidence,_that.wasDuplicate,_that.quarantined,_that.reason);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'event_id')  String? eventId,  String method,  double confidence, @JsonKey(name: 'was_duplicate')  bool wasDuplicate,  bool quarantined,  String? reason)?  $default,) {final _that = this;
switch (_that) {
case _IngestionResult() when $default != null:
return $default(_that.eventId,_that.method,_that.confidence,_that.wasDuplicate,_that.quarantined,_that.reason);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngestionResult implements IngestionResult {
  const _IngestionResult({@JsonKey(name: 'event_id') this.eventId, required this.method, required this.confidence, @JsonKey(name: 'was_duplicate') required this.wasDuplicate, required this.quarantined, this.reason});
  factory _IngestionResult.fromJson(Map<String, dynamic> json) => _$IngestionResultFromJson(json);

@override@JsonKey(name: 'event_id') final  String? eventId;
@override final  String method;
@override final  double confidence;
@override@JsonKey(name: 'was_duplicate') final  bool wasDuplicate;
@override final  bool quarantined;
@override final  String? reason;

/// Create a copy of IngestionResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngestionResultCopyWith<_IngestionResult> get copyWith => __$IngestionResultCopyWithImpl<_IngestionResult>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngestionResultToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngestionResult&&(identical(other.eventId, eventId) || other.eventId == eventId)&&(identical(other.method, method) || other.method == method)&&(identical(other.confidence, confidence) || other.confidence == confidence)&&(identical(other.wasDuplicate, wasDuplicate) || other.wasDuplicate == wasDuplicate)&&(identical(other.quarantined, quarantined) || other.quarantined == quarantined)&&(identical(other.reason, reason) || other.reason == reason));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,eventId,method,confidence,wasDuplicate,quarantined,reason);
}

@override
String toString() {
    return 'IngestionResult(eventId: $eventId, method: $method, confidence: $confidence, wasDuplicate: $wasDuplicate, quarantined: $quarantined, reason: $reason)';
}


}

/// @nodoc
abstract mixin class _$IngestionResultCopyWith<$Res> implements $IngestionResultCopyWith<$Res> {
  factory _$IngestionResultCopyWith(_IngestionResult value, $Res Function(_IngestionResult) _then) = __$IngestionResultCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'event_id') String? eventId, String method, double confidence,@JsonKey(name: 'was_duplicate') bool wasDuplicate, bool quarantined, String? reason
});




}
/// @nodoc
class __$IngestionResultCopyWithImpl<$Res>
    implements _$IngestionResultCopyWith<$Res> {
  __$IngestionResultCopyWithImpl(this._self, this._then);

  final _IngestionResult _self;
  final $Res Function(_IngestionResult) _then;

/// Create a copy of IngestionResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? eventId = freezed,Object? method = null,Object? confidence = null,Object? wasDuplicate = null,Object? quarantined = null,Object? reason = freezed,}) {
  return _then(_IngestionResult(
eventId: freezed == eventId ? _self.eventId : eventId // ignore: cast_nullable_to_non_nullable
as String?,method: null == method ? _self.method : method // ignore: cast_nullable_to_non_nullable
as String,confidence: null == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double,wasDuplicate: null == wasDuplicate ? _self.wasDuplicate : wasDuplicate // ignore: cast_nullable_to_non_nullable
as bool,quarantined: null == quarantined ? _self.quarantined : quarantined // ignore: cast_nullable_to_non_nullable
as bool,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
