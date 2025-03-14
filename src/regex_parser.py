# regex_parser.py

class RegexParser:
    # Precedencia de operadores: * tiene mayor, luego concatenación (.), luego alternación (|), y '(' tiene menor.
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def tokenize(regex: str) -> list:
        tokens = []
        i = 0
        while i < len(regex):
            c = regex[i]
            if c == "'":
                # Se encuentra un literal entre comillas simples.
                i += 1
                literal = ""
                while i < len(regex) and regex[i] != "'":
                    literal += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == "'":
                    i += 1  # saltar la comilla de cierre
                tokens.append("'" + literal + "'")
            elif c == '{':
                # Se agrupa una referencia o grupo entre llaves.
                token = c
                i += 1
                while i < len(regex) and regex[i] != '}':
                    token += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == '}':
                    token += '}'
                    i += 1
                tokens.append(token)
            else:
                tokens.append(c)
                i += 1
        return tokens

    @staticmethod
    def add_concatenation_operators_tokens(tokens: list) -> list:
        result = []
        for i in range(len(tokens)):
            token = tokens[i]
            result.append(token)
            if i < len(tokens) - 1:
                curr = token
                nxt = tokens[i + 1]
                if ((curr.endswith("'") or curr.endswith("}") or curr == '*' or curr == ')')
                    and (nxt.startswith("'") or nxt.startswith("{") or nxt == '(')):
                    result.append('.')
        return result

    @staticmethod
    def add_concatenation_operators(regex: str) -> list:
        tokens = RegexParser.tokenize(regex)
        return RegexParser.add_concatenation_operators_tokens(tokens)

    @staticmethod
    def infix_to_postfix(regex: str) -> str:
        tokens = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []
        for token in tokens:
            # Si el token es un operando (literal, referencia, alfanumérico o '#')
            if ((token.startswith("'") and token.endswith("'")) or 
                (token.startswith("{") and token.endswith("}")) or 
                token.isalnum() or token == "#"):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # quitar '('
            else:
                # Token es un operador: *, . o |
                while stack and RegexParser.precedence.get(token, 0) <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(token)
        while stack:
            output.append(stack.pop())
        output.append("#")  # Símbolo final (opcional)
        return " ".join(output)
