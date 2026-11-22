
from ..rules.equations import solve_quadratic
from ..rules.fractions import solve_fractions
from ..rules.linear import solve_linear
from ..rules.expand import solve_expand
from ..rules.like_terms import solve_like_terms
from ..rules.factorise import solve_factorise
from ..rules.add_subtract import solve_add_subtract
from ..rules.square_roots import solve_square_roots

SOLVERS = {
    "quadratic": solve_quadratic,
    "fractions": solve_fractions,
    "linear": solve_linear,
    "expand": solve_expand,
    "like_terms": solve_like_terms,
    "factorise": solve_factorise,
    "add_subtract": solve_add_subtract,
    "square_roots": solve_square_roots,
}


def solve_problem(topic: str, equation: str) -> dict:
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Select a calculator topic.")

    if not isinstance(equation, str) or not equation.strip():
        raise ValueError("Enter an equation.")

    topic = topic.strip().lower()
    equation = equation.strip()

    if topic not in SOLVERS:
        raise ValueError(f"Unsupported calculator: {topic}")

    result = SOLVERS[topic](equation)

    return {
        "topic": topic,
        "equation": equation,
        **result
    }
