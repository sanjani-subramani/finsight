import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/goal.dart';
import '../../core/models/income_source.dart';
import '../../core/providers/repository_providers.dart';

/// Mirrors app.platform.config.Settings' cold-start thresholds — how
/// many real observations move an income source from "declared" to
/// "hybrid" to fully "observed" (see app.modules.twin.forecast). Shown
/// as a progress bar so the user can watch the system learn instead of
/// wondering why an early forecast looks like a guess.
const int kMinObservationsForHybrid = 3;
const int kMinObservationsForObserved = 8;

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(currentUserProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Profile & Goals')),
      body: profileAsync.when(
        data: (profile) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(profile.email, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            _RiskToleranceSelector(current: profile.riskTolerance),
            const SizedBox(height: 24),
            Text('Goals', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            const _GoalsList(),
            const SizedBox(height: 24),
            Text('Income sources', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            const _IncomeSourcesList(),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Could not load profile: $err')),
      ),
    );
  }
}

class _RiskToleranceSelector extends ConsumerStatefulWidget {
  const _RiskToleranceSelector({required this.current});
  final String current;

  @override
  ConsumerState<_RiskToleranceSelector> createState() => _RiskToleranceSelectorState();
}

class _RiskToleranceSelectorState extends ConsumerState<_RiskToleranceSelector> {
  late String _selected = widget.current;
  bool _saving = false;

  Future<void> _select(String value) async {
    setState(() {
      _selected = value;
      _saving = true;
    });
    try {
      await ref.read(authRepositoryProvider).updateRiskTolerance(value);
      ref.invalidate(currentUserProfileProvider);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Risk tolerance', style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 4),
        // Feeds directly into app.modules.decision.gate's tolerance
        // adjustment and app.modules.decision.policy's reduction
        // ordering — this isn't cosmetic, it changes what the backend
        // actually recommends.
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: 'conservative', label: Text('Conservative')),
            ButtonSegment(value: 'balanced', label: Text('Balanced')),
            ButtonSegment(value: 'aggressive', label: Text('Aggressive')),
          ],
          selected: {_selected},
          onSelectionChanged: _saving ? null : (s) => _select(s.first),
        ),
      ],
    );
  }
}

class _GoalsList extends ConsumerWidget {
  const _GoalsList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<List<Goal>>(
      future: ref.read(twinRepositoryProvider).getGoals(),
      builder: (context, snap) {
        if (snap.hasError) return Text('Could not load goals: ${snap.error}');
        if (!snap.hasData) return const Center(child: CircularProgressIndicator());
        final goals = snap.data!;
        if (goals.isEmpty) return const Text('No goals set yet.');
        return Column(
          children: goals
              .map(
                (g) => Card(
                  child: ListTile(
                    title: Text(g.label),
                    subtitle: Text(
                      '₹${g.savedAmount} of ₹${g.targetAmount} · priority ${g.priority} · '
                      '${g.isFlexible ? "flexible" : "fixed"}',
                    ),
                    trailing: SizedBox(
                      width: 48,
                      child: CircularProgressIndicator(
                        value: g.targetAmount.toDouble() == 0 ? 0 : (g.savedAmount / g.targetAmount).toDouble(),
                      ),
                    ),
                  ),
                ),
              )
              .toList(),
        );
      },
    );
  }
}

class _IncomeSourcesList extends ConsumerWidget {
  const _IncomeSourcesList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<List<IncomeSource>>(
      future: ref.read(twinRepositoryProvider).getIncomeSources(),
      builder: (context, snap) {
        if (snap.hasError) return Text('Could not load income sources: ${snap.error}');
        if (!snap.hasData) return const Center(child: CircularProgressIndicator());
        final sources = snap.data!;
        if (sources.isEmpty) return const Text('No income sources on record yet.');
        return Column(children: sources.map((s) => _IncomeSourceTile(source: s)).toList());
      },
    );
  }
}

class _IncomeSourceTile extends StatelessWidget {
  const _IncomeSourceTile({required this.source});
  final IncomeSource source;

  @override
  Widget build(BuildContext context) {
    final target = source.forecastMode == 'declared' ? kMinObservationsForHybrid : kMinObservationsForObserved;
    final progress = target == 0 ? 1.0 : (source.observationCount / target).clamp(0.0, 1.0);
    final nextMode = source.forecastMode == 'declared'
        ? 'hybrid'
        : source.forecastMode == 'hybrid'
            ? 'observed'
            : null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(source.label, style: Theme.of(context).textTheme.titleSmall),
            Text('Mode: ${source.forecastMode} · ${source.observationCount} observation(s)'),
            if (nextMode != null) ...[
              const SizedBox(height: 6),
              LinearProgressIndicator(value: progress),
              const SizedBox(height: 2),
              Text(
                '${source.observationCount}/$target observations toward "$nextMode"',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ] else
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text('Fully learned from observed data.', style: TextStyle(fontStyle: FontStyle.italic)),
              ),
          ],
        ),
      ),
    );
  }
}
