from logging import ERROR
import traceback
from constants.lexical import TYPE_KEYWORDS, KeyWords
from constants.syntatical import *
from helper.analyser import TextAnalyser
from helper.informer import Informer
from logic.lexical.token_extractor import TokenExtractor
from storage.token_value_stack import TokenValueStack

class SyntaticalError(Informer):
    def __init__(self, message, index):
        super().__init__(message + f" (index: {index})", severity=ERROR, specification="Syntatical ")

class IterativeSyntaticalAnalyser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_level = 0
        self.variable_buffer = []
        self.syntatical_variable_list = []
        self.details_buffer = {}
        self.assigments = []
    
    def print_token(self):
        print(f'Token: {KeyWords().keyword_to_string(self.token[0])} = {self.token[1]}')
    def get_next_token(self):
        if self.index == len(self.tokens):
            self.token = (KeyWords.EOF, None)
            return self
        self.token = self.tokens[self.index]
        self.print_token()
        self.index += 1
        return self
    
    def unget_token(self):
        self.index = max(0, self.index - 1)
        self.token = self.tokens[self.index]
        self.print_token()
        return self

    def expect(self, expected):
        self.get_next_token()
        if self.token[0] != expected:
            raise SyntaticalError(f"Expected {KeyWords().keyword_to_string(expected)} but got {KeyWords().keyword_to_string(self.token[0])}", self.index)
        if self.token[0] == KeyWords.LEFT_CURLY_BRACKET:
            self.enter_block()
        if self.token[0] == KeyWords.RIGHT_CURLY_BRACKET:
            self.leave_block()
        return self

    def use_id(self, type, details = {}):
        self.variable_buffer.append([self.token[1], self.current_level, type, details])
        return len(self.variable_buffer) - 1
    
    def update_buffer(self, index, new_type = None):
        buffer = self.variable_buffer[index]
        buffer[3] = self.pop_details()
        if new_type != None:
            buffer[2] = new_type
        self.variable_buffer[index] = buffer
        return self
    
    def pop_details(self):
        details = self.details_buffer
        self.details_buffer = {}
        return details
    
    def enter_block(self):
        self.syntatical_variable_list += self.variable_buffer
        self.variable_buffer = []
        self.current_level += 1

    def leave_block(self):
        self.current_level -= 1
        self.syntatical_variable_list += self.variable_buffer
        self.variable_buffer = []
        
    def P(self):
        print("P")
        self.LDE()
        print("Leave P")
        return self
            
    def LDE(self):
        print("LDE")
        self.DE()
        while self.token[0] != KeyWords.EOF:
            self.DE()
            self.get_next_token()
        print("Leave LDE")
        return self

    def DE(self):
        print("DE")
        self.get_next_token()
        if self.token[0] == KeyWords.TYPE:
            self.DT()
        elif self.token[0] == KeyWords.FUNCTION:
            self.DF()
        elif self.token[0] == KeyWords.SEMICOLON:
            self.get_next_token()
        else:
            raise SyntaticalError("DE Expected a type or a function definition", self.index)
        print("Leave DE")
        return self
    
    def T(self):
        print("T")
        self.get_next_token()
        if self.token[0] not in [KeyWords.ID] + TYPE_KEYWORDS:
            raise SyntaticalError("T Expected a type", self.index)
        if self.token[0] == KeyWords.ID:
            self.use_id(type=TYPE_USAGE)
        print("Leave T")
        return self
    
    def DT(self):
        print("DT")
        self.expect(KeyWords.ID)
        buffer_index = self.use_id(TYPE_DECLARATION)
        self.expect(KeyWords.EQUAL)\
            .get_next_token()
        if (self.token[0] == KeyWords.ARRAY):
            self.expect(KeyWords.LEFT_SQUARE_BRACKET)\
                .get_next_token()
            if (self.token[0] != KeyWords.INTEGER):
                raise SyntaticalError("DT Expected integer between brackets", self.index)
            self.details_buffer = {
                "type": DETAIL_TYPE_ARRAY,
                "number": self.token[1]
            }
            self.expect(KeyWords.RIGHT_SQUARE_BRACKET)\
                .expect(KeyWords.OF)\
                .T()
            self.details_buffer['var_type'] = self.token[0]
        elif (self.token[0] == KeyWords.STRUCT):
            self.details_buffer = {
                "type": DETAIL_TYPE_STRUCT,
                "key_value_pairs": []
            }
            self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .DC()
        else:
            self.unget_token()\
                .T()
        self.update_buffer(buffer_index)
        self.expect(KeyWords.SEMICOLON)
        print("Leave DT")
        return self
    def DC(self):
        print("DC")
        self.expect(KeyWords.ID)
        id_name = self.token[1]
        self.use_id(TYPE_DECLARATION)
        self.expect(KeyWords.COLON)\
            .T()
        self.details_buffer['key_value_pairs'].append([id_name, self.token[1]])
        self.get_next_token()
        if self.token[0] == KeyWords.SEMICOLON:
            return self.DC()
        if self.token[0] == KeyWords.RIGHT_CURLY_BRACKET:
            print("Leave DC")
            return self
        raise SyntaticalError("DC Missing a right curly bracket or semicolon", self.index)
    
    def DF(self):
        print("DF")
        self.enter_block()
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("DF Missing function identification", self.index)
        self.use_id(type=FUNCTION_DECLARATION)
        self.expect(KeyWords.LEFT_ROUND_BRACKET)\
            .LP()\
            .expect(KeyWords.COLON)\
            .T()\
            .expect(KeyWords.LEFT_CURLY_BRACKET)\
            .S()\
            .expect(KeyWords.SEMICOLON)
        self.leave_block()
        print("Leave DF")
        return self
    
    def LP(self):
        print("LP")
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("LP Missing variable identification", self.index)
        self.use_id(type=VARIABLE_DECLARATION)
        self.expect(KeyWords.COLON)\
            .T()\
            .get_next_token()
        
        if self.token[0] == KeyWords.COMMA:
            return self.LP()
        if self.token[0] == KeyWords.RIGHT_ROUND_BRACKET:
            print("Leave LP")
            return self
        raise SyntaticalError("LP Missing a comma or right round bracket", self.index)

    def LIT(self):
        print("LIT")
        self.expect(KeyWords.ID)\
            .LITV()
        print("Leave LIT")
        return self
    def LITV(self):
        print("LITV")
        self.get_next_token()
        if self.token[0] == KeyWords.COMMA:
            self.get_next_token()
            if self.token[0] != KeyWords.ID:
                raise SyntaticalError("LITV Missing variable identification", self.index)
            self.use_id(type=VARIABLE_DECLARATION)
            return self.LITV()
        self.unget_token().T()
        print("Leave LITV")
        return self
    def EXP(self):
        print("EXP")
        self.L()\
            .get_next_token()
        if self.token[0] in OPBO:
            return self.EXP()
        self.unget_token()
        print("Leave EXP")
        return self
    def E(self):
        print("E")
        self.EXP().expect(KeyWords.RIGHT_ROUND_BRACKET)
        print("Leave E")
        return self
    
    def ES(self):
        print("ES")
        self.EXP().expect(KeyWords.RIGHT_SQUARE_BRACKET)
        print("Leave ES")
        return self
    def EP(self):
        print("EP")
        self.EXP().expect(KeyWords.SEMICOLON)
        print("Leave EP")
        return self
    def LE(self):
        print("LE")
        self.EXP()\
            .get_next_token()
        if self.token[0] == KeyWords.COMMA:
            return self.LE()
        if self.token[0] == KeyWords.RIGHT_ROUND_BRACKET:
            print("Leave LE")
            return self
        self.expect(KeyWords.RIGHT_ROUND_BRACKET)
        print("Leave LE")
        return self
    def LV(self):
        print("LV")
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError(F"LV Missing variable identification {KeyWords().keyword_to_string(self.token[0])}", self.index)
        buffer_index = self.use_id(type=VARIABLE_USAGE)
        self.get_next_token()
        if self.token[0] == KeyWords.DOT:
            self.details_buffer['type'] = "master"
            self.update_buffer(buffer_index)
            return self.LV()
        if self.token[0] == KeyWords.LEFT_ROUND_BRACKET:
            self.details_buffer['type'] = "function"
            self.update_buffer(buffer_index, new_type=FUNCTION_USAGE)
            self.LE()
            print("Leave LV")
            return self
        if self.token[0] == KeyWords.LEFT_SQUARE_BRACKET:
            self.details_buffer['type'] = "array"
            self.update_buffer(buffer_index, new_type=FUNCTION_USAGE)
            self.ES()
            print("Leave LV")
            return self
        print("Leave LV")
        return self.unget_token()
    
    def OPEQ(self):
        print("OPEQ")
        self.get_next_token()
        if self.token[0] not in OPEQ:
            raise SyntaticalError("OPEQ Equal operation missing", self.index)
        print("Leave OPEQ")
        return self
    
    def EQ(self):
        print("EQ")
        self.LV()\
            .OPEQ()\
            .EP()
        print("Leave EQ")
        return self
    def OPIT(self):
        print("OPIT")
        self.get_next_token()
        if self.token[0] not in OPIT:
            raise SyntaticalError("OPIT Missing in or of keyword", self.index)
        print("Leave OPIT")
        return self
    
    def I(self):
        print("I")
        self.expect(KeyWords.VAR)\
            .get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("I Missing variable identification", self.index)
        self.use_id(type=VARIABLE_DECLARATION)
        self.OPIT()
        
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("I Missing variable for iteration", self.index)
        self.use_id(type=VARIABLE_USAGE)
        self.expect(KeyWords.RIGHT_CURLY_BRACKET)
        print("Leave I")
        return self
    
    def ELIF(self):
        print("ELIF")
        self.get_next_token()
        if self.token[0] == KeyWords.ELSE_IF:
            return self.expect(KeyWords.RIGHT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .ELIF()
        if self.token[0] == KeyWords.ELSE:
            self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)
            print("Leave ELIF")
            return self
        if self.token[0] != KeyWords.SEMICOLON:
            raise SyntaticalError("ELIF Missing else, else_if or semicolon", self.index)
        print("Leave ELIF")
        return self
    
    def RE(self):
        print("RE")
        self.get_next_token()
        if self.token[0] == KeyWords.SEMICOLON:
            print("Leave RE")
            return self
        self.unget_token()
        self.EP()
        print("Leave RE")
        return self
    def S(self):
        print("S")
        self.get_next_token()
        if (self.token[0] == KeyWords.IF):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .ELIF()\
                .S()
        elif (self.token[0] == KeyWords.WHILE):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token[0] == KeyWords.DO):
            return self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.WHILE)\
                .expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token[0] == KeyWords.FOR):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .I()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token[0] == KeyWords.VAR):
            return self.LIT()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token[0] in [KeyWords.BREAK, KeyWords.CONTINUE]):
            return self.expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token[0] == KeyWords.RETURN):
            return self.RE()\
                .S()
        elif (self.token[0] == KeyWords.RIGHT_CURLY_BRACKET):
            print("Leave S")
            return self
        self.unget_token()
        return self.EQ()\
            .S()
    
    def L(self):
        print("L")
        self.R()\
            .get_next_token()
        if self.token[0] in OPDE:
            return self.L()
        print("Leave L")
        return self.unget_token()
        
    
    def R(self):
        print("R")
        self.Y()\
            .get_next_token()
        if self.token[0] in OPAR:
            return self.R()
        print("Leave R")
        return self.unget_token()
    
    def Y(self):
        print("Y")
        self.BO()\
            .get_next_token()
        if self.token[0] in OPMU:
            return self.Y()
        print("Leave Y")
        return self.unget_token()
    
    def BO(self):
        print("BO")
        self.F()\
            .get_next_token()
        if self.token[0] in OPAB:
            return self.BO()
        print("Leave BO")
        return self.unget_token()
    
    def LPT(self):
        print("LPT")
        self.get_next_token()
        if self.token[0] == KeyWords.COMMA:
            self.PT()\
                .LPT()
            print("Leave LPT")
            return self
        if self.token[0] == KeyWords.RIGHT_SQUARE_BRACKET:
            print("Leave LPT")
            return self
        raise SyntaticalError("LPT Missing comma or right square brackets", self.index)
    
    def VAL(self):
        print("VAL")
        self.get_next_token()
        if self.token[0] == KeyWords.ID:
            self.use_id(type=VARIABLE_USAGE)
            print("Leave VAL")
            return self
        self.PT()
        print("Leave PT")
        return self
    def KVP(self):
        print("KVP")
        self.expect(KeyWords.STRING)\
            .expect(KeyWords.COLON)\
            .VAL()\
            .KVPE()
        print("Leave KVP")
        return self
    def KVPE(self):
        print("KVPE")
        self.get_next_token()
        if self.token[0] == KeyWords.RIGHT_CURLY_BRACKET:
            print("Leave KVPE")
            return self
        if self.token[0] == KeyWords.COMMA:
            self.KVP()
            print("Leave KVPE")
            return self
        raise SyntaticalError("KVPE Missing comma or right square brackets", self.index)
        
    def PT(self):
        print("PT")
        self.get_next_token()
        if self.token[0] in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER]:
            print("Leave PT")
            return self
        if self.token[0] == KeyWords.LEFT_SQUARE_BRACKET:
            self.LPT()
            print("Leave PT")
            return self
        if self.token[0] == KeyWords.LEFT_CURLY_BRACKET:
            self.KVP()
            print("Leave PT")
            return self
        raise SyntaticalError("PT Invalid, missing brackets or simple value", self.index)
    
    def LVO(self):
        print("LVO")
        self.get_next_token()
        if self.token[0] == KeyWords.ID:
            self.unget_token()\
                .LV()\
                .get_next_token()
            print("Leave LVO")
            if self.token[0] in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
                return self
            return self.unget_token()
        if self.token[0] in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
            self.LV()
            print("Leave LVO")
            return self
        raise SyntaticalError("LVO Invalid missing keyword or ++ or --", self.index)
    
    def F(self):
        print("F")
        self.get_next_token()
        if self.token[0] == KeyWords.LEFT_ROUND_BRACKET:
            self.E()
            print("Leave F")
            return self
        if self.token[0] in [KeyWords.MINUS, KeyWords.NOT]:
            return self.F()
        if self.token[0] in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER, KeyWords.LEFT_SQUARE_BRACKET, KeyWords.LEFT_CURLY_BRACKET]:
            print("Leave F")
            return self
        self.unget_token()
        self.LVO()
        print("Leave F")
        return self

# Assuming all necessary imports and classes are defined above

if __name__ == "__main__":
    test = """
    type Point = struct {
        x: integer;
        y: integer
    };

    function distance(p1: Point, p2: Point): integer {
        var dx integer;
        var dy integer;
        dx = p1.x - p2.x;
        dy = p1.y - p2.y;
        dist = distance(p1, p2);
        if (dist > 5) {
            p = print("Far away");
        } else {
            p = print("Close");
        };
        return (dx * dx + dy * dy) ** 0.5;
    };
    """

    text_analyser = TextAnalyser(test)
    token_stack = TokenValueStack()
    token_extractor = TokenExtractor(text_analyser, token_stack)

    tokens = token_extractor.run_with_values()

    print("Tokens:")
    for token, value in tokens:
        token_name = KeyWords().keyword_to_string(token)
        print(f"{token_name}: {value}")

    syntactical_analyser = IterativeSyntaticalAnalyser(tokens)

    try:
        syntactical_analyser.P()
        print("Parsing completed successfully.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
