import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/auth_models.dart';
import '../repositories/auth_repository.dart';
import '../repositories/decision_repository.dart';
import '../repositories/ingestion_repository.dart';
import '../repositories/risk_repository.dart';
import '../repositories/simulation_repository.dart';
import '../repositories/threat_repository.dart';
import '../repositories/twin_repository.dart';
import 'core_providers.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(dio: ref.watch(dioProvider), tokenStore: ref.watch(tokenStoreProvider));
});

final twinRepositoryProvider = Provider<TwinRepository>((ref) {
  return TwinRepository(dio: ref.watch(dioProvider), database: ref.watch(appDatabaseProvider));
});

final simulationRepositoryProvider = Provider<SimulationRepository>((ref) {
  return SimulationRepository(dio: ref.watch(dioProvider), database: ref.watch(appDatabaseProvider));
});

final riskRepositoryProvider = Provider<RiskRepository>((ref) {
  return RiskRepository(dio: ref.watch(dioProvider));
});

final decisionRepositoryProvider = Provider<DecisionRepository>((ref) {
  return DecisionRepository(dio: ref.watch(dioProvider), database: ref.watch(appDatabaseProvider));
});

final threatRepositoryProvider = Provider<ThreatRepository>((ref) {
  return ThreatRepository(dio: ref.watch(dioProvider));
});

final ingestionRepositoryProvider = Provider<IngestionRepository>((ref) {
  return IngestionRepository(dio: ref.watch(dioProvider), outboxService: ref.watch(outboxServiceProvider));
});

/// The signed-in user's profile — screens derive the cache-key "user id"
/// from this rather than each hand-rolling their own /auth/me call.
final currentUserProfileProvider = FutureProvider<UserProfile>((ref) {
  return ref.watch(authRepositoryProvider).me();
});
