import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models/threat_event.dart';
import '../../core/providers/repository_providers.dart';

/// POST /threat/sms | /threat/url | /threat/qr.
///
/// A real camera-based QR scanner is out of scope here (would pull in a
/// camera plugin + permission flow) — the QR tab accepts a pasted
/// payload string instead, exercising the exact same backend endpoint
/// and rendering path a scanned code would.
class ScamCheckScreen extends StatefulWidget {
  const ScamCheckScreen({super.key});

  @override
  State<ScamCheckScreen> createState() => _ScamCheckScreenState();
}

class _ScamCheckScreenState extends State<ScamCheckScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 3, vsync: this);

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scam Check'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [Tab(text: 'SMS'), Tab(text: 'URL'), Tab(text: 'QR')],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          _SmsCheckTab(),
          _UrlCheckTab(),
          _QrCheckTab(),
        ],
      ),
    );
  }
}

class _SmsCheckTab extends ConsumerStatefulWidget {
  const _SmsCheckTab();
  @override
  ConsumerState<_SmsCheckTab> createState() => _SmsCheckTabState();
}

class _SmsCheckTabState extends ConsumerState<_SmsCheckTab> {
  final _bodyController = TextEditingController();
  final _senderController = TextEditingController();
  ThreatEvent? _result;
  bool _loading = false;
  String? _error;

  Future<void> _check() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await ref
          .read(threatRepositoryProvider)
          .checkSms(body: _bodyController.text, sender: _senderController.text);
      setState(() => _result = result);
    } catch (e) {
      setState(() => _error = 'Could not analyse: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _CheckForm(
      loading: _loading,
      error: _error,
      result: _result,
      onCheck: _check,
      fields: [
        TextField(
          controller: _senderController,
          decoration: const InputDecoration(labelText: 'Sender ID (optional)', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _bodyController,
          maxLines: 4,
          decoration: const InputDecoration(labelText: 'Paste SMS text', border: OutlineInputBorder()),
        ),
      ],
    );
  }
}

class _UrlCheckTab extends ConsumerStatefulWidget {
  const _UrlCheckTab();
  @override
  ConsumerState<_UrlCheckTab> createState() => _UrlCheckTabState();
}

class _UrlCheckTabState extends ConsumerState<_UrlCheckTab> {
  final _urlController = TextEditingController();
  ThreatEvent? _result;
  bool _loading = false;
  String? _error;

  Future<void> _check() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await ref.read(threatRepositoryProvider).checkUrl(_urlController.text.trim());
      setState(() => _result = result);
    } catch (e) {
      setState(() => _error = 'Could not analyse: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _CheckForm(
      loading: _loading,
      error: _error,
      result: _result,
      onCheck: _check,
      fields: [
        TextField(
          controller: _urlController,
          decoration: const InputDecoration(labelText: 'Paste URL', border: OutlineInputBorder()),
        ),
      ],
    );
  }
}

class _QrCheckTab extends ConsumerStatefulWidget {
  const _QrCheckTab();
  @override
  ConsumerState<_QrCheckTab> createState() => _QrCheckTabState();
}

class _QrCheckTabState extends ConsumerState<_QrCheckTab> {
  final _payloadController = TextEditingController();
  ThreatEvent? _result;
  bool _loading = false;
  String? _error;

  Future<void> _check() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await ref.read(threatRepositoryProvider).checkQr(_payloadController.text.trim());
      setState(() => _result = result);
    } catch (e) {
      setState(() => _error = 'Could not analyse: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return _CheckForm(
      loading: _loading,
      error: _error,
      result: _result,
      onCheck: _check,
      fields: [
        TextField(
          controller: _payloadController,
          maxLines: 2,
          decoration: const InputDecoration(labelText: 'QR payload (e.g. upi://pay?...)', border: OutlineInputBorder()),
        ),
      ],
    );
  }
}

class _CheckForm extends StatelessWidget {
  const _CheckForm({
    required this.fields,
    required this.loading,
    required this.error,
    required this.result,
    required this.onCheck,
  });

  final List<Widget> fields;
  final bool loading;
  final String? error;
  final ThreatEvent? result;
  final VoidCallback onCheck;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        ...fields,
        const SizedBox(height: 12),
        ElevatedButton(
          onPressed: loading ? null : onCheck,
          child: loading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Check'),
        ),
        if (error != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(error!, style: const TextStyle(color: Colors.red))),
        if (result != null) ...[
          const SizedBox(height: 24),
          _ThreatResultCard(threat: result!),
        ],
      ],
    );
  }
}

class _ThreatResultCard extends StatelessWidget {
  const _ThreatResultCard({required this.threat});
  final ThreatEvent threat;

  Color get _riskColor {
    if (threat.riskScore >= 0.6) return Colors.red;
    if (threat.riskScore >= 0.3) return Colors.orange;
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          color: _riskColor.withValues(alpha: 0.1),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  backgroundColor: _riskColor,
                  child: Text((threat.riskScore * 100).toStringAsFixed(0)),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Risk score: ${(threat.riskScore * 100).toStringAsFixed(0)}% · ${threat.primaryCategory}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
              ],
            ),
          ),
        ),
        // Financial impact shown PROMINENTLY, not buried — this is the
        // differentiator: not "suspicious link" but "this would leave
        // you unable to pay rent."
        if (threat.impact != null && threat.impact!.wouldCauseShortfall)
          Card(
            color: Colors.red.shade50,
            margin: const EdgeInsets.only(top: 12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.warning_amber_rounded, color: Colors.red),
                      SizedBox(width: 8),
                      Text('Financial impact', style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(threat.impact!.humanStatement),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),
        Text('Signal breakdown', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        if (threat.signals.isEmpty) const Text('No specific signals matched.'),
        ...threat.signals.map(
          (s) => Card(
            child: ListTile(
              title: Text(s.name),
              subtitle: Text(s.evidence ?? 'No evidence recorded'),
              trailing: Text(s.weight.toStringAsFixed(0), style: const TextStyle(fontWeight: FontWeight.bold)),
            ),
          ),
        ),
      ],
    );
  }
}
