from collections import defaultdict
from core.direct_construction import State 

class AFDMinimizer:
    def __init__(self, start_state):
        self.start = start_state
        self.states = []
        self.transitions = defaultdict(dict)
        self.alphabet = set()
        self.build_afd_info()
    
    def build_afd_info(self):
        visited = set()
        queue = [self.start]
        state_ids = {}
        
        while queue:
            state = queue.pop(0)
            if id(state) in visited:
                continue
            visited.add(id(state))
            
            if state not in state_ids:
                state_ids[state] = len(self.states)
                self.states.append({
                    'id': len(self.states),
                    'is_final': state.is_final
                })
            
            for sym, target in state.transitions.items():
                self.alphabet.add(sym)
                self.transitions[state_ids[state]][sym] = id(target)
                if target not in queue and id(target) not in visited:
                    queue.append(target)
        
        # Reemplazar IDs con referencias reales
        for src, trans in self.transitions.items():
            for sym, tgt in trans.items():
                self.transitions[src][sym] = state_ids[next(s for s in state_ids if id(s) == tgt)]
    
    def minimize(self):
        partitions = []
        finals = [s['id'] for s in self.states if s['is_final']]
        non_finals = [s['id'] for s in self.states if not s['is_final']]
        
        if finals:
            partitions.append(frozenset(finals))
        if non_finals:
            partitions.append(frozenset(non_finals))
        
        while True:
            new_partitions = []
            for part in partitions:
                split = defaultdict(list)
                for state in part:
                    key = tuple(self.transitions[state].get(sym, None) for sym in sorted(self.alphabet))
                    split[key].append(state)
                new_partitions.extend([frozenset(g) for g in split.values()])
            
            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions
        
        # Reconstruir el AFD minimizado
        state_map = {}
        new_states = []
        for i, part in enumerate(partitions):
            rep = next(iter(part))
            state_map[rep] = i
            new_states.append(State(positions=frozenset(part), is_final=self.states[rep]['is_final']))
        
        for src_rep, data in enumerate(partitions):
            for sym in self.alphabet:
                if sym in self.transitions[src_rep]:
                    dest = self.transitions[src_rep][sym]
                    for p in partitions:
                        if dest in p:
                            new_states[state_map[src_rep]].transitions[sym] = new_states[state_map[next(iter(p))]]
                            break
        
        return new_states[state_map[next(iter(partitions[0]))]]
