import 'package:decimal/decimal.dart';
import 'package:finsentinel/core/models/obligation.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('"18000.55" round-trips exactly through Obligation, never becomes a double', () {
    final json = {
      'obligation_id': 'abc-123',
      'label': 'Rent',
      'amount': '18000.55',
      'due_date': '2026-10-01',
      'category': 'rent',
      'is_fixed': true,
      'is_paid': false,
      'confidence_score': 0.9,
    };

    final obligation = Obligation.fromJson(json);

    expect(obligation.amount, Decimal.parse('18000.55'));
    expect(obligation.amount.toString(), '18000.55');

    final reEncoded = obligation.toJson();
    expect(reEncoded['amount'], '18000.55');
    expect(reEncoded['amount'], isA<String>(), reason: 'the wire format is a JSON string, never a JSON number');
  });

  test('Decimal arithmetic avoids the classic binary-float precision trap', () {
    // 0.1 + 0.2 != 0.3 in IEEE-754 double precision, but IS exact here --
    // this is the entire reason this app parses money as Decimal.
    final sum = Decimal.parse('0.1') + Decimal.parse('0.2');
    expect(sum, Decimal.parse('0.3'));
    expect(0.1 + 0.2 == 0.3, isFalse, reason: 'sanity check that the double trap is real in this Dart runtime');
  });
}
