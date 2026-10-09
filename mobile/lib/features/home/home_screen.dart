import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/models/financial_state_snapshot.dart';
import '../../core/providers/repository_providers.dart';
import '../../core/repositories/cache_status.dart';
import '../../core/widgets/confidence_indicator.dart';

/// Minimal, wiring-first Home/Balance screen: GET /twin/snapshot via
/// TwinRepository.watchSnapshot, with an always-visible staleness marker
/// and confidence-aware amounts. Polish is intentionally deferred; the
/// data path is real.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(currentUserProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Balance')),
      body: profileAsync.when(
        data: (profile) => _SnapshotBody(userId: profile.id),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Could not load profile: $err')),
      ),
    );
  }
}

class _SnapshotBody extends ConsumerWidget {
  const _SnapshotBody({required this.userId});
  final String userId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repo = ref.watch(twinRepositoryProvider);

    return StreamBuilder<Cached<FinancialStateSnapshot>>(
      stream: repo.watchSnapshot(userId),
      builder: (context, snap) {
        if (snap.hasError) {
          return Center(child: Text('Could not load your balance: ${snap.error}'));
        }
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final cached = snap.data!;
        final snapshot = cached.data;

        return RefreshIndicator(
          onRefresh: () => repo.fetchSnapshot(userId),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (cached.status != CacheStatus.fresh)
                _StalenessBanner(status: cached.status, fetchedAt: cached.fetchedAt),
              if (snapshot.containsSimulatedData)
                const Padding(padding: EdgeInsets.only(bottom: 8), child: SimulatedDataBadge()),
              Text('Cash available', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 4),
              UncertainAmount(
                amount: snapshot.cashAvailable,
                confidence: snapshot.stateConfidence,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 24),
              _WeatherTile(snapshot: snapshot),
              const SizedBox(height: 24),
              if (snapshot.timeToDangerDays != null)
                Card(
                  color: Colors.red.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(
                      '${snapshot.timeToDangerDays} days before risk exceeds 50%',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              const SizedBox(height: 24),
              Text('Upcoming obligations', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (snapshot.obligations.isEmpty) const Text('No upcoming obligations on record.'),
              ...snapshot.obligations.map(
                (o) => ListTile(
                  title: Text(o.label),
                  subtitle: Text(DateFormat.yMMMd().format(o.dueDate)),
                  trailing: UncertainAmount(amount: o.amount, confidence: o.confidenceScore),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StalenessBanner extends StatelessWidget {
  const _StalenessBanner({required this.status, this.fetchedAt});
  final CacheStatus status;
  final DateTime? fetchedAt;

  @override
  Widget build(BuildContext context) {
    final label = status == CacheStatus.offline
        ? 'Offline — showing last known data'
        : 'Showing cached data — refreshing…';
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(8),
      color: Colors.amber.shade100,
      child: Row(
        children: [
          const Icon(Icons.cloud_off, size: 16),
          const SizedBox(width: 8),
          Expanded(child: Text(label, style: const TextStyle(fontSize: 12))),
          if (fetchedAt != null) Text(_relativeTime(fetchedAt!), style: const TextStyle(fontSize: 11)),
        ],
      ),
    );
  }

  String _relativeTime(DateTime time) {
    final diff = DateTime.now().toUtc().difference(time.toUtc());
    if (diff.inMinutes < 1) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

class _WeatherTile extends StatelessWidget {
  const _WeatherTile({required this.snapshot});
  final FinancialStateSnapshot snapshot;

  static const _colors = {
    'stable': Colors.green,
    'pressure': Colors.orange,
    'risk': Colors.deepOrange,
    'critical': Colors.red,
  };

  @override
  Widget build(BuildContext context) {
    final color = _colors[snapshot.weather] ?? Colors.grey;
    final obligations30d = snapshot.totalFixedObligations;
    // Coverage ratio: cash on hand vs. what's committed — the same
    // figure compute_weather (app.modules.twin) bases the label on,
    // shown on tap so "pressure" isn't just a mood word.
    final coverageRatio = obligations30d.toDouble() == 0
        ? null
        : snapshot.cashAvailable.toDouble() / obligations30d.toDouble();

    return InkWell(
      onTap: () => showDialog<void>(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Coverage ratio'),
          content: Text(
            coverageRatio == null
                ? 'No fixed obligations on record to compare against.'
                : 'Cash available covers ${(coverageRatio * 100).toStringAsFixed(0)}% of your '
                    'total fixed obligations (₹${snapshot.cashAvailable} vs ₹$obligations30d).',
          ),
          actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Close'))],
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8)),
        child: Row(
          children: [
            Icon(Icons.cloud, color: color),
            const SizedBox(width: 8),
            Text('Financial weather: ${_capitalize(snapshot.weather)} (tap for detail)'),
          ],
        ),
      ),
    );
  }

  String _capitalize(String s) => s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';
}
