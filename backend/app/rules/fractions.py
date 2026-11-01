
import re
import ast
import sympy as sp
from fractions import Fraction
from math import gcd, lcm

PATTERN = re.compile(
    r"^\s*([+-]?\d+)\s*/\s*(\d+)\s*"
    r"([+\-*/])\s*([+-]?\d+)\s*/\s*(\d+)\s*$"
)

SYMBOLS = {
    "+": "+",
    "-": "-",
    "*": r"\cdot",
    "/": r"\div"
}


def fraction_latex(numerator, denominator, simplified=False):
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    if simplified and (numerator == 0 or denominator == 1):
        return str(numerator)

    return rf"\frac{{{numerator}}}{{{denominator}}}"


def solve_fractions(equation):
    if not isinstance(equation, str) or len(equation) > 160:
        raise ValueError("Enter two fractions and an operation.")

    match = PATTERN.fullmatch(equation)
    if not match:
        simple = re.sub(r"\(([+-]?\d+)\)", r"\1", equation)
        match = PATTERN.fullmatch(simple)

    if not match:
        return solve_fraction_expression(equation)

    first_n, first_d, operator, second_n, second_d = match.groups()

    if any(
        len(value.lstrip("+-")) > 12
        for value in (first_n, first_d, second_n, second_d)
    ):
        raise ValueError("Please use smaller integers.")

    a, b, c, d = (
        int(first_n),
        int(first_d),
        int(second_n),
        int(second_d)
    )

    if b == 0 or d == 0:
        raise ValueError("A denominator cannot be zero.")

    if operator == "/" and c == 0:
        raise ValueError("Cannot divide by zero.")

    steps = []

    def step(title, latex):
        steps.append({
            "title": title,
            "latex": latex
        })

    step(
        "fractionStepOriginal",
        rf"{fraction_latex(a, b)} "
        rf"{SYMBOLS[operator]} "
        rf"{fraction_latex(c, d)}"
    )

    if operator in ("+", "-"):
        common = lcm(b, d)

        left_scaled = a * (common // b)
        right_scaled = c * (common // d)

        if b != d:
            step(
                "fractionStepCommon",
                rf"\operatorname{{lcm}}({b},{d}) = {common}"
            )

            step(
                "fractionStepEquivalent",
                rf"{fraction_latex(a, b)} = "
                rf"{fraction_latex(left_scaled, common)},\quad "
                rf"{fraction_latex(c, d)} = "
                rf"{fraction_latex(right_scaled, common)}"
            )

        sign = "+" if operator == "+" else "-"
        formatted_right = (
            f"({right_scaled})"
            if right_scaled < 0
            else str(right_scaled)
        )

        raw_numerator = (
            left_scaled + right_scaled
            if operator == "+"
            else left_scaled - right_scaled
        )
        raw_denominator = common

        step(
            "fractionStepCombine",
            rf"\frac{{{left_scaled} {sign} {formatted_right}}}"
            rf"{{{common}}} = "
            rf"{fraction_latex(raw_numerator, common)}"
        )

    else:
        right_n, right_d = c, d

        if operator == "/":
            right_n = d if c > 0 else -d
            right_d = abs(c)

            step(
                "fractionStepReciprocal",
                rf"{fraction_latex(a, b)} \div "
                rf"{fraction_latex(c, d)} = "
                rf"{fraction_latex(a, b)} \cdot "
                rf"{fraction_latex(right_n, right_d)}"
            )

        raw_numerator = a * right_n
        raw_denominator = b * right_d

        step(
            "fractionStepMultiply",
            rf"\frac{{{a} \cdot {right_n}}}"
            rf"{{{b} \cdot {right_d}}} = "
            rf"{fraction_latex(raw_numerator, raw_denominator)}"
        )

    answer = Fraction(raw_numerator, raw_denominator)

    final_latex = fraction_latex(
        answer.numerator,
        answer.denominator,
        simplified=True
    )

    factor = gcd(abs(raw_numerator), raw_denominator)

    if factor > 1:
        step(
            "fractionStepSimplify",
            rf"{fraction_latex(raw_numerator, raw_denominator)} "
            rf"= {final_latex}"
        )

    return {
        "type": "fractions",
        "steps": steps,
        "answer": str(answer),
        "final_answer_latex": final_latex
    }


def solve_fraction_expression(equation):
    if not isinstance(equation, str) or len(equation) > 160:
        raise ValueError("Invalid mathematical expression.")

    source = equation.strip().replace("^", "**")

    if source.endswith("="):
        source = source[:-1]

    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError("Invalid mathematical expression.") from None

    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression is too complex.")

    steps = []

    def step(title, before, after):
        if before != after:
            steps.append({
                "title": title,
                "latex": rf"{before} = {after}"
            })

    def clean(value):
        value = sp.together(sp.radsimp(value))

        if sp.count_ops(value) > 80:
            raise ValueError("Expression is too complex.")

        return value

    def read(node, depth=0):
        if depth > 14:
            raise ValueError("Expression is too complex.")

        if isinstance(node, ast.Constant) and type(node.value) is int:
            if abs(node.value) > 10**9:
                raise ValueError("Please use smaller integers.")

            return sp.Integer(node.value)

        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            value = read(node.operand, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else -value

        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "sqrt"
            and len(node.args) == 1
            and not node.keywords
        ):
            arg = read(node.args[0], depth + 1)

            if arg.is_nonnegative is not True:
                raise ValueError(
                    "Square roots require a nonnegative value."
                )

            result = clean(sp.sqrt(arg))

            step(
                "fractionStepRoot",
                rf"\sqrt{{{sp.latex(arg)}}}",
                sp.latex(result)
            )
            return result

        if isinstance(node, ast.BinOp):
            left = read(node.left, depth + 1)
            right = read(node.right, depth + 1)

            lt = sp.latex(left)
            rt = sp.latex(right)

            if isinstance(node.op, (ast.Add, ast.Sub)):
                adding = isinstance(node.op, ast.Add)
                sign = "+" if adding else "-"
                title = (
                    "fractionStepAdd"
                    if adding else "fractionStepSubtract"
                )

                result = clean(
                    left + right if adding else left - right
                )

                if (
                    left.is_Rational
                    and right.is_Rational
                    and left.q != right.q
                ):
                    common = lcm(int(left.q), int(right.q))
                    first = int(left.p) * (common // int(left.q))
                    second = int(right.p) * (common // int(right.q))

                    step(
                        "fractionStepCommon",
                        rf"\operatorname{{lcm}}({left.q},{right.q})",
                        str(common)
                    )

                    step(
                        "fractionStepEquivalent",
                        rf"{lt} {sign} \left({rt}\right)",
                        rf"\frac{{{first}}}{{{common}}} "
                        rf"{sign} "
                        rf"\frac{{{second}}}{{{common}}}"
                    )

                    signed_second = (
                        f"({second})" if second < 0 else str(second)
                    )

                    step(
                        title,
                        rf"\frac{{{first} {sign} {signed_second}}}"
                        rf"{{{common}}}",
                        sp.latex(result)
                    )
                else:
                    step(
                        title,
                        rf"{lt} {sign} \left({rt}\right)",
                        sp.latex(result)
                    )

                return result

            if isinstance(node.op, ast.Mult):
                result = clean(left * right)

                step(
                    "fractionStepMultiply",
                    rf"\left({lt}\right)\cdot\left({rt}\right)",
                    sp.latex(result)
                )
                return result

            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("Cannot divide by zero.")

                result = clean(left / right)

                step(
                    "fractionStepDivide",
                    rf"\frac{{{lt}}}{{{rt}}}",
                    sp.latex(result)
                )
                return result

            if isinstance(node.op, ast.Pow):
                if not right.is_Integer or abs(right) > 8:
                    raise ValueError(
                        "Use an integer exponent between -8 and 8."
                    )

                if left == 0 and right <= 0:
                    raise ValueError(
                        "Zero cannot have a nonpositive exponent."
                    )

                if sp.count_ops(left) > 30:
                    raise ValueError("Expression is too complex.")

                if left.is_Rational and (abs(left.p).bit_length() > 256 or left.q.bit_length() > 256):
                    raise ValueError("Expression is too complex.")

                result = clean(left ** int(right))

                step(
                    "fractionStepPower",
                    rf"\left({lt}\right)^{{{rt}}}",
                    sp.latex(result)
                )
                return result

        raise ValueError("Invalid mathematical expression.")

    answer = clean(read(tree.body))

    return {
        "type": "fractions",
        "steps": steps,
        "answer": str(answer),
        "final_answer_latex": sp.latex(answer)
    }

