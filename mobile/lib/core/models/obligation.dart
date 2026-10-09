import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'obligation.freezed.dart';
part 'obligation.g.dart';

/// Mirrors app.contracts.events.Obligation exactly.
@freezed
abstract class Obligation with _$Obligation {
  const factory Obligation({
    @JsonKey(name: 'obligation_id') required String obligationId,
    required String label,
    @DecimalConverter() required Decimal amount,
    @JsonKey(name: 'due_date') required DateTime dueDate,
    String? category,
    @JsonKey(name: 'is_fixed') required bool isFixed,
    @JsonKey(name: 'is_paid') required bool isPaid,
    @JsonKey(name: 'confidence_score') required double confidenceScore,
  }) = _Obligation;

  factory Obligation.fromJson(Map<String, dynamic> json) => _$ObligationFromJson(json);
}
