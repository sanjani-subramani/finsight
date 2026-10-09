import 'package:freezed_annotation/freezed_annotation.dart';

part 'trace_step.freezed.dart';
part 'trace_step.g.dart';

/// Mirrors app.contracts.events.TraceStep exactly. `values` is the raw
/// evidence dict for this stage — numbers, amounts, dates, whatever the
/// backend's deterministic pipeline recorded — rendered directly in the
/// Alerts/Reasoning trace view; see docs on TraceStep's role as the
/// backend's own anti-hallucination grounding source.
@freezed
abstract class TraceStep with _$TraceStep {
  const factory TraceStep({
    required int order,
    required String stage,
    required String statement,
    @Default({}) Map<String, dynamic> values,
  }) = _TraceStep;

  factory TraceStep.fromJson(Map<String, dynamic> json) => _$TraceStepFromJson(json);
}
