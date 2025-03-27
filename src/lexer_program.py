
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

lexer.add_afd('delim', {
    'start': S0,
    'accepting': ['S1'],
    'transitions': {('S0', '\\s'): 'S1', ('S0', '\\t'): 'S1', ('S0', '\\n'): 'S1'}
}) 

lexer.add_afd('ws', {
    'start': S0,
    'accepting': ['S5'],
    'transitions': {('S0', 'd'): 'S1', ('S1', 'e'): 'S2', ('S2', 'l'): 'S3', ('S3', 'i'): 'S4', ('S4', 'm'): 'S5', ('S5', 'm'): 'S5'}
}) 

lexer.add_afd('ter', {
    'start': S0,
    'accepting': ['S1'],
    'transitions': {('S0', 'A'): 'S1', ('S0', 'B'): 'S1', ('S0', 'C'): 'S1', ('S0', 'D'): 'S1', ('S0', 'E'): 'S1', ('S0', 'F'): 'S1', ('S0', 'G'): 'S1', ('S0', 'H'): 'S1', ('S0', 'I'): 'S1', ('S0', 'J'): 'S1', ('S0', 'K'): 'S1', ('S0', 'L'): 'S1', ('S0', 'M'): 'S1', ('S0', 'N'): 'S1', ('S0', 'O'): 'S1', ('S0', 'P'): 'S1', ('S0', 'Q'): 'S1', ('S0', 'R'): 'S1', ('S0', 'S'): 'S1', ('S0', 'T'): 'S1', ('S0', 'U'): 'S1', ('S0', 'V'): 'S1', ('S0', 'W'): 'S1', ('S0', 'X'): 'S1', ('S0', 'Y'): 'S1', ('S0', 'Z'): 'S1', ('S0', 'a'): 'S1', ('S0', 'b'): 'S1', ('S0', 'c'): 'S1', ('S0', 'd'): 'S1', ('S0', 'e'): 'S1', ('S0', 'f'): 'S1', ('S0', 'g'): 'S1', ('S0', 'h'): 'S1', ('S0', 'i'): 'S1', ('S0', 'j'): 'S1', ('S0', 'k'): 'S1', ('S0', 'l'): 'S1', ('S0', 'm'): 'S1', ('S0', 'n'): 'S1', ('S0', 'o'): 'S1', ('S0', 'p'): 'S1', ('S0', 'q'): 'S1', ('S0', 'r'): 'S1', ('S0', 's'): 'S1', ('S0', 't'): 'S1', ('S0', 'u'): 'S1', ('S0', 'v'): 'S1', ('S0', 'w'): 'S1', ('S0', 'x'): 'S1', ('S0', 'y'): 'S1', ('S0', 'z'): 'S1'}
}) 

lexer.add_afd('str', {
    'start': S0,
    'accepting': ['S0'],
    'transitions': {('S0', '_'): 'S0'}
}) 

lexer.add_afd('digit', {
    'start': S0,
    'accepting': ['S1'],
    'transitions': {('S0', '0'): 'S1', ('S0', '1'): 'S1', ('S0', '2'): 'S1', ('S0', '3'): 'S1', ('S0', '4'): 'S1', ('S0', '5'): 'S1', ('S0', '6'): 'S1', ('S0', '7'): 'S1', ('S0', '8'): 'S1', ('S0', '9'): 'S1'}
}) 

lexer.add_afd('digits', {
    'start': S0,
    'accepting': ['S5'],
    'transitions': {('S0', 'd'): 'S1', ('S1', 'i'): 'S2', ('S2', 'g'): 'S3', ('S3', 'i'): 'S4', ('S4', 't'): 'S5', ('S5', 't'): 'S5'}
}) 

lexer.add_afd('id', {
    'start': S0,
    'accepting': ['S3'],
    'transitions': {('S0', 't'): 'S1', ('S1', 'e'): 'S2', ('S2', 'r'): 'S3', ('S3', 'd'): 'S4', ('S3', 't'): 'S5', ('S3', 's'): 'S6', ('S4', 'i'): 'S7', ('S5', 'e'): 'S8', ('S6', 't'): 'S9', ('S7', 'g'): 'S10', ('S8', 'r'): 'S3', ('S9', 'r'): 'S3', ('S10', 'i'): 'S11', ('S11', 't'): 'S3'}
}) 

lexer.add_afd('number', {
    'start': S0,
    'accepting': ['S20'],
    'transitions': {('S0', 'd'): 'S1', ('S1', 'i'): 'S2', ('S2', 'g'): 'S3', ('S3', 'i'): 'S4', ('S4', 't'): 'S5', ('S5', 's'): 'S6', ('S6', 'd'): 'S7', ('S7', 'i'): 'S8', ('S8', 'g'): 'S9', ('S9', 'i'): 'S10', ('S10', 't'): 'S11', ('S11', 's'): 'S12', ('S12', 'E'): 'S13', ('S13', '\\-'): 'S14', ('S13', '\\+'): 'S14', ('S14', 'd'): 'S15', ('S15', 'i'): 'S16', ('S16', 'g'): 'S17', ('S17', 'i'): 'S18', ('S18', 't'): 'S19', ('S19', 's'): 'S20'}
}) 

# Ejemplo de uso
input_string = 'a+b'
tokens = lexer.tokenize(input_string)
if tokens is not None:
    print(tokens)  # Muestra los tokens generados
