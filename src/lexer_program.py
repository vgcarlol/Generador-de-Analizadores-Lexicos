# lexer_program.py
# ⚠️ Este archivo fue generado automáticamente. No modificar manualmente.

AFDS = {
    'TOKEN_0': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\s'): 'S1',
        ('S0', '\\t'): 'S1',
        ('S0', '\\n'): 'S1',
        ('S1', 'm'): 'S1'
    }
    },
    'TOKEN_1': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11'],
        'start': 'S0',
        'accepting': ['S6'],
        'transitions': {
        ('S0', 'l'): 'S1',
        ('S1', 'e'): 'S2',
        ('S2', 't'): 'S3',
        ('S3', 't'): 'S4',
        ('S4', 'e'): 'S5',
        ('S5', 'r'): 'S6',
        ('S6', 'l'): 'S7',
        ('S6', '_'): 'S6',
        ('S6', '0'): 'S6',
        ('S6', '1'): 'S6',
        ('S6', '2'): 'S6',
        ('S6', '3'): 'S6',
        ('S6', '4'): 'S6',
        ('S6', '5'): 'S6',
        ('S6', '6'): 'S6',
        ('S6', '7'): 'S6',
        ('S6', '8'): 'S6',
        ('S6', '9'): 'S6',
        ('S7', 'e'): 'S8',
        ('S8', 't'): 'S9',
        ('S9', 't'): 'S10',
        ('S10', 'e'): 'S11',
        ('S11', 'r'): 'S6'
    }
    },
    'TOKEN_2': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17'],
        'start': 'S0',
        'accepting': ['S13', 'S0', 'S17'],
        'transitions': {
        ('S0', 'd'): 'S1',
        ('S0', 'E'): 'S2',
        ('S1', 'i'): 'S3',
        ('S2', 'd'): 'S4',
        ('S2', '\\+'): 'S5',
        ('S2', '\\-'): 'S5',
        ('S3', 'g'): 'S6',
        ('S4', 'i'): 'S7',
        ('S5', 'd'): 'S4',
        ('S6', 'i'): 'S8',
        ('S7', 'g'): 'S9',
        ('S8', 't'): 'S10',
        ('S9', 'i'): 'S11',
        ('S10', 't'): 'S10',
        ('S10', 'd'): 'S12',
        ('S11', 't'): 'S13',
        ('S12', 'i'): 'S14',
        ('S13', 't'): 'S13',
        ('S14', 'g'): 'S15',
        ('S15', 'i'): 'S16',
        ('S16', 't'): 'S17',
        ('S17', 't'): 'S17',
        ('S17', 'E'): 'S2'
    }
    },
    'TOKEN_3': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\;'): 'S1'
    }
    },
    'TOKEN_4': {
        'states': ['S0', 'S1', 'S2'],
        'start': 'S0',
        'accepting': ['S2'],
        'transitions': {
        ('S0', ':'): 'S1',
        ('S1', '='): 'S2'
    }
    },
    'TOKEN_5': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\<'): 'S1'
    }
    },
    'TOKEN_6': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\='): 'S1'
    }
    },
    'TOKEN_7': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\+'): 'S1'
    }
    },
    'TOKEN_8': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\-'): 'S1'
    }
    },
    'TOKEN_9': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\*'): 'S1'
    }
    },
    'TOKEN_10': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\/'): 'S1'
    }
    },
    'TOKEN_11': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\('): 'S1'
    }
    },
    'TOKEN_12': {
        'states': ['S0', 'S1'],
        'start': 'S0',
        'accepting': ['S1'],
        'transitions': {
        ('S0', '\\)'): 'S1'
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
    try:
        with open("./entradas/random_data_3.txt", "r", encoding="utf-8") as f:
            entrada = f.read()
    except FileNotFoundError:
        print("❌ No se encontró el archivo 'input.txt'")
        exit(1)

    resultado = analizar_cadena(entrada)

    with open("./salidas/random_data_3.txt", "w", encoding="utf-8") as f:
        for token, lexema in resultado:
            f.write(f"Token: {token}, Lexema: '{lexema}'\n")

    print("✅ Análisis completado. Revisa 'output.txt'.")
