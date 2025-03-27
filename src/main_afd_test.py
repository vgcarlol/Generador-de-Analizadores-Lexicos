import os
from utils.expand_expression import expand_expression
from utils.regex_postfix import to_postfix, graficar_arbol
from utils.syntax_tree.build_tree import build_syntax_tree
from utils.syntax_tree.afd_from_tree import construct_direct_afd


# Paso 1: Parsear el archivo YAL y separar definiciones y tokens
def parse_yalex(file_path):
    definitions = {}
    tokens = {}
    current_token = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Definiciones
            if '=' in line and 'let' not in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Quitar brackets exteriores si existen
                if value.startswith('[') and value.endswith(']'):
                    value = value[1:-1]

                # Quitar comillas exteriores si existen
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1].strip()

                # Sanear cualquier comilla interna que haya quedado
                value = value.replace('"', '').replace("'", '')

                definitions[key] = value


            # Tokens
            elif line.startswith('let'):
                parts = line.replace('let', '').split('=')
                token_name = parts[0].strip()
                regex = parts[1].strip()
                tokens[token_name] = regex

    return definitions, tokens




# Paso 2: Generar AFD por cada token y graficar su árbol de expresión
def generar_afds(yal_path):
    definitions, tokens = parse_yalex(yal_path)
    afds = {}

    for token, regex in tokens.items():
        print(f"\n🔎 Procesando token: {token}")
        expanded = expand_expression(regex, definitions)
        print(f"🧠 Expresion expandida: {expanded}")

        final_expr = f"({expanded}).#"
        postfix = to_postfix(final_expr)
        print(f"📤 Postfix: {postfix}")

        syntax_tree, pos_to_symbol = build_syntax_tree(postfix)
        graficar_arbol(syntax_tree, filename=f"tree_{token}")

        afd = construct_direct_afd(syntax_tree, pos_to_symbol)
        afds[token] = afd

    return afds


# Paso 3: Simular input sobre el AFD (a futuro)
def simular_afd(afd, entrada):
    current = afd['start']
    for c in entrada:
        if (current, c) in afd['transitions']:
            current = afd['transitions'][(current, c)]
        else:
            return False
    return current in afd['accepting']


# Ejemplo de ejecución:
if __name__ == "__main__":
    yal_file = "./yal/slr-4.yal"  # Cambia según el archivo que deseas procesar

    if not os.path.exists(yal_file):
        print(f"❌ Archivo {yal_file} no encontrado")
    else:
        afds = generar_afds(yal_file)

        print("\n✅ AFDs generados por token:")
        for token, afd in afds.items():
            print(f"  - {token}: {len(afd['states'])} estados, inicio {afd['start']}, aceptacion {afd['accepting']}")
