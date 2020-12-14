import unittest

from add import add


class TestAdd(unittest.TestCase):
    def test_returns_number(self):
        """Should return a number"""
        self.assertIsInstance(add(1, 2), (int, float), "Didn't return a number!")

    def test_works_with_ints(self):
        """Should correctly add integers"""
        self.assertEqual(add(1, 2), 3, "NOOO!")
        self.assertEqual(add(-2, 2), 0)
        self.assertEqual(add(-5, 100), 95, f":(")

    def test_works_with_floats(self):
        """Should correctly add floats"""
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)
        self.assertAlmostEqual(add(-0.2, 0.2), 0)

    def test_errors_on_non_numbers(self):
        """When fed a non-number, it should raise a TypeError"""
        bad_values = [["1", "2"], ["1", 2], [[], []], [{"hello": 3}, 5]]
        for first, second in bad_values:
            with self.assertRaises(TypeError):
                add(first, second)
