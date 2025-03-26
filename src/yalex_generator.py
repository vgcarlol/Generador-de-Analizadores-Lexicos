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
        # Se toma desde "rule" hasta que se encuentre una línea que comience con "{" o hasta el final
        after_rule = text[rule_index:]
        sep = "\n{"
        end_index = after_rule.find(sep)
        if end_index == -1:
            rule_block = after_rule
        else:
            rule_block = after_rule[:end_index]
        # Se busca el signo "=" que separa la cabecera de la definición
        eq_index = rule_block.find("=")
        if eq_index != -1:
            rule_block = rule_block[eq_index+1:].strip()
        # Se procesa línea a línea
        lines = [line.strip() for line in rule_block.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("|"):
                line = line[1:].strip()
            # Si la línea contiene una acción delimitada por llaves, se separa
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

# Función para extraer tokens entre comillas (simula re.findall para ["'([^']*)'", ...])
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

# Función para convertir una definición de conjunto, similar a convert_set original
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

# Función para reemplazar ocurrencias de una palabra completa (imitando \b en re)
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

# Función para escapar una cadena (imitando re.escape de forma simple)
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

def build_afd_for_rule(regex, definitions):
    # Si la regla coincide exactamente con una definición, se reemplaza
    if regex.strip() in definitions:
        regex = definitions[regex.strip()]
    
    # Procesar las definiciones en orden descendente (por longitud)
    for name in sorted(definitions, key=len, reverse=True):
        def_regex = definitions[name]
        conv = def_regex
        if def_regex.startswith('[') and def_regex.endswith(']'):
            conv = convert_set(def_regex)
        else:
            # Si no está ya entre comillas, y si no es compuesta (contiene operadores),
            # se envuelve en comillas; de lo contrario se deja tal cual.
            if not ((conv.startswith("'") and conv.endswith("'")) or (conv.startswith('"') and conv.endswith('"'))):
                if any(ch in conv for ch in "()*|.?+"):
                    pass
                else:
                    conv = "'" + conv + "'"
        # Si el conv es compuesto, se utiliza tal cual sin agregar paréntesis extra.
        if any(ch in conv for ch in "()*|.?+"):
            replacement = conv
        else:
            replacement = "(" + conv + ")"
        # Reemplazar ocurrencias de la definición en la expresión (buscando coincidencias completas)
        regex = replace_word(regex, name, replacement)
    
    final_regex = regex.strip()
    # Obtener la lista de tokens en postfix usando el parser (no se usa re aquí)
    regex_postfix = RegexParser.infix_to_postfix(final_regex)
    # Para impresión, se unen con espacios:
    postfix_str = " ".join(regex_postfix)
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()
    minimized_afd = AFDMinimizer(afd).minimize()
    
    print("\n===================================")
    print("Expresión final:")
    print(final_regex)
    print("\nPostfix generado:")
    print(postfix_str)
    print("\nMapping de marcadores:")
    print(afd_constructor.symbol_positions)
    print("===================================\n")
    
    return minimized_afd, final_regex, postfix_str, afd_constructor.symbol_positions, afd_constructor.syntax_tree

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
        rule_info.append((token_name, afd, action, final_regex, regex_postfix, mapping, syntax_tree))
    lexer_code = []
    lexer_code.append("# Archivo generado automáticamente por YALex Generator")
    if header:
        for line in header.splitlines():
            lexer_code.append("# " + line)
    lexer_code.append("")
    lexer_code.append("import sys")
    # Nota: en este código generado se sigue utilizando re para compilar las expresiones
    lexer_code.append("import re")
    lexer_code.append("")
    lexer_code.append("def simulate_afd(regex, input_string):")
    lexer_code.append("    pattern = re.compile(r'^' + regex)")
    lexer_code.append("    m = pattern.match(input_string)")
    lexer_code.append("    return len(m.group(0)) if m else 0")
    lexer_code.append("")
    lexer_code.append("def lex(input_string):")
    lexer_code.append("    tokens = []")
    lexer_code.append("    pos = 0")
    lexer_code.append("    while pos < len(input_string):")
    lexer_code.append("        max_length = 0")
    lexer_code.append("        selected_token = None")
    lexer_code.append("        selected_action = None")
    lexer_code.append("        # Evaluar cada regla (longest match + prioridad)")
    for token_name, afd, action, final_regex, regex_postfix, mapping, syntax_tree in rule_info:
        lexer_code.append(f"        # Regla {token_name}")
        # Escapar literales entre comillas simples o dobles para evitar error "unterminated subpattern"
        if (final_regex.startswith("'") and final_regex.endswith("'")) or \
           (final_regex.startswith('"') and final_regex.endswith('"')):
            content = final_regex[1:-1]         # quitar las comillas externas
            content = escape_string(content)
            final_regex = content
        lexer_code.append(f"        regex = {repr(final_regex)}")
        lexer_code.append("        pattern = re.compile(r'^' + regex)")
        lexer_code.append("        m = pattern.match(input_string[pos:])")
        lexer_code.append("        if m:")
        lexer_code.append("            length = len(m.group(0))")
        lexer_code.append("            if length > max_length:")
        lexer_code.append(f"                max_length = length")
        lexer_code.append(f"                selected_token = '{token_name}'")
        lexer_code.append(f"                selected_action = '''{action}'''")
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
    from visualization import visualize_syntax_tree
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
