# utils/expand_expression.py

SPECIAL_OPERATORS = {'+', '?', '*', '(', ')', '|', '.', '\\', '-', '[', ']', '{', '}'}


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
    max_depth = 10
    depth = 0
    while changed and depth < max_depth:
        changed = False
        for ident, rule in definitions.items():
            if ident == rule:
                continue
            new_expr = replace_whole_word(expr, ident, rule)
            if new_expr != expr:
                expr = new_expr
                changed = True
        depth += 1
    print(f"[LOG] Después de expand_lets: {expr}")
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
            content = expr[i+1:j].replace("'", "")

            expanded = []
            k = 0  # Asegúrate de que 'k' siempre esté inicializado
            while k < len(content):
                if k + 2 < len(content) and content[k + 1] == '-':  # Verifica si hay un rango
                    for c in range(ord(content[k]), ord(content[k + 2]) + 1):
                        ch = chr(c)
                        expanded.append(f"\\{ch}" if ch in SPECIAL_OPERATORS or ch.isspace() else ch)
                    k += 3  # Aumentamos 'k' después de procesar el rango
                else:
                    ch = content[k]
                    expanded.append(f"\\{ch}" if ch in SPECIAL_OPERATORS or ch.isspace() else ch)
                    k += 1  # Aumentamos 'k' normalmente
            joined = '|'.join(expanded)  # Unimos todas las opciones del rango
            result += '(' + joined + ')'
            i = j + 1  # Continuamos después del corchete de cierre ']'
        else:
            result += expr[i]
            i += 1
    print(f"[LOG] Después de expand_ranges: {result}")
    return result



def escape_literals(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == "'":
            j = i + 1
            literal = ""
            while j < len(expr) and expr[j] != "'":
                if expr[j] == '\\' and j + 1 < len(expr):
                    esc = expr[j+1]
                    # Asegurarse de que todos los caracteres de escape sean correctamente procesados
                    if esc == 'n':
                        literal += '\\n'
                    elif esc == 't':
                        literal += '\\t'
                    elif esc == 'r':
                        literal += '\\r'
                    elif esc == '\\':
                        literal += '\\\\'
                    elif esc == ' ':
                        literal += '\\s'
                    else:
                        literal += '\\' + esc
                    j += 2
                else:
                    if expr[j] == ' ':
                        literal += '\\s'
                    elif expr[j] in SPECIAL_OPERATORS or not expr[j].isalnum():
                        literal += '\\' + expr[j]
                    else:
                        literal += expr[j]
                    j += 1
            result += literal
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
            wrapped = f"({operand})" if not operand.startswith('(') else operand
            result = prefix + wrapped + f"{wrapped}*"
            i += 1
        else:
            result += expr[i]
            i += 1
    print(f"[LOG] Después de convert_plus: {result}")
    return result


def convert_optional(expr):
    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == '?' and (i == 0 or expr[i-1] != '\\'):
            operand, prefix = extract_last_operand(result)
            wrapped = f"({operand})" if not operand.startswith('(') else operand
            result = prefix + f"({wrapped}|ε)"
            i += 1
        else:
            result += expr[i]
            i += 1
    print(f"[LOG] Después de convert_optional: {result}")
    return result


def simplify_parens(expr):
    while expr.startswith('(') and expr.endswith(')'):
        count = 0
        for i in range(len(expr)):
            if expr[i] == '(': count += 1
            elif expr[i] == ')': count -= 1
            if count == 0 and i != len(expr) - 1:
                print(f"[LOG] Después de simplify_parens: {expr}")
                return expr
        expr = expr[1:-1]
    print(f"[LOG] Después de simplify_parens: {expr}")
    return expr


def expand_expression(expr, definitions):
    expr = escape_literals(expr)
    expr = expand_lets(expr, definitions)
    expr = expand_ranges(expr)
    expr = convert_plus(expr)
    expr = convert_optional(expr)
    expr = simplify_parens(expr)

    expr = expr.strip('|')

    if not validar_parentesis_balanceados(expr):
        raise ValueError(f"❌ Paréntesis no balanceados en expresión final: {expr}")

    print(f"[LOG] Final expression: {expr}")
    return expr


def validar_parentesis_balanceados(expr):
    balance = 0
    for ch in expr:
        if ch == '(': balance += 1
        elif ch == ')': balance -= 1
        if balance < 0:
            return False
    return balance == 0
