import 'package:freezed_annotation/freezed_annotation.dart';

part 'threat_signal.freezed.dart';
part 'threat_signal.g.dart';

/// Mirrors app.contracts.events.ThreatSignal exactly.
@freezed
abstract class ThreatSignal with _$ThreatSignal {
  const factory ThreatSignal({
    required String name,
    required String category,
    required double weight,
    String? evidence,
    // "rule" | "model" | "hybrid"
    required String detector,
  }) = _ThreatSignal;

  factory ThreatSignal.fromJson(Map<String, dynamic> json) => _$ThreatSignalFromJson(json);
}
