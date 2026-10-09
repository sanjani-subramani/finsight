import 'package:dio/dio.dart';

import '../models/threat_event.dart';

class ThreatRepository {
  ThreatRepository({required Dio dio}) : _dio = dio;

  final Dio _dio;

  Future<ThreatEvent> checkSms({required String body, String sender = ''}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/threat/sms',
      data: {'body': body, 'sender': sender},
    );
    return ThreatEvent.fromJson(response.data!);
  }

  Future<ThreatEvent> checkUrl(String url) async {
    final response = await _dio.post<Map<String, dynamic>>('/threat/url', data: {'url': url});
    return ThreatEvent.fromJson(response.data!);
  }

  Future<ThreatEvent> checkQr(String qrPayload, {String? claimedMerchantName}) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/threat/qr',
      data: {
        'qr_payload': qrPayload,
        if (claimedMerchantName != null) 'claimed_merchant_name': claimedMerchantName,
      },
    );
    return ThreatEvent.fromJson(response.data!);
  }

  Future<List<ThreatEventSummary>> getEvents() async {
    final response = await _dio.get<List<dynamic>>('/threat/events');
    return (response.data ?? []).map((e) => ThreatEventSummary.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<ThreatEventDetail> getEvent(String threatId) async {
    final response = await _dio.get<Map<String, dynamic>>('/threat/events/$threatId');
    return ThreatEventDetail.fromJson(response.data!);
  }
}
