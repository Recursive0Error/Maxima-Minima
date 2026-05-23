import sympy as sp


def normalize_text(text):
    return text.strip().lower()


def classification_match(user, expected):
    mapping = {
        "minimum": "minimum",
        "local minimum": "minimum",
        "min": "minimum",

        "maximum": "maximum",
        "local maximum": "maximum",
        "max": "maximum",

        "saddle": "saddle",
        "saddle point": "saddle",

        "inconclusive": "inconclusive"
    }

    return mapping.get(normalize_text(user)) == mapping.get(normalize_text(expected))


def point_match(user, expected):
    user = normalize_text(user).replace(" ", "")
    expected = normalize_text(expected).replace(" ", "")

    # Parse key=value pairs from both sides into a dict for order-insensitive comparison
    def parse_pairs(s):
        parts = s.split(",")
        d = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                d[k.strip()] = v.strip()
        return d

    user_dict = parse_pairs(user)
    expected_dict = parse_pairs(expected)

    if user_dict and expected_dict:
        return user_dict == expected_dict

    # Fallback: plain string comparisons
    acceptable = [
        expected,
        expected.replace("x=", "").replace("y=", ""),
        expected.replace(",", ""),
    ]
    return user in acceptable


def expression_match(user, expected):
    try:
        user_expr = sp.sympify(user)
        expected_expr = sp.sympify(expected)

        return sp.simplify(user_expr - expected_expr) == 0
    except:
        return normalize_text(user) == normalize_text(expected)


def is_equivalent(user, expected, answer_type):
    if answer_type == "classification":
        return classification_match(user, expected)

    elif answer_type == "point":
        return point_match(user, expected)

    else:
        return expression_match(user, expected)