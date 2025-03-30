# archivo: core/minimization.py

from collections import defaultdict, deque
from core.direct_construction import State

class AFDMinimizer:
    def __init__(self, start_state):
        self.start = start_state
        self.all_states = self._collect_states(start_state)
        self.state_id_map = {state.id: state for state in self.all_states}
        self.alphabet = self._get_alphabet()

    def _collect_states(self, start):
        """Recorre el AFD (por ejemplo, en BFS) y devuelve una lista con todos los estados alcanzables."""
        visited = {}
        stack = [start]
        while stack:
            state = stack.pop()
            if state.id in visited:
                continue
            visited[state.id] = state
            for target in state.transitions.values():
                stack.append(target)
        return list(visited.values())

    def _get_alphabet(self):
        """Extrae el conjunto de símbolos que aparecen en las transiciones."""
        alphabet = set()
        for state in self.all_states:
            for symbol in state.transitions.keys():
                alphabet.add(symbol)
        return alphabet

    def minimize(self):
        # Paso 1: Particionar los estados en finales y no finales
        finals = frozenset(s.id for s in self.all_states if s.is_final)
        non_finals = frozenset(s.id for s in self.all_states if not s.is_final)
        partitions = []
        if finals:
            partitions.append(finals)
        if non_finals:
            partitions.append(non_finals)

        # Paso 2: Construir la estructura de transiciones inversas
        inv_trans = {symbol: defaultdict(set) for symbol in self.alphabet}
        for state in self.all_states:
            for symbol, target in state.transitions.items():
                inv_trans[symbol][target.id].add(state.id)

        # Paso 3: Algoritmo de Hopcroft
        worklist = deque(partitions.copy())
        while worklist:
            A = worklist.popleft()
            for c in self.alphabet:
                # X = conjunto de estados que tienen una transición con c a algún estado de A
                X = set()
                for state_id in A:
                    if state_id in inv_trans[c]:
                        X.update(inv_trans[c][state_id])
                new_partitions = []
                for Y in partitions:
                    intersection = Y & X
                    difference = Y - X
                    if intersection and difference:
                        new_partitions.append(frozenset(intersection))
                        new_partitions.append(frozenset(difference))
                        if Y in worklist:
                            worklist.remove(Y)
                            worklist.append(frozenset(intersection))
                            worklist.append(frozenset(difference))
                        else:
                            # Añadimos el subconjunto más pequeño a la lista de trabajo
                            if len(intersection) <= len(difference):
                                worklist.append(frozenset(intersection))
                            else:
                                worklist.append(frozenset(difference))
                    else:
                        new_partitions.append(Y)
                partitions = new_partitions

        # Paso 4: Mapear cada estado original a su representante (por ejemplo, el de menor id)
        rep = {}
        for part in partitions:
            rep_state = min(part)  # Elige el de menor id como representante
            for state_id in part:
                rep[state_id] = rep_state

        # Paso 5: Reconstruir el DFA minimizado
        new_states = {}
        for part in partitions:
            rep_state_id = min(part)
            orig_state = self.state_id_map[rep_state_id]
            new_state = State(positions=frozenset(), is_final=orig_state.is_final)
            # Conserva el token_id si el estado es final (según tu implementación)
            if hasattr(orig_state, 'token_id'):
                new_state.token_id = orig_state.token_id
            new_states[rep_state_id] = new_state

        # Configurar las transiciones de los nuevos estados
        for state in self.all_states:
            src = rep[state.id]
            new_src = new_states[src]
            for symbol, target in state.transitions.items():
                tgt = rep[target.id]
                new_src.transitions[symbol] = new_states[tgt]

        # El nuevo estado inicial es el que corresponde al representante del estado inicial original
        new_start = new_states[rep[self.start.id]]
        return new_start
