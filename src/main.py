# archivo: main.py

import os
from parser.yal_parser import parse_yal_file
from parser.regex_expander import RegexExpander
from generator.afd_generator import AFDGenerator
from generator.lexer_generator import generate_lexer

from core.regex_parser import RegexParser

import pickle

OUTPUT_PICKLE = "afd.pkl"
OUTPUT_JSON = "afd.json"


def main(yal_file):
    print(f"📥 Procesando archivo: {yal_file}")
    parsed = parse_yal_file(yal_file)

    header = parsed['header']
    lets = parsed['lets']
    rules = parsed['rules']
    trailer = parsed['trailer']

    print("🔍 Expandiendo expresiones...")
    expander = RegexExpander(lets)

    token_regexes = []
    for i, (regex, action) in enumerate(rules):
        expanded = expander.normalize(regex)
        token_id = f"TOKEN_{i}"
        token_regexes.append((expanded, token_id))

    print("⚙️  Generando AFD...")
    generator = AFDGenerator(token_regexes)
    afd = generator.generate_afd()

    print("💾 Guardando AFD serializado...")
    generator.serialize_to_pickle(afd, OUTPUT_PICKLE)
    generator.serialize_to_json(afd, OUTPUT_JSON)

    print("🧠 Generando lexer.py...")
    os.makedirs("engine", exist_ok=True)
    generate_lexer()

    print("✅ Todo listo. Ejecuta 'python engine/lexer.py' para probar el lexer.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.yal")
    else:
        main(sys.argv[1])
