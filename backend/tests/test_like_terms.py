import unittest
from backend.app.rules.like_terms import solve_like_terms
class LikeTermsTests(unittest.TestCase):
    def check_answer(self, expression, expected):
        result = solve_like_terms(expression)
        self.assertEqual(result["answer"], expected)
        self.assertTrue(result["steps"])
    def test_basic(self):
        self.check_answer(
            "4x^2+3x-2x^2+5x-7",
            "2*x**2 + 8*x - 7"
        )

    def test_multiple_variables(self):
        self.check_answer(
            "3x+5x-2y+7-4x",
            "4*x - 2*y + 7"
        )

    def test_fractions(self):
        self.check_answer("1/2x+3/4x", "5*x/4")
    def test_cancellation(self):
        self.check_answer("x-x", "0")
    def test_reject_brackets(self):
        with self.assertRaises(ValueError):
            solve_like_terms("2(x+1)")
    def test_reject_equations(self):
        with self.assertRaises(ValueError):
            solve_like_terms("2x+3=7")
if __name__ == "__main__":
    unittest.main()