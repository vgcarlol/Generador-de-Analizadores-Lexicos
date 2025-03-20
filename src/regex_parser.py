class RegexParser:
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def tokenize(regex: str) -> list:
        tokens = []
        i = 0
        while i < len(regex):
            c = regex[i]
            if c == "\\":
                if i + 1 < len(regex):
                    tokens.append("\\" + regex[i+1])
                    i += 2
                else:
                    tokens.append(c)
                    i += 1
            elif c == "'":
                # Literal entre comillas simples
                i += 1
                literal = ""
                while i < len(regex) and regex[i] != "'":
                    literal += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == "'":
                    i += 1  # saltar la comilla de cierre
                tokens.append("'" + literal + "'")
            elif c == '"':
                # Literal entre comillas dobles
                i += 1
                literal = ""
                while i < len(regex) and regex[i] != '"':
                    literal += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == '"':
                    i += 1  # saltar la comilla de cierre
                tokens.append('"' + literal + '"')
            elif c == '{':
                token = c
                i += 1
                while i < len(regex) and regex[i] != '}':
                    token += regex[i]
                    i += 1
                if i < len(regex) and regex[i] == '}':
                    token += '}'
                    i += 1
                tokens.append(token)
            elif c.isalnum():
                # Agrupar toda la secuencia alfanumérica
                token = c
                i += 1
                while i < len(regex) and regex[i].isalnum():
                    token += regex[i]
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
                if ((curr.startswith("'") and curr.endswith("'")) or 
                    (curr.startswith("{") and curr.endswith("}")) or 
                    curr == '*' or curr == ')' or curr.startswith("\\") or curr.isalnum()) and \
                   ((nxt.startswith("'") and nxt.endswith("'")) or 
                    (nxt.startswith("{") and nxt.endswith("}")) or 
                    nxt == '(' or nxt.startswith("\\") or nxt.isalnum()):
                    result.append('.')
        return result

    @staticmethod
    def add_concatenation_operators(regex: str) -> list:
        tokens = RegexParser.tokenize(regex)
        return RegexParser.add_concatenation_operators_tokens(tokens)

    @staticmethod
    def infix_to_postfix(regex: str) -> str:
        if len(regex) == 1 and regex in {"*", "|", ".", "(", ")"}:
            regex = "'" + regex + "'"
        tokens = RegexParser.add_concatenation_operators(regex)
        output = []
        stack = []
        for token in tokens:
            if ((token.startswith("'") and token.endswith("'")) or 
                (token.startswith("{") and token.endswith("}")) or 
                token.startswith("\\") or token.isalnum() or token == "#"):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()
            else:
                while stack and RegexParser.precedence.get(token, 0) <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(token)
        while stack:
            output.append(stack.pop())
        output.append("#")
        return " ".join(output)
