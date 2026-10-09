import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/simulation_models.dart';
import '../../core/providers/repository_providers.dart';
import '../../core/repositories/cache_status.dart';

/// Forecast chart plots the p5/p25/p50/p75/p95 percentile BANDS from
/// balance_matrix_summary — never a single line. A single line implies a
/// certainty the Monte Carlo model does not have; the band IS the
/// message: "here is the real spread of outcomes," not "here is THE
/// number."
class InsightsScreen extends ConsumerWidget {
  const InsightsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(currentUserProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Insights')),
      body: profileAsync.when(
        data: (profile) => _ForecastBody(userId: profile.id),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Could not load profile: $err')),
      ),
    );
  }
}

class _ForecastBody extends ConsumerWidget {
  const _ForecastBody({required this.userId});
  final String userId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repo = ref.watch(simulationRepositoryProvider);

    return StreamBuilder<Cached<SimulationRunResult>>(
      stream: repo.watchRun(userId),
      builder: (context, snap) {
        if (snap.hasError) {
          return Center(child: Text('Could not load forecast: ${snap.error}'));
        }
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final cached = snap.data!;
        final result = cached.data;

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (cached.status != CacheStatus.fresh)
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: Text('Showing cached forecast', style: TextStyle(color: Colors.orange)),
              ),
            Text('Balance forecast (p5-p95 range)', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            SizedBox(height: 240, child: ForecastBandChart(summary: result.balanceMatrixSummary)),
            const SizedBox(height: 24),
            Text('Shortfall risk by horizon', style: Theme.of(context).textTheme.titleMedium),
            ...result.shortfallProbabilityByHorizon.entries.map(
              (e) => ListTile(
                dense: true,
                title: Text('${e.key} days'),
                trailing: Text('${(e.value * 100).toStringAsFixed(0)}%'),
              ),
            ),
          ],
        );
      },
    );
  }
}

/// Renders BalanceMatrixSummary as three nested shaded bands (p5-p95
/// outer, p25-p75 inner) plus a solid p50 centre line, using fl_chart's
/// layered belowBarData technique: each line's fill extends down to the
/// chart's minY, so a later "erase" line (filled with the background
/// colour) painted on top of an earlier shaded line leaves only the gap
/// between the two visible as a band.
class ForecastBandChart extends StatelessWidget {
  const ForecastBandChart({super.key, required this.summary});

  final BalanceMatrixSummary summary;

  @override
  Widget build(BuildContext context) {
    if (summary.days.isEmpty) {
      return const Center(child: Text('No forecast data available.'));
    }

    final background = Theme.of(context).scaffoldBackgroundColor;
    final outerColor = Colors.blue.withValues(alpha: 0.15);
    final innerColor = Colors.blue.withValues(alpha: 0.35);

    final allValues = [...summary.p5, ...summary.p95];
    final minY = allValues.reduce((a, b) => a < b ? a : b);
    final maxY = allValues.reduce((a, b) => a > b ? a : b);
    final padding = (maxY - minY).abs() * 0.1 + 1;

    List<FlSpot> spotsFor(List<double> values) =>
        [for (var i = 0; i < summary.days.length && i < values.length; i++) FlSpot(summary.days[i].toDouble(), values[i])];

    LineChartBarData band(List<double> values, Color fillColor) {
      return LineChartBarData(
        spots: spotsFor(values),
        isCurved: false,
        color: Colors.transparent,
        barWidth: 0,
        dotData: const FlDotData(show: false),
        belowBarData: BarAreaData(show: true, color: fillColor),
      );
    }

    return LineChart(
      LineChartData(
        minY: minY - padding,
        maxY: maxY + padding,
        titlesData: const FlTitlesData(
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        lineBarsData: [
          band(summary.p95, outerColor),
          band(summary.p5, background),
          band(summary.p75, innerColor),
          band(summary.p25, background),
          LineChartBarData(
            spots: spotsFor(summary.p50),
            isCurved: false,
            color: Colors.blue.shade800,
            barWidth: 2,
            dotData: const FlDotData(show: false),
          ),
        ],
      ),
    );
  }
}
