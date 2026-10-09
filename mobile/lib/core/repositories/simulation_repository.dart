import 'package:decimal/decimal.dart';
import 'package:dio/dio.dart';

import '../models/simulation_models.dart';
import '../offline/app_database.dart';
import 'cache_status.dart';
import 'cached_repository.dart';

class _SimulationRunResource extends CachedResource<SimulationRunResult> {
  _SimulationRunResource({required super.dio, required super.database});

  @override
  String cacheKeyFor(String userId) => 'simulation_run:$userId';

  @override
  Future<Map<String, dynamic>> fetchFromNetwork(String userId) async {
    final response = await dio.get<Map<String, dynamic>>('/simulation/run');
    return response.data!;
  }

  @override
  SimulationRunResult decode(Map<String, dynamic> json) => SimulationRunResult.fromJson(json);
}

class SimulationRepository {
  SimulationRepository({required Dio dio, required AppDatabase database})
      : _dio = dio,
        _runResource = _SimulationRunResource(dio: dio, database: database);

  final Dio _dio;
  final _SimulationRunResource _runResource;

  Future<Cached<SimulationRunResult>> fetchRun(String userId) => _runResource.fetch(userId);

  Stream<Cached<SimulationRunResult>> watchRun(String userId) => _runResource.watch(userId);

  Future<PurchaseVerdict> checkAffordability({required Decimal amount, String description = ''}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/simulation/afford',
      data: {'amount': amount.toString(), 'description': description},
    );
    return PurchaseVerdict.fromJson(response.data!);
  }
}
