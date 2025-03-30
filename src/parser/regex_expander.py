<<<<<<< Updated upstream
# archivo: parser/regex_expander.py

=======
>>>>>>> Stashed changes
class RegexExpander:
    def __init__(self, let_definitions):
        self.let_definitions = let_definitions

    def normalize(self, expr):
<<<<<<< Updated upstream
=======
        print(f"🔎 Normalizando: {expr}")
>>>>>>> Stashed changes
        expr = self._strip_quotes(expr)
        expr = self._expand_char_classes(expr)
        expr = self.expand_lets(expr)
        expr = self._expand_plus(expr)
        expr = self._expand_question(expr)
        return expr

    def _strip_quotes(self, expr):
        expr = expr.strip()

<<<<<<< Updated upstream
        # Si la expresión es un solo símbolo especial, protégelo SIEMPRE
        if expr in {'(', ')', '*', '+', '|', '.', '?'}:
            return f"({expr})"

        # Si estaba entre comillas, elimínalas
        if len(expr) >= 2 and expr[0] == expr[-1] and expr[0] in ("'", '"'):
            return expr[1:-1]
=======
        # Si está entre comillas
        if len(expr) >= 2 and expr[0] == expr[-1] and expr[0] in ("'", '"'):
            inner = expr[1:-1]
            # Si es símbolo especial, escápalo
            if len(inner) == 1 and inner in {'(', ')', '*', '+', '|', '.', '?'}:
                print(f"📌 Escapando literal especial: '{inner}' -> \\{inner}")
                return f"\\{inner}"  # Literal escapado, válido en AFD
            return inner

        # Si ya no tiene comillas, pero es especial
        if expr in {'(', ')', '*', '+', '|', '.', '?'}:
            print(f"📌 Escapando símbolo especial sin comillas: '{expr}' -> \\{expr}")
            return f"\\{expr}"
>>>>>>> Stashed changes

        return expr


    def expand_lets(self, expr):
<<<<<<< Updated upstream
        tokens = []
=======
        result = []
>>>>>>> Stashed changes
        i = 0
        while i < len(expr):
            if expr[i].isalpha():
                ident = ''
                while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                    ident += expr[i]
                    i += 1
                if ident in self.let_definitions:
                    expanded = self.let_definitions[ident]
<<<<<<< Updated upstream
                    if not (expanded.startswith('(') and expanded.endswith(')')):
                        expanded = f"({expanded})"
                    tokens.append(expanded)
                else:
                    tokens.append(ident)
            else:
                tokens.append(expr[i])
                i += 1
        return ''.join(tokens)
=======
                    result.append(f"({expanded})")
                else:
                    result.append(ident)
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)
>>>>>>> Stashed changes

    def _expand_char_classes(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == '[':
                j = i + 1
                class_expr = ''
                while j < len(expr) and expr[j] != ']':
                    class_expr += expr[j]
                    j += 1
                expanded = self._expand_class_content(class_expr)
                result.append('(' + '|'.join(expanded) + ')')
                i = j + 1
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)

    def _expand_class_content(self, content):
        expanded = []
        i = 0
        while i < len(content):
<<<<<<< Updated upstream
            if i + 2 < len(content) and content[i + 1] == '-':
                start = content[i]
                end = content[i + 2]
                expanded.extend([chr(c) for c in range(ord(start), ord(end) + 1)])
=======
            if i + 2 < len(content) and content[i+1] == '-':
                start, end = content[i], content[i+2]
                expanded.extend([chr(c) for c in range(ord(start), ord(end)+1)])
>>>>>>> Stashed changes
                i += 3
            else:
                expanded.append(content[i])
                i += 1
        return expanded

    def _expand_plus(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i + 1 < len(expr) and expr[i + 1] == '+':
<<<<<<< Updated upstream
                c = expr[i]
                if c == ')':
                    group = ''
                    count = 0
                    j = i
                    while j >= 0:
                        if expr[j] == ')': count += 1
                        if expr[j] == '(': count -= 1
                        group = expr[j] + group
                        if count == 0:
                            break
=======
                if expr[i] == ')':
                    group, j, count = '', i, 0
                    while j >= 0:
                        if expr[j] == ')': count += 1
                        elif expr[j] == '(': count -= 1
                        group = expr[j] + group
                        if count == 0: break
>>>>>>> Stashed changes
                        j -= 1
                    result = result[:-len(group)]
                    result.append(f"{group}.{group}*")
                    i += 2
                else:
<<<<<<< Updated upstream
=======
                    c = expr[i]
>>>>>>> Stashed changes
                    result.append(f"{c}.{c}*")
                    i += 2
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)

    def _expand_question(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i + 1 < len(expr) and expr[i + 1] == '?':
<<<<<<< Updated upstream
                c = expr[i]
                if c == ')':
                    group = ''
                    count = 0
                    j = i
                    while j >= 0:
                        if expr[j] == ')': count += 1
                        if expr[j] == '(': count -= 1
                        group = expr[j] + group
                        if count == 0:
                            break
=======
                if expr[i] == ')':
                    group, j, count = '', i, 0
                    while j >= 0:
                        if expr[j] == ')': count += 1
                        elif expr[j] == '(': count -= 1
                        group = expr[j] + group
                        if count == 0: break
>>>>>>> Stashed changes
                        j -= 1
                    result = result[:-len(group)]
                    result.append(f"({group}|ε)")
                    i += 2
                else:
<<<<<<< Updated upstream
=======
                    c = expr[i]
>>>>>>> Stashed changes
                    result.append(f"({c}|ε)")
                    i += 2
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)
