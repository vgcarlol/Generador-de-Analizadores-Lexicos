# utils/regex_postfix.py

from regex_parser import RegexParser, graficar_arbol

def to_postfix(expr):
    # Convertimos a postfix como string
    raw = RegexParser.infix_to_postfix(expr).replace(" ", "")

    # Convertimos el string en una lista de tokens, considerando escapes
    tokens = []
    i = 0
    while i < len(raw):
        if raw[i] == '\\':
            tokens.append(raw[i] + raw[i + 1])
            i += 2
        else:
            tokens.append(raw[i])
            i += 1

    return tokens
