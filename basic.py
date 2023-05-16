##########
#CONSTANTS
##########

DIGITS = '0123456789'


####################
# ERROR
####################

class Error:
    def __init__(self, pos_start, pos_end, error_name, info):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.info = info

    def as_string(self):
        result = f'{self.error_name}: {self.info}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.line_num + 1}'
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, 'Illegal Character', info)


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

    def advance(self, cur_char):
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
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value 

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
            elif self.cur_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.cur_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.cur_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.cur_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.cur_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.cur_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()

            else:
                pos_start = self.pos.copy()
                char = self.cur_char
                self.advance()
                return [], IllegalCharError(pos_start,  self.pos, "'" + char + "'")

        return tokens, None
    
    def create_number(self):
        num_str = ''
        dot_count = 0

        while self.cur_char != None and self.cur_char in DIGITS + '.':
            if self.cur_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.cur_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
        

####################
# RUN
####################

def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.create_tokens()

    return tokens, error
