import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/offline/outbox_service.dart';
import '../../core/providers/repository_providers.dart';

const List<String> kFinancialEventTypes = [
  'income_received',
  'income_expected',
  'expense',
  'bill_due',
  'bill_paid',
  'emi_due',
  'emi_paid',
  'transfer_in',
  'transfer_out',
  'balance_snapshot',
];

class AddEntryScreen extends ConsumerStatefulWidget {
  const AddEntryScreen({super.key});

  @override
  ConsumerState<AddEntryScreen> createState() => _AddEntryScreenState();
}

class _AddEntryScreenState extends ConsumerState<AddEntryScreen> {
  String _eventType = 'expense';
  final _amountController = TextEditingController();
  final _counterpartyController = TextEditingController();
  final _categoryController = TextEditingController();
  DateTime _occurredAt = DateTime.now();

  // Generated ONCE per logical submission and reused verbatim on every
  // retry of THAT SAME entry — a fresh key per attempt would defeat the
  // entire point of the Idempotency-Key header (a retried request must
  // look identical to the server, not like a brand-new one).
  String? _idempotencyKey;
  bool _submitting = false;
  String? _statusMessage;

  Future<void> _submit() async {
    _idempotencyKey ??= OutboxService.newIdempotencyKey();
    setState(() {
      _submitting = true;
      _statusMessage = null;
    });

    try {
      final result = await ref.read(ingestionRepositoryProvider).addManualEntry(
            eventType: _eventType,
            amount: _amountController.text.trim().isEmpty ? null : _amountController.text.trim(),
            occurredAt: _occurredAt,
            counterparty: _counterpartyController.text.trim().isEmpty ? null : _counterpartyController.text.trim(),
            category: _categoryController.text.trim().isEmpty ? null : _categoryController.text.trim(),
            idempotencyKey: _idempotencyKey,
          );
      if (!mounted) return;
      if (result == null) {
        setState(() => _statusMessage = 'Offline — queued and will sync automatically.');
      } else {
        setState(() => _statusMessage = result.quarantined
            ? 'Saved, but flagged for review: ${result.reason ?? "unclear entry"}'
            : 'Saved.');
        _idempotencyKey = null; // done with this entry; a new one starts a new key
      }
    } catch (e) {
      if (mounted) setState(() => _statusMessage = 'Could not save: $e (tap Save to retry)');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _counterpartyController.dispose();
    _categoryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add entry')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(
          children: [
            DropdownButtonFormField<String>(
              initialValue: _eventType,
              decoration: const InputDecoration(labelText: 'Type', border: OutlineInputBorder()),
              items: kFinancialEventTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
              onChanged: (v) => setState(() => _eventType = v ?? _eventType),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _amountController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Amount (₹)', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _counterpartyController,
              decoration: const InputDecoration(labelText: 'Counterparty', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _categoryController,
              decoration: const InputDecoration(labelText: 'Category', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 12),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Date: ${_occurredAt.toLocal().toString().split(' ').first}'),
              trailing: const Icon(Icons.calendar_today),
              onTap: () async {
                final picked = await showDatePicker(
                  context: context,
                  initialDate: _occurredAt,
                  firstDate: DateTime(2020),
                  lastDate: DateTime.now().add(const Duration(days: 1)),
                );
                if (picked != null) setState(() => _occurredAt = picked);
              },
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Save'),
            ),
            if (_statusMessage != null)
              Padding(padding: const EdgeInsets.only(top: 12), child: Text(_statusMessage!)),
          ],
        ),
      ),
    );
  }
}
