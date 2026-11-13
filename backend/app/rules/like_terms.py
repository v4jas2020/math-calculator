from statistics import variance

import sympy as sp
from sympy import true
from sympy.core import basic

from .expand import parse_brackets

def split_terms(expr):
    if expr.is_Add:
        result= []
        for part in expr.args:
            result.extend(split_terms(part))
        return result
    return [expr]
def has_unexpanded_brackets(expr):
    for node in sp.preorder_traversal(expr):
        if (node.is_Mul or node.is_Pow) and any(
            arg.is_Add for arg in node.args
        ):
            return True
    return False
def format_coefficients(coefficients, monomial=None):
    parts= []
    for coefficient in coefficients:
        if coefficient == 0:
            continue
        magnitude = abs(coefficient)
        suffix = (
            "" # Why does this fix the bug that its undefined, I have no idea personally but its like this according to documentation or smth.
            if monomial is None or monomial == 1
            else sp.latex(monomial)
        )
        number = (
            ""
            if suffix and magnitude == 1
            else sp.latex(magnitude)
        )
        value = number + suffix
        if not parts:
            parts.append(
                {"-" if coefficient < 0 else ""} + value
            )
        else:
            parts.append(
                (" - " if coefficient < 0 else "+") + value
            )
    return "".join(parts) or "0"
def join_groups(chunks):
    output = ""
    for chunk in chunks:
        if not output:
            output = chunk
        elif chunk.startswith("-"):
            output += " - " + chunk[1:]
        else:
            output += " + " + chunk
    return output
def solve_like_terms(expression):
    original = parse_brackets(expression)
    if has_unexpanded_brackets(original):
        raise ValueError(
            "Expand brackets before combining like terms."
        )
    variables = sorted(
        original.free_symbols,
        key=lambda symbol: symbol.name
    )
    groups = {}
    for term in split_terms(original):
        if variables:
            try:
                poly = sp.Poly(
                    term, *variables, domain=sp.QQ
                )
            except sp.PolynomialError:
                raise ValueError(
                    "Only polynomial terms are supported."
                ) from None
            entries = poly.terms()
            if len(entries) > 1:
                raise ValueError(
                    "Expand brackets before combining like terms."
                )
            if entries:
                powers, coefficient = entries[0]
            else:
                powers = (0,) * len(variables)
                coefficient = sp.Integer(0)
        else:
            powers = ()
            coefficient = sp.Rational(sp.simplify(term))
        groups.setdefault(powers, [].append(coefficient))
    order = sorted(
        groups,
        key=lambda powers: (
            not any(powers),
            -sum(powers),
            tuple(-power for power in powers)
        )
    )
    def monomial(powers):
        result = sp.Integer(1)
        for variable, power in zip(variables, powers):
            if power:
                result *= variable ** power
        return result
    steps = [{
        "title": "likeTermsStepOriginal",
        "latex": sp.latex(original)
    }]
    needs_combining = any(
        len(coefficients) > 1
        for coefficients in groups.values()
    )
    if needs_combining:
        grouped = []
        coefficient_groups = []

        for powers in order:
            coefficients = groups[powers]
            basis = monomial(powers)

            terms_latex = format_coefficients(
                coefficients, basis
                )
            if len(coefficients) > 1:
                grouped.append(
                    r"\left("+ terms_latex + r"\right)"
                )
            else:
                grouped.append(terms_latex)
            numbers_latex = format_coefficients(
                coefficients
            )
            if len(coefficients) > 1:
                numbers_latex = (
                    r"\left(" + numbers_latex + r"\right)"
                )
            if basis != 1:
                numbers_latex += sp.latex(basis)

            coefficient_groups.append(numbers_latex)
        group_latex = join_groups(grouped)
        coefficients_latex = join_groups(coefficient_groups)

        for title, latex in (
            ("likeTermsStepGroup", group_latex),
            ("likeTermsStepCoefficients", coefficients_latex)
        ):
            if latex != steps[-1]["latex"]:
                steps.append({
                    "title": title,
                    "latex": latex
                })
    simplified = sp.Add(
        *(
            sum(groups[powers], sp.Integer(0))
            * monomial(powers)
            for powers in order
        ),
        evaluate=True
    )
    if sp.count_ops(simplified) > 120:
        raise ValueError("Expression is too complex")
    return {
        "type": "like_terms",
        "steps": steps,
        "answer": str(simplified),
        "final_answer_latex": sp.latex(simplified)
    }
