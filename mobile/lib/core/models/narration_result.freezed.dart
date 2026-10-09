// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'narration_result.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$NarrationResult {

 String get text; String get source;@JsonKey(name: 'validation_passed') bool get validationPassed; List<String> get violations; bool get cached;@JsonKey(name: 'duration_ms') int get durationMs;
/// Create a copy of NarrationResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NarrationResultCopyWith<NarrationResult> get copyWith => _$NarrationResultCopyWithImpl<NarrationResult>(this as NarrationResult, _$identity);

  /// Serializes this NarrationResult to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  final _this = this as NarrationResult;
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NarrationResult&&(identical(other.text, _this.text) || other.text == _this.text)&&(identical(other.source, _this.source) || other.source == _this.source)&&(identical(other.validationPassed, _this.validationPassed) || other.validationPassed == _this.validationPassed)&&const DeepCollectionEquality().equals(other.violations, _this.violations)&&(identical(other.cached, _this.cached) || other.cached == _this.cached)&&(identical(other.durationMs, _this.durationMs) || other.durationMs == _this.durationMs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
  final _this = this as NarrationResult;
  return Object.hash(runtimeType,_this.text,_this.source,_this.validationPassed,const DeepCollectionEquality().hash(_this.violations),_this.cached,_this.durationMs);
}

@override
String toString() {
  final _this = this as NarrationResult;
  return 'NarrationResult(text: ${_this.text}, source: ${_this.source}, validationPassed: ${_this.validationPassed}, violations: ${_this.violations}, cached: ${_this.cached}, durationMs: ${_this.durationMs})';
}


}

/// @nodoc
abstract mixin class $NarrationResultCopyWith<$Res>  {
  factory $NarrationResultCopyWith(NarrationResult value, $Res Function(NarrationResult) _then) = _$NarrationResultCopyWithImpl;
@useResult
$Res call({
 String text, String source,@JsonKey(name: 'validation_passed') bool validationPassed, List<String> violations, bool cached,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class _$NarrationResultCopyWithImpl<$Res>
    implements $NarrationResultCopyWith<$Res> {
  _$NarrationResultCopyWithImpl(this._self, this._then);

  final NarrationResult _self;
  final $Res Function(NarrationResult) _then;

/// Create a copy of NarrationResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? text = null,Object? source = null,Object? validationPassed = null,Object? violations = null,Object? cached = null,Object? durationMs = null,}) {
  return _then(NarrationResult(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,validationPassed: null == validationPassed ? _self.validationPassed : validationPassed // ignore: cast_nullable_to_non_nullable
as bool,violations: null == violations ? _self.violations : violations // ignore: cast_nullable_to_non_nullable
as List<String>,cached: null == cached ? _self.cached : cached // ignore: cast_nullable_to_non_nullable
as bool,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [NarrationResult].
extension NarrationResultPatterns on NarrationResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _NarrationResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _NarrationResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _NarrationResult value)  $default,){
final _that = this;
switch (_that) {
case _NarrationResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _NarrationResult value)?  $default,){
final _that = this;
switch (_that) {
case _NarrationResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String text,  String source, @JsonKey(name: 'validation_passed')  bool validationPassed,  List<String> violations,  bool cached, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _NarrationResult() when $default != null:
return $default(_that.text,_that.source,_that.validationPassed,_that.violations,_that.cached,_that.durationMs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String text,  String source, @JsonKey(name: 'validation_passed')  bool validationPassed,  List<String> violations,  bool cached, @JsonKey(name: 'duration_ms')  int durationMs)  $default,) {final _that = this;
switch (_that) {
case _NarrationResult():
return $default(_that.text,_that.source,_that.validationPassed,_that.violations,_that.cached,_that.durationMs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String text,  String source, @JsonKey(name: 'validation_passed')  bool validationPassed,  List<String> violations,  bool cached, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,) {final _that = this;
switch (_that) {
case _NarrationResult() when $default != null:
return $default(_that.text,_that.source,_that.validationPassed,_that.violations,_that.cached,_that.durationMs);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _NarrationResult implements NarrationResult {
  const _NarrationResult({required this.text, required this.source, @JsonKey(name: 'validation_passed') required this.validationPassed,  List<String> violations = const [], required this.cached, @JsonKey(name: 'duration_ms') required this.durationMs}): _violations = violations;
  factory _NarrationResult.fromJson(Map<String, dynamic> json) => _$NarrationResultFromJson(json);

@override final  String text;
@override final  String source;
@override@JsonKey(name: 'validation_passed') final  bool validationPassed;
 final  List<String> _violations;
@override@JsonKey() List<String> get violations {
  if (_violations is EqualUnmodifiableListView) return _violations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_violations);
}

@override final  bool cached;
@override@JsonKey(name: 'duration_ms') final  int durationMs;

/// Create a copy of NarrationResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$NarrationResultCopyWith<_NarrationResult> get copyWith => __$NarrationResultCopyWithImpl<_NarrationResult>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NarrationResultToJson(this, );
}

@override
bool operator ==(Object other) {
    return identical(this, other) || (other.runtimeType == runtimeType&&other is _NarrationResult&&(identical(other.text, text) || other.text == text)&&(identical(other.source, source) || other.source == source)&&(identical(other.validationPassed, validationPassed) || other.validationPassed == validationPassed)&&const DeepCollectionEquality().equals(other.violations, _violations)&&(identical(other.cached, cached) || other.cached == cached)&&(identical(other.durationMs, durationMs) || other.durationMs == durationMs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode {
    return Object.hash(runtimeType,text,source,validationPassed,const DeepCollectionEquality().hash(_violations),cached,durationMs);
}

@override
String toString() {
    return 'NarrationResult(text: $text, source: $source, validationPassed: $validationPassed, violations: $violations, cached: $cached, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class _$NarrationResultCopyWith<$Res> implements $NarrationResultCopyWith<$Res> {
  factory _$NarrationResultCopyWith(_NarrationResult value, $Res Function(_NarrationResult) _then) = __$NarrationResultCopyWithImpl;
@override @useResult
$Res call({
 String text, String source,@JsonKey(name: 'validation_passed') bool validationPassed, List<String> violations, bool cached,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class __$NarrationResultCopyWithImpl<$Res>
    implements _$NarrationResultCopyWith<$Res> {
  __$NarrationResultCopyWithImpl(this._self, this._then);

  final _NarrationResult _self;
  final $Res Function(_NarrationResult) _then;

/// Create a copy of NarrationResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? text = null,Object? source = null,Object? validationPassed = null,Object? violations = null,Object? cached = null,Object? durationMs = null,}) {
  return _then(_NarrationResult(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,validationPassed: null == validationPassed ? _self.validationPassed : validationPassed // ignore: cast_nullable_to_non_nullable
as bool,violations: null == violations ? _self._violations : violations // ignore: cast_nullable_to_non_nullable
as List<String>,cached: null == cached ? _self.cached : cached // ignore: cast_nullable_to_non_nullable
as bool,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
