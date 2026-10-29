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
