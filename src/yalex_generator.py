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

    header = ""
    header_match = re.search(r'^\s*\{(.*?)\}', content, re.DOTALL)
    if header_match:
        header = header_match.group(1).strip()

    trailer = ""
    trailer_match = re.search(r'\{(.*?)\}\s*$', content, re.DOTALL)
    if trailer_match:
        trailer_candidate = trailer_match.group(1).strip()
        if ("rule" in trailer_candidate.lower()) or ("let" in trailer_candidate.lower()):
            trailer = ""
        else:
            trailer = trailer_candidate

    definitions = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("let "):
            eq_index = line.find("=")
            if eq_index != -1:
                name = line[4:eq_index].strip()
                regex_def = line[eq_index+1:].strip()
                definitions[name] = regex_def

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
                regex_rule = line[:last_open].strip()
                action = line[last_open+1:last_close].strip()
                if regex_rule:
                    rules.append((regex_rule, action))
            else:
                if line:
                    rules.append((line, ""))
    return header, definitions, rules, trailer

def build_afd_for_rule(regex, definitions):
    import re
    prev = None
    while prev != regex:
        prev = regex
        for name, def_regex in definitions.items():
            regex = re.sub(r'\{' + re.escape(name) + r'\}', f"({def_regex})", regex)
    if regex.startswith("'") and regex.endswith("'"):
        final_regex = re.escape(regex[1:-1])
    else:
        final_regex = regex
    regex_postfix = RegexParser.infix_to_postfix(final_regex)
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()
    minimized_afd = AFDMinimizer(afd).minimize()
    return minimized_afd, final_regex, afd_constructor.syntax_tree

def visualize_combined_syntax_trees(rule_tree_list, filename='combined_syntax_tree'):
    from graphviz import Digraph
    dot = Digraph()
    dot.node('root', 'Tokens')
    for token_name, syntax_tree in rule_tree_list:
        # Asigna un nodo al raíz de cada árbol
        root_id = str(id(syntax_tree))
        dot.node(root_id, token_name)
        dot.edge('root', root_id)
        # Función recursiva para agregar el árbol
        def traverse(node):
            if node is None:
                return
            node_id = str(id(node))
            dot.node(node_id, node.symbol)
            if node.left:
                left_id = str(id(node.left))
                dot.edge(node_id, left_id, label="L")
                traverse(node.left)
            if node.right:
                right_id = str(id(node.right))
                dot.edge(node_id, right_id, label="R")
                traverse(node.right)
        traverse(syntax_tree)
    dot.render(filename, format='png', view=True)

def generate_lexer_spec(yalex_file_path, output_file):
    header, definitions, rules, trailer = parse_yalex_file(yalex_file_path)
    print("=== Secciones del archivo YALex ===")
    print("Header:", header)
    print("Definiciones:", definitions)
    print("Reglas:", rules)
    print("Trailer:", trailer)
    
    # Para cada regla se genera el AFD y se obtiene la expresión final y el árbol sintáctico.
    rule_afd_list = []
    for idx, (regex_rule, action) in enumerate(rules):
        token_name = f"TOKEN_{idx}"
        afd, final_regex, syntax_tree = build_afd_for_rule(regex_rule, definitions)
        rule_afd_list.append((token_name, afd, action, final_regex, syntax_tree))
    
    # Generar el código para el analizador léxico en thelexer.py.
    lexer_code = []
    lexer_code.append(header)
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
    lexer_code.append("        # Evaluar cada regla")
    for token_name, afd, action, final_regex, syntax_tree in rule_afd_list:
        lexer_code.append("        # Regla " + token_name)
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
    
    # Generar un único árbol combinado de todas las reglas
    # Se recopilan los árboles de cada regla (token_name y syntax_tree)
    combined_tree_list = [(token_name, syntax_tree) for token_name, afd, action, final_regex, syntax_tree in rule_afd_list]
    if combined_tree_list:
        visualize_combined_syntax_trees(combined_tree_list, filename="combined_syntax_tree")
        print("Árbol sintáctico combinado guardado en 'combined_syntax_tree.png'.")
    else:
        print("No se encontraron reglas para combinar.")

def visualize_combined_syntax_trees(rule_tree_list, filename='combined_syntax_tree'):
    from graphviz import Digraph
    dot = Digraph()
    dot.node('root', 'Tokens')
    for token_name, syntax_tree in rule_tree_list:
        root_id = str(id(syntax_tree))
        dot.node(root_id, token_name)
        dot.edge('root', root_id)
        def traverse(node):
            if node is None:
                return
            node_id = str(id(node))
            dot.node(node_id, node.symbol)
            if node.left:
                dot.edge(node_id, str(id(node.left)), label="L")
                traverse(node.left)
            if node.right:
                dot.edge(node_id, str(id(node.right)), label="R")
                traverse(node.right)
        traverse(syntax_tree)
    dot.render(filename, format='png', view=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python yalex_generator.py <archivo_yalex> <archivo_salida>")
        sys.exit(1)
    yalex_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_lexer_spec(yalex_file, output_file)
