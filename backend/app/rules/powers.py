import ast
import re
import sympy as sp

MAX_EXPONENT = 12
MAX_NODES = 70

# this was fixed by AI sadly I could not figure out the problem.
def _exponent(node):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        value = node.value
    elif isinstance(node, ast.UnaryOp) and isinstance(
        node.op, (ast.UAdd, ast.USub)
    ):
        value = _exponent(node.operand)
        if isinstance(node.op, ast.USub):
            value = -value
    else:
        raise ValueError(
            "Use an integer exponent from -12 to 12."
        )
    if abs(value) > MAX_EXPONENT:
        raise ValueError(
            "Use an integer exponent from -12 to 12."
        )
    return value
# this was fixed by AI sadly I could not figure out the problem.
def _read(node, depth=0):
    if depth > 16:
        raise ValueError("Expression is too complex.")
    if isinstance(node, ast.Constant) and type(node.value) is int:
        if abs(node.value) > 100_000:
            raise ValueError("Use smaller integers.")
        return sp.Integer(node.value)

    if isinstance(node, ast.Name) and re.fullmatch(r"[a-z]", node.id):
        return sp.Symbol(node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(
        node.op, (ast.UAdd, ast.USub)
    ):
        value = _read(node.operand, depth + 1)
        if isinstance(node.op, ast.UAdd):
            return value
        return sp.Mul(-1, value, evaluate=False)
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Pow):
            base = _read(node.left, depth + 1)
            exponent = _exponent(node.right)
            if base.is_zero and exponent <= 0:
                raise ValueError(
                    "Zero cannot have a nonpositive exponent."
                )
            return sp.Pow(base, exponent, evaluate=False)
        left = _read(node.left, depth + 1)
        right = _read(node.right, depth + 1)
        if isinstance(node.op, ast.Mult):
            return sp.Mul(left, right, evaluate=False)
        if isinstance(node.op, ast.Div):
            if right.is_zero or sp.simplify(right) == 0:
                raise ValueError("Cannot divide by zero.")
            return sp.Mul(
                left,
                sp.Pow(right, -1, evaluate=False),
                evaluate=False
            )
        if isinstance(node.op, ast.Add):
            return sp.Add(left, right, evaluate=False)
        if isinstance(node.op, ast.Sub):
            return sp.Add(
                left,
                sp.Mul(-1, right, evaluate=False),
                evaluate=False
            )
    raise ValueError(
        "Use numbers, letters, parentheses and integer powers only."
    )
# Again fixed by gpt sol 6.2 ^^^^^  Apparently I cannot write code still edited it a bit.
def _power_latex(base, exponent):
    text = sp.latex(base)
    if not base.is_Atom or base.is_negative:
        text = rf"\left({text}\right)"
    return rf"{text}^{{{exponent}}}"
def _power_info(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        return _read(node.left), _exponent(node.right)
    if isinstance(node, (ast.Name, ast.Constant)):
        return _read(node), 1
    return None

def solve_powers(expression):
    if (
        not isinstance(expression, str)
        or not expression.strip()
        or len(expression) > 160
    ):
        raise ValueError("Enter a powers expression (up to 160 characters).")
    source = (
        expression.strip()
        .replace("^", "**")
        .replace("−", "-")
    )
    if not re.fullmatch(r"[0-9a-zA-Z+\-*/()\s]+", source):
        raise ValueError("Use numbers, letters, parentheses and integer powers only.")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError("Expression must be a valid mathematical expression.") from None
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise ValueError("Expression is too complex.")
    original = _read(tree.body)

    if (
        len(original.free_symbols) > 3
        or sp.count_ops(original) > 75
    ):
        raise ValueError("Expression is too complex.")
    steps = [{
        "title": "powersStepOriginal",
        "latex": sp.latex(original)
    }]
    def step(title, latex):
        if latex != steps[-1]["latex"]:
            steps.append({
                "title": title,
                "latex": latex
            })
    node = tree.body

    if (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, (ast.Mult, ast.Div)) # This was a simple fix I wrote mul instead of Mult
    ):
         left_info = _power_info(node.left)
         right_info = _power_info(node.right)

         if (
             left_info
             and right_info
             and left_info[0] == right_info[0]
         ):
             base, m = left_info
             n = right_info[1]
             multiplying = isinstance(node.op, ast.Mult)
             sign = "+" if multiplying else "-"
             combined = m + n if multiplying else m - n
             step(
                 "powersStepProduct"
                 if multiplying else "powersStepQuotient",
                 _power_latex(base, f"{m}{sign}({n})")
             )
             step(
                "powersStepCombine",
                 _power_latex(base, combined)
             )
             if combined < 0:
                 step (
                     "powersStepNegative",
                     rf"\frac{{1}}{{{_power_latex(base, -combined)}}}"
                 )
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        exponent = _exponent(node.right)
        base = _read(node.left)
        if exponent == 0:
            step("powersStepZero", "1")
        elif exponent < 0:
            step(
                "powersStepNegative",
                rf"\frac{{1}}{{{_power_latex(base, -exponent)}}}"
            )
        elif (
            isinstance(node.left, ast.BinOp)
            and isinstance(node.left.op, ast.Pow)
        ):
            inner_exponent = _exponent(node.left.right)
            inner_base = _read(node.left.left)
            step(
                "powersStepPowerOfPower",
                _power_latex(
                    inner_base,
                    rf"{inner_exponent}\cdot {exponent}"
                )
            )
            step (
                "powersStepCombine",
                _power_latex(
                    inner_base,
                    inner_exponent * exponent
                )
            )
        elif (
            isinstance(node.left, ast.BinOp)
            and isinstance(node.left.op, ast.Mult)
        ):
            left = _read(node.left.left)
            right = _read(node.left.right)

            step(
                "powersStepPowerOfProduct",
                rf"{_power_latex(left, exponent)}"
                rf"\cdot {_power_latex(right, exponent)}"
            )
    try:
        answer = sp.cancel(
            sp.powsimp(sp.simplify(original))
        )
    except (OverflowError, ValueError, ZeroDivisionError):
        raise ValueError(
            "Expression is too complex."
        ) from None
    if (
        answer.has(sp.zoo, sp.nan, sp.oo, -sp.oo)
        or sp.count_ops(answer) > 90
        or len(str(answer)) > 750
    ):
        raise ValueError("Expression is too complex.")
    final_latex = sp.latex(answer)
    step(
        "powersStepResult",
        final_latex
    )
    return {
        "type": "powers",
        "answer": str(answer),
        "final_answer_latex": final_latex,
        "steps": steps
    }