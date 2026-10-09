import 'package:decimal/decimal.dart';
import 'package:finsentinel/core/widgets/confidence_indicator.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  Widget wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

  group('ConfidenceIndicator renders differently per tier', () {
    testWidgets('0.9 (high): solid, no tooltip, no warning icon', (tester) async {
      await tester.pumpWidget(wrap(const ConfidenceIndicator(confidence: 0.9, child: Text('₹31,800'))));
      expect(find.text('₹31,800'), findsOneWidget);
      expect(find.byType(Tooltip), findsNothing);
      expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);
      expect(find.byType(Opacity), findsNothing);
    });

    testWidgets('0.6 (medium): subtle marker + tooltip, no warning icon', (tester) async {
      await tester.pumpWidget(wrap(const ConfidenceIndicator(confidence: 0.6, child: Text('₹31,800'))));
      expect(find.text('₹31,800'), findsOneWidget);

      final tooltipFinder = find.byType(Tooltip);
      expect(tooltipFinder, findsOneWidget);
      final tooltip = tester.widget<Tooltip>(tooltipFinder);
      expect(tooltip.message, contains('partly unconfirmed'));

      expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);

      final opacityWidget = tester.widget<Opacity>(find.byType(Opacity));
      expect(opacityWidget.opacity, 0.85);
    });

    testWidgets('0.3 (low): visibly muted + warning icon + explanatory tooltip', (tester) async {
      await tester.pumpWidget(wrap(const ConfidenceIndicator(confidence: 0.3, child: Text('₹31,800'))));
      expect(find.text('₹31,800'), findsOneWidget);
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);

      final tooltipFinder = find.byType(Tooltip);
      expect(tooltipFinder, findsOneWidget);
      final tooltip = tester.widget<Tooltip>(tooltipFinder);
      expect(tooltip.message, isNotEmpty);

      final opacityWidget = tester.widget<Opacity>(find.byType(Opacity));
      expect(opacityWidget.opacity, 0.6);
    });
  });

  testWidgets('SimulatedDataBadge appears when rendered and is not dismissible', (tester) async {
    await tester.pumpWidget(wrap(const SimulatedDataBadge()));
    expect(find.text('DEMO DATA'), findsOneWidget);
    // No dismiss affordance of any kind (no Dismissible, no close button).
    expect(find.byType(Dismissible), findsNothing);
    expect(find.byIcon(Icons.close), findsNothing);
  });

  testWidgets('UncertainAmount formats the same value differently per confidence tier', (tester) async {
    final amount = Decimal.parse('31800');

    await tester.pumpWidget(wrap(UncertainAmount(amount: amount, confidence: 0.9)));
    expect(find.textContaining('₹31,800'), findsOneWidget);
    expect(find.textContaining('~'), findsNothing);
    expect(find.textContaining('unconfirmed'), findsNothing);

    await tester.pumpWidget(wrap(UncertainAmount(amount: amount, confidence: 0.6)));
    expect(find.textContaining('~₹31,800'), findsOneWidget);

    await tester.pumpWidget(wrap(UncertainAmount(amount: amount, confidence: 0.3)));
    expect(find.textContaining('(unconfirmed)'), findsOneWidget);
  });
}
