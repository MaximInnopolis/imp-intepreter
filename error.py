##########
# IMPORTS
##########

from string_with_arrows import *

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
        result += '\n\n' + string_with_arrows(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, 'Illegal Character', info)

class InvalidSynaxError(Error):
    def __init__(self, pos_start, pos_end, info=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', info)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', info)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.info}\n'
        result += '\n\n' + string_with_arrows(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' File {pos.file_name}, line {str(pos.line_num + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result