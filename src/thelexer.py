# Archivo generado automáticamente por YALex Generator

import sys

def matches_symbol(sym, ch):
    if len(sym) == 1:
        return ch == sym
    if (sym.startswith("'") and sym.endswith("'")) or (sym.startswith('"') and sym.endswith('"')):
        return ch == sym[1:-1]
    if sym.startswith('\\'):
        return ch == sym[1:]
    if sym.startswith('[') and sym.endswith(']'):
        content = sym[1:-1]
        i = 0
        while i < len(content):
            if i + 2 < len(content) and content[i+1] == '-':
                if content[i] <= ch <= content[i+2]:
                    return True
                i += 3
            else:
                if content[i] == ch:
                    return True
                i += 1
        return False
    return ch == sym

def simulate_afd_longest(afd_dict, input_string):
    current = afd_dict['start']
    states = afd_dict['states']
    last_accepted = -1
    pos = 0
    while pos < len(input_string):
        ch = input_string[pos]
        transition_found = False
        for sym, target in states[current]['transitions'].items():
            if matches_symbol(sym, ch):
                current = target
                pos += 1
                transition_found = True
                if states[current]['is_final']:
                    last_accepted = pos
                break
        if not transition_found:
            break
    return last_accepted if last_accepted != -1 else 0

def lex(input_string):
    tokens = []
    pos = 0
    while pos < len(input_string):
        max_length = 0
        selected_token = None
        selected_action = None
        # Evaluar cada regla (longest match + prioridad)
        # Regla TOKEN_0
        afd_TOKEN_0 = {'start': '0', 'states': {'0': {'is_final': False, 'transitions': {'[ \\t\\n]': '1'}}, '1': {'is_final': False, 'transitions': {'+': '2'}}, '2': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_0, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_0'
            selected_action = ''''''

        # Regla TOKEN_1
        afd_TOKEN_1 = {'start': '3', 'states': {'3': {'is_final': False, 'transitions': {'[A-Za-z]': '4'}}, '4': {'is_final': True, 'transitions': {'[A-Za-z]': '4', '_': '4', '[0-9]': '4'}}}}
        length = simulate_afd_longest(afd_TOKEN_1, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_1'
            selected_action = '''return ID'''

        # Regla TOKEN_2
        afd_TOKEN_2 = {'start': '5', 'states': {'5': {'is_final': False, 'transitions': {'[0-9]': '6'}}, '6': {'is_final': False, 'transitions': {'+': '7'}}, '7': {'is_final': False, 'transitions': {'[0-9]': '8'}}, '8': {'is_final': False, 'transitions': {'+': '9'}}, '9': {'is_final': False, 'transitions': {"'E'": '10'}}, '10': {'is_final': False, 'transitions': {"['+''-']": '11'}}, '11': {'is_final': True, 'transitions': {'+': '12', '[0-9]': '13'}}, '12': {'is_final': True, 'transitions': {}}, '13': {'is_final': False, 'transitions': {'+': '12'}}}}
        length = simulate_afd_longest(afd_TOKEN_2, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_2'
            selected_action = '''return NUMBER'''

        # Regla TOKEN_3
        afd_TOKEN_3 = {'start': '14', 'states': {'14': {'is_final': False, 'transitions': {"';'": '15'}}, '15': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_3, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_3'
            selected_action = '''return SEMICOLON'''

        # Regla TOKEN_4
        afd_TOKEN_4 = {'start': '16', 'states': {'16': {'is_final': False, 'transitions': {'":="': '17'}}, '17': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_4, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_4'
            selected_action = '''return ASSIGNOP'''

        # Regla TOKEN_5
        afd_TOKEN_5 = {'start': '18', 'states': {'18': {'is_final': False, 'transitions': {"'<'": '19'}}, '19': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_5, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_5'
            selected_action = '''return LT'''

        # Regla TOKEN_6
        afd_TOKEN_6 = {'start': '20', 'states': {'20': {'is_final': False, 'transitions': {"'='": '21'}}, '21': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_6, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_6'
            selected_action = '''return EQ'''

        # Regla TOKEN_7
        afd_TOKEN_7 = {'start': '22', 'states': {'22': {'is_final': False, 'transitions': {"'+'": '23'}}, '23': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_7, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_7'
            selected_action = '''return PLUS'''

        # Regla TOKEN_8
        afd_TOKEN_8 = {'start': '24', 'states': {'24': {'is_final': False, 'transitions': {"'-'": '25'}}, '25': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_8, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_8'
            selected_action = '''return MINUS'''

        # Regla TOKEN_9
        afd_TOKEN_9 = {'start': '26', 'states': {'26': {'is_final': False, 'transitions': {"'*'": '27'}}, '27': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_9, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_9'
            selected_action = '''return TIMES'''

        # Regla TOKEN_10
        afd_TOKEN_10 = {'start': '28', 'states': {'28': {'is_final': False, 'transitions': {"'/'": '29'}}, '29': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_10, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_10'
            selected_action = '''return DIV'''

        # Regla TOKEN_11
        afd_TOKEN_11 = {'start': '30', 'states': {'30': {'is_final': False, 'transitions': {"'('": '31'}}, '31': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_11, input_string[pos:])
        if length > max_length:
            max_length = length
            selected_token = 'TOKEN_11'
            selected_action = '''return LPAREN'''

        # Regla TOKEN_12
        afd_TOKEN_12 = {'start': '32', 'states': {'32': {'is_final': False, 'transitions': {"')'": '33'}}, '33': {'is_final': True, 'transitions': {}}}}
        length = simulate_afd_longest(afd_TOKEN_12, input_string[pos:])
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

"""
return RPAREN
"""