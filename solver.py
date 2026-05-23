import sympy as sp
import re


x, y = sp.symbols("x y")


def normalize_input(expr):
    expr = expr.replace("²", "^2")
    expr = expr.replace("³", "^3")
    expr = expr.replace("√", "sqrt")
    expr = expr.replace("ln", "log")

    expr = re.sub(r"e\^\((.*?)\)", r"exp(\1)", expr)
    expr = re.sub(r"e\^([a-zA-Z0-9]+)", r"exp(\1)", expr)

    expr = expr.replace("^", "**")

    functions = ["sin", "cos", "tan", "log", "sqrt", "exp"]

    for fn in functions:
        expr = re.sub(rf"{fn}\s+([a-zA-Z0-9_]+)", rf"{fn}(\1)", expr)

    expr = re.sub(r"(\d)([xy])", r"\1*\2", expr)
    expr = re.sub(r"([xy])([xy])", r"\1*\2", expr)
    expr = re.sub(r"(\d)\(", r"\1*(", expr)
    expr = re.sub(r"\)([xy])", r")*\1", expr)

    return expr


def classify(D, fxx):
    try:
        D_val = float(sp.N(D))
        fxx_val = float(sp.N(fxx))
    except Exception:
        return "inconclusive"

    if D_val > 0 and fxx_val > 0:
        return "minimum"
    elif D_val > 0 and fxx_val < 0:
        return "maximum"
    elif D_val < 0:
        return "saddle"
    else:
        return "inconclusive"


def build_steps(function_input):
    normalized = normalize_input(function_input)

    expr = sp.sympify(normalized)

    fx = sp.simplify(sp.diff(expr, x))
    fy = sp.simplify(sp.diff(expr, y))

    critical_points = sp.solve(
        [sp.Eq(fx, 0), sp.Eq(fy, 0)],
        [x, y],
        dict=True
    )

    if not critical_points:
        raise Exception("No symbolic critical point found.")

    cp = critical_points[0]

    cp_x = cp[x]
    cp_y = cp[y]

    cp_text = f"x={cp_x}, y={cp_y}"

    fxx = sp.simplify(sp.diff(fx, x))
    fyy = sp.simplify(sp.diff(fy, y))
    fxy = sp.simplify(sp.diff(fx, y))

    D = sp.simplify(
        fxx.subs(cp) * fyy.subs(cp) - (fxy.subs(cp)) ** 2
    )

    classification = classify(D, fxx.subs(cp))

    function_value = sp.simplify(expr.subs(cp))

    steps = [
        {
            "type": "expression",
            "prompt": "Find ∂f/∂x",
            "guide": "Example answers: 2x+6, 3x^2, sin(y)",
            "hint": "Differentiate with respect to x while treating y as constant.",
            "answer": str(fx),
            "detailed_solution": f"""
Differentiate each term with respect to x:

Original function:
f(x,y) = {expr}

Result:
∂f/∂x = {fx}
"""
        },

        {
            "type": "expression",
            "prompt": "Find ∂f/∂y",
            "guide": "Example answers: 2y, cos(x), 0",
            "hint": "Differentiate with respect to y while treating x as constant.",
            "answer": str(fy),
            "detailed_solution": f"""
Differentiate each term with respect to y:

Original function:
f(x,y) = {expr}

Result:
∂f/∂y = {fy}
"""
        },

        {
            "type": "point",
            "prompt": "Solve for critical point",
            "guide": "Example answers: x=1, y=2",
            "hint": "Set both first derivatives equal to zero and solve simultaneously.",
            "answer": cp_text,
            "detailed_solution": f"""
Solve:

{fx} = 0
{fy} = 0

Critical point:
{cp_text}
"""
        },

        {
            "type": "expression",
            "prompt": "Find ∂²f/∂x²",
            "guide": "Example answers: 2, 6x",
            "hint": "Differentiate ∂f/∂x with respect to x.",
            "answer": str(fxx),
            "detailed_solution": f"""
Differentiate:
{fx}

With respect to x:

Result:
{fxx}
"""
        },

        {
            "type": "expression",
            "prompt": "Find ∂²f/∂y²",
            "guide": "Example answers: 2, 6y",
            "hint": "Differentiate ∂f/∂y with respect to y.",
            "answer": str(fyy),
            "detailed_solution": f"""
Differentiate:
{fy}

With respect to y:

Result:
{fyy}
"""
        },

        {
            "type": "expression",
            "prompt": "Find ∂²f/∂x∂y",
            "guide": "Example answers: 0, 3",
            "hint": "Differentiate ∂f/∂x with respect to y.",
            "answer": str(fxy),
            "detailed_solution": f"""
Differentiate:
{fx}

With respect to y:

Result:
{fxy}
"""
        },

        {
            "type": "expression",
            "prompt": "Compute D = fxx*fyy - (fxy)^2",
            "guide": "Example answers: 4, 16, 9",
            "hint": "Substitute values into determinant formula.",
            "answer": str(D),
            "detailed_solution": f"""
Formula:

D = fxx*fyy - (fxy)^2

Substitute:

D = ({fxx})({fyy}) - ({fxy})²

Result:

D = {D}
"""
        },

        {
            "type": "classification",
            "prompt": "Classify the critical point",
            "guide": "Answer: minimum / maximum / saddle",
            "hint": "Use the second derivative test.",
            "answer": classification,
            "detailed_solution": f"""
Second derivative test:

D = {D}
fxx = {fxx.subs(cp)}

Classification:
{classification}
"""
        },

        {
            "type": "expression",
            "prompt": "Find function value at critical point",
            "guide": "Example answers: 10, 3/2, sqrt(2)",
            "hint": "Substitute the critical point into original function.",
            "answer": str(function_value),
            "detailed_solution": f"""
Substitute:
{cp_text}

Into:
{expr}

Result:
{function_value}
"""
        }
    ]

    return steps