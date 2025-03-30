
# archivo: engine/lexer.py (generado automáticamente)
import pickle

class Lexer:
    def __init__(self, afd_file):
        with open(afd_file, 'rb') as f:
            self.start_state = pickle.load(f)

    def analyze(self, text):
        position = 0
        results = []

        while position < len(text):
            current = self.start_state
            last_accepting = None
            last_accepting_pos = position
            i = position

            while i < len(text):
                symbol = text[i]
                if symbol in current.transitions:
                    current = current.transitions[symbol]
                    i += 1
                    if current.is_final:
                        last_accepting = current
                        last_accepting_pos = i
                else:
                    break

            if last_accepting:
                lexeme = text[position:last_accepting_pos]
                token_id = self._extract_token_id(last_accepting)
                results.append((token_id, lexeme))
                position = last_accepting_pos
            else:
                results.append(("ERROR", text[position]))
                position += 1

        return results

    def _extract_token_id(self, state):
        for pos in state.positions:
            if isinstance(pos, int) and pos in self.start_state.positions:
                continue
            if isinstance(pos, str) and pos.startswith('#'):
                return pos.strip('#')
        return 'UNKNOWN'

if __name__ == "__main__":
    lexer = Lexer('afd.pkl')
    with open('entrada.txt', 'r', encoding='utf-8') as f:
        contenido = f.read()
    resultado = lexer.analyze(contenido)
    with open('salida.txt', 'w', encoding='utf-8') as out:
        for token, lexema in resultado:
            line = f"< {token}, {lexema} >"
            print(line)
            out.write(line + "\n")
