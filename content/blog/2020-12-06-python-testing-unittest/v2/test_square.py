# test_square.py
import unittest
from square import square


class TestSquare(unittest.TestCase):
    def test_correct_values(self):
        """ When applied to numbers, the result should be correct """

        # integers

        self.assertEqual(square(0), 0, f"Expected 0^2 to be zero!")
        self.assertEqual(square(1), 1, "Expected 1^1 to be 1")
        self.assertEqual(square(2), 4, "Expected 2^2 to be 4")
        self.assertEqual(square(-2), 4, "Expected (-2)^2 to be 4")

        # decimals
        self.assertEqual(square(1.5), 2.25, f"Expected 1.5^2 to be 2.25")
        self.assertEqual(square(-1.5), 2.25, f"Expected 1.5^2 to be 2.25")

    def test_non_numbers(self):
        """When the argument is not a number, it should raise a TypeError"""
        with self.assertRaises(TypeError):
            square("12")
        with self.assertRaises(TypeError):
            square([1, 2, 3])
        with self.assertRaises(TypeError):
            square({"this": "will not work"})
