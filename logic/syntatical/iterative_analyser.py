# P -> LDE
# LDE -> DE { DE }
# DE -> DF | DT
# T -> INTEGER | STRING | ... | ID
# DT -> type ID = T | array [ INTEGER ] of T | struct { DC }
# DC -> 

from constants.lexical import TYPE_KEYWORDS, KeyWords
from helper.informer import Informer

class SyntaticalError(Informer):
    def __init__(self, message):
        super().__init__(message, severity=Informer.ERROR, specification="Syntatical ")

class IterativeSyntaticalAnalyser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
    
    def get_next_token(self):
        if self.index == len(self.tokens):
            return KeyWords.EOF
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def unget_token(self):
        self.index = max(0, self.index - 1)

    def expect(self, expected):
        token = self.get_next_token()
        if token != expected:
            raise SyntaticalError(f"Expected {KeyWords().keyword_to_string(expected)} but got {KeyWords().keyword_to_string(token)}")
        return self

    def P(self):
        self.LDE()
        return self
            
    def LDE(self):
        last_token = self.DE()
        while last_token != KeyWords.EOF:
            last_token = self.DE()
        return self

    def DE(self):
        token = self.get_next_token()
        if token == KeyWords.TYPE:
            self.DT()
        elif token == KeyWords.FUNCTION:
            self.DF()
        else:
            raise SyntaticalError("Expected a type or a function definition")
        return self
    
    def DT(self):
        self.expect(KeyWords.ID).expect(KeyWords.EQUAL)
        token = self.get_next_token()
        if (token == KeyWords.ARRAY):
            self.expect(KeyWords.LEFT_SQUARE_BRACKET).expect(KeyWords.INTEGER)\
                .expect(KeyWords.RIGHT_SQUARE_BRACKET).expect(KeyWords.OF).T()
        elif (token == KeyWords.STRUCT):
            self.expect(KeyWords.LEFT_CURLY_BRACKET).DC().expect(KeyWords.RIGHT_CURLY_BRACKET)
        else:
            self.T()
        return self
    
    def DF(self):
        self.expect(KeyWords.ID).expect(KeyWords.LEFT_ROUND_BRACKET)\
            .LP().expect(KeyWords.RIGHT_ROUND_BRACKET).expect(KeyWords.COLON).T().B()
        return self
    
    def LP(self):
        # Allow empty parameter list
        self.expect(KeyWords.ID).expect(KeyWords.COLON).T()
        token = self.get_next_token()
        while token != KeyWords.RIGHT_ROUND_BRACKET:
            if token != KeyWords.ID:
                raise SyntaticalError("Expected an identifier")
            self.expect(KeyWords.COLON).T()
            token = self.get_next_token()
        self.unget_token()
        return self

    def T(self):
        token = self.get_next_token()
        if token not in [KeyWords.ID] + TYPE_KEYWORDS:
            raise SyntaticalError("Expected a type")
        return self

    def DC(self):
        self.LI_T()
        token = self.get_next_token()
        while token == KeyWords.COMMA:
            self.DC()
            token = self.get_next_token()
        self.unget_token()
        return self
    
    def LI_T(self):
        self.LI().expect(KeyWords.COLON).T()        
        return self
    
    def LI(self):
        self.expect(KeyWords.ID)
        next_token = self.get_next_token()
        while next_token == KeyWords.COMMA:
            self.expect(KeyWords.ID)
            next_token = self.get_next_token()
        self.unget_token()
        return self

    def B(self):
        self.expect(KeyWords.LEFT_CURLY_BRACKET).LDV()\
            .LS().expect(KeyWords.RIGHT_CURLY_BRACKET)
        return self

    def LDV(self):
        next_token = self.get_next_token()
        if next_token == KeyWords.VAR:
            self.DV()
        return self
    
    def DV(self):
        self.LI_T().expect(KeyWords.SEMICOLON)
        return self
    
    def LS(self):
        self.S()
        next_token = self.get_next_token()
        while next_token != KeyWords.RIGHT_CURLY_BRACKET:
            self.S()
            next_token = self.get_next_token()
        self.unget_token()
        return self
    
    def S(self):
        next_token = self.get_next_token()
        if (next_token == KeyWords.IF):
            self.expect(KeyWords.LEFT_ROUND_BRACKET).E()\
                .expect(KeyWords.RIGHT_ROUND_BRACKET).S()
            next_token = self.get_next_token()
            if next_token == KeyWords.ELSE:
                self.S()
            else:
                self.unget_token()
        elif (next_token == KeyWords.WHILE):
            self.expect(KeyWords.LEFT_ROUND_BRACKET).E()\
                .expect(KeyWords.RIGHT_ROUND_BRACKET).S()
        elif (next_token == KeyWords.DO):
            self.S().expect(KeyWords.WHILE).expect(KeyWords.LEFT_ROUND_BRACKET).E()\
                .expect(KeyWords.RIGHT_ROUND_BRACKET).expect(KeyWords.SEMICOLON)
        elif (next_token == KeyWords.BREAK):
            self.expect(KeyWords.SEMICOLON)
        elif (next_token == KeyWords.CONTINUE):
            self.expect(KeyWords.SEMICOLON)
        elif (next_token == KeyWords.LEFT_CURLY_BRACKET):
            self.B()
        self.LV()
        return self
    
    def E(self):
        self.L()
        next_token = self.get_next_token()
        if next_token in [KeyWords.LOGICAL_AND, KeyWords.LOGICAL_OR]:
            self.E()
        return self

    def L(self):
        self.R()
        next_token = self.get_next_token()
        while next_token in [KeyWords.EQUALITY, KeyWords.NOT_EQUAL, KeyWords.LESS_THAN, KeyWords.LESS_THAN_EQUAL, KeyWords.GREATER_THAN, KeyWords.GREATER_THAN_EQUAL]:
            self.R()
            next_token = self.get_next_token()
        self.unget_token()
    
    def R(self):
        self.Y()
        next_token = self.get_next_token()
        while next_token in [KeyWords.PLUS, KeyWords.MINUS]:
            self.Y()
            next_token = self.get_next_token()
        self.unget_token()
        return self
    
    def Y(self):
        self.F()
        next_token = self.get_next_token()
        while next_token in [KeyWords.MULTIPLY, KeyWords.DIVIDE, KeyWords.MODULO]:
            self.F()
            next_token = self.get_next_token()
        self.unget_token()
        return self
    
    def F(self):
        next_token = self.get_next_token()
        if next_token in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER]:
            return self
        elif next_token in [KeyWords.NOT, KeyWords.MINUS]:
            self.F()
        elif next_token == KeyWords.LEFT_ROUND_BRACKET:
            self.E().expect(KeyWords.RIGHT_ROUND_BRACKET)
        elif next_token == KeyWords.ID:
            next_token = self.get_next_token()
            if next_token == KeyWords.LEFT_ROUND_BRACKET:
                self.LE().expect(KeyWords.RIGHT_ROUND_BRACKET)
            else:
                self.unget_token()
                self.LV()
                next_token = self.get_next_token()
                if next_token not in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
                    SyntaticalError("Invalid mathmatical expression")
        elif next_token in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
            self.LV()
        else:
            SyntaticalError("Invalid mathmatical expression")
        return self
    
    def LE(self):
        self.E()
        next_token = self.get_next_token()
        while next_token == KeyWords.COMMA:
            self.E()
            next_token = self.get_next_token()
        self.unget_token()
        return self
    
    def LV(self):
        self.expect(KeyWords.ID)
        next_token = self.get_next_token()
        if next_token == KeyWords.LEFT_SQUARE_BRACKET:
            self.E().expect(KeyWords.RIGHT_SQUARE_BRACKET)
            return self
        while next_token == KeyWords.DOT:
            self.expect(KeyWords.ID)
            next_token = self.get_next_token()
        self.unget_token()
        return self
