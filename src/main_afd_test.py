import os
import pickle

from utils.expand_expression import expand_expression
from utils.lexer_generator import generar_lexer_program
from utils.regex_postfix import to_postfix, graficar_arbol
from utils.syntax_tree.build_tree import build_syntax_tree
from utils.syntax_tree.afd_from_tree import construct_direct_afd, visualize_afd, export_afd_to_json
from yal_parser import YALParser  # ⬅️ Importamos el parser real del .yal


def generar_afds(yal_path):
    with open(yal_path, encoding="utf-8") as f:
        yal_code = f.read()

    parser = YALParser(yal_code)
    parsed = parser.get_parsed()

    definitions = parsed["lets"]
    rules = parsed["rules"]

    afds = {}

    for i, rule in enumerate(rules):
        token_name = f"TOKEN_{i}"  # Si querés, usá: rule["action"].replace('return "', '').replace('";', '')
        regex = rule["pattern"]

        print(f"\n🔎 Procesando token: {token_name}")
        print(f"📥 Original: {regex}")

        # Expande y prepara la expresión
        final_expr = expand_expression(regex, definitions)
        print(f"[LOG] Final expression: {final_expr}")

        # Envolvés la expresión con el símbolo de aceptación
        final_expr_with_end = f"(({final_expr})).#"

        postfix = to_postfix(final_expr_with_end)
        print(f"📤 Postfix: {postfix}")

        syntax_tree, pos_to_symbol = build_syntax_tree(postfix)
        graficar_arbol(syntax_tree, filename=f"tree_{token_name}")

        afd = construct_direct_afd(syntax_tree, pos_to_symbol)

        visualize_afd(afd, output_path=f"./../../Graphviz/afd_{token_name}.gv")
        export_afd_to_json(afd, filename=f"afd_{token_name}.json")

        afds[token_name] = afd

    return afds


def save_afds_to_pickle(afds, filename="afds.pickle"):
    with open(filename, 'wb') as pickle_file:
        pickle.dump(afds, pickle_file)
    print(f"✅ AFDs guardados en {filename}")


def load_afds_from_pickle(filename="afds.pickle"):
    if os.path.exists(filename):
        with open(filename, 'rb') as pickle_file:
            afds = pickle.load(pickle_file)
        print(f"✅ AFDs cargados desde {filename}")
        return afds
    else:
        print(f"❌ El archivo {filename} no existe.")
        return None


def simular_afd(afd, entrada):
    current = afd['start']
    for c in entrada:
        if (current, c) in afd['transitions']:
            current = afd['transitions'][(current, c)]
        else:
            return False
    return current in afd['accepting']


if __name__ == "__main__":
    yal_file = "./yal/slr-4.yal"

    afds = load_afds_from_pickle()

    if afds is None:
        if not os.path.exists(yal_file):
            print(f"❌ Archivo {yal_file} no encontrado")
        else:
            afds = generar_afds(yal_file)
            save_afds_to_pickle(afds)

    lexer_program_code = generar_lexer_program(afds)

    with open("lexer_program.py", "w", encoding="utf-8") as f:
        f.write(lexer_program_code)

    print("✅ Lexer generado con éxito en lexer_program.py\n")

    print("📊 Resumen de AFDs:")
    for token, afd in afds.items():
        print(f"  - {token}: {len(afd['transitions'])} transiciones, inicio {afd['start']}, aceptación {afd['accepting']}")
