# lexer_program.py
# ⚠️ Este archivo fue generado automáticamente. No modificar manualmente.

AFDS = {
    'delim': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\s'): 'S1',
        ('S0', '\\t'): 'S1',
        ('S0', '\\n'): 'S1'
    }
    },
    'ws': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5'],
        'start': 'S0',
        'accepting': ['S5'],
        'transitions': {
        ('S0', 'd'): 'S1',
        ('S1', 'e'): 'S2',
        ('S2', 'l'): 'S3',
        ('S3', 'i'): 'S4',
        ('S4', 'm'): 'S5',
        ('S5', 'm'): 'S5'
    }
    },
    'digit': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '0'): 'S1',
        ('S0', '1'): 'S1',
        ('S0', '2'): 'S1',
        ('S0', '3'): 'S1',
        ('S0', '4'): 'S1',
        ('S0', '5'): 'S1',
        ('S0', '6'): 'S1',
        ('S0', '7'): 'S1',
        ('S0', '8'): 'S1',
        ('S0', '9'): 'S1'
    }
    },
    'digits': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5'],
        'start': 'S0',
        'accepting': ['S5'],
        'transitions': {
        ('S0', 'd'): 'S1',
        ('S1', 'i'): 'S2',
        ('S2', 'g'): 'S3',
        ('S3', 'i'): 'S4',
        ('S4', 't'): 'S5',
        ('S5', 't'): 'S5'
    }
    },
    'number': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 'S20'],
        'start': 'S0',
        'accepting': ['S20'],
        'transitions': {
        ('S0', 'd'): 'S1',
        ('S1', 'i'): 'S2',
        ('S2', 'g'): 'S3',
        ('S3', 'i'): 'S4',
        ('S4', 't'): 'S5',
        ('S5', 's'): 'S6',
        ('S6', 'd'): 'S7',
        ('S7', 'i'): 'S8',
        ('S8', 'g'): 'S9',
        ('S9', 'i'): 'S10',
        ('S10', 't'): 'S11',
        ('S11', 's'): 'S12',
        ('S12', 'E'): 'S13',
        ('S13', '\\-'): 'S14',
        ('S13', '\\+'): 'S14',
        ('S14', 'd'): 'S15',
        ('S15', 'i'): 'S16',
        ('S16', 'g'): 'S17',
        ('S17', 'i'): 'S18',
        ('S18', 't'): 'S19',
        ('S19', 's'): 'S20'
    }
    }
}

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
    entrada = input("📝 Ingresa una cadena para analizar: ")
    resultado = analizar_cadena(entrada)
    print("\n📍 Tokens encontrados:")
    for token, lexema in resultado:
        print(f"  - {token}: '{lexema}'")
