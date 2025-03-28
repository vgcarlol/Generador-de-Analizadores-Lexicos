# lexer_program.py
# ⚠️ Este archivo fue generado automáticamente. No modificar manualmente.

AFDS = {
    'TOKEN_0': {
        'states': ['S0', 'S1', 'S2'],
        'start': 'S0',
        'accepting': ['S2'],
        'transitions': {
        ('S0', 'w'): 'S1',
        ('S1', 's'): 'S2'
    }
    },
    'TOKEN_1': {
        'states': ['S0', 'S1', 'S2'],
        'start': 'S0',
        'accepting': ['S2'],
        'transitions': {
        ('S0', 'i'): 'S1',
        ('S1', 'd'): 'S2'
    }
    },
    'TOKEN_2': {
        'states': ['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6'],
        'start': 'S0',
        'accepting': ['S6'],
        'transitions': {
        ('S0', 'n'): 'S1',
        ('S1', 'u'): 'S2',
        ('S2', 'm'): 'S3',
        ('S3', 'b'): 'S4',
        ('S4', 'e'): 'S5',
        ('S5', 'r'): 'S6'
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
