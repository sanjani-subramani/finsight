import 'dart:async';

import 'package:finsentinel/core/offline/outbox_service.dart';

/// A controllable fake — never touches a platform channel, so plain
/// `flutter_test` unit tests can construct an OutboxService without any
/// plugin bindings at all.
class FakeConnectivityChecker implements ConnectivityChecker {
  final _controller = StreamController<bool>.broadcast();

  @override
  Stream<bool> get onlineStatusChanges => _controller.stream;

  void goOnline() => _controller.add(true);
  void goOffline() => _controller.add(false);

  void dispose() => _controller.close();
}
