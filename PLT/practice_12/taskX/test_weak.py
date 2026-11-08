import unittest

from discount import discount


class WeakTests(unittest.TestCase):
    def test_calls_all_paths(self):
        with self.assertRaises(ValueError):
            discount(-1, False)
        for amount, member in [(0, False), (100, False), (200, True), (2000, True)]:
            discount(amount, member)


if __name__ == "__main__":
    unittest.main()
