# archivo: generator/afd_generator.py

import json
import pickle
from core.regex_parser import RegexParser
from core.direct_construction import DirectAFDConstructor

class AFDGenerator:
    def __init__(self, token_regexes):
        self.token_regexes = token_regexes

    def build_combined_expression(self):
        parts = []
        for regex, token_id in self.token_regexes:
            # Si ws se quiere ignorar, se puede descartar (por ejemplo, TOKEN_0)
            if token_id == "TOKEN_0":
                continue
            regex = regex.strip()
            if regex.startswith('|'):
                regex = regex[1:].strip()
            if not regex:
                continue
            # Envolver la expresión en paréntesis (si no lo está)
            if not (regex.startswith('(') and regex.endswith(')')):
                regex = f"({regex})"
            # Ahora se encapsula agregando la marca, de modo que la parte final es el marcador:
            tagged = f"({regex}#{token_id})"
            parts.append(tagged)
        # Encapsular toda la unión para que la raíz sea una unión de todas las alternativas
        return "(" + "|".join(parts) + ")"

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
