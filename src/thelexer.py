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
                selected_action = ''''''

        # Regla TOKEN_1
        regex = '([A-Za-z])(([A-Za-z])|(_)*|([0-9]))*'
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_1'
                selected_action = '''return ID'''

        # Regla TOKEN_2
        regex = "([0-9])+(.([0-9])+)?('E'['+''-']?([0-9])+)?"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_2'
                selected_action = '''return NUMBER'''

        # Regla TOKEN_3
        regex = "';'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_3'
                selected_action = '''return SEMICOLON'''

        # Regla TOKEN_4
        regex = '":="'
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_4'
                selected_action = '''return ASSIGNOP'''

        # Regla TOKEN_5
        regex = "'<'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_5'
                selected_action = '''return LT'''

        # Regla TOKEN_6
        regex = "'='"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_6'
                selected_action = '''return EQ'''

        # Regla TOKEN_7
        regex = "'+'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_7'
                selected_action = '''return PLUS'''

        # Regla TOKEN_8
        regex = "'-'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_8'
                selected_action = '''return MINUS'''

        # Regla TOKEN_9
        regex = "'*'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_9'
                selected_action = '''return TIMES'''

        # Regla TOKEN_10
        regex = "'/'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_10'
                selected_action = '''return DIV'''

        # Regla TOKEN_11
        regex = "'('"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_11'
                selected_action = '''return LPAREN'''

        # Regla TOKEN_12
        regex = "')'"
        pattern = re.compile(r'^' + regex)
        m = pattern.match(input_string[pos:])
        if m:
            length = len(m.group(0))
            if length > max_length:
                max_length = length
                selected_token = 'TOKEN_12'
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

return ID }               
  | number    { return NUMBER }
  | ';'       { return SEMICOLON }
  | ":="      { return ASSIGNOP }
  | '<'       { return LT }
  | '='       { return EQ }
  | '+'       { return PLUS }
  | '-'       { return MINUS }
  | '*'       { return TIMES }
  | '/'       { return DIV }
  | '('       { return LPAREN }
  | ')'       { return RPAREN