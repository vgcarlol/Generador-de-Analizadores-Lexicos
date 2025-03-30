# archivo: engine/runner.py

<<<<<<< Updated upstream
from engine.lexer import Lexer
import sys
=======
import os
from lexer import Lexer
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
>>>>>>> Stashed changes


def run_lexer(input_file, output_file="salida.txt"):
    lexer = Lexer("afd.pkl")
    with open(input_file, 'r', encoding='utf-8') as f:
        contenido = f.read()

    resultado = lexer.analyze(contenido)

    with open(output_file, 'w', encoding='utf-8') as out:
        for token, lexema in resultado:
            line = f"< {token}, {lexema} >"
            print(line)
            out.write(line + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python runner.py entrada.txt [salida.txt]")
    elif len(sys.argv) == 2:
        run_lexer(sys.argv[1])
    else:
        run_lexer(sys.argv[1], sys.argv[2])
