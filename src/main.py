from regex_parser import RegexParser
from direct_construction import DirectAFDConstructor
from minimization import AFDMinimizer
from simulation import simulate_afd
from visualization import visualize_afd

def main():
    regex = input("Ingrese la expresión regular: ")
    string = input("Ingrese la cadena a evaluar: ")

    regex_postfix = RegexParser.infix_to_postfix(regex)
    print(f"\nExpresión en Postfix: {regex_postfix}")

    # Construcción Directa del AFD
    afd_constructor = DirectAFDConstructor(regex_postfix)
    afd = afd_constructor.get_afd()

    print("✅ AFD construido correctamente.")

    # Minimización del AFD
    minimized_afd = AFDMinimizer(afd).minimize()
    print("✅ AFD minimizado correctamente.")
    
    # Visualización del AFD
    visualize_afd(minimized_afd)

    # Simulación de la cadena
    result = simulate_afd(minimized_afd, string)
    if result:
        print(f"✅ La cadena '{string}' es **aceptada** por el AFD.")
    else:
        print(f"❌ La cadena '{string}' **NO** es aceptada por el AFD.")

if __name__ == "__main__":
    main()
