# utils/syntax_tree/afd_from_tree.py
from collections import deque


def construct_direct_afd(tree, pos_to_symbol):
    # Paso 1: calcular nullable, firstpos, lastpos, followpos
    from utils.syntax_tree.nullable_followpos import compute_nullable_first_last, compute_followpos

    compute_nullable_first_last(tree)
    followpos = {i: set() for i in pos_to_symbol}
    compute_followpos(tree, followpos)

    # Paso 2: construir el AFD desde firstpos(tree)
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
            if sym == '#':  # símbolo de fin
                accepting.add(state_names[current])
                continue
            if sym not in symbol_map:
                symbol_map[sym] = set()
            symbol_map[sym].update(followpos[pos])

        for sym, target in symbol_map.items():
            frozen_target = frozenset(target)
            if frozen_target not in state_names:
                state_names[frozen_target] = f'S{state_id}'
                states.append(frozen_target)
                unmarked.append(frozen_target)
                state_id += 1
            transitions[(state_names[current], sym)] = state_names[frozen_target]

    return {
        'states': list(state_names.values()),
        'start': state_names[start],
        'accepting': list(accepting),
        'transitions': transitions
    }
