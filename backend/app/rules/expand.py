"""Step-by-step polynomial bracket expansion."""
import ast
import re

import sympy as sp

TOKENS = re.compile(r"\d+(?:\.\d+)?|[a-z]|[()+\-*/^]")


def parse_brackets(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 160:
        raise ValueError("Enter a valid expression (up to 160 characters).")
    source = (text.lower().replace(" ", "").replace("²", "^2")
              .replace("³", "^3").replace("×", "*")
              .replace("÷", "/").replace("−", "-"))
    if "=" in source:
        raise ValueError("Enter an expression without an equals sign.")
    tokens = TOKENS.findall(source)
    if not tokens or "".join(tokens) != source:
        raise ValueError("Unsupported mathematical expression.")
    if len({token for token in tokens if token.isalpha()}) > 3:
        raise ValueError("Use at most three different variables.")

    parts = []
    def ends(token):
        return token.isalpha() or token == ")" or token[0].isdigit()
    def starts(token):
        return token.isalpha() or token == "(" or token[0].isdigit()

    for index, token in enumerate(tokens):
        if index and ends(tokens[index - 1]) and starts(token):
            parts.append("*")
        parts.append("**" if token == "^" else token)
    try:
        tree = ast.parse("".join(parts), mode="eval")
    except SyntaxError:
        raise ValueError("Invalid expression syntax.") from None
    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression is too complex.")

    def read(node, depth=0):
        if depth > 16:
            raise ValueError("Expression is too complex.")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**6:
                raise ValueError("Use smaller numbers.")
            return sp.Rational(str(node.value))
        if isinstance(node, ast.Name) and len(node.id) == 1 and node.id.isalpha():
            return sp.Symbol(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = read(node.operand, depth + 1)
            if isinstance(node.op, ast.UAdd):
                return value
            return sp.Mul(-1, value, evaluate=False) if value.free_symbols else -value
        if isinstance(node, ast.BinOp):
            left = read(node.left, depth + 1)
            right = read(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                return sp.Add(left, right, evaluate=False)
            if isinstance(node.op, ast.Sub):
                return sp.Add(left, sp.Mul(-1, right, evaluate=False), evaluate=False)
            if isinstance(node.op, ast.Mult):
                return sp.Mul(left, right, evaluate=False)
            if isinstance(node.op, ast.Div):
                divisor = sp.simplify(right)
                if divisor == 0:
                    raise ValueError("Cannot divide by zero.")
                if divisor.free_symbols:
                    raise ValueError("Variable denominators are not supported.")
                return sp.Mul(left, sp.Rational(1) / divisor, evaluate=False)
            if isinstance(node.op, ast.Pow):
                exponent = sp.simplify(right)
                if exponent.is_Integer is not True or not (0 <= exponent <= 3):
                    raise ValueError("Use an integer exponent from 0 to 3.")
                return sp.Pow(left, int(exponent), evaluate=False)
        raise ValueError("Unsupported mathematical expression.")

    return read(tree.body)


def rebuild(original, args):
    if original.is_Add:
        return sp.Add(*args, evaluate=False)
    if original.is_Mul:
        return sp.Mul(*args, evaluate=False)
    if original.is_Pow:
        return sp.Pow(*args, evaluate=False)
    return original


def flatten_add(expr):
    if expr.is_Add:
        terms = []
        for part in expr.args:
            updated = flatten_add(part)
            if updated.is_Add:
                terms.extend(updated.args)
            else:
                terms.append(updated)
        return sp.Add(*terms, evaluate=False)
    if expr.is_Mul or expr.is_Pow:
        return rebuild(expr, [flatten_add(part) for part in expr.args])
    return expr


def simplify_products(expr):
    if expr.is_Add:
        return sp.Add(*(simplify_products(arg) for arg in expr.args), evaluate=False)
    if expr.is_Mul:
        factors = [simplify_products(arg) for arg in expr.args]
        if all(not factor.has(sp.Add) for factor in factors):
            return sp.Mul(*factors)
        return sp.Mul(*factors, evaluate=False)
    if expr.is_Pow:
        return sp.Pow(simplify_products(expr.base), expr.exp, evaluate=False)
    return expr


def distribute_once(expr):
    if expr.is_Pow and expr.exp.is_Integer and expr.exp > 1 and expr.base.is_Add:
        return sp.Mul(*([expr.base] * int(expr.exp)), evaluate=False), "expandStepPower"
    if expr.is_Mul:
        factors = list(expr.args)
        for index, factor in enumerate(factors):
            if factor.is_Add:
                terms = [
                    sp.Mul(*(factors[:index] + [term] + factors[index + 1:]), evaluate=False)
                    for term in factor.args
                ]
                return sp.Add(*terms, evaluate=False), "expandStepDistribute"
    for index, child in enumerate(expr.args):
        replacement, title = distribute_once(child)
        if title is not None:
            args = list(expr.args)
            args[index] = replacement
            return rebuild(expr, args), title
    return expr, None


def solve_expand(expression):
    original = parse_brackets(expression)
    steps = [{"title": "expandStepOriginal", "latex": sp.latex(original)}]
    current = original

    for _ in range(32):
        updated, title = distribute_once(current)
        if title is None:
            break
        current = simplify_products(flatten_add(updated))
        latex = sp.latex(current)
        if latex != steps[-1]["latex"]:
            steps.append({"title": title, "latex": latex})
        if sp.count_ops(current) > 150 or len(latex) > 1500:
            raise ValueError("Expression is too complex.")
    else:
        raise ValueError("Expression is too complex.")

    expanded = sp.expand(sp.simplify(current))
    if sp.count_ops(expanded) > 150:
        raise ValueError("Expression is too complex.")
    final_latex = sp.latex(expanded)
    if final_latex != steps[-1]["latex"]:
        steps.append({"title": "expandStepCollect", "latex": final_latex})
    return {
        "type": "expand",
        "answer": str(expanded),
        "final_answer_latex": final_latex,
        "steps": steps,
    }
