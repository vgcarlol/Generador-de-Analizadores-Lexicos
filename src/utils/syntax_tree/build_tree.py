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
        if token in {'*', '+', '?'}:
            if len(stack) < 1:
                raise ValueError(f"Error: operador unario '{token}' sin operando suficiente. Stack actual: {stack}")
            child = stack.pop()
            node = TreeNode(token)
            node.left = child
            stack.append(node)

        elif token in {'|', '.'}:
            if len(stack) < 2:
                raise ValueError(f"Error: operador binario '{token}' sin operandos suficientes. Stack actual: {stack}")
            right = stack.pop()
            left = stack.pop()
            node = TreeNode(token, left, right)
            stack.append(node)

        else:
            node = TreeNode(token)
            node.position = position_counter[0]
            pos_to_symbol[position_counter[0]] = token
            node.firstpos = {node.position}
            node.lastpos = {node.position}
            stack.append(node)
            position_counter[0] += 1

    if len(stack) != 1:
        raise ValueError(f"Error: el stack no tiene exactamente un árbol al final. Stack actual: {stack}")

    tree = stack.pop()
    return tree, pos_to_symbol
