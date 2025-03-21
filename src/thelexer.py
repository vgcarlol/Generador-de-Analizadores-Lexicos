# Archivo generado automáticamente por YALex Generator

import sys
import re

def simulate_afd(regex, input_string):
    pattern = re.compile(r'^' + regex)
    m = pattern.match(input_string)
    return len(m.group(0)) if m else 0

def lex(input_string):
    tokens = []
    pos = 0
    while pos < len(input_string):
        max_length = 0
        selected_token = None
        selected_action = None
        # Evaluar cada regla (longest match + prioridad)
        # Regla TOKEN_0
        regex = '([ \\t\\n])+'
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_0'
                selected_action = '''return WHITESPACE'''

        # Regla TOKEN_1
        regex = "(([0123456789])+)(.(([0123456789])+))?('E'['+''-']?(([0123456789])+))?"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_1'
                selected_action = '''return NUMBER'''

        # Regla TOKEN_2
        regex = "'+'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_2'
                selected_action = '''return PLUS'''

        # Regla TOKEN_3
        regex = "'*'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_3'
                selected_action = '''return TIMES'''

        # Regla TOKEN_4
        regex = "'('"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_4'
                selected_action = '''return LPAREN'''

        # Regla TOKEN_5
        regex = "')'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_5'
                selected_action = '''return RPAREN'''

        if max_length == 0:
            print(f'Error léxico en la posición {pos}: {input_string[pos]}')
            pos += 1
        else:
            lexeme = input_string[pos:pos+max_length]
            tokens.append((selected_token, lexeme, selected_action))
            pos += max_length
    return tokens

def main():
    if len(sys.argv) < 2:
        print('Uso: python thelexer.py <archivo_de_entrada>')
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        input_string = f.read()
    tokens = lex(input_string)
    for token in tokens:
        print(token)

if __name__ == '__main__':
    main()

return WHITESPACE }               
  | number    { return NUMBER }
  | '+'       { return PLUS }
  | '*'       { return TIMES }
  | '('       { return LPAREN }
  | ')'       { return RPAREN