from collections import defaultdict
import sympy as sp

from .expand import (
    parse_brackets,
    distribute_once,
    flatten_add,
    simplify_products,
)
from .like_terms import split_terms, format_coefficients

def _sum_latex(terms):
    parts = []
    for term in terms:
        if term == 0:
            continue

        negative = term.could_extract_minus_sign()
        absolute = -term if negative else term
        latex = sp.latex(absolute)

        if not parts:
            parts.append(("-" if negative else "") + latex)
        else:
            parts.append(
                (" - " if negative else " + ") +latex
            )
    return "".join(parts) or "0"
def solve_add_subtract(expression):
    original = parse_brackets(expression)
    variables = sorted(
        original.free_symbols,
        key=lambda symbol: symbol.name
    )
    steps = [{
        "title": "addSubtractOriginal",
        "latex": sp.latex(original)
    }]
    def add_step(title, latex):
        if latex != steps[-1]["latex"]:
            steps.append({
                "title": title,
                "latex": latex
            })
    current = original
    for _ in range(40):
        updated, title = distribute_once(current)
        if title is None:
            break
        current = simplify_products(flatten_add(updated))
        if (
            sp.count_ops(current) > 150
            or len(sp.latex(current)) > 1500
        ):
            raise ValueError("Expression is too complex.")
    else:
        raise ValueError("Expression is too complex.")
    terms = []
    for term in split_terms(current):
        terms.extend(split_terms(sp.expand(term)))
    add_step(
        "addSubtractStepRemove",
        _sum_latex(terms)
    )
    groups = defaultdict(list)
    for term in terms:
        if term == 0:
            continue
        if variables:
            try:
                poly = sp.Poly(
                term,
                *variables,
                domain=sp.QQ
                )
            except (
                sp.PolynomialError,
                ValueError,
                TypeError
            ):
                raise ValueError("Only polynomial expressions are supported.") from None
            entries = poly.terms()

            if len(entries) != 1:
                raise ValueError("Only polynomial expressions are supported.")

            powers, coefficient = entries[0]
        else:
            powers = ()
            coefficient = sp.Rational(term)

        groups[powers].append(coefficient)
    order = sorted(
        groups,
        key=lambda powers: (
            not any(powers),
            -sum(powers),
            tuple(-power for power in powers)
        )
    )
    def basis_for(powers):
        result = sp.Integer(1)
        for variable, power in zip(variables, powers):
            result *= variable ** power
        return result
    if any(len(coeffs) > 1 for coeffs in groups.values()):
        grouped = []
        coefficients = []
        for powers in order:
            coeffs = groups[powers]
            basis = basis_for(powers)
            group = format_coefficients(coeffs, basis)
            grouped.append(group)
            numbers = format_coefficients(coeffs)
            if len(coeffs) > 1 or numbers.startswith("-"):
                numbers = (
                    r"\left(" + numbers + r"\right)"
                )
            if basis != 1:
                numbers += sp.latex(basis)
            coefficients.append(numbers)
        add_step(
            "addSubtractStepGroup",
            " + ".join(grouped)
        )
        add_step(
            "addSubtractStepCoefficients",
            " + ".join(coefficients)
        )
    answer = sp.expand(sp.simplify(original))
    if sp.count_ops(answer) > 150:
        raise ValueError("Expression is too complex.")
    final_latex = sp.latex(answer)
    add_step(
        "addSubtractStepResult",
        final_latex
    )
    return {
        "type": "add_subtract",
        "answer": str(answer),
        "final_answer_latex": final_latex,
        "steps": steps,
    }