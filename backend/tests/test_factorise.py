
import unittest
import sympy as sp

from backend.app.rules.expand import parse_brackets
from backend.app.rules.factorise import solve_factorise


class FactoriseTests(unittest.TestCase):
    def check_factorisation(self, expression):
        result = solve_factorise(expression)
        original = sp.expand(
            parse_brackets(expression)
        )
        factorised = sp.expand(
            sp.sympify(result["answer"])
        )
        self.assertEqual(
            sp.simplify(original - factorised),
            0,
            msg=f"Incorrect factorisation: {expression}"
        )
        self.assertEqual(result["type"], "factorise")
        self.assertTrue(result["steps"])
        self.assertTrue(result["final_answer_latex"])
        return result
    def test_common_factor(self):
        result = self.check_factorisation("6x^2+9x")
        titles = [
            step["title"] for step in result["steps"]
        ]
        self.assertIn("factoriseStepGCF", titles)
        self.assertIn("factoriseStepFactorOut", titles)
    def test_difference_of_squares(self):
        result = self.check_factorisation("x^2-9")
        self.assertIn(
            "factoriseStepDifferenceSquares",
            [step["title"] for step in result["steps"]]
        )
    def test_quadratic_trinomial(self):
        result = self.check_factorisation("x^2+5x+6")
        self.assertIn(
            "factoriseStepFindPair",
            [step["title"] for step in result["steps"]]
        )
    def test_repeated_factor(self):
        self.check_factorisation("x^2+4x+4")
    def test_non_monic_quadratic(self):
        self.check_factorisation("2x^2+7x+3")
    def test_common_factor_and_squares(self):
        self.check_factorisation("3x^2-12")
    def test_multiple_variables(self):
        self.check_factorisation("4x^2-9y^2")
    def test_fraction_coefficients(self):
        self.check_factorisation("1/2x^2+3/2x")
    def test_negative_coefficients(self):
        self.check_factorisation("-6x^2+9x")
    def test_multiple_variable_common_factor(self):
        self.check_factorisation("3a^2b+6ab")
    def test_already_factorised(self):
        self.check_factorisation("(x+2)(x+3)")
    def test_irreducible_over_rationals(self):
        result = self.check_factorisation("x^2+1")
        self.assertIn(
            "factoriseStepNoFactors",
            [step["title"] for step in result["steps"]]
        )
    def test_cancellation(self):
        result = self.check_factorisation("x-x")
        self.assertEqual(result["answer"], "0")
    def test_invalid_expressions(self):
        invalid = [
            "1/(x+1)",
            "2x/0",
            "(x+1)^4",
            "x^2=9",
            "sqrt(9)"
        ]
        for expression in invalid:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve_factorise(expression)

if __name__ == "__main__":
    unittest.main()
