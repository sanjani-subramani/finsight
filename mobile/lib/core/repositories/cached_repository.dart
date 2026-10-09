import 'dart:convert';

import 'package:dio/dio.dart';

import '../offline/app_database.dart';
import 'cache_status.dart';

/// Shared network-first-with-cache-fallback behaviour for a repository's
/// primary GET resource: fetch() tries the network and falls back to
/// cache on failure; watch() emits whatever is cached immediately (so
/// the UI has SOMETHING to show without waiting on a round trip), then
/// emits the fresh network result once it arrives.
///
/// Every subclass instance owns exactly one cached resource, addressed
/// by [cacheKeyFor]. A repository that exposes several distinct GET
/// resources (e.g. DecisionRepository's list AND its per-intervention
/// detail) composes multiple instances of this, one per resource — see
/// DecisionRepository for the pattern.
abstract class CachedResource<T> {
  CachedResource({required this.dio, required this.database});

  final Dio dio;
  final AppDatabase database;

  String cacheKeyFor(String userId);

  /// Performs the actual network call and returns the raw JSON payload
  /// (a decoded Map, ready to hand to [decode]).
  Future<Map<String, dynamic>> fetchFromNetwork(String userId);

  T decode(Map<String, dynamic> json);

  Future<Cached<T>> fetch(String userId) async {
    final key = cacheKeyFor(userId);
    try {
      final json = await fetchFromNetwork(userId);
      final now = DateTime.now().toUtc();
      await database.into(database.cachedSnapshots).insertOnConflictUpdate(
            CachedSnapshotsCompanion.insert(
              cacheKey: key,
              userId: userId,
              payload: jsonEncode(json),
              fetchedAt: now,
            ),
          );
      return Cached(data: decode(json), status: CacheStatus.fresh, fetchedAt: now);
    } on DioException catch (e) {
      final cachedEntry = await _readCache(key);
      if (cachedEntry == null) rethrow;
      final isOffline = e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout;
      return Cached(
        data: cachedEntry.value,
        status: isOffline ? CacheStatus.offline : CacheStatus.stale,
        fetchedAt: cachedEntry.fetchedAt,
      );
    }
  }

  /// Emits the cached value immediately (marked stale — it was NOT just
  /// fetched), then emits the outcome of a background refresh. A
  /// screen using this should keep showing the stale value (with its
  /// marker) while the fresh one is in flight, then swap seamlessly.
  Stream<Cached<T>> watch(String userId) async* {
    final key = cacheKeyFor(userId);
    final cachedEntry = await _readCache(key);
    if (cachedEntry != null) {
      yield Cached(data: cachedEntry.value, status: CacheStatus.stale, fetchedAt: cachedEntry.fetchedAt);
    }
    try {
      yield await fetch(userId);
    } catch (_) {
      if (cachedEntry == null) rethrow;
      // fetch() already returned a cache-fallback Cached<T> for any
      // DioException with a cache hit; a rethrow here only happens when
      // there was truly nothing cached, which we already handled above.
    }
  }

  Future<_CacheEntry<T>?> _readCache(String key) async {
    final row = await (database.select(database.cachedSnapshots)
          ..where((t) => t.cacheKey.equals(key)))
        .getSingleOrNull();
    if (row == null) return null;
    final json = jsonDecode(row.payload) as Map<String, dynamic>;
    return _CacheEntry(decode(json), row.fetchedAt);
  }
}

class _CacheEntry<T> {
  const _CacheEntry(this.value, this.fetchedAt);
  final T value;
  final DateTime fetchedAt;
}
