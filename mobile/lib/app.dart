import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/providers/core_providers.dart';
import 'features/add_entry/add_entry_screen.dart';
import 'features/affordability/affordability_screen.dart';
import 'features/alerts/alerts_screen.dart';
import 'features/auth/login_screen.dart';
import 'features/home/home_screen.dart';
import 'features/insights/insights_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/scam_check/scam_check_screen.dart';

class FinSentinelApp extends ConsumerWidget {
  const FinSentinelApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return MaterialApp(
      title: 'FinSentinel',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: switch (authState.status) {
        AuthStatus.unknown => const _SplashScreen(),
        AuthStatus.unauthenticated => const LoginScreen(),
        AuthStatus.authenticated => const _HomeShell(),
      },
    );
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}

/// Bottom-tab shell for the 5 persistent screens; Add-Entry and Scam
/// Check are reached via the app bar (action-oriented, not tabs you sit
/// on).
class _HomeShell extends StatefulWidget {
  const _HomeShell();

  @override
  State<_HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<_HomeShell> {
  int _index = 0;

  static const _tabs = [
    HomeScreen(),
    InsightsScreen(),
    AffordabilityScreen(),
    AlertsScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _tabs),
      floatingActionButton: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        mainAxisSize: MainAxisSize.min,
        children: [
          FloatingActionButton(
            heroTag: 'scam-check',
            tooltip: 'Scam Check',
            onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => const ScamCheckScreen())),
            child: const Icon(Icons.shield_outlined),
          ),
          const SizedBox(width: 12),
          FloatingActionButton(
            heroTag: 'add-entry',
            tooltip: 'Add entry',
            onPressed: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => const AddEntryScreen())),
            child: const Icon(Icons.add),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.account_balance_wallet_outlined), label: 'Balance'),
          NavigationDestination(icon: Icon(Icons.insights_outlined), label: 'Insights'),
          NavigationDestination(icon: Icon(Icons.calculate_outlined), label: 'Afford?'),
          NavigationDestination(icon: Icon(Icons.notifications_outlined), label: 'Alerts'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }
}
