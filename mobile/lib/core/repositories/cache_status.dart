/// Every repository fetch/watch result is paired with one of these so the
/// UI can NEVER show financial data without knowing — and being able to
/// show — how fresh it actually is.
///
/// Showing a cached balance as if it were live is the worst failure mode
/// in a finance app: the user makes a decision on a number that is no
/// longer true. Every screen wired to a repository in this app must
/// render a staleness marker whenever status != CacheStatus.fresh.
enum CacheStatus {
  /// Just fetched from the network successfully.
  fresh,

  /// Served from local cache because the network fetch failed; the data
  /// may no longer reflect the true current state.
  stale,

  /// No network connectivity at all; served from cache if any exists.
  offline,
}

/// A value paired with how it was obtained.
class Cached<T> {
  const Cached({required this.data, required this.status, this.fetchedAt});

  final T data;
  final CacheStatus status;
  final DateTime? fetchedAt;

  bool get isFresh => status == CacheStatus.fresh;
}
