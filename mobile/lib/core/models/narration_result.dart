import 'package:freezed_annotation/freezed_annotation.dart';

part 'narration_result.freezed.dart';
part 'narration_result.g.dart';

/// Mirrors app.modules.explain.narrator.NarrationResult
/// (NarrationResponse on the wire).
///
/// `source` is either "llm" or "template_fallback" — the UI MUST show
/// which one it is (see ConfidenceIndicator-adjacent honesty
/// requirements): a user should always be able to tell whether AI was
/// actually involved in the words they're reading.
@freezed
abstract class NarrationResult with _$NarrationResult {
  const factory NarrationResult({
    required String text,
    // "llm" | "template_fallback"
    required String source,
    @JsonKey(name: 'validation_passed') required bool validationPassed,
    @Default([]) List<String> violations,
    required bool cached,
    @JsonKey(name: 'duration_ms') required int durationMs,
  }) = _NarrationResult;

  factory NarrationResult.fromJson(Map<String, dynamic> json) => _$NarrationResultFromJson(json);
}
