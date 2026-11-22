import re
from random import expovariate

import sympy as sp

ROOT_PATTERN = re.compile(
    r"(?:(?P<factor>[+-]?\d+\*?|[+-]))?"
    r"sqrt\((?P<radicand>\d+)\)\Z"
)
def root_latex(coefficient, radicand):
    if coefficient == 1:
        prefix = ""
    elif coefficient == -1:
        prefix = "-"
    else:
        prefix = str(coefficient)
    return rf"{prefix}\sqrt{{{radicand}}}"
def coefficient_prefix(coefficient):
    if coefficient == 1:
        return ""
    if coefficient == -1:
        return "-"
    return str(coefficient) + r"\cdot "
def solve_square_roots(expression):
    if not isinstance(expression, str) or len(expression) > 160:
        raise ValueError("Enter a square root expression.")
    source = expression.replace(" ", "").replace("−", "-")
    match = ROOT_PATTERN.fullmatch(source)
    if not match:
        raise ValueError(
            "Enter one square root of a nonnegative integer,"
            "such as sqrt(72)"
        )
    raw_coefficient = match.group("factor")
    if raw_coefficient in (None, "+"):
        coefficient = 1
    elif raw_coefficient == "-":
        coefficient = -1
    else:
        coefficient = int(raw_coefficient.rstrip("*"))
    radicand = int(match.group("radicand"))
    if radicand > 1_000_000_000 or abs(coefficient) > 1_000_000_000:
        raise ValueError("Use smaller integers.")
    original = root_latex(coefficient, radicand)
    steps = [{
        "title": "squareRootStepOriginal",
        "latex": original
    }]
    def add_step(title, latex):
        previous = steps[-1]["latex"]
        if latex.replace(" ", "") != previous.replace(" ", ""):
            steps.append({
                "title": title,
                "latex": latex
            })
    if radicand in (0, 1) or coefficient == 0:
        result = sp.Integer(coefficient) * sp.sqrt(radicand)
        add_step(
            "squareRootStepEvaluate",
            sp.latex(result)
        )
    else:
        factors = sp.factorint(radicand)
        outside = 1
        inside = 1
        for prime, exponent in factors.items():
            outside *= prime ** (exponent // 2)
            inside *= prime ** (exponent % 2)
        if outside == 1:
            steps.append({
                "title": "squareRootStepSimplest",
                "latex": original
            })
        else:
            prefix = coefficient_prefix(coefficient)
            square = outside * outside
            if inside > 1:
                add_step(
                    "squareRootStepFactor",
                    rf"{prefix}\sqrt{{{square}\cdot {inside}}}"
                )
                add_step(
                    "squareRootStepSeparate",
                    rf"{prefix}\sqrt{{{square}}}"
                    rf"\cdot\sqrt{{{inside}}}"
                )
                add_step(
                    "squareRootStepEvaluate",
                    rf"{prefix}{outside}\sqrt{{{inside}}}"
                )
            else:
                add_step(
                    "squareRootStepFactor",
                    rf"{prefix}\sqrt{{{outside}^2}}"
                )
                add_step(
                    "squareRootStepEvaluate",
                    rf"{prefix}{outside}"
                )
        result = sp.Integer(coefficient) * outside * sp.sqrt(inside)
    final_latex = sp.latex(result)
    add_step(
        "squareRootStepCombine",
        final_latex
    )
    return {
        "type": "square_roots",
        "answer": str(result),
        "final_answer_latex": final_latex,
        "steps": steps
    }
