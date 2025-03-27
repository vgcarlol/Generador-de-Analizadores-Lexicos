# utils/expand_expression.py

SPECIAL_OPERATORS = {'+', '?', '*', '(', ')', '|', '.', '\\'}


def is_boundary(ch):
    return not (ch.isalnum() or ch == '_')


def replace_whole_word(s, word, replacement):
    result = ""
    i = 0
    while i < len(s):
        if s[i:i+len(word)] == word:
            prev = s[i-1] if i > 0 else None
            next = s[i+len(word)] if i + len(word) < len(s) else None
            if (prev is None or is_boundary(prev)) and (next is None or is_boundary(next)):
                result += replacement
                i += len(word)
                continue
        result += s[i]
        i += 1
    return result


def expand_lets(expr, definitions):
    changed = True
    while changed:
        changed = False
        for ident, rule in definitions.items():
            new_expr = replace_whole_word(expr, ident, f"({rule})")
            if new_expr != expr:
                expr = new_expr
                changed = True
    return expr


def expand_ranges(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == '[':
            j = i + 1
            while j < len(expr) and expr[j] != ']':
                j += 1
            if j >= len(expr):
                result += expr[i:]
                break
            content = expr[i+1:j]
            content = content.replace("'", "")  # quitar comillas simples
            expanded = []
            k = 0
            while k < len(content):
                if k+2 < len(content) and content[k+1] == '-':
                    for c in range(ord(content[k]), ord(content[k+2])+1):
                        expanded.append(chr(c))
                    k += 3
                else:
                    expanded.append(content[k])
                    k += 1
            result += '(' + '|'.join(expanded) + ')'
            i = j + 1
        else:
            result += expr[i]
            i += 1
    return result


def escape_literals(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == "'":
            j = i + 1
            literal = ""
            while j < len(expr) and expr[j] != "'":
                if expr[j] == '\\' and j+1 < len(expr):
                    literal += expr[j] + expr[j+1]
                    j += 2
                else:
                    literal += expr[j]
                    j += 1
            for ch in literal:
                if ch in SPECIAL_OPERATORS:
                    result += '\\' + ch
                else:
                    result += ch
            i = j + 1
        else:
            result += expr[i]
            i += 1
    return result


def extract_last_operand(result):
    if result and result[-1] == ')':
        count = 0
        j = len(result) - 1
        while j >= 0:
            if result[j] == ')': count += 1
            elif result[j] == '(': count -= 1
            if count == 0:
                return result[j:], result[:j]
            j -= 1
    return result[-1], result[:-1]


def convert_plus(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == '+' and (i == 0 or expr[i-1] != '\\'):
            operand, prefix = extract_last_operand(result)
            result = prefix + operand + f"({operand})*"
            i += 1
        else:
            result += expr[i]
            i += 1
    return result


def convert_optional(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == '?' and (i == 0 or expr[i-1] != '\\'):
            operand, prefix = extract_last_operand(result)
            result = prefix + f"({operand}|ε)"
            i += 1
        else:
            result += expr[i]
            i += 1
    return result


def simplify_parens(expr):
    while expr.startswith('(') and expr.endswith(')'):
        count = 0
        for i in range(len(expr)):
            if expr[i] == '(': count += 1
            elif expr[i] == ')': count -= 1
            if count == 0 and i != len(expr) - 1:
                return expr
        expr = expr[1:-1]
    return expr


def expand_expression(expr, definitions):
    expr = expand_lets(expr, definitions)
    expr = expand_ranges(expr)
    expr = escape_literals(expr)
    expr = convert_plus(expr)
    expr = convert_optional(expr)
    expr = simplify_parens(expr)
    return expr