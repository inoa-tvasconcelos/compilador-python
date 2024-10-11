from constants.lexical import TYPE_KEYWORDS, KeyWords
from constants.syntatical import *
from helper.informer import Informer

class SyntaticalError(Informer):
    def __init__(self, message, index):
        super().__init__(message + f" (index: {index})", severity=Informer.ERROR, specification="Syntatical ")

class IterativeSyntaticalAnalyser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_level = 0
        self.variable_buffer = []
        self.syntatical_variable_list = []
        self.details_buffer = {}
    
    def get_next_token(self):
        if self.index == len(self.tokens):
            return self
        self.token = self.tokens[self.index]
        self.index += 1
        return self
    
    def unget_token(self):
        self.index = max(0, self.index - 1)
        self.token = self.tokens[self.index]
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
        self.LDE()
            
    def LDE(self):
        self.DE()
        while self.token[0] != KeyWords.EOF:
            self.DE()
        return self

    def DE(self):
        self.get_next_token()
        if self.token[0] == KeyWords.TYPE:
            self.DT()
        elif self.token[0] == KeyWords.FUNCTION:
            self.DF()
        else:
            raise SyntaticalError("Expected a type or a function definition", self.index)
        return self
    
    def T(self):
        self.get_next_token()
        if self.token[0] not in [KeyWords.ID] + TYPE_KEYWORDS:
            raise SyntaticalError("Expected a type", self.index)
        if self.token[0] == KeyWords.ID:
            self.use_id(type=TYPE_USAGE)
        return self
    
    def DT(self):
        self.expect(KeyWords.ID)
        buffer_index = self.use_id(TYPE_DECLARATION)
        self.expect(KeyWords.EQUAL)\
            .get_next_token()
        if (self.token[0] == KeyWords.ARRAY):
            self.expect(KeyWords.LEFT_SQUARE_BRACKET)\
                .get_next_token()
            if (self.token[0] != KeyWords.INTEGER):
                raise SyntaticalError("Expected integer between brackets", self.index)
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
        return self.expect(KeyWords.SEMICOLON)

    def DC(self):
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
            return self
        raise SyntaticalError("Missing a right curly bracket or semicolon", self.index)
    
    def DF(self):
        self.enter_block()
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("Missing function identification", self.index)
        self.use_id(type=FUNCTION_DECLARATION)
        self.expect(KeyWords.LEFT_ROUND_BRACKET)\
            .LP()\
            .expect(KeyWords.COLON)\
            .T()\
            .S()\
            .expect(KeyWords.SEMICOLON)
        self.leave_block()
    
    def LP(self):
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("Missing variable identification", self.index)
        self.use_id(type=VARIABLE_DECLARATION)
        self.expect(KeyWords.COLON)\
            .T()\
            .get_next_token()
        
        if self.token[0] == KeyWords.COMMA:
            return self.LP()
        if self.token[0] == KeyWords.RIGHT_ROUND_BRACKET:
            return self
        raise SyntaticalError("Missing a comma or right round bracket", self.index)

    def LIT(self):
        return self.expect(KeyWords.ID)\
            .LITV()
    
    def LITV(self):
        self.get_next_token()
        if self.token[0] == KeyWords.COMMA:
            self.get_next_token()
            if self.token[0] != KeyWords.ID:
                raise SyntaticalError("Missing variable identification", self.index)
            self.use_id(type=VARIABLE_DECLARATION)
            return self.LITV()
        return self.unget_token().T()

    def EXP(self):
        self.L()\
            .get_next_token()
        if self.token[0] in OPBO:
            return self.EXP()
        return self.unget_token()
    
    def E(self):
        return self.EXP().expect(KeyWords.RIGHT_ROUND_BRACKET)
    
    def ES(self):
        return self.EXP().expect(KeyWords.RIGHT_SQUARE_BRACKET)
    
    def EP(self):
        return self.EXP().expect(KeyWords.SEMICOLON)
    
    def LE(self):
        self.EXP()\
            .get_next_token()
        if self.token[0] == KeyWords.COMMA:
            return self.LE()
        return self.expect(KeyWords.RIGHT_ROUND_BRACKET)
    
    def LV(self):
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("Missing variable identification", self.index)
        buffer_index = self.use_id(type=VARIABLE_USAGE)
        self.get_next_token()
        if self.token[0] == KeyWords.DOT:
            self.details_buffer['type'] = "master"
            self.update_buffer(buffer_index)
            return self.LV()
        if self.token[0] == KeyWords.LEFT_ROUND_BRACKET:
            self.details_buffer['type'] = "function"
            self.update_buffer(buffer_index, new_type=FUNCTION_USAGE)
            return self.LE()
        if self.token[0] == KeyWords.LEFT_SQUARE_BRACKET:
            self.details_buffer['type'] = "array"
            self.update_buffer(buffer_index, new_type=FUNCTION_USAGE)
            return self.ES()
        return self.unget_token()
    
    def OPEQ(self):
        self.get_next_token()
        if self.token[0] not in OPEQ:
            raise SyntaticalError("Equal operation missing", self.index)
        return self
    
    def EQ(self):
        return self.LV()\
            .OPEQ()\
            .EP()
    
    def OPIT(self):
        self.get_next_token()
        if self.token[0] not in OPIT:
            raise SyntaticalError("Missing in or of keyword", self.index)
        return self
    
    def I(self):
        self.expect(KeyWords.VAR)\
            .get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("Missing variable identification", self.index)
        self.use_id(type=VARIABLE_DECLARATION)
        self.OPIT()
        
        self.get_next_token()
        if self.token[0] != KeyWords.ID:
            raise SyntaticalError("Missing variable for iteration", self.index)
        self.use_id(type=VARIABLE_USAGE)
        return self.expect(KeyWords.RIGHT_CURLY_BRACKET)
    
    def ELIF(self):
        self.get_next_token()
        if self.token[0] == KeyWords.ELSE_IF:
            return self.expect(KeyWords.RIGHT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .ELIF()
        if self.token[0] == KeyWords.ELSE:
            return self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)
        if self.token[0] != KeyWords.SEMICOLON:
            raise SyntaticalError("Missing else, else_if or semicolon", self.index)
        return self
    
    def RE(self):
        self.get_next_token()
        if self.token[0] == KeyWords.SEMICOLON:
            return self
        return self.EP()
    
    def S(self):
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
            return self
        return self.EQ()\
            .S()
    
    def L(self):
        self.R()\
            .get_next_token()
        if self.token[0] in OPDE:
            return self.L()
        return self.unget_token()
        
    
    def R(self):
        self.Y()\
            .get_next_token()
        if self.token[0] in OPAR:
            return self.R()
        return self.unget_token()
    
    def Y(self):
        self.BO()\
            .get_next_token()
        if self.token[0] in OPMU:
            return self.Y()
        return self.unget_token()
    
    def BO(self):
        self.F()\
            .get_next_token()
        if self.token[0] in OPAB:
            return self.BO()
        return self.unget_token()
    
    def LPT(self):
        self.get_next_token()
        if self.token[0] == KeyWords.COMMA:
            return self.PT()\
                .LPT()
        if self.token[0] == KeyWords.RIGHT_SQUARE_BRACKET:
            return self
        raise SyntaticalError("Missing comma or right square brackets", self.index)
    
    def VAL(self):
        self.get_next_token()
        if self.token[0] == KeyWords.ID:
            self.use_id(type=VARIABLE_USAGE)
            return self
        return self.PT()
    
    def KVP(self):
        return self.expect(KeyWords.STRING)\
            .expect(KeyWords.COLON)\
            .VAL()\
            .KVPE()
    
    def KVPE(self):
        self.get_next_token()
        if self.token[0] == KeyWords.RIGHT_CURLY_BRACKET:
            return self
        if self.token[0] == KeyWords.COMMA:
            return self.KVP()
        raise SyntaticalError("Missing comma or right square brackets", self.index)
        
    def PT(self):
        self.get_next_token()
        if self.token[0] in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER]:
            return self
        if self.token[0] == KeyWords.LEFT_SQUARE_BRACKET:
            return self.LPT()
        if self.token[0] == KeyWords.LEFT_CURLY_BRACKET:
            return self.KVP()
        raise SyntaticalError("Invalid, missing brackets or simple value", self.index)
    
    def LVO(self):
        self.get_next_token()
        if self.token[0] == KeyWords.ID:
            self.unget_token()\
                .LV()\
                .get_next_token()
            if self.token[0] in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
                return self
            return self.unget_token()
        if self.token[0] in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
            return self.LV()
        raise SyntaticalError("Invalid missing keyword or ++ or --", self.index)
    
    def F(self):
        self.get_next_token()
        if self.token[0] == KeyWords.LEFT_ROUND_BRACKET:
            return self.E()
        if self.token[0] in [KeyWords.MINUS, KeyWords.NOT]:
            return self.F()
        if self.token[0] in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER, KeyWords.LEFT_SQUARE_BRACKET, KeyWords.LEFT_CURLY_BRACKET]:
            return self
        return self.LVO()
    