import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers/core_providers.dart';
import '../../core/providers/repository_providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isRegisterMode = false;
  bool _loading = false;
  String? _error;

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    final authRepo = ref.read(authRepositoryProvider);
    try {
      if (_isRegisterMode) {
        await authRepo.register(email: _emailController.text.trim(), password: _passwordController.text);
      }
      await authRepo.login(email: _emailController.text.trim(), password: _passwordController.text);
      ref.read(authStateProvider.notifier).markAuthenticated();
    } catch (e) {
      if (mounted) setState(() => _error = 'Could not sign in: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('FinSentinel')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _loading ? null : _submit,
                  child: _loading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : Text(_isRegisterMode ? 'Register & Sign in' : 'Sign in'),
                ),
                TextButton(
                  onPressed: () => setState(() => _isRegisterMode = !_isRegisterMode),
                  child: Text(_isRegisterMode ? 'Already have an account? Sign in' : 'New here? Register'),
                ),
                if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
