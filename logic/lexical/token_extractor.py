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
        elif (char == "*" and operator == '*'):
            value += '*'
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

def get_token_from_string(string):
    analyser = TextAnalyser(string)
    token_stack = TokenValueStack()
    extractor = TokenExtractor(analyser, token_stack)
    return extractor.next_token_with_value()

def test_whitespace():
    tests = {
        "    \n \r \t \v \f  ": (KeyWords.EOF, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Whitespace")

def test_numbers():
    tests = {
        "123": (KeyWords.INTEGER, "123"),
        "123.456": (KeyWords.INTEGER, "123.456"),
        "123'456''789": (KeyWords.INTEGER, "123'456''789"),
        "3.14159265359": (KeyWords.INTEGER, "3.14159265359"),
    }
    return StackTester(tests, get_token_from_string).printed_test("Numbers")

def test_words():
    tests = {
        "test": (ID, "test"),
        "test123": (ID, "test123"),
        "test_123": (ID, "test_123"),
        "test_123_": (ID, "test_123_"),
        "test_123_!": (ID, "test_123_"),
        "INTEGER": (KeyWords.INTEGER, None),
        "STRING": (KeyWords.STRING, None),
        "EOF": (KeyWords.EOF, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Words")

def test_strings():
    tests = {
        "'Hello, World!'": (KeyWords.STRING, "Hello, World!"),
        '"Hello, World!"': (KeyWords.STRING, "Hello, World!"),
        "'Hello, World!": (KeyWords.LEXICAL_ERROR, None),
        "'Test\\''": (KeyWords.STRING, "Test\\'"),
        "'Test\\'": (KeyWords.LEXICAL_ERROR, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Strings")

def test_isolated_chars():
    tests = {
        ":": (KeyWords.COLON, None),
        ";": (KeyWords.SEMICOLON, None),
        ",": (KeyWords.COMMA, None),
        "[": (KeyWords.LEFT_SQUARE_BRACKET, None),
        "]": (KeyWords.RIGHT_SQUARE_BRACKET, None),
        "{": (KeyWords.LEFT_CURLY_BRACKET, None),
        "}": (KeyWords.RIGHT_CURLY_BRACKET, None),
        "(": (KeyWords.LEFT_ROUND_BRACKET, None),
        ")": (KeyWords.RIGHT_ROUND_BRACKET, None),
        ".": (KeyWords.DOT, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Isolated Chars")

def test_mathmatical_operators():
    tests = {
        "=": (KeyWords.EQUAL, None),
        "==": (KeyWords.EQUALITY, None),
        "+": (KeyWords.PLUS, None),
        "+=": (KeyWords.PLUS_EQUAL, None),
        "-": (KeyWords.MINUS, None),
        "-=": (KeyWords.MINUS_EQUAL, None),
        "*": (KeyWords.MULTIPLY, None),
        "*=": (KeyWords.MULTIPLY_EQUAL, None),
        "/": (KeyWords.DIVIDE, None),
        "/=": (KeyWords.DIVIDE_EQUAL, None),
        "%": (KeyWords.MODULO, None),
        "%=": (KeyWords.MODULO_EQUAL, None),
        "<": (KeyWords.LESS_THAN, None),
        "<=": (KeyWords.LESS_THAN_EQUAL, None),
        ">": (KeyWords.GREATER_THAN, None),
        ">=": (KeyWords.GREATER_THAN_EQUAL, None),
        "!": (KeyWords.NOT, None),
        "!=": (KeyWords.NOT_EQUAL, None),
        "**": (KeyWords.EXPONENT, None),
        "++": (KeyWords.LEXICAL_ERROR, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Mathmatical Operators")

def test_boolean_operators():
    tests = {
        "&": (KeyWords.BOOLEAN_AND, None),
        "&&": (KeyWords.LOGICAL_AND, None),
        "|": (KeyWords.BOOLEAN_OR, None),
        "||": (KeyWords.LOGICAL_OR, None),
        "^": (KeyWords.XOR, None),
        "^^": (KeyWords.LEXICAL_ERROR, None),
        "^=": (KeyWords.XOR_EQUAL, None),
        "&=": (KeyWords.AND_EQUAL, None),
        "|=": (KeyWords.OR_EQUAL, None),
        "!": (KeyWords.NOT, None),
        "!=": (KeyWords.NOT_EQUAL, None),
    }
    return StackTester(tests, get_token_from_string).printed_test("Boolean Operators")

def test_token_extractor():
    return StackTester({
        test_whitespace: True,
        test_numbers: True,
        test_words: True,
        test_strings: True,
        test_isolated_chars: True,
        test_mathmatical_operators: True,
        test_boolean_operators: True,
    }, lambda test: test(), first_info='', reset=True).printed_test("Token Extractor", end="\n")

if __name__ == "__main__":
    test_token_extractor()