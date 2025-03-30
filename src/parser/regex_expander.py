class RegexExpander:
    def __init__(self, let_definitions):
        self.let_definitions = let_definitions

    def normalize(self, expr):
        print(f"🔎 Normalizando: {expr}")
        
        # Paso 1: quitar comillas
        expr = self._strip_quotes(expr)

        # Paso 2: expandir lets primero
        expr = self.expand_lets(expr)

        # Paso 3: expandir clases de caracteres (['a''b''c']) -> (a|b|c)
        expr = self._expand_char_classes(expr)

        # Paso 4: expandir operadores como + y ?
        expr = self._expand_plus(expr)
        expr = self._expand_question(expr)

        # Paso 5: balancear paréntesis
        expr = self._validate_and_balance_parentheses(expr)

        print(f"✅ Resultado final: {expr}")
        return expr


    def _strip_quotes(self, expr):
        expr = expr.strip()
        if len(expr) >= 2 and expr[0] == expr[-1] and expr[0] in ("'", '"'):
            inner = expr[1:-1]
            if len(inner) == 1 and inner in {'(', ')', '*', '+', '|', '.', '?'}:
                print(f"📌 Escapando literal especial: '{inner}' -> \\{inner}")
                return f"\\{inner}"
            return inner
        if expr in {'(', ')', '*', '+', '|', '.', '?'}:
            print(f"📌 Escapando símbolo especial sin comillas: '{expr}' -> \\{expr}")
            return f"\\{expr}"
        return expr

    def expand_lets(self, expr):
        def expand(expr):
            result = []
            i = 0
            while i < len(expr):
                if expr[i].isalpha():
                    ident = ''
                    while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                        ident += expr[i]
                        i += 1
                    if ident in self.let_definitions:
                        expanded = self.let_definitions[ident]
                        print(f"🔁 Expandiendo '{ident}' como '{expanded}'")
                        # Importante: No añadir paréntesis extras aquí
                        expanded_result = expand(expanded)
                        print(f"👉 Resultado de expandir '{ident}': '{expanded_result}'")
                        result.append(expanded_result)
                    else:
                        result.append(ident)
                else:
                    result.append(expr[i])
                    i += 1
            return ''.join(result)
        
        expanded = expand(expr)
        print(f"🔄 Expansión completa: '{expr}' -> '{expanded}'")
        return expanded

    def _expand_char_classes(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == '[':
                j = i + 1
                class_expr = ''
                bracket_level = 1  # Por si acaso hay anidamiento extraño (aunque no es estándar)

                while j < len(expr) and bracket_level > 0:
                    if expr[j] == ']' and bracket_level == 1:
                        break
                    class_expr += expr[j]
                    j += 1

                if j >= len(expr) or expr[j] != ']':
                    print(f"⚠️ Clase mal formada, sin cierre: [{class_expr}")
                    result.append('[' + class_expr)
                    i = j
                else:
                    expanded = self._expand_class_content(class_expr)
                    printable = ''.join(f"'{c}'" for c in expanded)
                    print(f"🧱 Expandida clase [{class_expr}] -> ({'|'.join(expanded)})")

                    result.append('(' + '|'.join(self._escape_char(c) for c in expanded) + ')')
                    i = j + 1
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)



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
            return ' '  # Espacio visible
        return c

    def _expand_class_content(self, content):
        expanded = []
        i = 0

        def parse_char(start):
            if start >= len(content) or content[start] != "'":
                return None, 1
            if start + 2 >= len(content):
                return None, 1
            if content[start + 1] == '\\':  # escape
                if start + 3 >= len(content) or content[start + 3] != "'":
                    return None, 1
                token = content[start + 1:start + 3]  # example: \n
                return self._unescape_char(token), 4
            else:  # regular char
                if start + 2 >= len(content) or content[start + 2] != "'":
                    return None, 1
                return content[start + 1], 3

        while i < len(content):
            if i < len(content) and content[i] == "'":
                ch1, len1 = parse_char(i)
                if ch1 is None:
                    i += 1
                    continue
                
                i += len1
                if i + 1 < len(content) and content[i] == '-' and content[i + 1] == "'":
                    ch2, len2 = parse_char(i + 1)
                    if ch2 is not None:
                        # Generar el rango de caracteres
                        char_range = [chr(c) for c in range(ord(ch1), ord(ch2) + 1)]
                        print(f"📊 Rango de caracteres: '{ch1}'-'{ch2}' -> {char_range}")
                        expanded.extend(char_range)
                        i += len2 + 1  # +1 por el '-'
                        continue
                
                expanded.append(ch1)
            else:
                i += 1
                
        return expanded

    def _unescape_char(self, token):
        if token == r'\n': return '\n'
        if token == r'\t': return '\t'
        if token == r'\r': return '\r'
        if token == r'\f': return '\f'
        if token == r'\\': return '\\'
        if token == r"\'": return "'"
        if len(token) == 2 and token[0] == '\\':
            return token[1]
        return token

    def _expand_plus(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i + 1 < len(expr) and expr[i + 1] == '+':
                if expr[i] == ')':
                    # Buscar el paréntesis de apertura correspondiente
                    j = i
                    count = 1
                    while j >= 0 and count > 0:
                        j -= 1
                        if expr[j] == ')':
                            count += 1
                        elif expr[j] == '(':
                            count -= 1

                    if j >= 0 and count == 0:
                        group = expr[j:i+1]
                        result = result[:-len(group)]
                        result.append(f"({group}.{group}*)")
                        print(f"➕ Expandiendo grupo {group}+ -> ({group}.{group}*)")
                        i += 2
                        continue
                    else:
                        print(f"⚠️ Error: '+' después de paréntesis no balanceados en {expr[i]}+")
                else:
                    c = expr[i]
                    result.append(f"({c}.{c}*)")
                    print(f"➕ Expandiendo '{c}+' -> '({c}.{c}*)'")
                    i += 2
                    continue
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)



    def _expand_question(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if i + 1 < len(expr) and expr[i + 1] == '?':
                if expr[i] == ')':
                    # Buscar el paréntesis de apertura correspondiente
                    j = i
                    count = 1  # Ya tenemos un paréntesis de cierre
                    while j > 0 and count > 0:
                        j -= 1
                        if expr[j] == ')':
                            count += 1
                        elif expr[j] == '(':
                            count -= 1
                    
                    if j >= 0 and count == 0:
                        group = expr[j:i+1]  # Incluir los paréntesis
                        
                        # Eliminar el grupo original
                        result = result[:-len(group)]
                        
                        # Agregar la expansión de a? como (a|ε)
                        result.append(f"({group}|ε)")
                        print(f"❓ Expandiendo '{group}?' -> '({group}|ε)'")
                    else:
                        # Error: no se encontró el paréntesis de apertura
                        result.append(expr[i])
                        result.append(expr[i+1])
                        print(f"⚠️ Error al expandir '?': No se encontró paréntesis de apertura para ')?' en posición {i}")
                    i += 2
                else:
                    c = expr[i]
                    result.append(f"({c}|ε)")
                    print(f"❓ Expandiendo '{c}?' -> '({c}|ε)'")
                    i += 2
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)
    
    def _validate_and_balance_parentheses(self, expr):
        """Verifica y corrige paréntesis desbalanceados ignorando escapes como \( o \)"""
        stack = []
        fixed_expr = list(expr)
        i = 0

        # Primera pasada: marcar paréntesis problemáticos
        while i < len(fixed_expr):
            char = fixed_expr[i]
            if char == '\\':
                i += 2  # Saltar el carácter escapado y el siguiente
                continue
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    stack.pop()
                else:
                    print(f"🔻 Paréntesis de cierre sin abrir en posición {i}: '{expr}'")
                    fixed_expr[i] = '#'  # Marcar para eliminar
            i += 1

        # Marcar paréntesis de apertura sin cierre
        while stack:
            pos = stack.pop()
            print(f"🔻 Paréntesis de apertura sin cerrar en posición {pos}: '{expr}'")
            fixed_expr[pos] = '#'  # Marcar para eliminar

        # Segunda pasada: eliminar los marcados
        result = ''.join(c for c in fixed_expr if c != '#')

        if result != expr:
            print(f"🛠️ Expresión corregida: '{expr}' -> '{result}'")

        return result