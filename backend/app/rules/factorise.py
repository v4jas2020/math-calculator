import math
import sympy as sp
from jinja2.runtime import identity

from .expand import parse_brackets

def _common_factor(poly):
    terms = [
        (powers, sp.Rational(coeff))
        for powers, coeff in poly.terms()
        if coeff
    ]
    if len(terms) < 2:
        return sp.Integer(1)
    numerator = math.gcd(
        *(abs(int(coeff.p)) for _, coeff in terms)
    )
    denominator = math.lcm(
        *(int(coeff.q) for _, coeff in terms)
    )
    factor =sp.Rational(numerator, denominator)

    for index, variable in enumerate(poly.gens):
        power = min(
            powers[index] for powers, _ in terms
        )
        if power:
            factor *= variable ** power
    return factor
def _square_root_term(powers, coefficient, symbols):
    coefficient = sp.Rational(coefficient)

    if coefficient <= 0 or any(p % 2 for p in powers):
        return None
    root_num, ok_num = sp.integer_nthroot(
        int(coefficient.p), 2
    )
    root_den, ok_den = sp.integer_nthroot(
        int(coefficient.q), 2
    )
    if not ok_num or not ok_den:
        return None
    result = sp.Rational(root_num, root_den)
    for variable, power in zip(symbols, powers):
        result *= variable ** (power // 2)
    return result
def _difference_of_squares(expr, symbols):
    terms = sp.Poly(
        expr, *symbols, domain=sp.QQ
    ).terms()
    if len(terms) != 2:
        return None
    positive = [
        (powers, coeff)
        for powers, coeff in terms
        if coeff > 0
    ]
    negative = [
        (powers, -coeff)
        for powers, coeff in terms
        if coeff < 0
    ]
    if len(positive) != 1 or len(negative) != 1:
        return None
    a = _square_root_term(*positive[0], symbols)
    b = _square_root_term(*negative[0], symbols)

    if a is None or b is None:
        return None
    return a, b
def solve_factorise(expression):
    original = parse_brackets(expression)
    preliminary = sp.expand(sp.simplify(original))

    symbols = sorted(
        original.free_symbols,
        key=lambda symbol: symbol.name
    )
    if sp.count_ops(preliminary) > 120:
        raise ValueError("Expression is too complex.")
    try:
        polynomial = (
            sp.Poly(preliminary, *symbols, domain=sp.QQ)
            if symbols else None
        )
    except (sp.PolynomialError, ValueError):
        raise ValueError("Only polynomial expressions are supported.") from None
    expanded = (
        polynomial.as_expr()
        if polynomial
        else sp.simplify(preliminary)
    )
    steps = [{
        "title": "factoriseStepOriginal",
        "latex": sp.latex(original)
    }]
    if sp.count_ops(expanded) > 120:
        raise ValueError("Expression is too complex.")
    if sp.latex(expanded) != steps[-1]["latex"]:
        steps.append({
            "title": "factoriseStepSimplify",
            "latex": sp.latex(expanded)
        })
    if not symbols or expanded == 0:
        return {
            "type": "factorise",
            "steps": steps,
            "answer": str(expanded),
            "final_answer_latex": sp.latex(expanded)
        }
    if (
        polynomial.total_degree() > 8
        or len(polynomial.terms()) > 35
    ):
        raise ValueError("Expression is too complex.")
    common = _common_factor(polynomial)
    remainder = (
        sp.cancel(expanded / common)
        if common != 1
        else expanded
    )
    if common != 1:
        steps.append({
            "title": "factoriseStepGCF",
            "latex": (
                r"\operatorname{GCF} = "
                + sp.latex(common)
            )
        })
        partial = sp.Mul(
            common, remainder, evaluate=False
        )
        steps.append({
            "title": "factoriseStepFactorOut",
            "latex": sp.latex(partial)
        })
    reduced_factorised = sp.factor(remainder)
    factored = (
        sp.Mul(
            common, reduced_factorised, evaluate=False
        )
        if common != 1
        else reduced_factorised
    )
    difference = _difference_of_squares(
        remainder, symbols
    )
    if (
        reduced_factorised != remainder
        and difference is not None
    ):
        a, b = difference
        identity = sp.Mul(
            a - b, a + b, evaluate=False
        )
        step_expr = (
            sp.Mul(common, identity, evaluate=False)
            if common != 1
            else identity
        )
        steps.append({
            "title": "factoriseStepDifferenceSquares",
            "latex": sp.latex(step_expr)
        })
        if sp.srepr(step_expr) != sp.srepr(factored):
            steps.append({
                "title": "factoriseStepFactorFurther",
                "latex": sp.latex(factored)
            })
    elif reduced_factorised != remainder:
        used_pair = False
        if len(symbols) == 1:
            q = sp.Poly(
                remainder, symbols[0], domain=sp.QQ
            )
            if q.degree() == 2:
                a, b, c = q.all_coeffs()
                roots = sp.roots(
                    remainder, symbols[0]
                )
                if (
                    a == 1
                    and sum(roots.values()) == 2
                    and all(root.is_Integer for root in roots)
                ):
                    numbers = sorted(
                        (
                            -root
                            for root, multiplicity in roots.items()
                            for _ in range(multiplicity)
                        ),
                        key=sp.default_sort_key
                    )
                    steps.append({
                        "title": "factoriseStepFindPair",
                        "latex": (
                            rf"m+n={sp.latex(b)},"
                            rf"\quad mn={sp.latex(c)}"
                        )
                    })
                    steps.append({
                        "title": "factoriseStepChoosePair",
                        "latex": (
                            rf"m={sp.latex(numbers[0])},"
                            rf"\quad n={sp.latex(numbers[1])}"
                        )
                    })

                    used_pair = True
        steps.append({
            "title": (
                "factoriseStepFactorQuadratic"
                if used_pair
                else "factoriseStepFactorFurther"
            ),
            "latex": sp.latex(factored)
        })
    elif common == 1:
        steps.append({
            "title": "factoriseStepNoFactors",
            "latex": sp.latex(expanded)
        })
    return {
        "type": "factorise",
        "steps": steps,
        "answer": str(factored),
        "final_answer_latex": sp.latex(factored)
    }


