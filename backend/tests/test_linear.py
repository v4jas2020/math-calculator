import unittest

from backend.app.rules.linear import solve_linear

class LinearTests(unittest.TestCase):
    def check_solution(self, equation, expected):
        result = solve_linear(equation)
        self.assertEqual(result["solution_type"], "single")
        self.assertEqual(result["solution"], expected)
        self.assertTrue(result["steps"])
    def test_brackets(self):
        self.check_solution("3(2x-1)+5=20", "3")
    def test_variables_on_both_sides(self):
        self.check_solution("2x+5=x+9", "4")
    def test_fraction(self):
        self.check_solution("(x+1)/2=5", "9")
    def test_fractional_answer(self):
        self.check_solution("2x=1", "1/2")
    def test_different_letter(self):
        self.check_solution("3y-4=8", "4")
    def test_negative_solution(self):
        self.check_solution("-3a+5=11", "-2")
    def test_decimal_coefficient(self):
        self.check_solution("3.5t=7", "2")
    def test_infinitely_many_solutions(self):
        result = solve_linear("2(x+1)=2x+2")
        self.assertEqual(result["solution_type"], "infinite")
    def test_no_solution(self):
        result = solve_linear("2x+1=2x+4")
        self.assertEqual(result["solution_type"], "none")
    def test_rejects_quadratic(self):
        with self.assertRaises(ValueError):
            solve_linear("x^2+3x=4")
    def test_rejects_two_variables(self):
        with self.assertRaises(ValueError):
            solve_linear("x+y=3")
    def test_rejects_variable_denominator(self):
        with self.assertRaises(ValueError):
            solve_linear("1/(x+1)=2")
if __name__ == "__main__":
    unittest.main()