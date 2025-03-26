import os
import sys
from regex_parser import RegexParser
from direct_construction import DirectAFDConstructor
from minimization import AFDMinimizer
from visualization import visualize_afd, visualize_syntax_tree

# Función para eliminar comentarios delimitados por "(*" y "*)"
def remove_comments(text):
    while True:
        start = text.find("(*")
        if start == -1:
            break
        end = text.find("*)", start + 2)
        if end == -1:
            break
        text = text[:start] + text[end+2:]
    return text

# Función para extraer el header (contenido entre llaves al inicio)
def extract_header(text):
    stripped = text.lstrip()
    if stripped.startswith("{"):
        end = stripped.find("}")
        if end != -1:
            return stripped[1:end].strip()
    return ""

# Función para extraer el trailer (contenido entre llaves al final)
def extract_trailer(text):
    text_rstrip = text.rstrip()
    last_close = text_rstrip.rfind("}")
    if last_close != -1:
        last_open = text_rstrip.rfind("{", 0, last_close)
        if last_open != -1:
            trailer_candidate = text_rstrip[last_open+1:last_close].strip()
            if ("rule" in trailer_candidate.lower()) or ("let" in trailer_candidate.lower()):
                return ""
            else:
                return trailer_candidate
    return ""

# Función para extraer las definiciones (líneas que comienzan con "let ")
def extract_definitions(text):
    definitions = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("let "):
            eq_index = line.find("=")
            if eq_index != -1:
                name = line[4:eq_index].strip()
                regex_def = line[eq_index+1:].strip()
                definitions[name] = regex_def
    return definitions

# Función para extraer el bloque de reglas
def extract_rules(text):
    rules = []
    lower = text.lower()
    rule_index = lower.find("rule")
    if rule_index != -1:
        after_rule = text[rule_index:]
        sep = "\n{"
        end_index = after_rule.find(sep)
        if end_index == -1:
            rule_block = after_rule
        else:
            rule_block = after_rule[:end_index]
        eq_index = rule_block.find("=")
        if eq_index != -1:
            rule_block = rule_block[eq_index+1:].strip()
        lines = [line.strip() for line in rule_block.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("|"):
                line = line[1:].strip()
            last_open = line.rfind("{")
            last_close = line.rfind("}")
            if last_open != -1 and last_close != -1 and last_close > last_open:
                regex_rule = line[:last_open].strip()
                action = line[last_open+1:last_close].strip()
                if regex_rule:
                    rules.append((regex_rule, action))
            else:
                if line:
                    rules.append((line, ""))
    return rules

# Función para extraer tokens entre comillas
def extract_quoted_tokens(inner):
    tokens = []
    i = 0
    while i < len(inner):
        if inner[i] in ("'", '"'):
            quote = inner[i]
            i += 1
            start = i
            while i < len(inner) and inner[i] != quote:
                i += 1
            token = inner[start:i]
            tokens.append(token)
            i += 1
        else:
            i += 1
    return tokens

# Función para convertir una definición de conjunto
def convert_set(def_str):
    def_str = def_str.strip()
    if def_str.startswith('[') and def_str.endswith(']'):
        inner = def_str[1:-1].strip()
        tokens = extract_quoted_tokens(inner)
        if tokens:
            if len(tokens) >= 2 and len(tokens) % 2 == 0:
                ranges = []
                for i in range(0, len(tokens), 2):
                    start = tokens[i]
                    end = tokens[i+1]
                    ranges.append(f"{start}-{end}")
                return "[" + "".join(ranges) + "]"
            else:
                return "[" + "".join(tokens) + "]"
        else:
            return "[" + inner.replace(" ", "") + "]"
    return def_str

# Función para reemplazar ocurrencias de una palabra completa
def replace_word(text, word, replacement):
    result = ""
    i = 0
    while i < len(text):
        if text[i:i+len(word)] == word:
            before = (i == 0) or (not (text[i-1].isalnum() or text[i-1] == '_'))
            after = (i+len(word) >= len(text)) or (not (text[i+len(word)].isalnum() or text[i+len(word)] == '_'))
            if before and after:
                result += replacement
                i += len(word)
                continue
        result += text[i]
        i += 1
    return result

# Función para escapar una cadena
def escape_string(s):
    specials = ".^$*+?{}[]\\|()"
    escaped = ""
    for ch in s:
        if ch in specials:
            escaped += "\\" + ch
        else:
            escaped += ch
    return escaped

def parse_yalex_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = remove_comments(content)
    header = extract_header(content)
    trailer = extract_trailer(content)
    definitions = extract_definitions(content)
    rules = extract_rules(content)
    return header, definitions, rules, trailer

# Serializa el AFD usando claves de tipo cadena
def serialize_afd(state):
    visited = {}
    queue = [state]

    while queue:
        s = queue.pop(0)
        sid = str(s.id)

        if sid in visited:
            continue

        visited[sid] = {
            "is_final": s.is_final,
            "transitions": {}
        }

        for sym, target in s.transitions.items():
            if sym is not None and sym != "":
                visited[sid]["transitions"][sym] = str(target.id)

                if str(target.id) not in visited:
                    queue.append(target)

    return {"start": str(state.id), "states": visited}



def build_afd_for_rule(regex, definitions):
    # Si la regla coincide con una definición, reemplazarla
    if regex.strip() in definitions:
        regex = definitions[regex.strip()]

    # Reemplazar referencias a definiciones en la expresión regular
    for name in sorted(definitions, key=len, reverse=True):
        def_regex = definitions[name]
        conv = def_regex
        if def_regex.startswith('[') and def_regex.endswith(']'):
            conv = convert_set(def_regex)
        else:
            if not ((conv.startswith("'") and conv.endswith("'")) or 
                    (conv.startswith('"') and conv.endswith('"'))):
                if any(ch in conv for ch in "()*|.?+"):
                    pass
                else:
                    conv = "'" + conv + "'"

        regex = replace_word(regex, name, conv)

    # Convertir la expresión a postfix y construir el AFD
    final_regex = regex.strip()
    regex_postfix = RegexParser.infix_to_postfix(final_regex)
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()

    # 🔥 Agregar un print para depuración
    print(f"\n✅ Generando AFD para: {final_regex}")
    print(f"Postfix: {' '.join(regex_postfix)}")
    print(f"Estados del AFD:")
    for state in afd_constructor.get_afd().transitions:
        print(f"  {state}: {afd_constructor.get_afd().transitions[state]}")

    return afd, final_regex, regex_postfix, afd_constructor.symbol_positions, afd_constructor.syntax_tree


# matches_symbol actualizado para cubrir varios casos
def matches_symbol(sym, ch):
    sym = sym.strip()

    if sym.startswith("'") and sym.endswith("'"):
        sym = sym[1:-1]

    if sym.startswith("[") and sym.endswith("]"):
        return ch in sym[1:-1]

    if sym.startswith("\\"):
        sym = sym[1:]

    if sym in {"+", "-", "=", "(", ")"}:
        return ch == sym  # 🔥 Compara directamente

    return ch == sym


# Función para simular el AFD y obtener la longitud del prefijo aceptado.
def simulate_afd_longest(afd_dict, input_string):
    current = afd_dict['start']
    states = afd_dict['states']
    last_accepted = -1
    pos = 0
    print(f"Probando: {input_string}")
    print(f"Estado inicial: {current}")
    while pos < len(input_string):
        ch = input_string[pos]
        transition_found = False
        # Itera sobre las transiciones del estado actual.
        for sym, target in states[current]['transitions'].items():
            if matches_symbol(sym, ch):
                current = target
                pos += 1
                transition_found = True
                if states[current]['is_final']:
                    last_accepted = pos
                break
        if not transition_found:
            break
    return last_accepted if last_accepted != -1 else 0

def generate_lexer_spec(yalex_file_path, output_file):
    header, definitions, rules, trailer = parse_yalex_file(yalex_file_path)
    print("=== Secciones del archivo YALex ===")
    print("Header:", header)
    print("Definiciones:", definitions)
    print("Reglas:", rules)
    print("Trailer:", trailer)
    rule_info = []
    for idx, (regex_rule, action) in enumerate(rules):
        token_name = f"TOKEN_{idx}"
        afd, final_regex, regex_postfix, mapping, syntax_tree = build_afd_for_rule(regex_rule, definitions)
        serialized_afd = serialize_afd(afd)
        rule_info.append((token_name, serialized_afd, action, final_regex, regex_postfix, mapping, syntax_tree))
    lexer_code = []
    lexer_code.append("# Archivo generado automáticamente por YALex Generator")
    if header:
        for line in header.splitlines():
            lexer_code.append("# " + line)
    lexer_code.append("")
    lexer_code.append("import sys")
    lexer_code.append("")
    # Se incluye la definición de matches_symbol y simulate_afd_longest en el código generado.
    lexer_code.append("def matches_symbol(sym, ch):")
    lexer_code.append("    if len(sym) == 1:")
    lexer_code.append("        return ch == sym")
    lexer_code.append("    if (sym.startswith(\"'\") and sym.endswith(\"'\")) or (sym.startswith('\"') and sym.endswith('\"')):")
    lexer_code.append("        return ch == sym[1:-1]")
    lexer_code.append("    if sym.startswith('\\\\'):")
    lexer_code.append("        return ch == sym[1:]")
    lexer_code.append("    if sym.startswith('[') and sym.endswith(']'):")
    lexer_code.append("        content = sym[1:-1]")
    lexer_code.append("        i = 0")
    lexer_code.append("        while i < len(content):")
    lexer_code.append("            if i + 2 < len(content) and content[i+1] == '-':")
    lexer_code.append("                if content[i] <= ch <= content[i+2]:")
    lexer_code.append("                    return True")
    lexer_code.append("                i += 3")
    lexer_code.append("            else:")
    lexer_code.append("                if content[i] == ch:")
    lexer_code.append("                    return True")
    lexer_code.append("                i += 1")
    lexer_code.append("        return False")
    lexer_code.append("    return ch == sym")
    lexer_code.append("")
    lexer_code.append("def simulate_afd_longest(afd_dict, input_string):")
    lexer_code.append("    current = afd_dict['start']")
    lexer_code.append("    states = afd_dict['states']")
    lexer_code.append("    last_accepted = -1")
    lexer_code.append("    pos = 0")
    lexer_code.append("    while pos < len(input_string):")
    lexer_code.append("        ch = input_string[pos]")
    lexer_code.append("        transition_found = False")
    lexer_code.append("        for sym, target in states[current]['transitions'].items():")
    lexer_code.append("            if matches_symbol(sym, ch):")
    lexer_code.append("                current = target")
    lexer_code.append("                pos += 1")
    lexer_code.append("                transition_found = True")
    lexer_code.append("                if states[current]['is_final']:")
    lexer_code.append("                    last_accepted = pos")
    lexer_code.append("                break")
    lexer_code.append("        if not transition_found:")
    lexer_code.append("            break")
    lexer_code.append("    return last_accepted if last_accepted != -1 else 0")
    lexer_code.append("")
    lexer_code.append("def lex(input_string):")
    lexer_code.append("    tokens = []")
    lexer_code.append("    pos = 0")
    lexer_code.append("    while pos < len(input_string):")
    lexer_code.append("        max_length = 0")
    lexer_code.append("        selected_token = None")
    lexer_code.append("        selected_action = None")
    lexer_code.append("        # Evaluar cada regla (longest match + prioridad)")
    for token_name, serialized_afd, action, final_regex, regex_postfix, mapping, syntax_tree in rule_info:
        lexer_code.append(f"        # Regla {token_name}")
        lexer_code.append(f"        afd_{token_name} = {repr(serialized_afd)}")
        lexer_code.append(f"        length = simulate_afd_longest(afd_{token_name}, input_string[pos:])")
        lexer_code.append("        if length > max_length:")
        lexer_code.append(f"            max_length = length")
        lexer_code.append(f"            selected_token = '{token_name}'")
        lexer_code.append(f"            selected_action = '''{action}'''")
        lexer_code.append("")
    lexer_code.append("        if max_length == 0:")
    lexer_code.append("            print(f'Error léxico en la posición {pos}: {input_string[pos]}')")
    lexer_code.append("            pos += 1")
    lexer_code.append("        else:")
    lexer_code.append("            lexeme = input_string[pos:pos+max_length]")
    lexer_code.append("            tokens.append((selected_token, lexeme, selected_action))")
    lexer_code.append("            pos += max_length")
    lexer_code.append("    return tokens")
    lexer_code.append("")
    lexer_code.append("def main():")
    lexer_code.append("    if len(sys.argv) < 2:")
    lexer_code.append("        print('Uso: python thelexer.py <archivo_de_entrada>')")
    lexer_code.append("        sys.exit(1)")
    lexer_code.append("    with open(sys.argv[1], 'r', encoding='utf-8') as f:")
    lexer_code.append("        input_string = f.read()")
    lexer_code.append("    tokens = lex(input_string)")
    lexer_code.append("    for token in tokens:")
    lexer_code.append("        print(token)")
    lexer_code.append("")
    lexer_code.append("if __name__ == '__main__':")
    lexer_code.append("    main()")
    lexer_code.append("")
    if trailer.strip():
        lexer_code.append('"""')
        lexer_code.append(trailer)
        lexer_code.append('"""')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lexer_code))
    print(f"Archivo lexer generado: {output_file}")
    output_folder = "syntax_trees"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for idx, (token_name, afd, action, final_regex, regex_postfix, mapping, syntax_tree) in enumerate(rule_info):
        tree_filename = os.path.join(output_folder, f"syntax_tree_{token_name}")
        visualize_syntax_tree(syntax_tree, filename=tree_filename)
        print(f"Árbol sintáctico de la regla '{token_name}' guardado en '{tree_filename}.png'.")

def main():
    if len(sys.argv) < 3:
        print("Uso: python yalex_generator.py <archivo_yalex> <archivo_salida>")
        sys.exit(1)
    yalex_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_lexer_spec(yalex_file, output_file)

if __name__ == "__main__":
    main()
