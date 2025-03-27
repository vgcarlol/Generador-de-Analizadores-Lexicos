# main_afd_test.py

from direct_construction import DirectAFDConstructor
from utils.expand_expression import expand_expression
from utils.regex_postfix import to_postfix


def prueba_afd(expr_raw, definitions):
    print("Expresión original:", expr_raw)

    # 1. Expandimos la expresión con las definiciones del YAL
    expr_exp = expand_expression(expr_raw, definitions)
    print("Expresion expandida:", expr_exp)

    if not expr_exp:
        print("❌ Error: expresión vacía después de expandir.")
        return

    # 2. Agregamos '#' y '.'
    expr_final = f"({expr_exp})#."
    postfix = to_postfix(expr_final)
    print("Postfix:", postfix)

    # 3. Construimos el AFD directamente con tu clase
    afd_inicio = DirectAFDConstructor(postfix).get_afd()

    # 4. Recorremos el AFD para imprimir los estados y transiciones
    print("\nAFD generado:")
    estados = []
    transiciones = {}
    aceptacion = []
    visitados = set()
    cola = [afd_inicio]

    while cola:
        estado = cola.pop(0)
        if estado.id in visitados:
            continue
        visitados.add(estado.id)
        nombre = f"S{estado.id}"
        estados.append(nombre)
        if estado.is_final:
            aceptacion.append(nombre)

        for simbolo, destino in estado.transitions.items():
            transiciones[(nombre, simbolo)] = f"S{destino.id}"
            if destino.id not in visitados:
                cola.append(destino)

    print("Estados:", estados)
    print("Estado inicial:", f"S{afd_inicio.id}")
    print("Estados de aceptación:", aceptacion)
    print("Transiciones:")
    for (origen, simbolo), destino in transiciones.items():
        print(f"  {origen} --{simbolo}--> {destino}")


if __name__ == "__main__":
    definitions = {
        'digit': "['0'-'9']"
    }
    prueba_afd('digit+(\\.digit+)?(E(\\+|\\-)?digit+)?', definitions)
