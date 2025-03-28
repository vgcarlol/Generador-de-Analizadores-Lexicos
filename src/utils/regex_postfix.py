# utils/regex_postfix.py

from regex_parser import RegexParser, graficar_arbol

def to_postfix(expr):
    print(f"[DEBUG] to_postfix input: {expr}")

    # Limpieza manual: evitar || y '|' al inicio/final
    while '||' in expr:
        expr = expr.replace('||', '|')
    expr = expr.strip('|')

    tokens = RegexParser.infix_to_postfix(expr)
    print(f"[DEBUG] Final tokens: {tokens}")
    return tokens
