import unittest
from pickletools import read_uint1

from backend.app.rules.add_subtract import solve_add_subtract
class AddSubtractTests(unittest.TestCase):
    def check_answer(self, expression, expected):
        result = solve_add_subtract(expression)

        self.assertEqual(result["type"], "add_subtract")
        self.assertEqual(result["answer"], expected)
        self.assertTrue(result["steps"])
        self.assertEqual(
            result["steps"][0]["title"],
            "addSubtractStepOriginal"
        )
    def test_add_polynomials(self):
        self.check_answer(
            "(3x^2+5x-2)+(2x^2-3x+7)",
            "5*x**2 + 2*x + 5"
        )
    def test_subtract_polynomials(self):
        self.check_answer(
            "(5x^2+3x-4)-(2x^2-x+6)",
            "3*x**2 + 4*x - 10"
        )
    def test_multiple_variables(self):
        self.check_answer(
            "(3a-2b)+(5a+4b)",
            "8*a + 2*b"
        )
    def test_subtraction_and_cancellation(self):
        self.check_answer("(x+2)-(x+3)", "-1")
        self.check_answer("(x-x)+(y-y)", "0")
    def test_distribute_coefficients(self):
        self.check_answer(
            "2(x+3)-3(x-1)",
            "9 - x"
        )
    def test_fractional_coefficients(self):
        self.check_answer(
            "1/2x+3/4x",
            "5*x/4"
        )
    def test_square_brackets(self):
        self.check_answer(
            "(x+1)^2-(x-1)^2",
            "4*x"
        )
    def test_explanations_present(self):
        result = solve_add_subtract("(x+2)-(x+3)")
        titles = [
            step["title"]
            for step in result["steps"]
        ]
        self.assertIn("addSubtractStepRemove", titles)
        self.assertIn("addSubtractStepGroup", titles)
        self.assertIn("addSubtractStepResult", titles)
    def test_invalid_input(self):
        for expression in (
            "x+1=4",
            "1/(x+1)",
            "(x+1)^4",
            "2x/0",
            "sqrt(9)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve_add_subtract(expression)
if __name__ == "__main__":
    unittest.main()