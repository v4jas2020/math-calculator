import ast
import re

import sympy as sp

X = sp.Symbol("x")
TOKENS = re.compile(r"\d+(?:\.\d+)?|x|[()+\-*/^]")

def parse_expression(text):
    """Parse basic algebra safely without executing Python code."""
    source = (
        text.lower()
        .replace(" ", "")
        .replace("²", "^2")
        .replace("-", "-")
        .replace("x", "*")
        .replace("÷", "/")
    )
    if not source or len(source) > 150:
        raise ValueError("Enter a shorter, valid equation")

    tokens = TOKENS.findall(source)
    if "".join(tokens) != source:
        raise ValueError("Unsupported characters")
    output = []

    for index, token in enumerate(tokens):
        if index:
            previous = tokens[index - 1]
            ends_term = (
                previous == "x"
                or previous == ")"
                or (
                token[0].isdigit()
                and previous in ("x", ")")
                )
            )
            if ends_term and starts_term:
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
        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return sp.Rational(str(node.value))
            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, (ast.Usub, ast.UAdd)):
                    value = read(node.operand)
                    if isinstance(node.op, ast.USub):
                        return -value
                    return value
                if isinstance(node, ast.BinOp):
                    a = read(node.left)
                    b = read(node.right)

                    if isinstance(node.op, ast.Add):
                        return a + b
                    if isinstance(node.op, ast.Sub):
                        return a - b
                    if isinstance(node.op, ast.Mult):
                        return a * b
                    if isinstance(node.op, ast.Div):
                        if b == 0 or b.has(X):
                            raise ValueError(
                                   "Division must not be by zero"
                            )
                        return a / b
                    if isinstance(node.op, ast.Pow):
                        if b not in (0, 1, 2):
                            raise ValueError(
                                "Only powers 0, 1 and 2 are allowed for quadratic equations."
                            )
                        return a ** int(b)
                    raise ValueError("Unsupported operation/expression")
                return sp.expand(read(tree))

            def solve_quadratic(equation):
                if equation.count("=") != 1:
                    raise ValueError(
                        "Use one equals sign, for example x^2-10x+20=0"
                    )
                lhs_text, rhs_text = equation.split("=")
                lhs = parse_expression(lhs_text)
                rhs = parse_expression(rhs_text)
                difference = sp.expand(lhs - rhs)

                try:
                    poly = sp.Poly(difference, X)
                except sp.PolynomialError:
                    raise ValueError(
                        "Enter a polynomial expression"
                    ) from None
                if poly.degree() != 2:
                    raise ValueError(
                        "The coefficient of x² must be nonzero."
                    )
                a, b, c = poly.all_coeffs()
                steps = []
                tex = sp.latex

                def step(title, expression, explanation=""):
                    steps.append({
                        "title": title,
                        "lates": expression,
                        "explanation": explanation,
                    })
                step(
                    "Original equation",
                    rf"{tex(lhs)} = {tex(rhs)}"
                )
                if rhs != 0:
                    step(
                        "Move all terms to the left",
                        rf"{tex(lhs)} - \left({tex(rhs)}\right) = 0",
                        "Subtract the entire right-hand side from both sides."
                    )

                    step(
                        "Collect and reorder terms",
                        rf"{tex(difference)} = 0",
                        "Write the x² term first, then x, then constant."
                    )

                    step(
                        "Standart form",
                        r"ax^2 + bx + c = 0",
                    )

                    def signed(value):
                        return (
                            "+" if value > 0 else "-"
                            tex(abs(value))
                        )

                        bs, bt = signed(b)
                        cs, ct = signed(c)
                    step(
                        "Insert all coefficients",
                    rf"{tex(a)}x^2 {bs} {bt}x {cs} {ct} = 0",
                    "Keep zero coefficients visible for incomplete equations."
                    )
                    step(
                        "Identify coefficients",
                        rf"a = {tex(a)},\quad "
                        rf"b = {tex(b)},\quad "
                        rf"c = {tex(c)}"
                    )

                    if b == 0 or c == 0:
                        kind = "incomplete"
                    else:
                        kind = "full"

                    step(
                        "Discriminant formula",
                        r"D = b^2 - 4ac"
                    )
                    step(
                        "Substitute a, b and c",
                        rf"D = \left({tex(b)}\right)^2"
                        rf"- 4\cdot\left({tex(a)}\right"
                        rf"\cdot\left({tex(c)}\right"
                    )
                    b_squared = sp.expand(b ** 2)
                    product = sp.expand(4 * a * c)

                    step(
                        "Sqaure and multiply",
                        rf"D = {tex(b_squared)} - "
                        rf"\left({tex(product)}\right)"
                    )
                    d = sp.expand(b_squared - product)
                    step(
                        "Discriminant result",
                        rf"D = {tex(d)}"
                    )
                    if d < 0:
                        step(
                            "Interpret the discriminant",
                            rf"D = {tex(d)} < 0",
                            "A negative discriminant does not have a solution since there are no real numbers that you can sqaure and get a negative number."
                        )
                        return {
                            "type": kind,
                            "coefficients": {
                                "a": str(a),
                                "b": str(b),
                                "c": str(c),
                            },
                            "discriminant": str(d),
                            "steps": steps,
                            "roots": [],
                            "final_answer_latex": r"\text{No real roots}"
                        }

                    sqrt_d = sp.sqrt(d)
                    if sqrt_d.is_Rational:
                        step(
                            "Recognise the sqaure",
                            rf"{tex(d)} ="
                            rf"\left(tex({sqrt_d}\right)^2"
                        )
                    step(
                        "Take the exact square root",
                        rf"\sqrt{{D}} = "
                        rf"\sqrt{{{tex(sqrt_d)}}} = {tex(sqrt_d)}",
                        "Leave imperfect roots as radicals never round decimals."
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
                            f"Root {number}: evaluate signs",
                            rf"x_{number} = "
                            rf"\frac{{{tex(-b)} {operator} {tex(sqrt_d)}}}"
                            rf"{{{tex(denominator)}}}"
                        )
                        numerator = sp.expand(-b + sign * sqrt_d)
                        step(
                            f"Root {number} = "
                            rf"x_{number} = "
                            rf"\frac{{{tex(numerator)}}}"
                            rf"{{{tex(denominator)}}}"
                        )
                        root = sp.cancel(numerator / denominator)
                        if root.has(sp.sqrt(d)) and d != 0:
                            root = sp.together(root)
                        roots.append(root)
                        step(
                            f"Root {number}: exact answer"
                            rf"x {number} = {tex(root)}",
                            "Keep the exact fractions and radicals."
                        )

                        if d == 0
                            final = rf"x_1 = x_2 = {tex(roots[0])}"
                        else:
                            final = (
                                rf"x_1 = {tex(roots[0])}, \quad "
                                rf"x_2 = {tex(roots[1])}"
                            )
                        step(
                            "Final answer",
                            final
                        )
                        return {
                            "type": kind,
                            "coefficients": {
                                "a": str(a),
                                "b": str(b),
                                "c": str(c),
                            },
                            "discriminant": str(d),
                            "steps": steps,
                            "roots": [str(root) for root in roots],
                            "final_answer_latex": final
                        }











