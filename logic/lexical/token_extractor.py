from constants.informer import *
from constants.lexical import *

from helper.analyser import Analyser, TextAnalyser
from helper.informer import Informer
from helper.lexical import *
from helper.tester import StackTester
from storage.token_value_stack import TokenValueStack

class LexicalError(Informer):
    def __init__(self, message, position, severity=ERROR, specification="Lexical "):
        super().__init__(f'{message} in character {position - 1}', severity, specification)

class TokenExtractor:
    def __init__(self, analyser: Analyser, token_stack: TokenValueStack) -> None:
        self.analyser = analyser
        self.token_stack = token_stack

    def run(self):
        tokens = []
        token, index = self.next_token()
        while token != KeyWords.EOF:
            tokens.append((token, index))
            token, index = self.next_token()
        return tokens
    
    def run_with_values(self):
        tokens = []
        token, index = self.next_token_with_value()
        while token != KeyWords.EOF:
            tokens.append((token, index))
            token, index = self.next_token_with_value()
        return tokens

    def next_token(self):
        char = self.ignore_whitespace()
        if (not char):
            return self.get_eof_token()
        if (is_digit(char)):
            return self.get_number_token(char)
        if (is_alphabetical(char)):
            return self.get_word_token(char)
        # I do not diferentiate between single and double quotes (so char is a type of string)
        if (is_start_of_string(char)):
            return self.get_string_token(char)
        if (char in ISOLATED_CHARS):
            return self.get_isolated_token(char)
        if (char in MATHMATICAL_OPERATORS or char in COMPARISON_OPERATORS):
            return self.get_mathmatical_operator_token(char)
        if (char in BOOLEAN_OPERATORS):
            return self.get_boolean_operator_token(char)
        LexicalError(f"Unknown character: {char}", position=self.analyser.get_current_index(), severity=WARNING)
        return KeyWords.UNKNOWN, None
    
    def next_token_with_value(self):
        try:
            token, index = self.next_token()
            return token, self.token_stack.get(index)
        except Exception as e:
            return KeyWords.LEXICAL_ERROR, None    

    def get_number_token(self, digit):
        value = ""
        while(is_digit(digit) or digit in ACCEPTED_DIGIT_CHARS):
            value += digit
            digit = self.analyser.get_next_char()
        secondary_token = self.token_stack.store(value)
        return KeyWords.INTEGER, secondary_token
    
    def get_word_token(self, char):
        value = ""
        while(is_alphabetical(char) or is_digit(char) or char in ACCEPTED_WORD_CHARS):
            value += char
            char = self.analyser.get_next_char()
        keyword = KeyWords().get(value)
        if keyword != -1:
            return keyword, None
        secondary_token = self.token_stack.store(value)
        return ID, secondary_token
    
    def get_eof_token(self):
        return KeyWords.EOF, None
    
    def get_string_token(self, starter):
        value = ""
        prev_char = starter
        char = self.analyser.get_next_char()
        if (char in PROHIBITED_STRING_CHARS):
            LexicalError("String must end with a quote", position=self.analyser.get_current_index())
        while(char != starter or prev_char == '\\'):
            value += char
            prev_char = char
            char = self.analyser.get_next_char()
            if (char in PROHIBITED_STRING_CHARS):
                LexicalError("String must end with a quote", position=self.analyser.get_current_index())
        secondary_token = self.token_stack.store(value)
        return KeyWords.STRING, secondary_token
    
    def get_isolated_token(self, char):
        if char == ':':
            return KeyWords.COLON, None
        if char == ';':
            return KeyWords.SEMICOLON, None
        if char == ',':
            return KeyWords.COMMA, None
        if char == '[':
            return KeyWords.LEFT_SQUARE_BRACKET, None
        if char == ']':
            return KeyWords.RIGHT_SQUARE_BRACKET, None
        if char == '{':
            return KeyWords.LEFT_CURLY_BRACKET, None
        if char == '}':
            return KeyWords.RIGHT_CURLY_BRACKET, None
        if char == '(':
            return KeyWords.LEFT_ROUND_BRACKET, None
        if char == ')':
            return KeyWords.RIGHT_ROUND_BRACKET, None
        if char == '.':
            return KeyWords.DOT, None
        LexicalError("Unknown isolated character: " + char, position=self.analyser.get_current_index())

    def get_mathmatical_operator_token(self, operator):
        value = operator
        char = self.analyser.get_next_char()
        if (char == '='):
            value += '='
        elif (char == operator and char in ['+', '-', '*']):
            value += char
        elif (char == operator):
            LexicalError("Unknown operator: " + value + char, position=self.analyser.get_current_index())
        else:
            self.analyser.revert_to_last_char()
        if value == '=':
            return KeyWords.EQUAL, None
        if value == '==':
            return KeyWords.EQUALITY, None
        if value == '+':
            return KeyWords.PLUS, None
        if value == '+=':
            return KeyWords.PLUS_EQUAL, None
        if value == '-':
            return KeyWords.MINUS, None
        if value == '-=':
            return KeyWords.MINUS_EQUAL, None
        if value == '*':
            return KeyWords.MULTIPLY, None
        if value == '*=':
            return KeyWords.MULTIPLY_EQUAL, None
        if value == '/':
            return KeyWords.DIVIDE, None
        if value == '/=':
            return KeyWords.DIVIDE_EQUAL, None
        if value == '%':
            return KeyWords.MODULO, None
        if value == '%=':
            return KeyWords.MODULO_EQUAL, None
        if value == '<':
            return KeyWords.LESS_THAN, None
        if value == '<=':
            return KeyWords.LESS_THAN_EQUAL, None
        if value == '>':
            return KeyWords.GREATER_THAN, None
        if value == '>=':
            return KeyWords.GREATER_THAN_EQUAL, None
        if value == '!':
            return KeyWords.NOT, None
        if value == '!=':
            return KeyWords.NOT_EQUAL, None
        if value == "**":
            return KeyWords.EXPONENT, None
        if value == "++":
            return KeyWords.PLUS_PLUS, None
        if value == "--":
            return KeyWords.MINUS_MINUS, None
        LexicalError("Unknown mathematical operator: " + value, position=self.analyser.get_current_index())

    def get_boolean_operator_token(self, operator):
        value = operator
        char = self.analyser.get_next_char()
        if (char == operator):
            if (char == '^'):
                LexicalError("Unknown operator: " + value + char, position=self.analyser.get_current_index())
            value += operator
        elif (char == '='):
            value += '='
        else:
            self.analyser.revert_to_last_char()
        if value == '&':
            return KeyWords.BOOLEAN_AND, None
        if value == '&&':
            return KeyWords.LOGICAL_AND, None
        if value == '|':
            return KeyWords.BOOLEAN_OR, None
        if value == '||':
            return KeyWords.LOGICAL_OR, None
        if value == '^':
            return KeyWords.XOR, None
        if value == '^=':
            return KeyWords.XOR_EQUAL, None
        if value == '&=':
            return KeyWords.AND_EQUAL, None
        if value == '|=':
            return KeyWords.OR_EQUAL, None
        LexicalError("Unknown boolean operator: " + value, position=self.analyser.get_current_index())

    def ignore_whitespace(self):
        char = self.analyser.get_next_char()
        while char in WHITESPACE and char != '':
            char = self.analyser.get_next_char()
        return char