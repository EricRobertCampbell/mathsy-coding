# test_square.py
import unittest
from square import square


class TestSquare(unittest.TestCase):
    def test_correct_values(self):
        """ When applied to numbers, the result should be correct """
        self.assertEqual(square(1), 1)
