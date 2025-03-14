# yalex_generator.py

import re
import os
import sys
from regex_parser import RegexParser
from direct_construction import DirectAFDConstructor
from minimization import AFDMinimizer

def remove_comments(text):
    pattern = re.compile(r'\(\*.*?\*\)', re.DOTALL)
    return re.sub(pattern, '', text)

def parse_yalex_file(file_path):
    import re
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = remove_comments(content)

    # Extraer header (la primera sección entre llaves)
    header = ""
    header_match = re.search(r'^\s*\{(.*?)\}', content, re.DOTALL)
    if header_match:
        header = header_match.group(1).strip()

    # Extraer trailer (la última sección entre llaves)
    trailer = ""
    trailer_match = re.search(r'\{(.*?)\}\s*$', content, re.DOTALL)
    if trailer_match:
        trailer = trailer_match.group(1).strip()

    # Extraer definiciones: líneas que comienzan con "let "
    definitions = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("let "):
            # Extraer el nombre: se toma lo que está entre "let " y el "="
            eq_index = line.find("=")
            if eq_index != -1:
                name = line[4:eq_index].strip()
                regex_def = line[eq_index+1:].strip()
                definitions[name] = regex_def

    # Extraer reglas: se asume que la sección de reglas inicia con "rule"
    rules = []
    rule_match = re.search(r'rule\s+\w+\s*(\[[^\]]*\])?\s*=(.*?)(?=\n\s*\{)', content, re.DOTALL | re.IGNORECASE)
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
    # Aplicar sustitución recursiva hasta que no cambie la expresión.
    prev = None
    while prev != regex:
        prev = regex
        for name, def_regex in definitions.items():
            regex = re.sub(r'\{' + re.escape(name) + r'\}', f"({def_regex})", regex)
    final_regex = regex  # Esta es la versión procesada
    # Conversión a postfix usando la expresión final
    regex_postfix = RegexParser.infix_to_postfix(final_regex)
    # Construcción y minimización del AFD
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()
    minimized_afd = AFDMinimizer(afd).minimize()
    return minimized_afd, final_regex


def generate_lexer_spec(yalex_file_path, output_file):
    header, definitions, rules, trailer = parse_yalex_file(yalex_file_path)
    print("=== Secciones del archivo YALex ===")
    print("Header:", header)
    print("Definiciones:", definitions)
    print("Reglas:", rules)
    print("Trailer:", trailer)
    
    # Para cada regla se genera el AFD (se asigna un token secuencialmente)
    rule_afd_list = []
    for idx, (regex_rule, action) in enumerate(rules):
        token_name = f"TOKEN_{idx}"
        afd, final_regex = build_afd_for_rule(regex_rule, definitions)
        rule_afd_list.append((token_name, afd, action, final_regex))
    
    # Generar código para el analizador léxico en thelexer.py
    lexer_code = []
    lexer_code.append("# Archivo generado automáticamente por YALex Generator")
    lexer_code.append(header)
    lexer_code.append("\nimport sys\n")
    lexer_code.append("# Se define una función de simulación de AFD (se usa 're' como placeholder)\n")
    lexer_code.append("def simulate_afd(regex, input_string):\n")
    lexer_code.append("    import re\n")
    lexer_code.append("    pattern = re.compile(r'^' + regex)\n")
    lexer_code.append("    m = pattern.match(input_string)\n")
    lexer_code.append("    return len(m.group(0)) if m else 0\n\n")
    
    lexer_code.append("def lex(input_string):\n")
    lexer_code.append("    tokens = []\n")
    lexer_code.append("    pos = 0\n")
    lexer_code.append("    while pos < len(input_string):\n")
    lexer_code.append("        max_length = 0\n")
    lexer_code.append("        selected_token = None\n")
    lexer_code.append("        selected_action = None\n")
    # Para cada regla se simula el reconocimiento usando la expresión regular procesada (final_regex)
    for token_name, afd, action, final_regex in rule_afd_list:
        lexer_code.append("        {\n")
        lexer_code.append("            import re\n")
        lexer_code.append(f"            pattern = re.compile(r'^{final_regex}')\n")
        lexer_code.append("            m = pattern.match(input_string[pos:])\n")
        lexer_code.append("            if m:\n")
        lexer_code.append("                length = len(m.group(0))\n")
        lexer_code.append("                if length > max_length:\n")
        lexer_code.append(f"                    max_length = length\n")
        lexer_code.append(f"                    selected_token = '{token_name}'\n")
        lexer_code.append(f"                    selected_action = '''{action}'''\n")
        lexer_code.append("        }\n")
    lexer_code.append("        if max_length == 0:\n")
    lexer_code.append("            print(f'Error léxico en la posición {pos}: {input_string[pos]}')\n")
    lexer_code.append("            pos += 1\n")
    lexer_code.append("        else:\n")
    lexer_code.append("            lexeme = input_string[pos:pos+max_length]\n")
    lexer_code.append("            tokens.append((selected_token, lexeme, selected_action))\n")
    lexer_code.append("            pos += max_length\n")
    lexer_code.append("    return tokens\n\n")
    
    lexer_code.append("def main():\n")
    lexer_code.append("    if len(sys.argv) < 2:\n")
    lexer_code.append("        print('Uso: python thelexer.py <archivo_de_entrada>')\n")
    lexer_code.append("        sys.exit(1)\n")
    lexer_code.append("    with open(sys.argv[1], 'r', encoding='utf-8') as f:\n")
    lexer_code.append("        input_string = f.read()\n")
    lexer_code.append("    tokens = lex(input_string)\n")
    lexer_code.append("    for token in tokens:\n")
    lexer_code.append("        print(token)\n\n")
    
    lexer_code.append("if __name__ == '__main__':\n")
    lexer_code.append("    main()\n")
    lexer_code.append("\n")
    lexer_code.append(trailer)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lexer_code))
    print(f"Archivo lexer generado: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python yalex_generator.py <archivo_yalex> <archivo_salida>")
        sys.exit(1)
    yalex_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_lexer_spec(yalex_file, output_file)
