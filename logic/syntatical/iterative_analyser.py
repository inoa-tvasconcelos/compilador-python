# New block on start of function F( a, b )
#                                 ^ Bota um MF, cria um NEW BLOCK
# não cria novo bloco em {, cria no caso acima ou no caso de aparecer um B em um caso especifico
# ou seja, bota o MF entre os caras qdo quer inicia o bloco.
# Faz também IDU e IDD para diferenciar definição e utilização
# a cada bloco que cria 
from constants.lexical import TYPE_KEYWORDS, KeyWords
from constants.syntatical import *
from helper.informer import Informer


class IterativeSyntaticalAnalyser:
    class SyntaticalError(Informer):
        def __init__(self, message):
            super().__init__(message+f" (index: {self.index})", severity=Informer.ERROR, specification="Syntatical ")

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
    
    def get_next_token(self):
        if self.index == len(self.tokens):
            return KeyWords.EOF
        self.token = self.tokens[self.index]
        self.index += 1
        return self
    
    def unget_token(self):
        self.index = max(0, self.index - 1)
        self.token = self.tokens[self.index]
        return self

    def expect(self, expected):
        self.get_next_token()
        if self.token != expected:
            raise self.SyntaticalError(f"Expected {KeyWords().keyword_to_string(expected)} but got {KeyWords().keyword_to_string(self.token)}")
        return self

    def P(self):
        self.LDE()
            
    def LDE(self):
        self.DE()
        while self.token != KeyWords.EOF:
            self.DE()
        return self

    def DE(self):
        self.get_next_token()
        if self.token == KeyWords.TYPE:
            self.DT()
        elif self.token == KeyWords.FUNCTION:
            self.DF()
        else:
            raise self.SyntaticalError("Expected a type or a function definition")
        return self
    
    def T(self):
        self.get_next_token()
        if self.token not in [KeyWords.ID] + TYPE_KEYWORDS:
            raise self.SyntaticalError("Expected a type")
        return self
    
    def DT(self):
        self.expect(KeyWords.ID).expect(KeyWords.EQUAL).get_next_token()
        if (self.token == KeyWords.ARRAY):
            self.expect(KeyWords.LEFT_SQUARE_BRACKET)\
                .expect(KeyWords.INTEGER)\
                .expect(KeyWords.RIGHT_SQUARE_BRACKET)\
                .expect(KeyWords.OF)\
                .T()
        elif (self.token == KeyWords.STRUCT):
            self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .DC()
        else:
            self.unget_token()\
                .T()
        return self.expect(KeyWords.SEMICOLON)

    def DC(self):
        self.LI()\
            .T()
        token = self.get_next_token()
        if token == KeyWords.SEMICOLON:
            return self.DC()
        if token == KeyWords.RIGHT_CURLY_BRACKET:
            return self
        raise self.SyntaticalError("Missing a right curly bracket or semicolon")
    
    def DF(self):
        return self.expect(KeyWords.ID)\
            .expect(KeyWords.LEFT_ROUND_BRACKET)\
            .LP()\
            .expect(KeyWords.COLON)\
            .T()\
            .B()\
            .expect(KeyWords.SEMICOLON)
    
    def LP(self):
        self.expect(KeyWords.ID)\
            .expect(KeyWords.COLON)\
            .T()\
            .get_next_token()
        
        if self.token == KeyWords.COMMA:
            return self.LP()
        if self.token == KeyWords.RIGHT_ROUND_BRACKET:
            return self
        raise self.SyntaticalError("Missing a comma or right round bracket")
    
    def LI(self):
        return self.expect(KeyWords.ID)\
            .LIV()

    def LIV(self):
        self.get_next_token()
        if self.token == KeyWords.COMMA:
            return self.expect(KeyWords.ID)\
                .LIV()
        if self.token == KeyWords.COLON:
            return self
        raise self.SyntaticalError("Missing comma or colon")

    def LIT(self):
        return self.expect(KeyWords.ID)\
            .LITV()
    
    def LITV(self):
        self.get_next_token()
        if self.token == KeyWords.COMMA:
            return self.expect(KeyWords.ID)\
                .LITV()
        return self.unget_token().T()

    def EXP(self):
        self.L()\
            .get_next_token()
        if self.token in OPBO:
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
        if self.token == KeyWords.COMMA:
            return self.LE()
        return self.expect(KeyWords.RIGHT_ROUND_BRACKET)
    
    def LV(self):
        self.expect(KeyWords.ID)\
            .get_next_token()
        if self.token == KeyWords.DOT:
            return self.LV()
        if self.token == KeyWords.LEFT_ROUND_BRACKET:
            return self.LE()
        if self.token == KeyWords.LEFT_SQUARE_BRACKET:
            return self.ES()
        return self.unget_token()
    
    def OPEQ(self):
        self.get_next_token()
        if self.token not in OPEQ:
            raise self.SyntaticalError("Equal operation missing")
        return self
    
    def EQ(self):
        return self.LV()\
            .OPEQ()\
            .EP()
    
    def OPIT(self):
        self.get_next_token()
        if self.token not in OPIT:
            raise self.SyntaticalError("Missing in or of keyword")
        return self
    
    def I(self):
        return self.expect(KeyWords.VAR)\
            .expect(KeyWords.ID)\
            .OPIT()\
            .expect(KeyWords.ID)\
            .expect(KeyWords.RIGHT_CURLY_BRACKET)
    
    def ELIF(self):
        self.get_next_token()
        if self.token == KeyWords.ELSE_IF:
            return self.expect(KeyWords.RIGHT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .ELIF()
        if self.token == KeyWords.ELSE:
            return self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)
        if self.token == KeyWords.SEMICOLON:
            return self
        raise self.SyntaticalError("Missing else, else_if or semicolon")
    
    def RE(self):
        self.get_next_token()
        if self.token == KeyWords.SEMICOLON:
            return self
        return self.EP()
    
    def S(self):
        self.get_next_token()
        if (self.token == KeyWords.IF):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .ELIF()\
                .S()
        elif (self.token == KeyWords.WHILE):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token == KeyWords.DO):
            return self.expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.WHILE)\
                .expect(KeyWords.LEFT_ROUND_BRACKET)\
                .E()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token == KeyWords.FOR):
            return self.expect(KeyWords.LEFT_ROUND_BRACKET)\
                .I()\
                .expect(KeyWords.LEFT_CURLY_BRACKET)\
                .S()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token == KeyWords.VAR):
            return self.LIT()\
                .expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token in [KeyWords.BREAK, KeyWords.CONTINUE]):
            return self.expect(KeyWords.SEMICOLON)\
                .S()
        elif (self.token == KeyWords.RETURN):
            return self.RE()\
                .S()
        elif (self.token == KeyWords.RIGHT_CURLY_BRACKET):
            return self
        return self.EQ()\
            .S()
    
    def L(self):
        self.R()\
            .get_next_token()
        if self.token in OPDE:
            return self.L()
        return self.unget_token()
        
    
    def R(self):
        self.Y()\
            .get_next_token()
        if self.token in OPAR:
            return self.R()
        return self.unget_token()
    
    def Y(self):
        self.BO()\
            .get_next_token()
        if self.token in OPMU:
            return self.Y()
        return self.unget_token()
    
    def BO(self):
        self.F()\
            .get_next_token()
        if self.token in OPAB:
            return self.BO()
        return self.unget_token()
    
    def LPT(self):
        self.get_next_token()
        if self.token == KeyWords.COMMA:
            return self.PT()\
                .LPT()
        if self.token == KeyWords.RIGHT_SQUARE_BRACKET:
            return self
        raise self.SyntaticalError("Missing comma or right square brackets")
    
    def VAL(self):
        self.get_next_token()
        if self.token == KeyWords.ID:
            return self
        return self.PT()
    
    def KVP(self):
        return self.expect(KeyWords.STRING)\
            .expect(KeyWords.COLON)\
            .VAL()\
            .KVPE()
    
    def KVPE(self):
        self.get_next_token()
        if self.token == KeyWords.RIGHT_CURLY_BRACKET:
            return self
        if self.token == KeyWords.COMMA:
            return self.KVP()
        raise self.SyntaticalError("Missing comma or right square brackets")
        
    def PT(self):
        self.get_next_token()
        if self.token in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER]:
            return self
        if self.token == KeyWords.LEFT_SQUARE_BRACKET:
            return self.LPT()
        if self.token == KeyWords.LEFT_CURLY_BRACKET:
            return self.KVP()
        raise self.SyntaticalError("Invalid, missing brackets or simple value1")
    
    def LVO(self):
        self.get_next_token()
        if self.token == KeyWords.ID:
            self.unget_token()\
                .LV()\
                .get_next_token()
            if self.token in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
                return self
            return self.unget_token()
        if self.token in [KeyWords.PLUS_PLUS, KeyWords.MINUS_MINUS]:
            return self.LV()
        raise self.SyntaticalError("Invalid missing keyword or ++ or --")
    
    def F(self):
        self.get_next_token()
        if self.token == KeyWords.LEFT_ROUND_BRACKET:
            return self.E()
        if self.token in [KeyWords.MINUS, KeyWords.NOT]:
            return self.F()
        if self.token in [KeyWords.TRUE, KeyWords.FALSE, KeyWords.STRING, KeyWords.INTEGER, KeyWords.LEFT_SQUARE_BRACKET, KeyWords.LEFT_CURLY_BRACKET]:
            return self
        return self.LVO()
    