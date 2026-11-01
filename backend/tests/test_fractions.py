
import unittest

from backend.app.rules.fractions import solve_fractions


class FractionTests(unittest.TestCase):

    def test_addition(self):
        result = solve_fractions("1/2+3/4")
        self.assertEqual(result["answer"], "5/4")

    def test_subtraction(self):
        result = solve_fractions("2/3-1/6")
        self.assertEqual(result["answer"], "1/2")

    def test_multiplication(self):
        result = solve_fractions("2/3*9/4")
        self.assertEqual(result["answer"], "3/2")

    def test_division(self):
        result = solve_fractions("5/6/10/3")
        self.assertEqual(result["answer"], "1/4")

    def test_negative_fractions(self):
        result = solve_fractions("-1/2+-3/4")
        self.assertEqual(result["answer"], "-5/4")

    def test_whole_number_answer(self):
        result = solve_fractions("1/2+1/2")
        self.assertEqual(result["answer"], "1")

    def test_zero_denominator(self):
        with self.assertRaisesRegex(ValueError, "denominator"):
            solve_fractions("1/0+3/4")

    def test_division_by_zero(self):
        with self.assertRaisesRegex(ValueError, "divide by zero"):
            solve_fractions("1/2/0/3")


if __name__ == "__main__":
    unittest.main()
