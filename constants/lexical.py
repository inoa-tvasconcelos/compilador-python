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


    def is_keyword(self, token):
        return token in self.__dict__.values()

