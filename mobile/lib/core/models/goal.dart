import 'package:decimal/decimal.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'decimal_converter.dart';

part 'goal.freezed.dart';
part 'goal.g.dart';

/// Mirrors app.contracts.events.Goal exactly.
@freezed
abstract class Goal with _$Goal {
  const factory Goal({
    @JsonKey(name: 'goal_id') required String goalId,
    required String label,
    @JsonKey(name: 'target_amount') @DecimalConverter() required Decimal targetAmount,
    @JsonKey(name: 'saved_amount') @DecimalConverter() required Decimal savedAmount,
    @JsonKey(name: 'target_date') DateTime? targetDate,
    required int priority,
    @JsonKey(name: 'is_flexible') required bool isFlexible,
  }) = _Goal;

  factory Goal.fromJson(Map<String, dynamic> json) => _$GoalFromJson(json);
}
