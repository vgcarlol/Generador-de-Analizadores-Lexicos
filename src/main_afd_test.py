# main.py

import os
import pickle  # Usamos pickle para serializar los AFDs

from utils.expand_expression import expand_expression
from utils.lexer_generator import generar_lexer_program
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
        print(f"🧠 Expresión expandida: {expanded}")

        final_expr = f"({expanded}).#"
        postfix = to_postfix(final_expr)
        print(f"📤 Postfix: {postfix}")

        syntax_tree, pos_to_symbol = build_syntax_tree(postfix)
        graficar_arbol(syntax_tree, filename=f"tree_{token}")

        afd = construct_direct_afd(syntax_tree, pos_to_symbol)
        afds[token] = afd

    return afds


# Paso 3: Guardar los AFDs en un archivo usando pickle
def save_afds_to_pickle(afds, filename="afds.pickle"):
    """Guardar los AFDs generados en un archivo binario utilizando pickle."""
    with open(filename, 'wb') as pickle_file:
        pickle.dump(afds, pickle_file)
    print(f"✅ AFDs guardados en {filename}")


# Paso 4: Cargar los AFDs desde un archivo usando pickle
def load_afds_from_pickle(filename="afds.pickle"):
    """Cargar los AFDs desde un archivo binario usando pickle."""
    if os.path.exists(filename):
        with open(filename, 'rb') as pickle_file:
            afds = pickle.load(pickle_file)
        print(f"✅ AFDs cargados desde {filename}")
        return afds
    else:
        print(f"❌ El archivo {filename} no existe.")
        return None


# Paso 5: Simular input sobre el AFD (a futuro)
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
    yal_file = "./yal/slr-4.yal"  # Cambia esto si es necesario

    # Intentamos cargar los AFDs desde un archivo pickle
    afds = load_afds_from_pickle()

    # Si no se cargan, generamos los AFDs
    if afds is None:
        if not os.path.exists(yal_file):
            print(f"❌ Archivo {yal_file} no encontrado")
        else:
            afds = generar_afds(yal_file)  # Generamos los AFDs
            save_afds_to_pickle(afds)  # Guardamos los AFDs generados en un archivo pickle

    # Ahora generamos el código fuente del lexer
    lexer_program_code = generar_lexer_program(afds)

    # Guardamos el código del lexer en un archivo
    with open("lexer_program.py", "w", encoding="utf-8") as f:
        f.write(lexer_program_code)

    print("✅ Lexer generado con éxito en lexer_program.py")

    print("\n✅ AFDs generados por token:")
    for token, afd in afds.items():
        print(f"  - {token}: {len(afd['transitions'])} transiciones, inicio {afd['start']}, aceptación {afd['accepting']}")
