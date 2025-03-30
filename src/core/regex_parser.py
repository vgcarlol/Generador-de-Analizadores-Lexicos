# archivo: core/regex_parser.py

class RegexParser:
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def add_concatenation_operators(regex):
        new_regex = ""
        i = 0
        print("[DEBUG] add_concatenation_operators - Entrada:", regex)
        while i < len(regex):
            c = regex[i]
            # Si se detecta un marcador, copiarlo completo sin modificarlo
            if c == '#':
                marker = "#"
                i += 1
                while i < len(regex) and (regex[i].isalnum() or regex[i] == '_'):
                    marker += regex[i]
                    i += 1
                new_regex += marker
                continue  # Continuamos sin insertar concatenación dentro del marcador

            # Manejar secuencias escapadas
            if c == '\\' and i + 1 < len(regex):
                new_regex += regex[i:i+2]
                i += 2
                continue

            # Copiar el carácter actual
            new_regex += c

            # Determinar si se debe insertar un operador de concatenación
            if i + 1 < len(regex):
                next_char = regex[i + 1]
                # Se inserta concatenación si:
                # - c es literal, cierre de grupo o cierre de operador y
                # - next_char es literal, apertura de grupo, inicio de escape o inicio de marcador ('#')
                if ((c.isalnum() or c in [')', '*', '+', '?', '_']) and 
                    (next_char.isalnum() or next_char in ['(', '\\', '_', '#'])):
                    new_regex += '.'
                    print(f"[DEBUG] add_concatenation_operators - Insertando concatenación entre '{c}' y '{next_char}'")
            i += 1

        print("[DEBUG] add_concatenation_operators - Salida:", new_regex)
        return new_regex


    @staticmethod
    def infix_to_postfix(regex):
        # Primero, se insertan los operadores de concatenación.
        regex = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []
        i = 0
        while i < len(regex):
            # Manejo de secuencias escapadas.
            if regex[i] == '\\' and i + 1 < len(regex):
                token = regex[i] + regex[i+1]
                output.append(token)
                i += 2
                continue
            # Manejo de marcadores (por ejemplo, "#TOKEN_0").
            if regex[i] == '#':
                token = "#"
                i += 1
                while i < len(regex) and (regex[i].isalnum() or regex[i] == '_'):
                    token += regex[i]
                    i += 1
                output.append(token)
                continue
            # Ignorar ε.
            if regex[i] == 'ε':
                i += 1
                continue
            # Si el carácter no es un operador reconocido (ni paréntesis ni los de precedencia), lo tratamos como literal.
            if regex[i] not in {'*', '.', '|', '(', ')'}:
                token = ''
                # Acumular todos los caracteres consecutivos que no sean operadores.
                while i < len(regex) and regex[i] not in {'*', '.', '|', '(', ')', 'ε'}:
                    token += regex[i]
                    i += 1
                output.append(token)
                continue
            elif regex[i] == '(':
                stack.append('(')
            elif regex[i] == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Error: Paréntesis desbalanceados, falta '('")
                stack.pop()
            else:
                # Es un operador: *, . o |
                op = regex[i]
                while stack and stack[-1] != '(' and RegexParser.precedence.get(stack[-1], 0) >= RegexParser.precedence.get(op, 0):
                    output.append(stack.pop())
                stack.append(op)
            i += 1

        while stack:
            if stack[-1] == '(':
                raise ValueError("Error: Paréntesis desbalanceados, falta ')'")
            output.append(stack.pop())

        if not output or output[-1] != "#":
            output.append("#")
        return output
