import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../auth/token_store.dart';
import '../offline/app_database.dart';
import '../offline/outbox_service.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthState {
  const AuthState(this.status);
  final AuthStatus status;
}

/// Drives app-level routing: the router watches this and shows the login
/// flow whenever status is `unauthenticated`, regardless of which screen
/// was on-screen when the token died.
class AuthStateNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    _checkInitial();
    return const AuthState(AuthStatus.unknown);
  }

  Future<void> _checkInitial() async {
    final has = await ref.read(tokenStoreProvider).hasTokens();
    state = AuthState(has ? AuthStatus.authenticated : AuthStatus.unauthenticated);
  }

  void markAuthenticated() => state = const AuthState(AuthStatus.authenticated);

  /// Called both on an explicit user logout AND on an AuthExpiredEvent
  /// from ApiClient (refresh failed) — either way, the router reacts the
  /// same way: back to login.
  void markLoggedOut() => state = const AuthState(AuthStatus.unauthenticated);
}

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());

final authStateProvider = NotifierProvider<AuthStateNotifier, AuthState>(AuthStateNotifier.new);

final apiClientProvider = Provider<ApiClient>((ref) {
  final tokenStore = ref.watch(tokenStoreProvider);
  return ApiClient(
    tokenStore: tokenStore,
    onAuthExpired: () => ref.read(authStateProvider.notifier).markLoggedOut(),
  );
});

final dioProvider = Provider<Dio>((ref) => ref.watch(apiClientProvider).dio);

final appDatabaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});

final connectivityProvider = Provider<ConnectivityChecker>((ref) => ConnectivityPlusChecker());

final outboxServiceProvider = Provider<OutboxService>((ref) {
  final service = OutboxService(
    database: ref.watch(appDatabaseProvider),
    dio: ref.watch(dioProvider),
    connectivity: ref.watch(connectivityProvider),
  );
  ref.onDispose(service.dispose);
  return service;
});
