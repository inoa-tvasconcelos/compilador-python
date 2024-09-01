from constants.lexical import ID, KeyWords
from helper.analyser import TextAnalyser
from helper.tester import StackTester
from logic.lexical.token_extractor import TokenExtractor
from storage.token_value_stack import TokenValueStack

def get_token_from_string(string):
    analyser = TextAnalyser(string)
    token_stack = TokenValueStack()
    extractor = TokenExtractor(analyser, token_stack)
    return extractor.next_token_with_value()

def get_tokens_from_string(string):
    analyser = TextAnalyser(string)
    token_stack = TokenValueStack()
    extractor = TokenExtractor(analyser, token_stack)
    return extractor.run_with_values()


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
        "++": (KeyWords.PLUS_PLUS, None),
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

def test_compositions():
    tests = {
        "123 test 'Hello, World!' : ; , [ ] { } ( ) . = == + += - ARRAY 103'23": [
            (KeyWords.INTEGER, "123"), (ID, "test"), (KeyWords.STRING, "Hello, World!"), (KeyWords.COLON, None), (KeyWords.SEMICOLON, None),
            (KeyWords.COMMA, None), (KeyWords.LEFT_SQUARE_BRACKET, None), (KeyWords.RIGHT_SQUARE_BRACKET, None), (KeyWords.LEFT_CURLY_BRACKET, None),
            (KeyWords.RIGHT_CURLY_BRACKET, None), (KeyWords.LEFT_ROUND_BRACKET, None), (KeyWords.RIGHT_ROUND_BRACKET, None), (KeyWords.DOT, None),
            (KeyWords.EQUAL, None), (KeyWords.EQUALITY, None), (KeyWords.PLUS, None), (KeyWords.PLUS_EQUAL, None), (KeyWords.MINUS, None),
            (KeyWords.ARRAY, None), (KeyWords.INTEGER, "103'23")
        ]
    }
    return StackTester(tests, get_tokens_from_string).printed_test("Compositions")

def test_token_extractor():
    return StackTester({
        test_whitespace: True,
        test_numbers: True,
        test_words: True,
        test_strings: True,
        test_isolated_chars: True,
        test_mathmatical_operators: True,
        test_boolean_operators: True,
        test_compositions: True
    }, lambda test: test(), first_info='', reset=True).printed_test("Token Extractor", end="\n")

if __name__ == "__main__":
    test_token_extractor()