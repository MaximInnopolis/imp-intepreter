##########
# IMPORTS
##########

import error
import string


##########
# CONSTANTS
##########

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = DIGITS + LETTERS


####################
# POSITION
####################

class Position:
    def __init__(self, index, line_num, col_num, file_name, file_text):
        self.index = index
        self.line_num = line_num
        self.col_num = col_num
        self.file_name = file_name
        self.file_text = file_text

    def advance(self, cur_char=None):
        self.index += 1
        self.col_num += 1

        if cur_char == '\n':
            self.line_num += 1
            self.col_num = 0

        return self
    
    def copy(self):
        return Position(self.index, self.line_num, self.col_num, self.file_name, self.file_text)


####################
# TOKENS
####################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQ = 'EQ'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

KEYWORDS = ['VAR']


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value 

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value


    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'        


####################
# LEXER
####################

class Lexer:
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.cur_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.cur_char)
        self.cur_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def create_tokens(self):
        tokens = []

        while self.cur_char != None:
            if self.cur_char in ' \t' :
                self.advance()
            elif self.cur_char in DIGITS:
                tokens.append(self.create_number())
            elif self.cur_char in LETTERS:
                tokens.append(self.create_identifier())
            elif self.cur_char == '=':
                tokens.append(Token(TT_EQ, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.cur_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()

            else:
                pos_start = self.pos.copy()
                char = self.cur_char
                self.advance()
                return [], error.IllegalCharError(pos_start,  self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def create_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.cur_char != None and self.cur_char in DIGITS + '.':
            if self.cur_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.cur_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        
    def create_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()
        
        while self.cur_char != None and self.cur_char in LETTERS_DIGITS + '_':
            id_str += self.cur_char
            self.advance()
            
        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, id_str, pos_start, self.pos)
    