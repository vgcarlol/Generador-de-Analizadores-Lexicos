from collections import defaultdict

class Node:
    def __init__(self, symbol, nullable=False):
        self.symbol = symbol
        self.left = None
        self.right = None
        self.nullable = nullable
        self.firstpos = set()
        self.lastpos = set()
        self.position = None  # Se asignará solo a hojas

class State:
    _id_counter = 0 

    def __init__(self, positions, is_final=False):
        self.id = State._id_counter  
        State._id_counter += 1
        self.positions = positions
        self.transitions = {}  
        self.is_final = is_final

    def __repr__(self):
        return f"State(id={self.id}, final={self.is_final}, positions={self.positions}, transitions={self.transitions})"

class DirectAFDConstructor:
    
    def __init__(self, regex_postfix):
        # Ahora regex_postfix es una lista de tokens
        self.regex_postfix = regex_postfix
        self.symbol_positions = {}  # Mapear símbolos a posiciones en el árbol
        self.followpos = defaultdict(set)  # Mapa de followpos para cada posición
        self.syntax_tree = self.build_syntax_tree()
        self.start_state = self.construct_afd()

    def build_syntax_tree(self):
        stack = []
        position_counter = 1  # Contador para asignar posiciones únicas a hojas

        for symbol in self.regex_postfix:
            # Caso operandos: alfanuméricos, '#' o literales (entre comillas), conjuntos (entre corchetes)
            # y ahora el caso en que el símbolo es exactamente "_"
            if (symbol.isalnum() or symbol == "#" or symbol == "_" or
                (symbol.startswith("'") and symbol.endswith("'")) or
                (symbol.startswith('"') and symbol.endswith('"')) or
                (symbol.startswith("[") and symbol.endswith("]")) or
                symbol in {"+", "-", "=", ":", "(", ")"}):

                node = Node(symbol)
                node.position = position_counter
                node.firstpos.add(position_counter)
                node.lastpos.add(position_counter)
                self.symbol_positions[position_counter] = symbol
                position_counter += 1
                stack.append(node)

            elif symbol == '*':  # Operador Kleene
                if len(stack) < 1:
                    raise ValueError(f"Error: * sin operandos en '{self.regex_postfix}'")
                child = stack.pop()
                node = Node('*', nullable=True)
                node.left = child
                node.firstpos = child.firstpos
                node.lastpos = child.lastpos
                for pos in node.lastpos:
                    self.followpos[pos].update(node.firstpos)
                stack.append(node)

            elif symbol == '+':  # X+ se transforma en X . X*
                if len(stack) < 1:
                    raise ValueError(f"Error: + sin operandos en '{self.regex_postfix}'")
                child = stack.pop()
                star_node = Node('*', nullable=True)
                star_node.left = child
                star_node.firstpos = child.firstpos
                star_node.lastpos = child.lastpos
                for pos in star_node.lastpos:
                    self.followpos[pos].update(star_node.firstpos)
                node = Node('.')
                node.left = child
                node.right = star_node
                node.nullable = child.nullable
                node.firstpos = child.firstpos
                node.lastpos = star_node.lastpos
                for pos in child.lastpos:
                    self.followpos[pos].update(star_node.firstpos)
                stack.append(node)

            elif symbol == '?':  # X? se transforma en (X | ε)
                if len(stack) < 1:
                    raise ValueError(f"Error: ? sin operandos en '{self.regex_postfix}'")
                child = stack.pop()
                epsilon_node = Node("ε", nullable=True)
                node = Node('|', nullable=True)
                node.left = child
                node.right = epsilon_node
                node.firstpos = child.firstpos
                node.lastpos = child.lastpos
                stack.append(node)

            elif symbol == '|':  # Unión
                if len(stack) < 2:
                    raise ValueError(f"Error: | sin suficientes operandos en '{self.regex_postfix}'")
                right = stack.pop()
                left = stack.pop()
                node = Node('|', nullable=left.nullable or right.nullable)
                node.left = left
                node.right = right
                node.firstpos = left.firstpos | right.firstpos
                node.lastpos = left.lastpos | right.lastpos
                stack.append(node)

            elif symbol == '.':  # Concatenación
                if len(stack) < 2:
                    raise ValueError(f"Error: . sin suficientes operandos en '{self.regex_postfix}'")
                right = stack.pop()
                left = stack.pop()
                node = Node('.')
                node.left = left
                node.right = right
                node.nullable = left.nullable and right.nullable
                node.firstpos = left.firstpos if not left.nullable else left.firstpos | right.firstpos
                node.lastpos = right.lastpos if not right.nullable else right.lastpos | left.lastpos
                for pos in left.lastpos:
                    self.followpos[pos].update(right.firstpos)
                stack.append(node)
            
            else:
                raise ValueError(f"Operador desconocido: {symbol}")

        if len(stack) > 1:
            root = stack.pop()
            while stack:
                left = stack.pop()
                new_root = Node('.')
                new_root.left = left
                new_root.right = root
                new_root.firstpos = left.firstpos
                new_root.lastpos = root.lastpos
                for pos in left.lastpos:
                    self.followpos[pos].update(root.firstpos)
                root = new_root
            stack.append(root)

        if len(stack) != 1:
            raise ValueError(f"Error: Expresión postfix mal formada '{self.regex_postfix}', pila final: {len(stack)} elementos")

        return stack.pop()

    def construct_afd(self):
        syntax_tree_root = self.syntax_tree
        start_positions = frozenset(syntax_tree_root.firstpos)
        estados_pendientes = [start_positions]
        mapeo_estados = {
            start_positions: State(
                start_positions,
                is_final=('#' in [self.symbol_positions[p] for p in start_positions])
            )
        }
        estados_afd = [mapeo_estados[start_positions]]

        from collections import defaultdict
        while estados_pendientes:
            current_set = estados_pendientes.pop(0)
            current_state = mapeo_estados[current_set]
            symbol_to_positions = defaultdict(set)
            for pos in current_set:
                if pos not in self.symbol_positions:
                    continue
                symbol = self.symbol_positions[pos]
                symbol_to_positions[symbol].update(self.followpos[pos])
            for symbol, new_set in symbol_to_positions.items():
                new_set = frozenset(new_set)
                if not new_set:
                    continue
                if new_set not in mapeo_estados:
                    is_final = '#' in [self.symbol_positions[p] for p in new_set]
                    new_state = State(new_set, is_final=is_final)
                    mapeo_estados[new_set] = new_state
                    estados_afd.append(new_state)
                    estados_pendientes.append(new_set)
                current_state.transitions[symbol] = mapeo_estados[new_set]
        return estados_afd[0]

    def get_afd(self):
        return self.start_state
