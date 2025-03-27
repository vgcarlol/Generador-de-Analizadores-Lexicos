# utils/syntax_tree/afd_from_tree.py
from collections import deque
import json
import os

def construct_direct_afd(tree, pos_to_symbol):
    from utils.syntax_tree.nullable_followpos import compute_nullable_first_last, compute_followpos

    compute_nullable_first_last(tree)
    followpos = {i: set() for i in pos_to_symbol}
    compute_followpos(tree, followpos)

    start = frozenset(tree.firstpos)
    states = [start]
    unmarked = deque([start])
    transitions = {}
    accepting = set()
    state_names = {start: 'S0'}
    state_id = 1

    while unmarked:
        current = unmarked.popleft()
        symbol_map = {}
        for pos in current:
            sym = pos_to_symbol[pos]
            if sym == '#':
                accepting.add(state_names[current])
                continue
            symbol_map.setdefault(sym, set()).update(followpos[pos])

        for sym, target in symbol_map.items():
            frozen_target = frozenset(target)
            if frozen_target not in state_names:
                state_names[frozen_target] = f'S{state_id}'
                states.append(frozen_target)
                unmarked.append(frozen_target)
                state_id += 1
            transitions[(state_names[current], sym)] = state_names[frozen_target]

    afd = {
        'states': list(state_names.values()),
        'start': state_names[start],
        'accepting': list(accepting),
        'transitions': transitions
    }

    return afd


def export_afd_to_json(afd, filename="afd.json"):
    """Exporta el AFD a un archivo JSON dentro de la carpeta 'json', adaptando las claves de transiciones."""
    # Asegurar que el directorio 'json' existe
    output_dir = "json"
    os.makedirs(output_dir, exist_ok=True)

    # Crear el path completo
    full_path = os.path.join(output_dir, filename)

    # Preparar el AFD para ser serializado
    json_ready = {
        "states": afd["states"],
        "start": afd["start"],
        "accepting": afd["accepting"],
        "transitions": {
            f"{state},{symbol}": target
            for (state, symbol), target in afd["transitions"].items()
        }
    }

    # Guardar en archivo .json
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(json_ready, f, indent=4)

    print(f"📄 AFD exportado a JSON en {full_path}")


def visualize_afd(afd, output_path='./../../Graphviz/afd.gv'):
    try:
        from graphviz import Digraph
        dot = Digraph()

        for state in afd['states']:
            if state in afd['accepting']:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state)

        dot.node('start', shape='point')
        dot.edge('start', afd['start'])

        for (origin, symbol), target in afd['transitions'].items():
            dot.edge(origin, target, label=symbol)

        output_dir = os.path.dirname(output_path)
        output_filename = os.path.splitext(os.path.basename(output_path))[0]

        dot.render(filename=output_filename, directory=output_dir, format='png', cleanup=True)
        print(f'AFD guardado como imagen en {output_dir}/{output_filename}.png')

    except ImportError:
        print("Graphviz no está instalado. Ejecuta: pip install graphviz")
