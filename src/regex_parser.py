class RegexParser:
    precedence = {'*': 3, '?': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def add_concatenation_operators(regex):
        new_regex = ""
        i = 0
        while i < len(regex):
            c = regex[i]

            # Copiar el caracter actual
            new_regex += c

            # Determinar el siguiente caracter válido (sin salir del índice)
            if i + 1 < len(regex):
                curr = regex[i]
                next_c = regex[i + 1]

                # Si se requiere concatenación
                if ((curr.isalnum() or curr in [')', '*', '?']) and
                    (next_c.isalnum() or next_c == '(')):
                    new_regex += '.'

            i += 1

        return new_regex

    @staticmethod
    def infix_to_postfix(regex):
        regex = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []

        i = 0
        while i < len(regex):
            char = regex[i]

            if char == '\\':
                output.append(char + regex[i + 1])
                i += 2
                continue

            if char.isalnum() or char in ['#', 'ε']:
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                while stack and RegexParser.precedence.get(char, 0) <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(char)

            i += 1

        while stack:
            output.append(stack.pop())

        return ''.join(output)


def to_postfix(expr):
    raw = RegexParser.infix_to_postfix(expr).replace(" ", "")

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
