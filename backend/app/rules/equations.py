import ast
import operator
import re

import sympy as sp
from sympy.integrals.manualintegrate import parts_rule

X = sp.Symbol("x")
TOKENS = re.compile(r"\d+(?:\.\d+)?|x|[()+\-*/^]")
ALLOWED_POWERS = (sp.Integer(0), sp.Integer(1), sp.Integer(2))


def parse_expression(text, preserve=False):
    if not isinstance(text, str):
        raise ValueError("Enter a valid expression")

    source = (
        text.lower()
        .replace(" ", "")
        .replace("²", "^2")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
    )
    if not source or len(source) > 150:
        raise ValueError("Enter a shorter, valid equation")

    tokens = TOKENS.findall(source)
    if "".join(tokens) != source:
        raise ValueError("Unsupported characters")

    output = []
    for index, token in enumerate(tokens):
        if index and _ends_term(tokens[index - 1]) and _starts_term(token):
            output.append("*")
        output.append("**" if token == "^" else token)

    try:
        tree = ast.parse("".join(output), mode="eval")
    except SyntaxError:
        raise ValueError("Invalid syntax") from None

    def read(node):
        if isinstance(node, ast.Expression):
            return read(node.body)
        if isinstance(node, ast.Name) and node.id == "x":
            return X
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return sp.Rational(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = read(node.operand)
            if isinstance(node.op, ast.UAdd):
                return value
            if preserve:
                return sp.Mul(-1, value, evaluate=False)
            return -value
        if isinstance(node, ast.BinOp):
            left = read(node.left)
            right = read(node.right)

            if isinstance(node.op, ast.Add):
                if preserve:
                    return sp.Add(left, right, evaluate=False)
                return left + right
            if isinstance(node.op, ast.Sub):
                if preserve:
                    return sp.Add(
                        left,
                        sp.Mul(-1, right, evaluate=False),
                        evaluate=False
                    )
                return left - right
            if isinstance(node.op, ast.Mult):
                if preserve:
                    return sp.Mul(left, right, evaluate=False)
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0 or right.has(X):
                    raise ValueError("Division must not be by zero or contain x")
                if preserve:
                    return sp.Mul(
                        left,
                        sp.Pow(right, -1, evaluate=False),
                        evaluate=False
                    )
                return left / right
            if isinstance(node.op, ast.Pow):
                if right not in ALLOWED_POWERS:
                    raise ValueError(
                        "Only powers 0, 1 and 2 are allowed for quadratic equations."
                    )
                if preserve:
                    return sp.Pow(left, int(right), evaluate=False)
                return left ** int(right)

        raise ValueError("Unsupported operation/expression")

    expression = read(tree)
    return expression if preserve else sp.expand(expression)

def distribute_once(expr):
    if expr.is_Add:
        parts = [distribute_once(term) for term in expr.args]
        return sp.Add(*parts, evaluate=False)
    if expr.is_Pow and expr.exp == 2 and expr.base.is.Add:
        return sp.Mul(expr.base, expr.base, evaluate=False)
    if expr.is_Mul:
        factors = list(expr.args)
        for index, factor in enumerate(factors):
            if factor.is_Add:
                terms = []
                for term in factor.args:
                    new_factors = (
                        factors[:index]
                        + [term]
                        + factors[index + 1:]
                    )
                    terms.append(
                        sp.Mul(*new_factors, evaluate=False)
                    )
                    return sp.Add(*terms, evaluate=False)
                return expr
def solve_quadratic(equation):

    if not isinstance(equation, str) or equation.count("=") != 1:
        raise ValueError("Use one equals sign, for example x^2-10x+20=0")

    lhs_text, rhs_text = equation.split("=")
    lhs = parse_expression(lhs_text)
    rhs = parse_expression(rhs_text)
    difference = sp.expand(lhs - rhs)

    try:
        polynomial = sp.Poly(difference, X)
    except sp.PolynomialError:
        raise ValueError("Enter a polynomial expression") from None

    if polynomial.degree() != 2:
        raise ValueError("The coefficient of x² must be nonzero.")

    a, b, c = polynomial.all_coeffs()
    steps = []
    tex = sp.latex

    def step(title, latex, explanation=""):
        steps.append(
            {"title": title, "latex": latex, "explanation": explanation}
        )

    step("Original equation", rf"{tex(lhs)} = {tex(rhs)}")
    lhs_work = parse_expression(lhs_text, preserve=True)
    rhs_work = parse_expression(rhs_text, preserve=True)

    for _ in range(6)
        next_lhs = distribute_once(lhs_work)
        next_rhs = distribute_once(rhs_work)

        if next_lhs == lhs_work and next_rhs == rhs_work:
            break
        step(
            "Expand brackets",
            rf"{tex(next_lhs, mul_symbol='dot')} = "
            rf"{tex(next_rhs, mul_symbol='dot')}"
        )

        lhs_work = next_lhs
        rhs_work = next_lhs
    if rhs != 0:
        step(
            "Move all terms to the left",
            rf"{tex(lhs)} - \left({tex(rhs)}\right) = 0",
            "Subtract the entire right-hand side from both sides.",
        )
    step(
        "Collect and reorder terms",
        rf"{tex(difference)} = 0",

    )
    step("Standard form", r"ax^2 + bx + c = 0")
    step(
        "Insert all coefficients",
        _coefficient_form(a, b, c, tex),

    )
    step(
        "Identify coefficients",
        rf"a = {tex(a)},\quad b = {tex(b)},\quad c = {tex(c)}",
    )

    kind = "incomplete" if b == 0 or c == 0 else "full"
    step("Discriminant formula", r"D = b^2 - 4ac")
    step(
        "Substitute a, b and c",
        rf"D = \left({tex(b)}\right)^2 - 4\cdot\left({tex(a)}\right)"
        rf"\cdot\left({tex(c)}\right)",
    )
    b_squared = sp.expand(b**2)
    product = sp.expand(4 * a * c)
    step("Square and multiply", rf"D = {tex(b_squared)} - \left({tex(product)}\right)")
    discriminant = sp.expand(b_squared - product)
    step("Discriminant result", rf"D = {tex(discriminant)}")

    result = {
        "type": kind,
        "coefficients": {"a": str(a), "b": str(b), "c": str(c)},
        "discriminant": str(discriminant),
        "steps": steps,
    }
    if discriminant < 0:
        step(
            "Interpret the discriminant",
            rf"D = {tex(discriminant)} < 0",
            "A negative discriminant has no real roots.",
        )
        return {**result, "roots": [], "final_answer_latex": r"\text{No real roots}"}

    sqrt_discriminant = sp.sqrt(discriminant)
    if sqrt_discriminant.is_Rational:
        step(
            "Recognise the square",
            rf"{tex(discriminant)} = \left({tex(sqrt_discriminant)}\right)^2",
        )
    step(
        "Take the exact square root",
        rf"\sqrt{{D}} = \sqrt{{{tex(discriminant)}}} = {tex(sqrt_discriminant)}",

    )

    denominator = sp.expand(2 * a)
    roots = []
    for number, sign in enumerate((-1, 1), start=1):
        operator = "-" if sign == -1 else "+"

        step(
            f"Root {number}: formula",
            rf"x_{number} = "
            rf"\frac{{-b {operator} \sqrt{{D}}}}{{2a}}"
        )

        step(
            f"Root {number}: substitute values",
            rf"x_{number} = "
            rf"\frac{{-\left({tex(b)}\right) {operator} "
            rf"\sqrt{{{tex(discriminant)}}}}}"
            rf"{{2\cdot\left({tex(a)}\right)}}"
        )

        step(
            f"Root {number}: evaluate signs and denominator",
            rf"x_{number} = "
            rf"\frac{{{tex(-b)} {operator}"
            rf"{tex(sqrt_discriminant)}}}"
            rf"{{{tex(denominator)}}}"
        )
        numerator = sp.expand(-b + sign * sqrt_discriminant)

        step(
            f"Root {number}: simplify numerator",
            rf"x_{number} = "
            rf"\frac{{{tex(numerator)}}}"
            rf"{{{tex(denominator)}}}"
        )

        root = sp.cancel(numerator / denominator)

        if not any(
                sp.simplify(root - existing) == 0
                for existing in roots
        ):
            roots.append(root)

        step(
            f"Root {number}: exact answer",
            rf"x_{number} = {tex(sp.together(root))}",

        )

    if discriminant == 0:
        final = rf"x_1 = x_2 = {tex(sp.together(roots[0]))}"
    else:
        final = (
            rf"x_1 = {tex(sp.together(roots[0]))},\quad "
            rf"x_2 = {tex(sp.together(roots[1]))}"
        )
    step("Final answer", final)
    return {**result, "roots": [str(root) for root in roots], "final_answer_latex": final}


def _ends_term(token):
    return token == "x" or token == ")" or token[0].isdigit()


def _starts_term(token):
    return token == "x" or token == "(" or token[0].isdigit()


def _coefficient_form(a, b, c, tex):
    def signed(value):
        return "+" if value >= 0 else "-", tex(abs(value))

    b_sign, b_value = signed(b)
    c_sign, c_value = signed(c)
    return rf"{tex(a)}x^2 {b_sign} {b_value}x {c_sign} {c_value} = 0"
