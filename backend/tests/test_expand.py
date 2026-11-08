import unittest

from backend.app.rules.expand import solve_expand


class ExpandTests(unittest.TestCase):
    def check_answer(self, expression, expected):
        result = solve_expand(expression)
        self.assertEqual(result["answer"], expected)
        self.assertEqual(result["steps"][0]["title"], "expandStepOriginal")
        self.assertTrue(result["final_answer_latex"])

    def test_single_brackets(self):
        self.check_answer("3(2x-1)+5", "6*x + 2")

    def test_two_brackets(self):
        self.check_answer("(x+2)(x-3)", "x**2 - x - 6")

    def test_square(self):
        self.check_answer("(2x+1)^2", "4*x**2 + 4*x + 1")

    def test_cube(self):
        self.check_answer("(x+1)^3", "x**3 + 3*x**2 + 3*x + 1")

    def test_negative(self):
        self.check_answer("-2(x-4)", "8 - 2*x")

    def test_fraction(self):
        self.check_answer("1/2(x+2)", "x/2 + 1")

    def test_multiple_variables(self):
        self.check_answer("(a+b)(a-b)", "a**2 - b**2")

    def test_three_brackets(self):
        self.check_answer("(x+1)(x+2)(x+3)", "x**3 + 6*x**2 + 11*x + 6")

    def test_invalid(self):
        for expression in ("2(x+1)/0", "1/(x+1)", "(x+1)^4", "2(x+1)=6"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve_expand(expression)


if __name__ == "__main__":
    unittest.main()
