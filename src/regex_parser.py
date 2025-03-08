class RegexParser:
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0}  

    @staticmethod
    def add_concatenation_operators(regex):
        new_regex = ""
        i = 0

        while i < len(regex):
            if regex[i] == '+':
                if i == 0 or not regex[i - 1].isalnum():
                    raise ValueError(f"Uso incorrecto de '+': {regex}")
                prev_char = regex[i - 1]
                new_regex = new_regex[:-1]  
                new_regex += f"{prev_char}.{prev_char}*"  
            else:
                new_regex += regex[i]

                # Insertar concatenación cuando:
                if i + 1 < len(regex) and (
                    (regex[i].isalnum() or regex[i] in ['*', ')'])
                    and (regex[i + 1].isalnum() or regex[i + 1] == '(')
                ):
                    new_regex += '.'

            i += 1

        return new_regex

    @staticmethod
    def infix_to_postfix(regex):
        regex = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []

        for char in regex:
            if char.isalnum() or char == "#":  
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:  
                while stack and RegexParser.precedence[char] <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())

        if output[-1] == '.':
            output.pop()
        output.append("#")

        return ''.join(output)
