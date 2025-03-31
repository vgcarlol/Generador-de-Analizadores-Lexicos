class RegexExpander:
    def __init__(self, let_definitions):
        self.let_definitions = let_definitions
        self.atomic_substitutions = {}


class RegexExpander:
    def __init__(self, let_definitions):
        self.let_definitions = let_definitions
        # Diccionario para almacenar marcadores atómicos
        self.atomic_substitutions = {}

    def normalize(self, expr):
        print(f"🔎 Normalizando: {expr}")
        # Paso 1: Procesar literales
        expr = self.process_literals(expr)
        # Paso 2: Expandir LETS (aquí se insertan los marcadores para ws y number)
        expr = self.expand_lets(expr)
        # Paso 3: Expandir clases de caracteres, +, ? y balancear paréntesis
        expr = self._expand_char_classes(expr)
        expr = self._expand_plus(expr)
        expr = self._expand_question(expr)
        expr = self._validate_and_balance_parentheses(expr)
        # Reemplazar los marcadores atómicos (sellados) por sus patrones finales
        for marker, pattern in self.atomic_substitutions.items():
            expr = expr.replace(marker, pattern)
        print(f"✅ Resultado final: {expr}")
        return expr

    def process_literals(self, expr):
        """
        Procesa la cadena expr para detectar fragmentos entre comillas simples.
        Si el contenido es de un solo carácter y es uno de los símbolos que deben tratarse como literales
        (por ejemplo: (, ), *, +, :, .), lo escapa; en caso contrario, devuelve el contenido sin las comillas.
        """
        result = ""
        i = 0
        # Los símbolos que queremos que se traten como literales
        special_set = {"(", ")", "*", "+", ":", "."}
        while i < len(expr):
            if expr[i] == "'":
                literal = ""
                i += 1  # Saltamos la comilla de apertura
                while i < len(expr) and expr[i] != "'":
                    literal += expr[i]
                    i += 1
                # Saltar la comilla de cierre (si existe)
                if i < len(expr) and expr[i] == "'":
                    i += 1
                inner = literal  # Contenido sin las comillas
                # Si es un solo carácter que está en el conjunto especial, lo escapamos.
                if len(inner) == 1 and inner in special_set:
                    result += "\\" + inner
                    print(f"📌 Escapando literal especial: '{literal}' -> \\{inner}")
                else:
                    result += inner
                    print(f"🔎 Desempaquetando literal compuesto: '{literal}' -> {inner}")
            else:
                result += expr[i]
                i += 1
        return result


    def _strip_quotes(self, expr):
        expr = expr.strip()
        if len(expr) >= 2 and expr[0] == expr[-1] and expr[0] in ("'", '"'):
            inner = expr[1:-1]
            if len(inner) == 1 and inner in {'(', ')', '*', '+', '|', '.', '?'}:
                print(f"📌 Escapando literal especial: '{inner}' -> \\{inner}")
                return f"\\{inner}"
            elif len(inner) > 1:
                print(f"🔎 Desempaquetando literal compuesto: '{expr}' -> {inner}")
            return ''.join(inner)

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
                        # Intercepción especial para 'ws' y 'number'
                        if ident == 'ws':
                            marker = "\uF001"
                            final_ws = "[ \\t\\n\\r]+"
                            self.atomic_substitutions[marker] = final_ws
                            result.append(marker)
                            continue
                        elif ident == 'number':
                            # Usamos la nueva función para sellar el patrón de número
                            protected = self._freeze_number(self.let_definitions[ident])
                            result.append(protected)
                            continue
                        else:
                            expanded = self.let_definitions[ident]
                            print(f"🔁 Expandiendo '{ident}' como '{expanded}'")
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

    def _freeze_number(self, token_expr):
        """
        Expande recursivamente la definición interna de número y la "sella"
        para que no sea alterada por expansiones posteriores.
        """
        expanded_inner = self.expand_lets(token_expr)
        # En lugar de aplicar _expand_plus o _expand_question, simplemente se sella:
        protected = f"<FINAL>{expanded_inner}</FINAL>"
        print(f"🔁 Sellando token de número: {token_expr} -> {protected}")
        # Guardamos en atomic_substitutions para luego reemplazar la marca
        self.atomic_substitutions[f"<FINAL>{expanded_inner}</FINAL>"] = expanded_inner
        return f"<FINAL>{expanded_inner}</FINAL>"

    def _expand_whitespace_token(self, token_expr):
        if token_expr.endswith('+'):
            base = token_expr[:-1]
        else:
            base = token_expr
        if base in self.let_definitions:
            base_expanded = self.expand_lets(self.let_definitions[base])
        else:
            base_expanded = base
        content = base_expanded.strip().strip("[]").replace("'", "").replace(",", "").strip()
        regex_class = f"[{content}]"
        expanded = f"({regex_class})+"
        protected = f"<FINAL>{expanded}</FINAL>"
        print(f"🔁 Expandiendo token de whitespace: {token_expr} -> {protected}")
        return protected

    def _expand_number_token(self, token_expr):
        expanded_inner = self.expand_lets(token_expr)
        expanded = f"({expanded_inner})"
        protected = f"<FINAL>{expanded}</FINAL>"
        print(f"🔁 Expandiendo token de número: {token_expr} -> {protected}")
        return protected

    def _expand_char_classes(self, expr):
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == '[':
                j = i + 1
                class_expr = ''
                bracket_level = 1  # Por si hay anidamiento (aunque no es estándar)
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
                    # Si el contenido NO tiene comillas simples, lo dejamos intacto.
                    if "'" not in class_expr:
                        result.append(expr[i:j+1])
                    else:
                        expanded = self._expand_class_content(class_expr)
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
        # Quitar espacios en blanco al inicio y al final
        content = content.strip()
        expanded = []
        i = 0

        def parse_char(start):
            if start >= len(content) or content[start] != "'":
                return None, 1
            if start + 1 >= len(content):
                return None, 1
            # Si se encuentran dos comillas consecutivas, interpretamos que es un literal vacío
            if content[start + 1] == "'":
                return "", 2
            if content[start + 1] == '\\':  # secuencia de escape
                if start + 3 >= len(content) or content[start + 3] != "'":
                    return None, 1
                token = content[start + 1:start + 3]  # ejemplo: \n
                return self._unescape_char(token), 4
            else:  # carácter normal
                if start + 2 >= len(content) or content[start + 2] != "'":
                    return None, 1
                return content[start + 1], 3

        while i < len(content):
            if content[i] == "'":
                ch1, len1 = parse_char(i)
                # Si el literal es None o está vacío, se descarta para evitar alternativas vacías
                if ch1 is None or ch1 == "":
                    i += len1
                    continue
                i += len1
                if i + 1 < len(content) and content[i] == '-' and content[i + 1] == "'":
                    ch2, len2 = parse_char(i + 1)
                    if ch2 is not None and ch2 != "":
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
        """
        Reescribe 'a+' como '(a)(a)*' y '(...)+' como '((...))((...)*)',
        pero si 'a' es un literal escapado como '\.', no expandimos,
        para no destruir el literal que disingue '.' del operador de concat.
        """
        result = []
        i = 0
        while i < len(expr):
            # Verifica si viene un '+' inmediato
            if i + 1 < len(expr) and expr[i+1] == '+':
                print(f"[DEBUG _expand_plus] Pos={i}, encontré '+': alrededor='{expr[i:i+2]}' | expr=«{expr}»")
                
                # 1) Caso: si es una secuencia escapada, p.ej. '\.'
                if expr[i] == '\\':
                    # Ejemplo:  '\.'+  => lo consideramos un literal escapado, no expandir
                    print(f"[DEBUG _expand_plus] --> Hallado literal escapado '{expr[i:i+2]}'. NO expandimos.")
                    # Copiamos tal cual '\.' y '+'
                    result.append(expr[i])     # '\'
                    result.append(expr[i+1])   # '.'
                    # Ojo: la variable i+1 es '+', la siguiente es i+2
                    # en expr[i:i+2], i+1 era '+', no '.' (depende del string real)
                    # De modo que hay que tener cuidado:
                    #   si la expresión era "\.+", en expr[i] tienes '\', en expr[i+1] tienes '.'
                    #   pero 'expr[i+1] == '+' se contradiría con "'.' == '+'"? 
                    #   Revisa si en tu grammar saldría algo como '\.'+ sin separar.
                    
                    # Para mayor robustez, chequemos el siguiente carácter
                    # (el "escaped" en realidad es expr[i+1]?) 
                    # Con logs, verás si funciona como esperas.
                    
                    i += 2
                # 2) Caso: '(...)+' (grupo)
                elif expr[i] == ')':
                    # Buscar la '(' correspondiente
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
                        group = expr[j : i+1]  # e.g. "(abc)"
                        print(f"[DEBUG _expand_plus] --> Expandiendo grupo '{group}+' como '({group}.{group}*)'")
                        # Removemos ese substring del result
                        group_len = len(group)
                        result = result[:-group_len]
                        # Insertamos la expansión
                        result.append(f"({group}.{group}*)")
                    else:
                        print(f"⚠️ [DEBUG _expand_plus] Error: no encontré '(' que empareje antes de '+'. No expando.")
                        # Simplemente lo dejamos tal cual
                        result.append(expr[i])
                        result.append(expr[i+1])
                    i += 2
                else:
                    # 3) Caso normal: 'a+' => '(a)(a)*'
                    c = expr[i]
                    print(f"[DEBUG _expand_plus] --> Expandiendo '{c}+' como '({c}.{c}*)'")
                    result.append(f"({c}.{c}*)")
                    i += 2
            else:
                # No hay '+', se copia tal cual
                result.append(expr[i])
                i += 1

        expanded_expr = ''.join(result)
        print(f"[DEBUG _expand_plus] Resultado final => «{expanded_expr}»")
        return expanded_expr

    def _expand_question(self, expr):
        """
        Reescribe 'a?' como '(a|ε)' y '(...)?' como '((...)|ε)'.
        Pero si 'a' es un literal escapado como '\.', no expandimos.
        """
        result = []
        i = 0
        while i < len(expr):
            # Verifica si viene un '?' inmediato
            if i + 1 < len(expr) and expr[i+1] == '?':
                print(f"[DEBUG _expand_question] Pos={i}, encontré '?': alrededor='{expr[i:i+2]}' | expr=«{expr}»")
                
                # 1) Caso: si es secuencia escapada, p.ej. '\.'
                if expr[i] == '\\':
                    print(f"[DEBUG _expand_question] --> Hallado literal escapado '{expr[i:i+2]}'. NO expandimos.")
                    result.append(expr[i])
                    result.append(expr[i+1])
                    i += 2
                # 2) Caso '(...)?'
                elif expr[i] == ')':
                    # Buscar la '(' correspondiente
                    j = i
                    count = 1
                    while j > 0 and count > 0:
                        j -= 1
                        if expr[j] == ')':
                            count += 1
                        elif expr[j] == '(':
                            count -= 1
                            
                    if j >= 0 and count == 0:
                        group = expr[j : i+1]  # e.g. "(xyz)"
                        # Removerlo de result
                        group_len = len(group)
                        result = result[:-group_len]
                        print(f"[DEBUG _expand_question] --> Expandiendo grupo '{group}?' como '({group}|ε)'")
                        result.append(f"({group}|ε)")
                    else:
                        print(f"⚠️ [DEBUG _expand_question] Error al expandir '?': No hallé '(' que empareje.")
                        # Dejarlo tal cual
                        result.append(expr[i])
                        result.append(expr[i+1])
                    i += 2
                else:
                    # 3) Caso normal: 'a?' => '(a|ε)'
                    c = expr[i]
                    print(f"[DEBUG _expand_question] --> Expandiendo '{c}?' como '({c}|ε)'")
                    result.append(f"({c}|ε)")
                    i += 2
            else:
                # No hay '?', copiamos tal cual
                result.append(expr[i])
                i += 1
        
        expanded_expr = ''.join(result)
        print(f"[DEBUG _expand_question] Resultado final => «{expanded_expr}»")
        return expanded_expr

    
    def _validate_and_balance_parentheses(self, expr):
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
    

    def _process_embedded_literals(self, expr):
        """
        Procesa manualmente la cadena 'expr' para detectar fragmentos entre comillas simples
        y, en caso de que sean literales especiales (de un solo carácter entre ' y '), los
        reemplaza por su versión escapada (por ejemplo, convierte '.' en '\.').
        """
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == "'":
                # Encontramos el inicio de un literal
                literal = ""
                literal += expr[i]  # añade la comilla de apertura
                i += 1
                # Acumular el contenido hasta la siguiente comilla
                while i < len(expr) and expr[i] != "'":
                    literal += expr[i]
                    i += 1
                # Añadir la comilla de cierre (si existe)
                if i < len(expr) and expr[i] == "'":
                    literal += expr[i]
                    i += 1
                # Procesar el literal
                inner = literal[1:-1]  # contenido sin las comillas
                if len(inner) == 1 and inner in {'(', ')', '*', '+', '|', '.', '?'}:
                    # Si es un literal especial de un solo carácter, escaparlo
                    escaped = "\\" + inner
                    print(f"📌 Escapando literal especial: {literal} -> {escaped}")
                    result.append(escaped)
                else:
                    # Si es un literal compuesto, lo dejamos tal cual (o lo procesamos como requieras)
                    print(f"🔎 Desempaquetando literal compuesto: {literal} -> {inner}")
                    result.append(inner)
            else:
                result.append(expr[i])
                i += 1
        return ''.join(result)