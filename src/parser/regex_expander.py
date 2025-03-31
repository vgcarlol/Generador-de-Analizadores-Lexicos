class RegexExpander:
    def __init__(self, let_definitions):
        self.let_definitions = let_definitions
        # Diccionario para almacenar marcadores atómicos (ya casi no usado)
        self.atomic_substitutions = {}

    def normalize(self, expr):
        print(f"🔎 Normalizando: {expr}")
        # 1) Procesar literales entre comillas
        expr = self.process_literals(expr)
        # 2) Expandir los LET (sustituir "digits", "ws", "number", etc.)
        expr = self.expand_lets(expr)
        # 3) Expandir clases de caracteres, luego +, ? 
        expr = self._expand_char_classes(expr)
        expr = self._expand_plus(expr)
        expr = self._expand_question(expr)
        # (Opcional) Intentar corregir paréntesis mal balanceados
        expr = self._validate_and_balance_parentheses(expr)

        # Reemplazar marcadores si hubiera (ya no usamos <FINAL>, idealmente)
        for marker, pattern in self.atomic_substitutions.items():
            expr = expr.replace(marker, pattern)

        print(f"✅ Resultado final: {expr}")
        return expr

    # ---------------------------------------------------------
    # (1) Manejo de literales entre comillas
    # ---------------------------------------------------------
    def process_literals(self, expr):
        result = ""
        i = 0
        special_set = {"(", ")", "*", "+", ":", "."}
        while i < len(expr):
            if expr[i] == "'":
                literal = ""
                i += 1
                while i < len(expr) and expr[i] != "'":
                    literal += expr[i]
                    i += 1
                if i < len(expr) and expr[i] == "'":
                    i += 1  # saltar la comilla de cierre
                # si es un caracter especial, lo escapamos
                if len(literal) == 1 and literal in special_set:
                    result += "\\" + literal
                    print(f"📌 Escapando literal especial: '{literal}' -> \\{literal}")
                else:
                    result += literal
                    print(f"🔎 Desempaquetando literal compuesto: '{literal}' -> {literal}")
            else:
                result += expr[i]
                i += 1
        return result

    # ---------------------------------------------------------
    # (2) Expandir LETS 
    # ---------------------------------------------------------
    def expand_lets(self, expr):
        def expand(subexpr):
            result = []
            i = 0
            while i < len(subexpr):
                if subexpr[i].isalpha():
                    ident = ''
                    # extraer la palabra
                    while i < len(subexpr) and (subexpr[i].isalnum() or subexpr[i] == '_'):
                        ident += subexpr[i]
                        i += 1
                    # Si ident está en let_definitions
                    if ident in self.let_definitions:
                        if ident == 'ws':
                            # Manejo especial del whitespace
                            marker = "\uF001"
                            final_ws = "[ \\t\\n\\r]+"
                            self.atomic_substitutions[marker] = final_ws
                            result.append(marker)
                        elif ident == 'number':
                            # Llamamos a _freeze_number
                            expanded_number = self._freeze_number(self.let_definitions[ident])
                            result.append(expanded_number)
                        else:
                            # Expansión normal
                            expanded_def = self.let_definitions[ident]
                            print(f"🔁 Expandiendo '{ident}' como '{expanded_def}'")
                            subexpansion = expand(expanded_def)
                            print(f"👉 Resultado de expandir '{ident}': '{subexpansion}'")
                            result.append(subexpansion)
                    else:
                        # No está en let_definitions, lo copiamos tal cual
                        result.append(ident)
                else:
                    result.append(subexpr[i])
                    i += 1
            return ''.join(result)

        expanded = expand(expr)
        print(f"🔄 Expansión completa: '{expr}' -> '{expanded}'")
        return expanded

    def _freeze_number(self, token_expr):
        print(f"🔁 Sellando token de número: {token_expr}")
        # Expande "digits('\.'digits)?('E'['+''-']?digits)?", etc.
        expanded_inner = self.expand_lets(token_expr)
        # Simplemente devolvemos expanded_inner tal cual 
        # (sin <FINAL>…</FINAL>), para no meter < y >.
        return expanded_inner

    # ---------------------------------------------------------
    # (3) Expandir char classes, +, ? 
    # ---------------------------------------------------------
    def _expand_char_classes(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == '[':
                j = i + 1
                class_expr = ''
                bracket_level = 1
                while j < len(expr) and bracket_level > 0:
                    if expr[j] == ']' and bracket_level == 1:
                        break
                    if expr[j] == '[':
                        bracket_level += 1
                    elif expr[j] == ']':
                        bracket_level -= 1
                    class_expr += expr[j]
                    j += 1
                if j >= len(expr) or expr[j] != ']':
                    print(f"⚠️ Clase mal formada, sin cierre: [{class_expr}")
                    result.append('[' + class_expr)
                    i = j
                else:
                    # [ ... ] bien formado
                    if "'" not in class_expr:
                        # lo dejamos tal cual
                        result.append(expr[i:j+1])
                    else:
                        # expandir los literales con _expand_class_content
                        expanded = self._expand_class_content(class_expr)
                        result.append('(' + '|'.join(self._escape_char(c) for c in expanded) + ')')
                    i = j + 1
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)

    def _expand_plus(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i+1 < len(expr) and expr[i+1] == '+':
                print(f"[DEBUG _expand_plus] Pos={i}, encontré '+': alrededor='{expr[i:i+2]}' | expr=«{expr}»")
                if expr[i] == '\\':
                    # Caso \.+
                    print(f"[DEBUG _expand_plus] --> Hallado literal escapado '{expr[i:i+2]}'. NO expandimos.")
                    result.append(expr[i])
                    result.append(expr[i+1])
                    i += 2
                elif expr[i] == ')':
                    # Caso ( ... )+
                    j = i
                    count = 1
                    while j > 0:
                        j -= 1
                        if expr[j] == ')':
                            count += 1
                        elif expr[j] == '(':
                            count -= 1
                            if count == 0:
                                break
                    if count == 0:
                        group = expr[j : i+1]
                        print(f"[DEBUG _expand_plus] --> Expandiendo grupo '{group}+' -> '({group}.{group}*)'")
                        group_len = len(group)
                        result = result[:-group_len]
                        result.append(f"({group}.{group}*)")
                    else:
                        print(f"⚠️ [DEBUG _expand_plus] no encontré '(' que empareje antes de '+'.")
                        # dejamos tal cual
                        result.append(expr[i])
                        result.append(expr[i+1])
                    i += 2
                else:
                    # Caso normal: a+
                    c = expr[i]
                    print(f"[DEBUG _expand_plus] --> Expandiendo '{c}+' -> '({c}.{c}*)'")
                    result.append(f"({c}.{c}*)")
                    i += 2
            else:
                result.append(expr[i])
                i += 1
        expanded_expr = ''.join(result)
        print(f"[DEBUG _expand_plus] Resultado final => «{expanded_expr}»")
        return expanded_expr

    def _expand_question(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i+1 < len(expr) and expr[i+1] == '?':
                print(f"[DEBUG _expand_question] Pos={i}, encontré '?': '{expr[i:i+2]}' | expr=«{expr}»")
                if expr[i] == '\\':
                    print(f"[DEBUG _expand_question] --> Hallado literal escapado '{expr[i:i+2]}'. NO expandimos.")
                    result.append(expr[i])
                    result.append(expr[i+1])
                    i += 2
                elif expr[i] == ')':
                    # Caso ( ... )?
                    j = i
                    count = 1
                    while j > 0 and count > 0:
                        j -= 1
                        if expr[j] == ')':
                            count += 1
                        elif expr[j] == '(':
                            count -= 1
                    if j >= 0 and count == 0:
                        group = expr[j : i+1]
                        group_len = len(group)
                        result = result[:-group_len]
                        print(f"[DEBUG _expand_question] --> Expandiendo '{group}?' -> '({group}|ε)'")
                        result.append(f"({group}|ε)")
                    else:
                        print(f"⚠️ [DEBUG _expand_question] no hallé '(' que empareje para '?'.")
                        result.append(expr[i])
                        result.append(expr[i+1])
                    i += 2
                else:
                    # Caso normal: a?
                    c = expr[i]
                    print(f"[DEBUG _expand_question] --> Expandiendo '{c}?' -> '({c}|ε)'")
                    result.append(f"({c}|ε)")
                    i += 2
            else:
                result.append(expr[i])
                i += 1
        expanded_expr = ''.join(result)
        print(f"[DEBUG _expand_question] Resultado final => «{expanded_expr}»")
        return expanded_expr

    # ---------------------------------------------------------
    # (Opcional) Corregir paréntesis sueltos
    # ---------------------------------------------------------
    def _validate_and_balance_parentheses(self, expr):
        stack = []
        fixed_expr = list(expr)
        i = 0
        while i < len(fixed_expr):
            char = fixed_expr[i]
            if char == '\\':
                i += 2
                continue
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    stack.pop()
                else:
                    print(f"🔻 Paréntesis de cierre sin abrir en posición {i}: '{expr}'")
                    fixed_expr[i] = '#'
            i += 1

        # Paréntesis de apertura sin cierre
        while stack:
            pos = stack.pop()
            print(f"🔻 Paréntesis de apertura sin cerrar en posición {pos}: '{expr}'")
            fixed_expr[pos] = '#'

        result = ''.join(c for c in fixed_expr if c != '#')
        if result != expr:
            print(f"🛠️ Expresión corregida: '{expr}' -> '{result}'")
        return result

    # ---------------------------------------------------------
    # Funciones auxiliares
    # ---------------------------------------------------------
    def _escape_char(self, c):
        if c in {'(', ')', '*', '+', '|', '.', '?', '\\'}:
            return '\\' + c
        elif c == '\n':
            return '\\n'
        elif c == '\t':
            return '\\t'
        elif c == '\r':
            return '\\r'
        elif c == '\f':
            return '\\f'
        elif c == ' ':
            return ' '
        return c

    def _expand_class_content(self, content):
        content = content.strip()
        expanded = []
        i = 0

        def parse_char(start):
            if start >= len(content) or content[start] != "'":
                return None, 1
            if start + 1 >= len(content):
                return None, 1
            if content[start+1] == "'":
                # '' -> nada
                return "", 2
            if content[start+1] == '\\':
                # \n, etc.
                if start+3 >= len(content) or content[start+3] != "'":
                    return None, 1
                token = content[start+1:start+3]
                return self._unescape_char(token), 4
            else:
                if start+2 >= len(content) or content[start+2] != "'":
                    return None, 1
                return content[start+1], 3

        while i < len(content):
            if content[i] == "'":
                ch1, len1 = parse_char(i)
                if ch1 is None or ch1 == "":
                    i += len1
                    continue
                i += len1
                # Rango 'a'-'z'
                if i+1 < len(content) and content[i] == '-' and content[i+1] == "'":
                    ch2, len2 = parse_char(i+1)
                    if ch2 is not None and ch2 != "":
                        char_range = [chr(c) for c in range(ord(ch1), ord(ch2)+1)]
                        print(f"📊 Rango de '{ch1}'-'{ch2}' -> {char_range}")
                        expanded.extend(char_range)
                        i += len2 + 1
                        continue
                expanded.append(ch1)
            else:
                i += 1

        return expanded
