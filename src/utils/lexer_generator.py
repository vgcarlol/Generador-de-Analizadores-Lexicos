# utils/lexer_generator.py

def generar_lexer_program(afds):
    def formatear_diccionario(dic):
        return "{\n" + ",\n".join([f"        {repr(k)}: {repr(v)}" for k, v in dic.items()]) + "\n    }"

    afd_definiciones = []
    for token, afd in afds.items():
        afd_code = f"""    '{token}': {{
        'states': {afd['states']},
        'start': {repr(afd['start'])},
        'accepting': {afd['accepting']},
        'transitions': {formatear_diccionario(afd['transitions'])}
    }}"""
        afd_definiciones.append(afd_code)

    lexer_code = f'''# lexer_program.py
# ⚠️ Este archivo fue generado automáticamente. No modificar manualmente.

AFDS = {{
{",\n".join(afd_definiciones)}
}}

def analizar_cadena(cadena):
    tokens_encontrados = []
    i = 0
    while i < len(cadena):
        mejor_match = None
        mejor_token = None
        longitud_match = 0

        for token, afd in AFDS.items():
            estado_actual = afd['start']
            j = i
            aceptado = False
            ultimo_estado_aceptado = -1

            while j < len(cadena) and (estado_actual, cadena[j]) in afd['transitions']:
                estado_actual = afd['transitions'][(estado_actual, cadena[j])]
                j += 1
                if estado_actual in afd['accepting']:
                    aceptado = True
                    ultimo_estado_aceptado = j

            if aceptado and ultimo_estado_aceptado - i > longitud_match:
                mejor_match = cadena[i:ultimo_estado_aceptado]
                mejor_token = token
                longitud_match = ultimo_estado_aceptado - i

        if mejor_match:
            tokens_encontrados.append((mejor_token, mejor_match))
            i += longitud_match
        else:
            tokens_encontrados.append(('ERROR', cadena[i]))
            i += 1

    return tokens_encontrados


if __name__ == "__main__":
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            entrada = f.read()
    except FileNotFoundError:
        print("❌ No se encontró el archivo 'input.txt'")
        exit(1)

    resultado = analizar_cadena(entrada)

    with open("output.txt", "w", encoding="utf-8") as f:
        for token, lexema in resultado:
            f.write(f"{{token}}: '{{lexema}}'\\n")

    print("✅ Análisis completado. Revisa 'output.txt'.")
'''

    return lexer_code
