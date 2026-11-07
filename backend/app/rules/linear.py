import re
import sympy as sp

from .equations import parse_expression

def expand_once(expr):
    if expr.is_Add:
        return sp.Add(
            *(expand_once(term) for term in expr.args),
            evaluate=False
        )
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
                    terms.append(sp.Mul(*new_factors))
                return sp.Add(*terms, evaluate=False)
    return expr

def solve_linear(equation):
    if (
        not isinstance(equation, str)
        or len(equation) > 160
        or equation.count("=") != 1
    ):
        raise ValueError("Enter one linear equation with an equals sign")

    lhs_text, rhs_text = equation.split("=")
    variable_names = set(re.findall(r"[a-z]", equation.lower()))

    if len(variable_names) != 1:
        raise ValueError("Use exactly one variable letter.")

    variable = sp.Symbol(variable_names.pop())

    lhs_original = parse_expression(
        lhs_text, preserve=True, variable=variable
    )
    rhs_original = parse_expression(
        rhs_text, preserve=True, variable=variable
    )
    lhs = sp.expand(lhs_original)
    rhs = sp.expand(rhs_original)

    for expr in (lhs_original, rhs_original):
        for node in sp.preorder_traversal(expr):
            if (
                node.is_Pow
                and node.exp == 2
                and node.base.has(variable)
            ):
                raise ValueError("Only first-degree equations are supported")
    for expr in (lhs, rhs):
        try:
            polynomial = sp.Poly(expr, variable)
        except sp.PolynomialError:
            raise ValueError("Only first-degree equations are supported") from None
        if polynomial.degree() > 1:
            raise ValueError("Only first-degree equations are supported")

        steps = []
        previous_latex = None
        tex = sp.latex

        def add_step(title, left, right):
            nonlocal previous_latex

            latex = rf"{tex(left)} = {tex(right)}"

            if latex != previous_latex:
                steps.append({
                    "title": title,
                    "latex": latex,
                })
                previous_latex = latex
        add_step("linearStepOriginal", lhs_original, rhs_original)

        work_lhs = lhs_original
        work_rhs = rhs_original

        for _ in range(6):
            next_lhs = expand_once(work_lhs)
            next_rhs = expand_once(work_rhs)

            if (
                tex(next_lhs) == tex(work_lhs)
                and tex(next_rhs) == tex(work_rhs)
            ):
                break
            work_lhs = next_lhs
            work_rhs = next_rhs
            add_step("linearStepExpand", work_lhs, work_rhs)

        if tex(work_lhs) != tex(lhs) or tex(work_rhs) != tex(rhs):
            add_step("linearStepSimplify", lhs, rhs)

        left_poly = sp.Poly(lhs, variable)
        right_poly = sp.Poly(rhs, variable)

        a = left_poly.coeff_monomial(variable)
        b = lhs.subs(variable, 0)
        c = right_poly.coeff_monomial(variable)
        d = rhs.subs(variable, 0)

        coefficient = sp.expand(a - c)
        constant = sp.expand(d - b)

        if c != 0:
            add_step(
                "linearStepMoveVariables",
                sp.expand(coefficient * variable + b),
                d
            )
        if b != 0:
            add_step(
                "linearStepMoveConstants",
                sp.expand(coefficient * variable),
                constant
            )
        if coefficient == 0:
            solution_type = (
                "infinite" if constant == 0 else "none"
            )
            add_step(
            "linearStepCompare",
                sp.Integer(0),
                constant
            )
            final_latex = (
                r"\text{Infinitely many solutions}"
                if solution_type == "infinite"
                else r"\text{No solution}"
            )
            return {
                "type": "linear",
                "solution_type": solution_type,
                "variable": str(variable),
                "solution": None,
                "steps": steps,
                "final_answer_latex": final_latex,
            }
        solution = sp.cancel(constant / coefficient)
        if coefficient != 1:
            add_step(
                "linearStepDivide",
                variable,
                solution
            )
        return {
            "type": "linear",
            "solution_type": "single",
            "variable": str(variable),
            "solution": str(solution),
            "steps": steps,
            "final_answer_latex": (
                rf"{tex(variable)} = {tex(solution)}"
            )
        }

