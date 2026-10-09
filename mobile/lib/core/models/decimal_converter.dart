import 'package:decimal/decimal.dart';
import 'package:json_annotation/json_annotation.dart';

/// Converts between the backend's Decimal-as-JSON-string wire format and
/// Dart's [Decimal] type.
///
/// Confirmed against the actual backend: Pydantic v2 serializes every
/// `Decimal` field as a JSON STRING (e.g. `"18000.55"`), never a JSON
/// number — because a JSON number is parsed by most runtimes (including
/// Dart's `double`) as an IEEE-754 binary float, which cannot represent
/// every decimal fraction exactly (0.1 + 0.2 != 0.3 in binary floating
/// point). The backend was built end-to-end on `Decimal` specifically to
/// avoid that class of bug in money arithmetic; parsing amounts into
/// `double` here would silently reintroduce it on the client, one
/// currency conversion at a time. Every model in this package uses this
/// converter for every money field — never a raw `double`.
class DecimalConverter implements JsonConverter<Decimal, String> {
  const DecimalConverter();

  @override
  Decimal fromJson(String json) => Decimal.parse(json);

  @override
  String toJson(Decimal object) => object.toString();
}

/// Same reasoning as [DecimalConverter], for a field that may legitimately
/// be absent (null) on the wire.
class NullableDecimalConverter implements JsonConverter<Decimal?, String?> {
  const NullableDecimalConverter();

  @override
  Decimal? fromJson(String? json) => json == null ? null : Decimal.parse(json);

  @override
  String? toJson(Decimal? object) => object?.toString();
}
