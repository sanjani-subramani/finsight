import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';

typedef FakeResponder = ResponseBody Function(RequestOptions options);

/// A minimal, fully in-memory [HttpClientAdapter] for tests: no real
/// sockets, no timers, fully deterministic. Register one handler per
/// (method, path); an unmatched request throws immediately so a test
/// notices a missing stub rather than silently hitting the real network.
class FakeHttpClientAdapter implements HttpClientAdapter {
  final Map<String, FakeResponder> _handlers = {};
  final List<RequestOptions> requests = [];

  void on(String method, String path, FakeResponder responder) {
    _handlers['${method.toUpperCase()} $path'] = responder;
  }

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(options);
    final key = '${options.method.toUpperCase()} ${options.path}';
    final handler = _handlers[key];
    if (handler == null) {
      throw StateError('No fake handler registered for $key');
    }
    return handler(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody jsonResponse(Map<String, dynamic> body, int statusCode, {Map<String, List<String>>? headers}) {
  return ResponseBody.fromString(
    jsonEncode(body),
    statusCode,
    headers: {
      'content-type': ['application/json'],
      ...?headers,
    },
  );
}
