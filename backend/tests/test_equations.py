import unittest

from app.rules.equations import parse_expression, solve_quadratic


class EquationRuleTests(unittest.TestCase):
    def test_parses_implicit_multiplication(self):
        self.assertEqual(
            parse_expression("2x(x+3)").expand(),
            (2 * parse_expression("x") * (parse_expression("x") + 3)).expand(),
        )

    def test_solves_two_real_roots(self):
        result = solve_quadratic("2x^2 - 5x + 2 = 0")

        self.assertEqual(result["coefficients"], {"a": "2", "b": "-5", "c": "2"})
        self.assertEqual(result["discriminant"], "9")
        self.assertEqual(result["roots"], ["1/2", "2"])

    def test_solves_incomplete_equation_with_a_double_root(self):
        result = solve_quadratic("x^2 + 2x + 1 = 0")

        self.assertEqual(result["roots"], ["-1"])
        self.assertEqual(result["final_answer_latex"], "x_1 = x_2 = -1")

    def test_rearranges_terms_from_both_sides(self):
        result = solve_quadratic("x^2 = 5x - 3")

        self.assertEqual(
            result["roots"], ["5/2 - sqrt(13)/2", "sqrt(13)/2 + 5/2"]
        )

    def test_reports_no_real_roots_for_a_negative_discriminant(self):
        result = solve_quadratic("x^2 + 1 = 0")

        self.assertEqual(result["discriminant"], "-4")
        self.assertEqual(result["roots"], [])
        self.assertEqual(result["final_answer_latex"], r"\text{No real roots}")

    def test_rejects_unsupported_power(self):
        with self.assertRaisesRegex(ValueError, "Only powers"):
            parse_expression("x^3")


if __name__ == "__main__":
    unittest.main()
