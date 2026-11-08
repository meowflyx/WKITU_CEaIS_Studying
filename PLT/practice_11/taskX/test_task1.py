import unittest

from task1 import SCENARIOS, partial_save_demo, process


class FailureTests(unittest.TestCase):
    def test_ten_injected_failures_match_contract(self):
        expected = [
            "STOP",
            "STOP",
            "STOP",
            "OK",
            "STOP",
            "STOP",
            "STOP",
            "STOP",
            "STOP",
            "PARTIAL",
        ]
        for scenario, status in zip(SCENARIOS, expected, strict=True):
            with self.subTest(scenario=scenario):
                result = process(scenario)
                self.assertEqual(result["status"], status)
                self.assertEqual(result["rows"], 2 if status != "STOP" else 0)

    def test_retry_limit_and_eventual_recovery(self):
        self.assertEqual(process("timeout_once")["attempts"], 2)
        self.assertEqual(process("timeout_always")["attempts"], 3)

    def test_partial_commit_is_detected_and_transaction_rolls_back(self):
        self.assertEqual(partial_save_demo(), (1, 3, 0))

    def test_success_and_notification_degradation(self):
        self.assertEqual(process("normal")["status"], "OK")
        self.assertIn("notification", process("notify")["message"])


if __name__ == "__main__":
    unittest.main()
