import 'package:dio/dio.dart';

/// Kept intentionally minimal: none of the Step 13 screens read directly
/// from /risk/* (they consume risk findings already folded into
/// decisions and threat impact), but the repository exists per the
/// module list so future screens have a real, tested seam to build on
/// rather than reaching for Dio directly.
class RiskRepository {
  RiskRepository({required Dio dio}) : _dio = dio;

  final Dio _dio;

  Future<Map<String, dynamic>> getAssessment() async {
    final response = await _dio.get<Map<String, dynamic>>('/risk/assessment');
    return response.data!;
  }
}
