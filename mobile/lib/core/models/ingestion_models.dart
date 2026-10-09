import 'package:freezed_annotation/freezed_annotation.dart';

part 'ingestion_models.freezed.dart';
part 'ingestion_models.g.dart';

/// POST /ingest/manual (IngestionResponse) — used synchronously, so a
/// definite event_id/quarantine outcome is always known immediately.
@freezed
abstract class IngestionResult with _$IngestionResult {
  const factory IngestionResult({
    @JsonKey(name: 'event_id') String? eventId,
    required String method,
    required double confidence,
    @JsonKey(name: 'was_duplicate') required bool wasDuplicate,
    required bool quarantined,
    String? reason,
  }) = _IngestionResult;

  factory IngestionResult.fromJson(Map<String, dynamic> json) => _$IngestionResultFromJson(json);
}
