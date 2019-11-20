import re
from token import Token
from dictionary import keywords, operators, brackets

class Lexer:
    def __init__(self, source_code):
        self.src = source_code
        self.len = len(source_code)
        self.__char = self.src[0]
        self.__pos = 0
        self.__line_pos = 0
        self.__line = 0
        self.__prev_token = None
        self.__token = None

    def peekChar(self):
        if self.__pos < self.len:
            if self.src[self.__pos] == '\\':
                self.__char = self.src[self.__pos:self.__pos + 2]
            else:
                self.__char = self.src[self.__pos]
        else:
            self.__char = None

        return self.__char

    def popChar(self):
        if self.src[self.__pos] == '\\':
            self.__pos += 1
        self.__pos += 1
        self.__line_pos += 1
        return self.peekChar()

    def peekToken(self):
        return self.__token

    def popToken(self, token):
        self.__prev_token = self.__token
        self.__token = token

    def linePos(self):
        return self.__pos - self.__line_pos

    def isStringConstant(self):
        """
        String constants can start either with `"` (one double quote character)
        or `L"` (an `L` immediatly followed by a double quote character).
        """

        if self.peekChar() == 'L':
            return True if self.src[self.__pos + 1] == '"' else False
        elif self.peekChar() == '"':
            return True
        else:
            return False

    def stringConstant(self):
        tkn_value = ""
        if self.peekChar() == 'L':
            tkn_value += self.peekChar()
            self.popChar()
        tkn_value += self.peekChar()
        self.popChar()
        while self.peekChar() not in ["\"", "\n", None]:
            tkn_value += self.peekChar()
            self.popChar()
        tkn_value += self.peekChar()
        if self.peekChar() in ["\n", None]:
            self.popToken(Token("ERROR", self.linePos()))
            """
            The string has no closing quote character, it is not properly
            formatted, we'll stop parsing from here
            """
        else:
            self.popToken(Token("STRING_CONSTANT", self.linePos(), tkn_value))
        self.popChar()
        pass

    def multComment(self):
        self.popChar(), self.popChar()
        tkn_value = "/*"
        while self.peekChar():
            tkn_value += self.peekChar()
            if self.peekChar() == '\n':
                self.__line += 1
                self.__line_pos = 0
            self.popChar()
            if self.src[self.__pos:].startswith("*/"):
                tkn_value += "*/"
                self.popChar(), self.popChar()
                break
        if tkn_value.endswith("*/"):
            self.popToken(Token("MULT_COMMENT", self.linePos(), tkn_value))
        else:
            self.popToken(Token("ERROR", self.linePos()))

    def comment(self):
        tkn_value = "//"
        self.popChar(), self.popChar()
        while self.peekChar():
            tkn_value += self.peekChar()
            self.popChar()
            if self.peekChar() == '\n':
                break
        self.popToken(Token("COMMENT", self.linePos(), tkn_value))

    def charConstant(self):
        tkn_value = '\''
        while self.peekChar():
            tkn_value += self.peekChar()
            self.popChar()
            if self.peekChar() =='\'':
                self.popChar()
                tkn_value += '\''
                break

    def identifier(self):
        tkn_value = re.findall(
                            "^\w\w*",
                            self.src[self.__pos:])[0]
        self.__pos += len(tkn_value)
        if tkn_value in keywords:
            self.popToken(Token(
                            keywords[tkn_value],
                            self.linePos()))
        else:
            self.popToken(Token(
                            "IDENTIFIER",
                            self.linePos(),
                            tkn_value))


    def getNextToken(self):
        """
        This method creates and return 1 token at a time by reading the source
        code character after character and matching a character or set of
        characters to a pattern related to a token type.
        If no pattern matches the current character or set of character, an
        "ERROR" token will be returned.
        After reading the whole file, an "EOF" token is returned
        """
        while self.peekChar() != None:

            if self.isStringConstant():
                self.stringConstant()

            elif self.peekChar().isalpha() or self.peekChar() == '_':
                self.identifier()

#            elif self.peekChar() == '\'':
#                continue
#               #CHARACTER_CONSTANT

#            elif self.peekChar().isdigit():
#                continue
#                #NUMERIC CONSTANT token

            elif self.src[self.__pos:].startswith("/*"):
                self.multComment()

            elif self.src[self.__pos:].startswith("//"):
                self.comment()

#            #elif self.peekChar() == IS A SYMBOL
#                #continue

            elif self.peekChar() == ' ':
                self.popToken(Token("SPACE", self.linePos()))
                self.popChar()

            elif self.peekChar() == '\t':
                self.popToken(Token("TAB", self.linePos()))
                self.popChar()

            elif self.peekChar() == '\n':
                self.popToken(Token("NEWLINE", self.linePos()))
                self.__line_pos = 0
                self.__line += 1
                self.popChar()

            elif self.peekChar() in brackets:
                self.popToken(Token(brackets[self.peekChar()], self.linePos()))
                self.popChar()

            else:
                self.popToken(Token("ERROR", self.linePos()))
                self.popChar()

            return self.peekToken()

        self.popToken(Token("EOF",  self.linePos()))
        return self.peekToken()

def tokenization_test(source):
    with open(source) as file:
        text = file.read()
        import lexer
        source = lexer.Lexer(text)
        while source.getNextToken().type != "EOF":
            if source.peekToken().type == "NEWLINE":
                print(source.peekToken())
            else:
                print(source.peekToken(), end="")