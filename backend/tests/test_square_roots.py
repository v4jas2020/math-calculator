import unittest
from backend.app.rules.square_roots import solve_square_roots
class SquareRootTests(unittest.TestCase):
    def check_answer(self, expression, expected):
        result = solve_square_roots(expression)
        self.assertEqual(result["type"], "square_roots")
        self.assertEqual(result["answer"], expected)
        self.assertTrue(result["steps"])
        self.assertEqual(
            result["steps"][0]["title"],
            "squareRootStepOriginal"
        )
    def test_simplify_72(self):
        self.check_answer("sqrt(72)", "6*sqrt(2)")
    def test_simplify_50(self):
        self.check_answer("sqrt(50)", "5*sqrt(2)")
    def test_simplify98(self):
        self.check_answer("sqrt(98)", "7*sqrt(2)")
    def test_perfect_square(self):
        self.check_answer("sqrt(144)", "12")
    def test_prime_number(self):
        self.check_answer("sqrt(7)", "sqrt(7)")
    def test_zero(self):
        self.check_answer("sqrt(0)", "0")
    def test_one(self):
        self.check_answer("sqrt(1)", "1")
    def test_coefficient(self):
        self.check_answer("3*sqrt(12)", "6*sqrt(3)")
    def test_negative_coefficient(self):
        self.check_answer("-2*sqrt(18)", "-6*sqrt(2)")
    def test_negative_root(self):
        self.check_answer("-sqrt(4)", "-2")
    def test_invalid_expressions(self):
        invalid = (
            "sqrt(-4)",
            "sqrt(4+5)",
            "sqrt(4)+sqrt(9)",
            "sqrt(1.5)",
            "sqrt(1000000001)",
            "sqrt(x)",
            ""
        )
        for expression in invalid:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve_square_roots(expression)
if __name__ == "__main__":
    unittest.main()