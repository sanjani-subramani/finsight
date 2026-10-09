import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/models/contextual_intervention.dart';
import '../../core/providers/repository_providers.dart';
import '../../core/repositories/cache_status.dart';
import 'alert_detail_screen.dart';

const Map<String, Color> kSeverityColors = {
  'ignore': Colors.grey,
  'monitor': Colors.blue,
  'notify': Colors.orange,
  'critical': Colors.red,
};

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(currentUserProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Alerts')),
      body: profileAsync.when(
        data: (profile) => _AlertsList(userId: profile.id),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, st) => Center(child: Text('Could not load profile: $err')),
      ),
    );
  }
}

class _AlertsList extends ConsumerWidget {
  const _AlertsList({required this.userId});
  final String userId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repo = ref.watch(decisionRepositoryProvider);

    return StreamBuilder<Cached<List<InterventionSummary>>>(
      stream: repo.watchList(userId),
      builder: (context, snap) {
        if (snap.hasError) {
          return Center(child: Text('Could not load alerts: ${snap.error}'));
        }
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final cached = snap.data!;
        final items = cached.data;

        return RefreshIndicator(
          onRefresh: () => repo.fetchList(userId),
          child: Column(
            children: [
              if (cached.status != CacheStatus.fresh)
                Container(
                  width: double.infinity,
                  color: Colors.amber.shade100,
                  padding: const EdgeInsets.all(8),
                  child: const Text('Showing cached alerts', style: TextStyle(fontSize: 12)),
                ),
              Expanded(
                child: items.isEmpty
                    ? ListView(children: const [Padding(padding: EdgeInsets.all(24), child: Text('No alerts right now.'))])
                    : ListView.builder(
                        itemCount: items.length,
                        itemBuilder: (context, index) {
                          final item = items[index];
                          final color = kSeverityColors[item.severity] ?? Colors.grey;
                          return ListTile(
                            leading: CircleAvatar(backgroundColor: color, radius: 8, child: const SizedBox()),
                            title: Text(item.headline),
                            subtitle: Text(
                              '${DateFormat.yMMMd().add_jm().format(item.createdAt)} · ${item.severity.toUpperCase()}',
                            ),
                            trailing: item.userAcknowledged ? null : const Icon(Icons.circle, size: 8, color: Colors.blue),
                            onTap: () => Navigator.of(context).push(
                              MaterialPageRoute<void>(builder: (_) => AlertDetailScreen(interventionId: item.id)),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}
