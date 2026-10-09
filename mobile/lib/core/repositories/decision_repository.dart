import 'package:dio/dio.dart';

import '../models/contextual_intervention.dart';
import '../models/narration_result.dart';
import '../models/trace_step.dart';
import '../offline/app_database.dart';
import 'cache_status.dart';
import 'cached_repository.dart';

class _InterventionListResource extends CachedResource<List<InterventionSummary>> {
  _InterventionListResource({required super.dio, required super.database});

  @override
  String cacheKeyFor(String userId) => 'decisions_list:$userId';

  @override
  Future<Map<String, dynamic>> fetchFromNetwork(String userId) async {
    final response = await dio.get<List<dynamic>>('/decisions');
    // Wrapped under a stable key so a plain JSON array still round-trips
    // through CachedResource's Map<String, dynamic>-based cache storage.
    return {'items': response.data ?? []};
  }

  @override
  List<InterventionSummary> decode(Map<String, dynamic> json) {
    final items = json['items'] as List<dynamic>;
    return items.map((e) => InterventionSummary.fromJson(e as Map<String, dynamic>)).toList();
  }
}

class DecisionRepository {
  DecisionRepository({required Dio dio, required AppDatabase database})
      : _dio = dio,
        _listResource = _InterventionListResource(dio: dio, database: database);

  final Dio _dio;
  final _InterventionListResource _listResource;

  Future<Cached<List<InterventionSummary>>> fetchList(String userId) => _listResource.fetch(userId);

  Stream<Cached<List<InterventionSummary>>> watchList(String userId) => _listResource.watch(userId);

  Future<ContextualIntervention> getDetail(String interventionId) async {
    final response = await _dio.get<Map<String, dynamic>>('/decisions/$interventionId');
    return ContextualIntervention.fromJson(response.data!);
  }

  Future<List<TraceStep>> getTrace(String interventionId) async {
    final response = await _dio.get<List<dynamic>>('/decisions/$interventionId/trace');
    return (response.data ?? []).map((e) => TraceStep.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> acknowledge(String interventionId) async {
    await _dio.post<void>('/decisions/$interventionId/acknowledge');
  }

  Future<void> markActed(String interventionId, bool acted) async {
    await _dio.post<void>('/decisions/$interventionId/acted', data: {'acted': acted});
  }

  /// GET /explain/intervention/{id} — plain-language narration of an
  /// intervention. Not a separate repository: it's the same underlying
  /// resource (an intervention), just phrased differently, and every
  /// caller that wants a narration already holds an intervention id.
  Future<NarrationResult> getNarration(String interventionId, {String style = 'concise'}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/explain/intervention/$interventionId',
      queryParameters: {'style': style},
    );
    return NarrationResult.fromJson(response.data!);
  }
}
