import unittest

from discount import discount


class DiscountTests(unittest.TestCase):
    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            discount(-1, False)

    def test_boundary_is_inclusive(self):
        self.assertEqual(discount(99, False), 0)
        self.assertEqual(discount(100, False), 10)
        self.assertEqual(discount(101, False), 10)

    def test_member_rate_and_integer_rounding(self):
        self.assertEqual(discount(105, True), 21)
        self.assertEqual(discount(105, False), 10)

    def test_zero_and_cap(self):
        self.assertEqual(discount(0, False), 0)
        self.assertEqual(discount(2499, True), 499)
        self.assertEqual(discount(2500, True), 500)
        self.assertEqual(discount(5000, True), 500)


if __name__ == "__main__":
    unittest.main()
