class RegexParser:
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def add_concatenation_operators(regex):
        new_regex = ""
        i = 0

        while i < len(regex):
            c1 = regex[i]

<<<<<<< Updated upstream
            # Detecta '+' como símbolo literal (cuando está entre paréntesis o solo)
            if c1 == '+' and (i == 0 or regex[i-1] in '(|.'):
                new_regex += c1  # no es operador, solo símbolo literal
            elif c1 == '+':
                raise ValueError(f"Uso incorrecto de '+': {regex}")
            else:
                new_regex += c1

                if i + 1 < len(regex):
                    c2 = regex[i + 1]
                    if (
                        (c1.isalnum() or c1 in ['*', ')', '_', '#']) and
                        (c2.isalnum() or c2 == '(' or c2 == '_')
                    ):
                        new_regex += '.'

            i += 1
=======
            # Detectar secuencia escapada (como \* o \+ o \()
            if c1 == '\\' and i + 1 < len(regex):
                token1 = regex[i:i+2]
                new_regex += token1
                i += 2
            else:
                new_regex += c1
                if i + 1 < len(regex):
                    c2 = regex[i + 1]
                    # Verificar contexto para insertar '.'
                    if (
                        (c1.isalnum() or c1 in ['*', ')', '_', '#', '\\']) and
                        (c2.isalnum() or c2 == '(' or c2 == '_' or c2 == '\\')
                    ):
                        new_regex += '.'
                i += 1
>>>>>>> Stashed changes

        return new_regex


    @staticmethod
    def infix_to_postfix(regex):
        regex = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []
<<<<<<< Updated upstream

        for char in regex:
            if char == 'ε':
                continue  # no lo agregues como símbolo en postfix
            elif char.isalnum() or char in ['#', '_']:
                output.append(char)

            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Error: Paréntesis desbalanceados, falta '('")
                stack.pop()

            else:  # operadores
                while stack and RegexParser.precedence.get(char, 0) <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())

        # Asegurar que # esté al final
=======
        i = 0

        while i < len(regex):
            char = regex[i]

            # Manejar secuencia escapada como símbolo literal completo
            if char == '\\' and i + 1 < len(regex):
                escaped = '\\' + regex[i + 1]
                output.append(escaped)
                i += 2
                continue

            if char == 'ε':
                i += 1
                continue
            elif char.isalnum() or char in ['#', '_']:
                token = ''
                while i < len(regex) and (regex[i].isalnum() or regex[i] in ['#', '_']):
                    token += regex[i]
                    i += 1
                output.append(token)
                continue
            elif char == '(':
                # Asegurar que no sea un paréntesis escapado, ya procesado
                if i > 0 and regex[i - 1] == '\\':
                    output.append(char)
                else:
                    stack.append(char)
            elif char == ')':
                # Asegurar que no sea un paréntesis escapado, ya procesado
                if i > 0 and regex[i - 1] == '\\':
                    output.append(char)
                else:
                    while stack and stack[-1] != '(':
                        output.append(stack.pop())
                    if not stack:
                        raise ValueError("Error: Paréntesis desbalanceados, falta '('")
                    stack.pop()
            i += 1

        while stack:
            if stack[-1] == '(':
                raise ValueError("Error: Paréntesis desbalanceados, falta ')'")
            output.append(stack.pop())

>>>>>>> Stashed changes
        if output and output[-1] != "#":
            output.append("#")

        return ''.join(output)
