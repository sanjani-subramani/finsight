import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/contextual_intervention.dart';
import '../../core/models/narration_result.dart';
import '../../core/models/recommended_action.dart';
import '../../core/models/trace_step.dart';
import '../../core/providers/repository_providers.dart';
import 'alerts_screen.dart' show kSeverityColors;

/// The explainability showcase: every trace step rendered in order with
/// its own evidence values, an LLM-or-template narration with a visible
/// source indicator (honest about whether AI was actually involved), and
/// every recommended action's VERIFIED projected_risk_after.
class AlertDetailScreen extends ConsumerStatefulWidget {
  const AlertDetailScreen({super.key, required this.interventionId});

  final String interventionId;

  @override
  ConsumerState<AlertDetailScreen> createState() => _AlertDetailScreenState();
}

class _AlertDetailScreenState extends ConsumerState<AlertDetailScreen> {
  ContextualIntervention? _intervention;
  NarrationResult? _narration;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = ref.read(decisionRepositoryProvider);
    try {
      final intervention = await repo.getDetail(widget.interventionId);
      if (!mounted) return;
      setState(() => _intervention = intervention);
      await repo.acknowledge(widget.interventionId);
      final narration = await repo.getNarration(widget.interventionId);
      if (!mounted) return;
      setState(() => _narration = narration);
    } catch (e) {
      if (mounted) setState(() => _error = 'Could not load this alert: $e');
    }
  }

  Future<void> _reportActed(bool acted) async {
    await ref.read(decisionRepositoryProvider).markActed(widget.interventionId, acted);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(acted ? 'Thanks — marked as acted on.' : 'Noted — marked as not acted on.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final intervention = _intervention;
    return Scaffold(
      appBar: AppBar(title: const Text('Alert detail')),
      body: _error != null
          ? Center(child: Text(_error!))
          : intervention == null
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    _HeaderCard(intervention: intervention),
                    const SizedBox(height: 16),
                    if (_narration != null) _NarrationCard(narration: _narration!),
                    const SizedBox(height: 24),
                    if (intervention.recommendedActions.isNotEmpty) ...[
                      Text('Recommended actions', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      ...intervention.recommendedActions.map((a) => _ActionTile(action: a)),
                      const SizedBox(height: 24),
                    ],
                    Text('How this was worked out', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    ...intervention.decisionTrace.map((step) => _TraceStepTile(step: step)),
                    const SizedBox(height: 24),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _reportActed(true),
                            child: const Text('I acted on this'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => _reportActed(false),
                            child: const Text('Not yet'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
    );
  }
}

class _HeaderCard extends StatelessWidget {
  const _HeaderCard({required this.intervention});
  final ContextualIntervention intervention;

  @override
  Widget build(BuildContext context) {
    final color = kSeverityColors[intervention.severity] ?? Colors.grey;
    return Card(
      color: color.withValues(alpha: 0.08),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Chip(
                  label: Text(intervention.severity.toUpperCase()),
                  backgroundColor: color.withValues(alpha: 0.2),
                ),
                if (intervention.confidenceCeilingApplied)
                  const Padding(
                    padding: EdgeInsets.only(left: 8),
                    child: Tooltip(
                      message: 'Severity was capped because the underlying data confidence was low',
                      child: Icon(Icons.info_outline, size: 18),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(intervention.headline, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(intervention.body),
          ],
        ),
      ),
    );
  }
}

class _NarrationCard extends StatelessWidget {
  const _NarrationCard({required this.narration});
  final NarrationResult narration;

  @override
  Widget build(BuildContext context) {
    final isLlm = narration.source == 'llm';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(isLlm ? Icons.auto_awesome : Icons.description_outlined, size: 16),
                const SizedBox(width: 6),
                // Honest about when AI was and was not involved — never
                // implied, always stated.
                Text(
                  isLlm ? 'AI-narrated' : 'Template narration (AI unavailable or unverified)',
                  style: Theme.of(context).textTheme.labelSmall,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(narration.text),
          ],
        ),
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  const _ActionTile({required this.action});
  final RecommendedAction action;

  @override
  Widget build(BuildContext context) {
    final projectedRiskAfter = action.projectedRiskAfter;
    return Card(
      child: ListTile(
        title: Text(action.label),
        subtitle: action.expectedEffect != null ? Text(action.expectedEffect!) : null,
        trailing: projectedRiskAfter != null
            ? Text('${(projectedRiskAfter * 100).toStringAsFixed(0)}%\nafter', textAlign: TextAlign.center)
            : null,
      ),
    );
  }
}

class _TraceStepTile extends StatelessWidget {
  const _TraceStepTile({required this.step});
  final TraceStep step;

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      title: Text('${step.order + 1}. ${step.stage}'),
      subtitle: Text(step.statement, maxLines: 2, overflow: TextOverflow.ellipsis),
      children: [
        if (step.values.isEmpty)
          const Padding(padding: EdgeInsets.all(8), child: Text('No supporting values recorded.'))
        else
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: step.values.entries
                  .map((e) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text('${e.key}: ${e.value}', style: Theme.of(context).textTheme.bodySmall),
                      ))
                  .toList(),
            ),
          ),
      ],
    );
  }
}
