from decimal import Decimal

from app.models import NotifyTriggerClauseEnum
from app.tasks_notifications import is_triggered
from suite.test.testcases import SimpleTestCase


class IsTriggeredTest(SimpleTestCase):
    def test_more(self):
        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.more,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("100"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.more,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("101"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.more,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("99"),
            )
        )

    def test_less(self):
        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.less,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("99"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.less,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("100"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.less,
                trigger_value=Decimal("0"),
                last_notification_rate=Decimal("100"),
                current_rate=Decimal("101"),
            )
        )

    def test_diff(self):
        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("101"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("100"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("79"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("80"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("81"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.diff,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("99"),
            )
        )

    def test_percent(self):
        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("99"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("100"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("81"),
            )
        )

        self.assertTrue(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("80"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("82"),
            )
        )

        self.assertFalse(
            is_triggered(
                trigger_clause=NotifyTriggerClauseEnum.percent,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("98"),
            )
        )

    def test_unknown_clause(self):
        with self.assertRaises(ValueError):
            is_triggered(
                trigger_clause=None,
                trigger_value=Decimal("10"),
                last_notification_rate=Decimal("90"),
                current_rate=Decimal("99"),
            )
