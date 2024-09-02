from constants.informer import ERROR
from helper.informer import Informer


WHITESPACE = [' ', '\t', '\n', '\r', '\f', '\v']
ACCEPTED_DIGIT_CHARS = ['.', "'"]
ACCEPTED_WORD_CHARS = ['_', '-']
PROHIBITED_STRING_CHARS = ['\n', '\r', '\f', '\v', '']
ISOLATED_CHARS = [":", ";", ",", "[", "]", "{", "}", "(", ")", "."]
MATHMATICAL_OPERATORS = ['=', '+', '-', '*', '/', '%']
COMPARISON_OPERATORS = ['<', '>', '!']
BOOLEAN_OPERATORS = ['&', '|', "^"]
# Represents words that are not keywords
ID = 0 
class KeyWords:
    INTEGER = 1                         # 10, 1.5 ...
    STRING = 2                          # "Hello, World!" or 'Hello, World!'
    EOF = 3                             # End of file
    COLON = 4                           # :
    SEMICOLON = 5                       # ;
    COMMA = 6                           # ,
    LEFT_SQUARE_BRACKET = 7             # [
    RIGHT_SQUARE_BRACKET = 8            # ]
    LEFT_CURLY_BRACKET = 9              # {
    RIGHT_CURLY_BRACKET = 10            # }
    LEFT_ROUND_BRACKET = 11             # (
    RIGHT_ROUND_BRACKET = 12            # )
    DOT = 13                            # .
    EQUAL = 14                          # =
    EQUALITY = 15                       # ==
    PLUS = 15                           # +
    PLUS_EQUAL = 16                     # +=
    MINUS = 17                          # -
    MINUS_EQUAL = 18                    # -=
    MULTIPLY = 19                       # *
    MULTIPLY_EQUAL = 20                 # *=
    DIVIDE = 21                         # /
    DIVIDE_EQUAL = 22                   # /=
    MODULO = 23                         # %
    MODULO_EQUAL = 24                   # %=
    XOR = 25                            # ^
    XOR_EQUAL = 26                      # ^=
    BOOLEAN_AND = 27                    # &
    LOGICAL_AND = 28                    # &&
    BOOLEAN_OR = 29                     # &
    LOGICAL_OR = 30                     # |
    NOT = 31                            # !
    NOT_EQUAL = 32                      # !=
    LESS_THAN = 33                      # <
    LESS_THAN_EQUAL = 34                # <=
    GREATER_THAN = 35                   # >
    GREATER_THAN_EQUAL = 36             # >=
    UNKNOWN = 37                        # Unknown character
    AND_EQUAL = 38                      # &=
    OR_EQUAL = 39                       # |=
    EXPONENT = 40                       # **
    LEXICAL_ERROR = 41                  # Represents a Error that is not raised
    RETURN = 65
    
    # Reserve types
    ARRAY = 42
    BREAK = 43
    CONTINUE = 44
    ELSE_IF = 47
    FOR = 49
    FUNCTION = 50
    TRUE = 53
    FALSE = 54
    OF = 57
    STRUCT = 59
    TYPE = 60
    VAR = 61
    DO = 62
    PLUS_PLUS = 63
    MINUS_MINUS = 64

    def get(self, name):
        try:
            return getattr(KeyWords, name)
        except:
            return -1
    def keyword_to_string(self, keyword):
        for key, value in KeyWords.__dict__.items():
            if value == keyword:
                return key
        return None

TYPE_KEYWORDS = [
    KeyWords.INTEGER,
    KeyWords.STRING,
    KeyWords.ARRAY,
    KeyWords.STRUCT,    
]