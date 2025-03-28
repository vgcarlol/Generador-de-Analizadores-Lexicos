# utils/syntax_tree/build_tree.py
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        self.position = None  # Solo para hojas

    def is_leaf(self):
        return self.left is None and self.right is None


def build_syntax_tree(postfix):
    stack = []
    position_counter = [1]
    pos_to_symbol = {}

    for token in postfix:
        print(f"[DEBUG] Procesando token: {token}")
        
        # Para operadores unarios (como *, +, ?)
        if token in {'*', '+', '?'}:
            if len(stack) < 1:
                raise ValueError(f"Error: operador unario '{token}' sin operando suficiente. Stack actual: {stack}")
            child = stack.pop()
            node = TreeNode(token)
            node.left = child
            stack.append(node)
            print(f"[DEBUG] Pushed unary operator tree for {token}")

        # Para operadores binarios (|, .)
        elif token in {'|', '.'}:
            print(f"[DEBUG] Stack antes de procesar el operador {token}: {stack}")
            if token == '|':
                if len(stack) < 2:
                    raise ValueError(f"Error: operador binario '{token}' sin operandos suficientes para alternancia. Stack actual: {stack}")
                right = stack.pop()
                left = stack.pop()
                print(f"[DEBUG] Operador binario | con operando izquierdo: {left.value} y derecho: {right.value}")
                node = TreeNode(token, left, right)
                stack.append(node)
                print(f"[DEBUG] Alternancia con operando izquierdo: {left.value} y derecho: {right.value}")
            
            elif token == '.':
                # Comprobamos si la pila tiene al menos 2 operandos
                if len(stack) < 2:
                    print(f"[DEBUG] No hay suficientes operandos para procesar el operador '.'. Stack actual: {stack}")
                    continue  # No procesamos el operador hasta que haya suficientes operandos

                right = stack.pop()
                left = stack.pop()
                print(f"[DEBUG] Operador binario . con operando izquierdo: {left.value} y derecho: {right.value}")
                
                # Concatenación, si el operando derecho es ε, solo agregamos el izquierdo
                if right.value == "ε":
                    print(f"[DEBUG] Concatenación con ε, solo agregando el operando izquierdo.")
                    stack.append(left)
                else:
                    node = TreeNode(token, left, right)
                    stack.append(node)
                    print(f"[DEBUG] Concatenando {left.value} y {right.value}")

        # Para operadores literales (tokens)
        else:
            node = TreeNode(token)
            if token == 'ε':
                node.nullable = True
                node.firstpos = set()
                node.lastpos = set()
                print(f"[DEBUG] Procesado ε como nodo terminal especial (sin posición)")
            else:
                node.position = position_counter[0]
                pos_to_symbol[position_counter[0]] = token
                node.firstpos = {node.position}
                node.lastpos = {node.position}
                print(f"[DEBUG] Literal procesado: {token}, pos: {node.position}")
                position_counter[0] += 1
            stack.append(node)


        print(f"[DEBUG] Stack actual después de procesar el token {token}: {stack}")
    
    # Verificar que la pila contenga solo un nodo (el árbol completo)
    if len(stack) != 1:
        raise ValueError(f"Error: el stack no tiene exactamente un árbol al final. Stack actual: {stack}")

    tree = stack.pop()
    return tree, pos_to_symbol
