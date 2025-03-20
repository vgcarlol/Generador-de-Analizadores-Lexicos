# yalex_generator.py

import re
import os
import sys
from regex_parser import RegexParser
from direct_construction import DirectAFDConstructor
from minimization import AFDMinimizer
from visualization import visualize_afd, visualize_syntax_tree

def remove_comments(text):
    pattern = re.compile(r'\(\*.*?\*\)', re.DOTALL)
    return re.sub(pattern, '', text)

def parse_yalex_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = remove_comments(content)

    # Extraer header (primer bloque entre llaves)
    header = ""
    header_match = re.search(r'^\s*\{(.*?)\}', content, re.DOTALL)
    if header_match:
        header = header_match.group(1).strip()

    # Extraer trailer (último bloque entre llaves), descartándolo si contiene "rule" o "let"
    trailer = ""
    trailer_match = re.search(r'\{(.*?)\}\s*$', content, re.DOTALL)
    if trailer_match:
        trailer_candidate = trailer_match.group(1).strip()
        if ("rule" in trailer_candidate.lower()) or ("let" in trailer_candidate.lower()):
            trailer = ""
        else:
            trailer = trailer_candidate

    # Definiciones: líneas con "let"
    definitions = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("let "):
            eq_index = line.find("=")
            if eq_index != -1:
                name = line[4:eq_index].strip()
                regex_def = line[eq_index+1:].strip()
                definitions[name] = regex_def

    # Reglas: a partir de "rule <nombre> =" hasta la siguiente llave o fin de archivo
    rules = []
    rule_match = re.search(r'rule\s+\w+\s*(\[[^\]]*\])?\s*=(.*?)(?=\n\s*\{|\Z)', content, re.DOTALL | re.IGNORECASE)
    if rule_match:
        rule_block = rule_match.group(2).strip()
        lines = [line.strip() for line in rule_block.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("|"):
                line = line[1:].strip()
            last_open = line.rfind('{')
            last_close = line.rfind('}')
            if last_open != -1 and last_close != -1 and last_close > last_open:
                # regex_rule es lo que está antes de '{'
                regex_rule = line[:last_open].strip()
                # action es lo que está dentro de '{ ... }'
                action = line[last_open+1:last_close].strip()
                if regex_rule:
                    rules.append((regex_rule, action))
            else:
                # no hay acción con llaves, o la línea es solo la expresión
                if line:
                    rules.append((line, ""))
    return header, definitions, rules, trailer

def build_afd_for_rule(regex, definitions):
    import re
    # Si la regla coincide exactamente con una definición, reemplazarla
    if regex.strip() in definitions:
        regex = definitions[regex.strip()]

    # Reemplazo de palabras completas: para cada definición,
    # se sustituye la aparición exacta del nombre por su definición entre paréntesis.
    for name, def_regex in definitions.items():
        # Usamos \b para asegurar que se reemplaza el nombre como palabra completa
        regex = re.sub(r'\b' + re.escape(name) + r'\b', f"({def_regex})", regex)

    # Si la ER está entre comillas simples o dobles, quitar las comillas, escapar y volver a envolver
    if (regex.startswith("'") and regex.endswith("'")) or (regex.startswith('"') and regex.endswith('"')):
        inner = re.escape(regex[1:-1])
        final_regex = "'" + inner + "'"
    else:
        final_regex = regex

    # Convertir a postfix usando nuestro parser modificado
    regex_postfix = RegexParser.infix_to_postfix(final_regex)
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()
    minimized_afd = AFDMinimizer(afd).minimize()

    print("\n===================================")
    print("Expresión final:")
    print(final_regex)
    print("\nPostfix generado:")
    print(regex_postfix)
    print("\nMapping de marcadores:")
    print(afd_constructor.symbol_positions)
    print("===================================\n")

    return minimized_afd, final_regex, regex_postfix, afd_constructor.symbol_positions, afd_constructor.syntax_tree



def generate_lexer_spec(yalex_file_path, output_file):
    header, definitions, rules, trailer = parse_yalex_file(yalex_file_path)
    print("=== Secciones del archivo YALex ===")
    print("Header:", header)
    print("Definiciones:", definitions)
    print("Reglas:", rules)
    print("Trailer:", trailer)

    # Generar un AFD (y árbol) para cada regla
    rule_info = []
    for idx, (regex_rule, action) in enumerate(rules):
        token_name = f"TOKEN_{idx}"
        afd, final_regex, regex_postfix, mapping, syntax_tree = build_afd_for_rule(regex_rule, definitions)
        rule_info.append((token_name, afd, action, final_regex, regex_postfix, mapping, syntax_tree))

    # Generar thelexer.py
    lexer_code = []
    lexer_code.append("# Archivo generado automáticamente por YALex Generator")
    # Incluir el header como comentarios para evitar errores de ejecución
    if header:
        for line in header.splitlines():
            lexer_code.append("# " + line)
    lexer_code.append("")
    lexer_code.append("import sys")
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
    lexer_code.append(trailer)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lexer_code))
    print(f"Archivo lexer generado: {output_file}")


    # Generar un árbol sintáctico (y un PNG) por cada regla, en lugar de un "árbol combinado"
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
