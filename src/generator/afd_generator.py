# archivo: generator/afd_generator.py

import json
import pickle
from core.regex_parser import RegexParser
from core.direct_construction import DirectAFDConstructor

class AFDGenerator:
    def __init__(self, token_regexes):
        """
        token_regexes: Lista de tuplas (regex, token_id), ya expandidas y normalizadas.
        Se construye una única expresión general para todo el AFD, distinguiendo tokens con #id
        """
        self.token_regexes = token_regexes

    def build_combined_expression(self):
        parts = []
        for idx, (regex, token_id) in enumerate(self.token_regexes):
            regex = regex.strip()
            print(f"🧪 TOKEN {token_id}: {regex}")  # <-- Línea nueva


            # ⚠️ Elimina | inicial si existe
            if regex.startswith('|'):
                regex = regex[1:].strip()

            if not regex:
                print(f"⚠️ Regex vacía ignorada para {token_id}")
                continue

            def debug_parentheses(expr):
                stack = []
                for i, c in enumerate(expr):
                    if c == '(':
                        stack.append(i)
                    elif c == ')':
                        if stack:
                            stack.pop()
                        else:
                            print(f"🔻 Paréntesis de cierre sin abrir en posición {i}: '{expr}'")
                for pos in stack:
                    print(f"🔺 Paréntesis de apertura sin cerrar en posición {pos}: '{expr}'")

            if not self._parenthesis_balanced(regex):
                print(f"⚠️ Regex con paréntesis desbalanceados para {token_id}: '{regex}'")
                debug_parentheses(regex)
                continue

            if not (regex.startswith('(') and regex.endswith(')')):
                regex = f"({regex})"
            tagged = f"{regex}#{token_id}"

            parts.append(tagged)

        return '|'.join(parts)

    def _parenthesis_balanced(self, regex):
        count = 0
        i = 0
        while i < len(regex):
            if regex[i] == '\\' and i + 1 < len(regex):
                # Ignorar secuencias escapadas: \(
                i += 2
                continue
            elif regex[i] == '(':
                count += 1
            elif regex[i] == ')':
                count -= 1
                if count < 0:
                    return False
            i += 1
        return count == 0

    def generate_afd(self):
        combined_expr = self.build_combined_expression()

        # DEBUG: Mostrar la regex combinada antes de convertir a postfix
        print("\n📦 Expresión regular combinada:")
        print(combined_expr)

        postfix = RegexParser.infix_to_postfix(combined_expr)

        # DEBUG: Mostrar la postfix generada
        print("\n🔄 Expresión en postfix:")
        print(postfix)

        constructor = DirectAFDConstructor(postfix)
        afd = constructor.get_afd()
        return afd


    def serialize_to_json(self, afd, filename):
        """
        Serializa el AFD a formato JSON (legible para humanos)
        """
        def state_to_dict(state):
            return {
                'id': state.id,
                'positions': list(state.positions),
                'is_final': state.is_final,
                'transitions': {symbol: target.id for symbol, target in state.transitions.items()}
            }

        all_states = self._collect_states(afd)
        serialized = {
            'states': [state_to_dict(s) for s in all_states],
            'start': afd.id
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serialized, f, indent=2)

    def serialize_to_pickle(self, afd, filename):
        with open(filename, 'wb') as f:
            pickle.dump(afd, f)

    def _collect_states(self, start):
        visited = set()
        states = []
        stack = [start]

        while stack:
            current = stack.pop()
            if current.id in visited:
                continue
            visited.add(current.id)
            states.append(current)
            for target in current.transitions.values():
                stack.append(target)

        return states
