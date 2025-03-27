class RegexParser:
    precedence = {'*': 3, '?': 3, '.': 2, '|': 1, '(': 0}

    @staticmethod
    def add_concatenation_operators(regex):
        new_regex = ""
        i = 0
        while i < len(regex):
            c = regex[i]
            new_regex += c
            if i + 1 < len(regex):
                curr = regex[i]
                next_c = regex[i + 1]
                if ((curr.isalnum() or curr in [')', '*', '?']) and
                    (next_c.isalnum() or next_c == '(' or next_c == '\\')):

                    # Verificar si ya hay un '|' antes de añadirlo
                    if new_regex[-1] != '|':
                        new_regex += '.'
                        print(f"[DEBUG] Adding concatenation: {curr} . {next_c}")
            i += 1
        return new_regex


    @staticmethod
    def infix_to_postfix(regex):
        print(f"[DEBUG] Infix input: {regex}")
        regex = RegexParser.add_concatenation_operators(regex)
        print(f"[DEBUG] After adding concatenation: {regex}")
        output = []
        stack = []

        i = 0
        while i < len(regex):
            char = regex[i]

            if char == '\\':
                if i + 1 < len(regex):
                    output.append(char + regex[i + 1])
                    print(f"[DEBUG] Escaped char: {char + regex[i + 1]}")
                    i += 2
                    continue
                else:
                    raise ValueError("Escape character at end of input")

            if char.isalnum() or char in ['#', 'ε', '_', ' ', '\t', '\n']:
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Unmatched closing parenthesis")
                stack.pop()
            else:
                while stack and RegexParser.precedence.get(char, 0) <= RegexParser.precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(char)

            print(f"[DEBUG] Char processed: {char}, Stack: {stack}, Output: {output}")
            i += 1

        while stack:
            if stack[-1] == '(':
                raise ValueError("Unmatched opening parenthesis")
            output.append(stack.pop())

        print(f"[DEBUG] Final Postfix Output: {''.join(output)}")
        return ''.join(output)

def to_postfix(expr):
    print(f"[DEBUG] to_postfix input: {expr}")
    
    # Limpieza para eliminar '||' consecutivos
    expr = re.sub(r'\|\|+', '|', expr)
    expr = expr.strip('|')  # Eliminar | al principio y al final
    print(f"[DEBUG] Postfix cleaned input: {expr}")
    
    raw = RegexParser.infix_to_postfix(expr).replace(" ", "")
    print(f"[DEBUG] Postfix raw string: {raw}")

    tokens = []
    i = 0
    while i < len(raw):
        if raw[i] == '\\':
            tokens.append(raw[i] + raw[i + 1])
            i += 2
        else:
            tokens.append(raw[i])
            i += 1

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
