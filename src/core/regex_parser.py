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
            
            # 1) Manejo de marcadores
            if c == '#':
                marker = "#"
                i += 1
                while i < len(regex) and (regex[i].isalnum() or regex[i] == '_'):
                    marker += regex[i]
                    i += 1
                new_regex += marker
                continue
            
            # 2) Literal entre comillas => copiar completo sin insertar concatenación dentro
            if c in ['"', "'"]:
                quote = c
                literal = c
                i += 1
                while i < len(regex) and regex[i] != quote:
                    literal += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == quote:
                    literal += regex[i]
                    i += 1
                new_regex += literal
                continue
            
            # 3) Secuencias escapadas => copiar \ + siguiente char
            if c == '\\' and i + 1 < len(regex):
                new_regex += regex[i:i+2]
                i += 2
                continue
            
            # 4) Copiamos el carácter actual
            new_regex += c
            
            # 5) Insertar concatenación si el siguiente carácter inicia un átomo
            if i + 1 < len(regex):
                next_char = regex[i + 1]
                
                # Caso especial: si acabamos de poner `'\.'`, NO añadimos '.' de concatenación
                # => chequeamos si c == '\\' y next_char == '.'
                #    En tal caso, saltamos la inyección
                if c == '\\' and next_char == '.':
                    # Ejemplo: tienes "\."
                    # No vamos a meter más concatenación aquí:
                    pass
                else:
                    # Caso general: si c es alfanumérico o uno de ) * + ? _ / : < = - >
                    # y next_char es alfanumérico, ( o \ ... => inyectamos '.'
                    if ((c.isalnum() or c in [')', '*', '+', '?', '_', '/', ':', '<', '=', '-', '>']) 
                        and (next_char.isalnum() or next_char in ['(', '\\', '_', '#', '/', ':', '<', '=', '-', '>', '"', "'"])):
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
