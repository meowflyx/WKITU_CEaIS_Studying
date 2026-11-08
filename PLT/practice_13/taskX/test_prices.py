import unittest

from prices import discounted_price


class PriceTests(unittest.TestCase):
    def test_regular_and_full_discount(self) -> None:
        self.assertEqual(discounted_price(123, 0), 123)
        self.assertEqual(discounted_price(123, 100), 0)

    def test_half_is_rounded_up(self) -> None:
        self.assertEqual(discounted_price(101, 50), 51)
        self.assertEqual(discounted_price(105, 10), 95)

    def test_invalid_arguments_are_rejected(self) -> None:
        for amount, percent in [(-1, 10), (100, -1), (100, 101)]:
            with self.subTest(amount=amount, percent=percent):
                with self.assertRaises(ValueError):
                    discounted_price(amount, percent)

    def test_zero_amount_and_large_integer(self) -> None:
        self.assertEqual(discounted_price(0, 30), 0)
        self.assertEqual(discounted_price(10**20 + 1, 0), 10**20 + 1)


if __name__ == "__main__":
    unittest.main()
