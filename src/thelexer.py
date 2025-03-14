# Archivo generado automáticamente por YALex Generator
# Código de header que se copiará al inicio del analizador generado
import sys

import sys

# Se define una función de simulación de AFD (se usa 're' como placeholder)

def simulate_afd(regex, input_string):

    import re

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

        {

            import re

            pattern = re.compile(r'^[' ' '\t']')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_0'

                    selected_action = '''/* Saltar espacios y tabulaciones */'''

        }

        {

            import re

            pattern = re.compile(r'^['\n']')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_1'

                    selected_action = '''return EOL;'''

        }

        {

            import re

            pattern = re.compile(r'^([0-9])+')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_2'

                    selected_action = '''return INT;'''

        }

        {

            import re

            pattern = re.compile(r'^'+'')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_3'

                    selected_action = '''return PLUS;'''

        }

        {

            import re

            pattern = re.compile(r'^'-'')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_4'

                    selected_action = '''return MINUS;'''

        }

        {

            import re

            pattern = re.compile(r'^'*'')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_5'

                    selected_action = '''return TIMES;'''

        }

        {

            import re

            pattern = re.compile(r'^'/'')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_6'

                    selected_action = '''return DIV;'''

        }

        {

            import re

            pattern = re.compile(r'^'('')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_7'

                    selected_action = '''return LPAREN;'''

        }

        {

            import re

            pattern = re.compile(r'^')'')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_8'

                    selected_action = '''return RPAREN;'''

        }

        {

            import re

            pattern = re.compile(r'^(([a-zA-Z])(([a-zA-Z])|([0-9]))*)')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_9'

                    selected_action = '''return IDENTIFIER;'''

        }

        {

            import re

            pattern = re.compile(r'^eof')

            m = pattern.match(input_string[pos:])

            if m:

                length = len(m.group(0))

                if length > max_length:

                    max_length = length

                    selected_token = 'TOKEN_10'

                    selected_action = '''return EOF;'''

        }

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



# Código de header que se copiará al inicio del analizador generado
import sys
}

let digit      = [0-9]
let letter     = [a-zA-Z]
let identifier = {letter}({letter}|{digit})*

rule gettoken =
    [' ' '\t']       { /* Saltar espacios y tabulaciones */ }
  | ['\n']           { return EOL; }
  | {digit}+         { return INT; }
  | '+'              { return PLUS; }
  | '-'              { return MINUS; }
  | '*'              { return TIMES; }
  | '/'              { return DIV; }
  | '('              { return LPAREN; }
  | ')'              { return RPAREN; }
  | {identifier}     { return IDENTIFIER; }
  | eof              { return EOF; }

{
# Código de trailer que se copiará al final del analizador generado
# Fin del analizador léxico