import 'package:decimal/decimal.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// Confidence-tier thresholds. Kept as named constants (not inlined
/// magic numbers) so every widget in this file agrees on exactly the
/// same boundaries — see app.modules.confidence for the backend
/// equivalent this mirrors conceptually (Confidence.high/medium/low).
const double kConfidenceHighThreshold = 0.75;
const double kConfidenceMediumThreshold = 0.50;

enum ConfidenceTier { high, medium, low }

ConfidenceTier confidenceTierOf(double confidence) {
  if (confidence >= kConfidenceHighThreshold) return ConfidenceTier.high;
  if (confidence >= kConfidenceMediumThreshold) return ConfidenceTier.medium;
  return ConfidenceTier.low;
}

/// Reusable uncertainty display. This is a PRODUCT REQUIREMENT, not
/// decoration: every figure this app shows is backed by data of varying
/// confidence (a fresh, LLM-confirmed bank SMS vs. a declared-but-never-
/// observed income guess), and hiding that difference behind a single
/// confident-looking number would let a user make a decision on data
/// that might be wrong. ConfidenceIndicator is how the app tells the
/// truth about how sure it is, at the point where the number is shown —
/// not buried in a settings screen nobody visits.
///
///   >= 0.75            solid, full opacity, no marker.
///   0.50 - 0.74         subtle dashed underline + tooltip ("Based on
///                       partly unconfirmed data").
///   <  0.50             visibly muted + a warning icon + a tooltip
///                       explaining why and what improves it.
class ConfidenceIndicator extends StatelessWidget {
  const ConfidenceIndicator({
    super.key,
    required this.confidence,
    required this.child,
    this.improveHint,
  });

  /// 0.0-1.0, mirroring the backend's *_confidence / confidence_score
  /// fields exactly (never re-derived on the client).
  final double confidence;

  final Widget child;

  /// Shown in the low-confidence tooltip as "what the user can do to
  /// improve it" — e.g. "Confirm this income source to raise
  /// confidence." Falls back to a generic hint if omitted.
  final String? improveHint;

  @override
  Widget build(BuildContext context) {
    final tier = confidenceTierOf(confidence);

    switch (tier) {
      case ConfidenceTier.high:
        return child;

      case ConfidenceTier.medium:
        return Tooltip(
          message: 'Based on partly unconfirmed data',
          child: DecoratedBox(
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Colors.orange,
                  width: 1.5,
                  style: BorderStyle.solid,
                ),
              ),
            ),
            child: Opacity(opacity: 0.85, child: child),
          ),
        );

      case ConfidenceTier.low:
        final hint = improveHint ??
            'Confidence is low because this is based on unconfirmed or '
                'conflicting data. Confirming the underlying transaction '
                'will improve it.';
        return Tooltip(
          message: hint,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Opacity(opacity: 0.6, child: child),
              const SizedBox(width: 4),
              const Icon(Icons.warning_amber_rounded, size: 16, color: Colors.redAccent),
            ],
          ),
        );
    }
  }
}

/// A permanent, non-dismissible badge whenever
/// FinancialStateSnapshot.contains_simulated_data is true.
///
/// Real and demo data must never blur together — a hard product
/// requirement. A user deciding whether they can afford rent must never
/// be looking, even partially, at numbers seeded for a demo. This badge
/// cannot be dismissed or hidden by the user; it is only ever removed by
/// the underlying data itself no longer being simulated.
class SimulatedDataBadge extends StatelessWidget {
  const SimulatedDataBadge({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.purple.shade100,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.purple.shade400),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.science_outlined, size: 14, color: Colors.purple.shade700),
          const SizedBox(width: 4),
          Text(
            'DEMO DATA',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: Colors.purple.shade700,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}

/// Formats a rupee [Decimal] amount honestly for its confidence tier:
///   high    "₹31,800"
///   medium  "~₹31,800"
///   low     "₹31,800 (unconfirmed)"
///
/// The prefix/suffix is not decoration — it is the difference between
/// "this is true" and "this is our best guess," rendered in the number
/// itself so it can't be missed even by a user who never hovers a
/// tooltip.
class UncertainAmount extends StatelessWidget {
  const UncertainAmount({
    super.key,
    required this.amount,
    required this.confidence,
    this.style,
  });

  final Decimal amount;
  final double confidence;
  final TextStyle? style;

  static final NumberFormat _rupeeFormat = NumberFormat.currency(
    locale: 'en_IN',
    symbol: '₹',
    decimalDigits: 0,
  );

  String get formattedText {
    // toDouble() here is purely for NumberFormat's display rendering
    // (it has no Decimal-aware formatter) — the VALUE itself is never
    // passed through a double anywhere it would be stored, compared, or
    // used in arithmetic; only this final render step touches it.
    final formatted = _rupeeFormat.format(amount.toDouble());
    switch (confidenceTierOf(confidence)) {
      case ConfidenceTier.high:
        return formatted;
      case ConfidenceTier.medium:
        return '~$formatted';
      case ConfidenceTier.low:
        return '$formatted (unconfirmed)';
    }
  }

  @override
  Widget build(BuildContext context) {
    return ConfidenceIndicator(
      confidence: confidence,
      child: Text(formattedText, style: style),
    );
  }
}
