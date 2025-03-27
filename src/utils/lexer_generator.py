import json
import os
from utils.expand_expression import expand_expression
from utils.regex_postfix import to_postfix
from utils.syntax_tree.build_tree import build_syntax_tree
from utils.syntax_tree.afd_from_tree import construct_direct_afd

# Definir los estados globalmente
S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20 = range(21)

class Lexer:
    def __init__(self, afds):
        self.afds = afds  # Los AFDs definidos por cada token
        self.current_afd = None
        self.current_state = None

    def set_afd(self, token):
        """Establece el AFD para el token que se quiere procesar."""
        self.current_afd = self.afds.get(token)
        self.current_state = self.current_afd['start'] if self.current_afd else None

    def next_token(self, char):
        """Procesa el siguiente carácter sobre el AFD."""
        if (self.current_state, char) in self.current_afd['transitions']:
            self.current_state = self.current_afd['transitions'][(self.current_state, char)]
        else:
            return None
        
        if self.current_state in self.current_afd['accepting']:
            return self.current_afd['accepting'][0]  # Devolver el nombre del token si se acepta
        
        return None

    def tokenize(self, input_str):
        """Tokeniza una cadena de entrada, devolviendo los tokens reconocidos."""
        tokens = []
        self.set_afd('start')  # Asumimos que 'start' es el estado inicial
        
        for char in input_str:
            token_type = self.next_token(char)
            if token_type:
                tokens.append(token_type)
                self.set_afd(token_type)  # Cambiar el AFD al siguiente token
            else:
                # Si no se encuentra un token válido, reportar un error léxico
                print(f"Error léxico: caracter no reconocido '{char}'")
                return None
        return tokens

    def add_afd(self, token, afd):
        """Añade un AFD a la lista de AFDs disponibles."""
        self.afds[token] = afd

    def tokenize_from_file(self, file_path):
        """Tokeniza el contenido de un archivo."""
        with open(file_path, 'r') as f:
            input_str = f.read()
        return self.tokenize(input_str)

# Función para guardar los AFDs generados en un archivo JSON
def save_afds_to_file(afds, filename="afds.json"):
    with open(filename, 'w') as f:
        json.dump(afds, f)
    print(f"AFDs guardados en {filename}.")

# Función para cargar los AFDs desde un archivo JSON
def load_afds_from_file(filename="afds.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            afds = json.load(f)
        print(f"AFDs cargados desde {filename}.")
        return afds
    else:
        print(f"No se encontraron AFDs en {filename}.")
        return None

# Función para generar los AFDs si no existen, y cargarlos si ya están guardados
def generar_afds_yalex(yalex_file):
    afds = load_afds_from_file()  # Cargar los AFDs guardados si existen
    
    if afds is None:  # Si no se cargaron, los generamos desde el archivo YALex
        definitions, tokens = parse_yalex(yalex_file)  # Parsear el archivo YALex
        afds = {}

        for token, regex in tokens.items():
            print(f"\n🔎 Procesando token: {token}")
            expanded = expand_expression(regex, definitions)
            print(f"🧠 Expresión expandida: {expanded}")

            final_expr = f"({expanded}).#"
            postfix = to_postfix(final_expr)
            print(f"📤 Postfix: {postfix}")

            syntax_tree, pos_to_symbol = build_syntax_tree(postfix)
            graficar_arbol(syntax_tree, filename=f"tree_{token}")

            afd = construct_direct_afd(syntax_tree, pos_to_symbol)
            afds[token] = afd
        
        # Guardar los AFDs generados
        save_afds_to_file(afds)
    
    return afds

# Función para generar el programa fuente del lexer
def generar_lexer_program(afds):
    lexer_code = """
class Lexer:
    def __init__(self, afds):
        self.afds = afds
        self.current_afd = None
        self.current_state = None

    def set_afd(self, token):
        self.current_afd = self.afds.get(token)
        self.current_state = self.current_afd['start'] if self.current_afd else None

    def next_token(self, char):
        if (self.current_state, char) in self.current_afd['transitions']:
            self.current_state = self.current_afd['transitions'][(self.current_state, char)]
        else:
            return None
        if self.current_state in self.current_afd['accepting']:
            return self.current_afd['accepting'][0] 

    def tokenize(self, input_str):
        tokens = []
        self.set_afd('start')
        for char in input_str:
            token_type = self.next_token(char)
            if token_type:
                tokens.append(token_type)
        return tokens

    def add_afd(self, token, afd):
        self.afds[token] = afd

lexer = Lexer(afds)
"""
    # Generar la integración de los AFDs en el código del lexer
    for token, afd in afds.items():
        lexer_code += f"""
lexer.add_afd('{token}', {{
    'start': {afd['start']},
    'accepting': {afd['accepting']},
    'transitions': {afd['transitions']}
}}) 
"""
    lexer_code += """
# Ejemplo de uso
input_string = 'a+b'
tokens = lexer.tokenize(input_string)
if tokens is not None:
    print(tokens)  # Muestra los tokens generados
"""
    return lexer_code

# Guardar el código generado para el lexer en un archivo
def save_lexer_code(afds):
    lexer_program = generar_lexer_program(afds)
    with open('lexer_program.py', 'w') as f:
        f.write(lexer_program)
    print("Lexer program generado en 'lexer_program.py'.")
