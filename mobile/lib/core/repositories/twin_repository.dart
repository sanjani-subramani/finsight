import 'package:dio/dio.dart';

import '../models/financial_state_snapshot.dart';
import '../models/goal.dart';
import '../models/income_source.dart';
import '../offline/app_database.dart';
import 'cache_status.dart';
import 'cached_repository.dart';

class _SnapshotResource extends CachedResource<FinancialStateSnapshot> {
  _SnapshotResource({required super.dio, required super.database});

  @override
  String cacheKeyFor(String userId) => 'twin_snapshot:$userId';

  @override
  Future<Map<String, dynamic>> fetchFromNetwork(String userId) async {
    final response = await dio.get<Map<String, dynamic>>('/twin/snapshot');
    return response.data!;
  }

  @override
  FinancialStateSnapshot decode(Map<String, dynamic> json) => FinancialStateSnapshot.fromJson(json);
}

class TwinRepository {
  TwinRepository({required Dio dio, required AppDatabase database})
      : _dio = dio,
        _snapshotResource = _SnapshotResource(dio: dio, database: database);

  final Dio _dio;
  final _SnapshotResource _snapshotResource;

  Future<Cached<FinancialStateSnapshot>> fetchSnapshot(String userId) => _snapshotResource.fetch(userId);

  Stream<Cached<FinancialStateSnapshot>> watchSnapshot(String userId) => _snapshotResource.watch(userId);

  Future<List<Goal>> getGoals() async {
    final response = await _dio.get<List<dynamic>>('/twin/goals');
    return (response.data ?? []).map((e) => Goal.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<IncomeSource>> getIncomeSources() async {
    final response = await _dio.get<List<dynamic>>('/twin/income-sources');
    return (response.data ?? []).map((e) => IncomeSource.fromJson(e as Map<String, dynamic>)).toList();
  }
}
