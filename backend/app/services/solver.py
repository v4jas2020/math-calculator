
from ..rules.equations import solve_quadratic
from ..rules.fractions import solve_fractions

SOLVERS = {
    "quadratic": solve_quadratic,
    "fractions": solve_fractions
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
