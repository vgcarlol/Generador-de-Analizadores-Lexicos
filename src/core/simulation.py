# archivo: core/simulation.py

def simulate_afd(afd, input_string):
    current_state = afd
    for symbol in input_string:
        if symbol in current_state.transitions:
            current_state = current_state.transitions[symbol]
        elif 'ε' in current_state.transitions:  # Manejo de ε-transiciones
            epsilon_targets = current_state.transitions['ε']
            if isinstance(epsilon_targets, list):
                current_state = epsilon_targets[0]  # Tomamos el primer ε-movimiento
            else:
                current_state = epsilon_targets
        else:
            print(f"❌ ERROR: No hay transición para '{symbol}'. Cadena rechazada.")
            return False
    return current_state.is_final