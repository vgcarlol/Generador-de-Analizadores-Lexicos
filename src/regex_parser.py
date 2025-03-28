# regex_parser.py

class RegexParser:
    precedence = {'*': 3, '?': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def add_concatenation_operators(regex):
        result = ''
        i = 0
        tokens_dobles = [":=", "<=", ">=", "==", "!=", "<<", ">>"]  # Agregá los que necesites

        while i < len(regex):
            # Detectar tokens dobles primero
            if any(regex.startswith(tok, i) for tok in tokens_dobles):
                for tok in tokens_dobles:
                    if regex.startswith(tok, i):
                        result += tok
                        i += len(tok)
                        # Concatenación si sigue algo
                        if i < len(regex):
                            result += '.'
                        break
                continue

            c1 = regex[i]

            # Manejo de escapes
            if c1 == '\\' and i + 1 < len(regex):
                result += c1 + regex[i + 1]
                i += 2
                if i < len(regex):
                    c2 = regex[i]
                    if RegexParser._needs_concatenation('\\' + regex[i - 1], c2):
                        result += '.'
                continue

            result += c1

            if i + 1 < len(regex):
                c2 = regex[i + 1]
                if RegexParser._needs_concatenation(c1, c2):
                    result += '.'

            i += 1
        return result

        
    

    @staticmethod
    def _needs_concatenation(c1, c2):
        """
        Decide si se necesita concatenación entre c1 y c2
        """
        valid_end = lambda c: c.isalnum() or c in ['*', '?', ')', 'ε'] or (len(c) == 2 and c[0] == '\\')
        valid_start = lambda c: c.isalnum() or c in ['(', 'ε', '#'] or (len(c) == 2 and c[0] == '\\')
        return valid_end(c1) and valid_start(c2)



    @staticmethod
    def infix_to_postfix(regex):
        print(f"[DEBUG] Infix input: {regex}")
        regex = RegexParser.add_concatenation_operators(regex)
        print(f"[DEBUG] After adding concatenation: {regex}")
        output = []
        stack = []


        def is_valid_operand(token):
            if not token:
                return False
            if token.startswith('\\'):
                return True
            if token in ['|', '.', '(']:
                return False
            return True


        i = 0
        while i < len(regex):
            char = regex[i]

            # Manejo de escapes
            if char == '\\':
                if i + 1 < len(regex):
                    output.append(char + regex[i + 1])
                    print(f"[DEBUG] Escaped char: {char + regex[i + 1]}")
                    i += 2
                    continue
                else:
                    raise ValueError("Escape character at end of input")

            # Literales y símbolos válidos
            if char.isalnum() or char in ['#', 'ε', '_', ' ', '\t', '\n', ':', ';', '=', '<', '>', '+', '-', '*', '/', '!']:
                output.append(char)

            elif char == '(':
                stack.append(char)

            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Unmatched closing parenthesis")
                stack.pop()  # Eliminar '('

            elif char in RegexParser.precedence:
                # Evitar operadores binarios consecutivos o sin operandos
                if char in ['|', '.']:
                    if not output:
                        raise ValueError(f"Operador binario '{char}' sin operando antes")

                    last = output[-1]

                while (stack and stack[-1] != '(' and
                    RegexParser.precedence.get(char, 0) <= RegexParser.precedence.get(stack[-1], 0)):
                    output.append(stack.pop())
                stack.append(char)

            else:
                raise ValueError(f"Carácter inválido en la expresión: '{char}'")

            print(f"[DEBUG] Char processed: {char}, Stack: {stack}, Output: {output}")
            i += 1

        while stack:
            if stack[-1] == '(':
                raise ValueError("Unmatched opening parenthesis")
            output.append(stack.pop())

        print(f"[DEBUG] Final Postfix Output: {''.join(output)}")
        return output
        


def to_postfix(expr):
    print(f"[DEBUG] to_postfix input: {expr}")

    # Limpieza manual: evitar || y '|' al inicio/final
    while '||' in expr:
        expr = expr.replace('||', '|')
    expr = expr.strip('|')

    tokens = RegexParser.infix_to_postfix(expr)
    print(f"[DEBUG] Final tokens: {tokens}")
    return tokens





# ----------------------------
# 🔧 FUNCIONALIDAD EXTRA: GRAFICAR ÁRBOL
# ----------------------------

def graficar_arbol(node, filename="syntax_tree"):
    import os
    from graphviz import Digraph

    # Ruta absoluta al dot.exe local
    dot_path = os.path.abspath("./Graphviz/bin/dot.exe")
    os.environ["PATH"] += os.pathsep + os.path.dirname(dot_path)

    # Crear carpeta de salida si no existe
    output_dir = "./output_trees"
    os.makedirs(output_dir, exist_ok=True)

    # Ruta completa para el archivo
    output_path = os.path.join(output_dir, filename)

    dot = Digraph(comment="Árbol de Sintaxis")
    dot.engine = 'dot'

    def recorrer(nodo):
        if nodo is None:
            return "None"

        node_id = str(id(nodo))
        label = nodo.value if nodo.value else ""
        if nodo.position is not None:
            label += f"\n[{nodo.position}]"

        dot.node(node_id, label)

        if nodo.left:
            left_id = recorrer(nodo.left)
            dot.edge(node_id, left_id)

        if nodo.right:
            right_id = recorrer(nodo.right)
            dot.edge(node_id, right_id)

        return node_id

    recorrer(node)
    dot.render(output_path, format="png", cleanup=True)
    print(f"✅ Árbol de expresión graficado como {output_path}.png")
