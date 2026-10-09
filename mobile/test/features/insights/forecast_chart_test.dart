import 'package:fl_chart/fl_chart.dart';
import 'package:finsentinel/core/models/simulation_models.dart';
import 'package:finsentinel/features/insights/insights_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('forecast chart renders percentile BANDS, not a single line', (tester) async {
    final summary = BalanceMatrixSummary(
      days: [0, 10, 20, 30],
      p5: [100, 80, 60, 40],
      p25: [150, 130, 110, 90],
      p50: [200, 190, 180, 170],
      p75: [250, 240, 230, 220],
      p95: [300, 290, 280, 270],
    );

    await tester.pumpWidget(
      MaterialApp(home: Scaffold(body: SizedBox(height: 300, child: ForecastBandChart(summary: summary)))),
    );

    final lineChart = tester.widget<LineChart>(find.byType(LineChart));

    // A single-line forecast would have exactly one series. This chart
    // must plot the full p5/p25/p50/p75/p95 spread -- a single line
    // implies a certainty the Monte Carlo model does not have.
    expect(
      lineChart.data.lineBarsData.length,
      greaterThan(1),
      reason: 'must plot multiple percentile series to form bands, not collapse to one line',
    );
    expect(lineChart.data.lineBarsData.length, 5);

    // Exactly one of the five series is the solid, visible p50 centre
    // line (non-transparent, non-zero width); the rest are the
    // (possibly transparent/fill-only) band edges.
    final visibleLines = lineChart.data.lineBarsData.where((bar) => bar.barWidth > 0 && bar.color != Colors.transparent);
    expect(visibleLines.length, 1, reason: 'exactly one solid centre line (p50); the bands are shaded, not drawn as lines');

    // The band-edge series must actually carry the DISTINCT percentile
    // values passed in -- proving this isn't rendering the same line
    // five times.
    final ySeries = lineChart.data.lineBarsData.map((bar) => bar.spots.map((s) => s.y).toSet()).toSet();
    expect(ySeries.length, 5, reason: 'each percentile series must carry its own distinct values');
  });

  testWidgets('forecast chart handles empty data without throwing', (tester) async {
    const emptySummary = BalanceMatrixSummary();
    await tester.pumpWidget(
      MaterialApp(home: Scaffold(body: SizedBox(height: 300, child: ForecastBandChart(summary: emptySummary)))),
    );
    expect(find.byType(LineChart), findsNothing);
    expect(find.textContaining('No forecast data'), findsOneWidget);
  });
}
