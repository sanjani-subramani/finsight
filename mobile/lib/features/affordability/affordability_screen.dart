import 'package:decimal/decimal.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/simulation_models.dart';
import '../../core/providers/repository_providers.dart';

/// POST /simulation/afford — a purchase-specific verdict — combined with
/// the "top sensitivity factor" from GET /simulation/run's general
/// sensitivity analysis (PurchaseVerdictResponse itself carries no
/// sensitivity data; RunResponse.sensitivity is where "what would change
/// this" actually lives on the backend).
class AffordabilityScreen extends ConsumerStatefulWidget {
  const AffordabilityScreen({super.key});

  @override
  ConsumerState<AffordabilityScreen> createState() => _AffordabilityScreenState();
}

class _AffordabilityScreenState extends ConsumerState<AffordabilityScreen> {
  final _controller = TextEditingController();
  PurchaseVerdict? _verdict;
  bool _loading = false;
  String? _error;

  Future<void> _check() async {
    final raw = _controller.text.trim();
    if (raw.isEmpty) return;
    final Decimal amount;
    try {
      amount = Decimal.parse(raw);
    } catch (_) {
      setState(() => _error = 'Enter a valid amount');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final verdict = await ref.read(simulationRepositoryProvider).checkAffordability(amount: amount);
      setState(() => _verdict = verdict);
    } catch (e) {
      setState(() => _error = 'Could not check affordability: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(currentUserProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Can I afford this?')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _controller,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Amount (₹)', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _loading ? null : _check,
              child: _loading
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Check'),
            ),
            if (_error != null)
              Padding(padding: const EdgeInsets.only(top: 8), child: Text(_error!, style: const TextStyle(color: Colors.red))),
            if (_verdict != null) ...[
              const SizedBox(height: 24),
              _VerdictCard(verdict: _verdict!),
              const SizedBox(height: 16),
              profileAsync.when(
                data: (profile) => _TopSensitivityFactor(userId: profile.id),
                loading: () => const SizedBox.shrink(),
                error: (_, _) => const SizedBox.shrink(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _VerdictCard extends StatelessWidget {
  const _VerdictCard({required this.verdict});
  final PurchaseVerdict verdict;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: verdict.affordable ? Colors.green.shade50 : Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              verdict.affordable ? 'Affordable' : 'Not recommended right now',
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.copyWith(color: verdict.affordable ? Colors.green.shade800 : Colors.red.shade800),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _ProbColumn(label: 'Before', value: verdict.probBefore),
                const Icon(Icons.arrow_forward),
                _ProbColumn(label: 'After', value: verdict.probAfter),
              ],
            ),
            if (!verdict.affordable && verdict.waitDaysRecommended != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.orange.shade100, borderRadius: BorderRadius.circular(8)),
                child: Text(
                  'Wait ${verdict.waitDaysRecommended} day(s) before this purchase',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ProbColumn extends StatelessWidget {
  const _ProbColumn({required this.label, required this.value});
  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: Theme.of(context).textTheme.labelMedium),
        Text('${(value * 100).toStringAsFixed(0)}%', style: Theme.of(context).textTheme.headlineSmall),
      ],
    );
  }
}

class _TopSensitivityFactor extends ConsumerWidget {
  const _TopSensitivityFactor({required this.userId});
  final String userId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder(
      future: ref.read(simulationRepositoryProvider).fetchRun(userId),
      builder: (context, snap) {
        if (!snap.hasData) return const SizedBox.shrink();
        final sensitivity = snap.data!.data.sensitivity;
        if (sensitivity.isEmpty) return const SizedBox.shrink();
        final top = sensitivity.reduce((a, b) => a.delta.abs() > b.delta.abs() ? a : b);
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('What would change this most', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 4),
                Text(top.description),
                Text(
                  '${(top.probBefore * 100).toStringAsFixed(0)}% → ${(top.probAfter * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
