import os
import logging
from graphviz import Digraph

GRAPHVIZ_PATH = os.path.abspath("./Graphviz/bin")  # Ajuste para tu sistema
os.environ["PATH"] += os.pathsep + GRAPHVIZ_PATH

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

def visualize_afd(afd, filename='afd_output'):
    dot = Digraph()
    visited = set()
    state_map = {}  # Mapeo de estados con nombres más legibles
    state_counter = 0

    def get_state_name(state):
        nonlocal state_counter
        if state not in state_map:
            state_map[state] = f"q{state_counter}"
            state_counter += 1
        return state_map[state]

    def add_nodes(state):
        if state in visited:
            return
        visited.add(state)

        state_name = get_state_name(state)
        dot.node(state_name, shape="doublecircle" if state.is_final else "circle")

        logging.debug(f"Agregando nodo: {state_name}")

        for symbol, target in state.transitions.items():
            target_name = get_state_name(target)
            dot.edge(state_name, target_name, label=symbol)
            logging.debug(f"Agregando transición: {state_name} --{symbol}--> {target_name}")
            add_nodes(target)


    add_nodes(afd)

    dot.render(filename, format='png', view=True)


def visualize_syntax_tree(syntax_tree, filename='syntax_tree'):
    dot = Digraph()
    visited = set()

    def traverse(node):
        if node is None or id(node) in visited:
            return
        visited.add(id(node))
        # El label muestra el símbolo y, opcionalmente, otras propiedades
        label = f"{node.symbol}"
        dot.node(str(id(node)), label=label)
        if node.left:
            dot.edge(str(id(node)), str(id(node.left)), label="L")
            traverse(node.left)
        if node.right:
            dot.edge(str(id(node)), str(id(node.right)), label="R")
            traverse(node.right)

    traverse(syntax_tree)
    dot.render(filename, format='png', view=True)