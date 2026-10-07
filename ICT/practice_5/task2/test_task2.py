import unittest

from task2 import orbital_period, orbital_speed, time_seconds


class CalculationTests(unittest.TestCase):
    def test_iss_period(self):
        self.assertAlmostEqual(orbital_period(420.5) / 60, 92.8343, places=4)

    def test_iridium_period(self):
        self.assertAlmostEqual(orbital_period(777.5) / 60, 100.2495, places=4)

    def test_iss_speed(self):
        self.assertAlmostEqual(orbital_speed(420.5), 7.6610, places=4)

    def test_iridium_speed(self):
        self.assertAlmostEqual(orbital_speed(777.5), 7.4673, places=4)

    def test_first_iss_pass(self):
        self.assertEqual(
            time_seconds("10:19:24") - time_seconds("10:13:46"), 338
        )

    def test_first_iridium_pass(self):
        self.assertEqual(
            time_seconds("03:11:29") - time_seconds("03:01:15"), 614
        )

    def test_midnight(self):
        self.assertEqual(time_seconds("00:00:00"), 0)

    def test_last_second(self):
        self.assertEqual(time_seconds("23:59:59"), 86399)


if __name__ == "__main__":
    unittest.main()
