import unittest
from backend.app.rules.powers import solve_powers
class PowersTests(unittest.TestCase):
    def check_answer(self, expression, expected):
        result = solve_powers(expression)
        self.assertEqual(result["type"], "powers")
        self.assertEqual(result["answer"], expected)
        self.assertTrue(result["steps"])
        self.assertEqual(
            result["steps"][0]["title"],
           "powersStepOriginal"
        )
    def test_product_of_powers(self):
        self.check_answer("2^3*2^4", "128")
    def test_quotient_of_powers(self):
        self.check_answer("x^7/x^3", "x**4")
    def test_power_of_power(self):
        self.check_answer("(x^2)^3", "x**6")
    def test_power_of_product(self):
        self.check_answer("(3*x^2)^3", "27*x**6")
    def test_negative_exponent(self):
        self.check_answer("5^-2", "1/25")
    def test_symbolic_negative_exponent(self):
        self.check_answer("x^3/x^5", "x**(-2)")
    def test_zero_exponent(self):
        self.check_answer("x^0", "1")
    def test_negative_base(self):
        self.check_answer("(-2)^4", "16")
    def test_order_of_operations(self):
        self.check_answer("-2^2", "-4")
    def test_addition_of_powers(self):
        self.check_answer("2^3+3^2", "17")
    def test_zero_to_negative_power(self):
        with self.assertRaises(ValueError):
            solve_powers("0^-2")
    def test_zero_to_zero(self):
        with self.assertRaises(ValueError):
            solve_powers("0^0")
    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            solve_powers("2/(2-2)")
    def test_unsupported_exponent(self):
        with self.assertRaises(ValueError):
            solve_powers("2^13")
    def test_unsupported_function(self):
        with self.assertRaises(ValueError):
            solve_powers("sqrt(4)")
if __name__ == "__main__":
    unittest.main()