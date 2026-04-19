
OPS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OPS = {"-", "~"}
KEYWORD_CONSTANTS = {"true", "false", "null", "this"}

class CompilationEngine:
    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer
        self.out = output
        self.indent = 0


    def escape(self, value):
        if value == "<":
            return "&lt;"
        if value == ">":
            return "&gt;"
        if value == "&":
            return "&amp;"
        return value
    

    def writeCurrentToken(self):
        token_type = self.tokenizer.tokenType()
        if token_type == "KEYWORD":
            tag = "keyword"
            value = self.tokenizer.keyWord()
        elif token_type == "SYMBOL":
            tag = "symbol"
            value = self.tokenizer.symbol()
        elif token_type == "IDENTIFIER":
            tag = "identifier"
            value = self.tokenizer.identifier()
        elif token_type == "INT_CONST":
            tag = "integerConstant"
            value = str(self.tokenizer.intVal())
        elif token_type == "STRING_CONST":
            tag = "stringConstant"
            value = self.tokenizer.stringVal()
        else:
            raise ValueError(f"Unknown token type: {token_type}")
        
        self.write(f"<{tag}> {self.escape(value)} </{tag}>")


    def openTag(self, tag):
        self.write(f"<{tag}>")
        self.indent += 1


    def closeTag(self, tag):
        self.indent -= 1
        self.write(f"</{tag}>")
    

    def eat(self, expected=None):
        if not self.tokenizer.hasMoreTokens():
            raise ValueError("Unexpected end of input")

        self.tokenizer.advance()

        if expected is not None and self.tokenizer.current != expected:
            raise ValueError(f"Expected '{expected}', got '{self.tokenizer.current}'")

        self.writeCurrentToken()
    

    def write(self, text):
        self.out.write("  " * self.indent + text + "\n")


    def compileClass(self) -> None:
        self.openTag("class")

        self.eat("class")
        self.eat()
        self.eat("{")

        while self.tokenizer.peek() in ("static", "field"):
            self.compileClassVarDec()

        while self.tokenizer.peek() in ("constructor", "function", "method"):
            self.compileSubroutine()

        self.eat("}")
        self.closeTag("class")


    def compileClassVarDec(self) -> None:
        self.openTag("classVarDec")

        self.eat()
        self.eat()
        self.eat()

        while self.tokenizer.peek() == ",":
            self.eat(",")
            self.eat()

        self.eat(";")
        self.closeTag("classVarDec")


    def compileSubroutine(self) -> None:
        self.openTag("subroutineDec")

        self.eat()
        self.eat()
        self.eat()
        self.eat("(")
        self.compileParameterList()
        self.eat(")")

        self.openTag("subroutineBody")
        self.eat("{")

        while self.tokenizer.peek() == "var":
            self.compileVarDec()

        self.compileStatements()

        self.eat("}")
        self.closeTag("subroutineBody")
        self.closeTag("subroutineDec")


    def compileParameterList(self) -> None:
        self.openTag("parameterList")

        if self.tokenizer.peek() != ")":
            self.eat()
            self.eat()

            while self.tokenizer.peek() == ",":
                self.eat(",")
                self.eat()
                self.eat()

        self.closeTag("parameterList")


    def compileVarDec(self) -> None:
        self.openTag("varDec")

        self.eat("var")
        self.eat()
        self.eat()

        while self.tokenizer.peek() == ",":
            self.eat(",")
            self.eat()

        self.eat(";")
        self.closeTag("varDec")


    def compileStatements(self) -> None:
        self.openTag("statements")

        while self.tokenizer.peek() in ("let", "if", "while", "do", "return"):
            nxt = self.tokenizer.peek()
            if nxt == "let":
                self.compileLet()
            elif nxt == "if":
                self.compileIf()
            elif nxt == "while":
                self.compileWhile()
            elif nxt == "do":
                self.compileDo()
            elif nxt == "return":
                self.compileReturn()

        self.closeTag("statements")


    def compileDo(self) -> None:
        self.openTag("doStatement")

        self.eat("do")
        self.eat()

        if self.tokenizer.peek() == ".":
            self.eat(".")
            self.eat()

        self.eat("(")
        self.compileExpressionList()
        self.eat(")")
        self.eat(";")

        self.closeTag("doStatement")


    def compileLet(self) -> None:
        self.openTag("letStatement")

        self.eat("let")
        self.eat()

        if self.tokenizer.peek() == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")

        self.eat("=")
        self.compileExpression()
        self.eat(";")

        self.closeTag("letStatement")


    def compileWhile(self) -> None:
        self.openTag("whileStatement")

        self.eat("while")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")

        self.closeTag("whileStatement")


    def compileReturn(self) -> None:
        self.openTag("returnStatement")

        self.eat("return")

        if self.tokenizer.peek() != ";":
            self.compileExpression()

        self.eat(";")
        self.closeTag("returnStatement")


    def compileIf(self) -> None:
        self.openTag("ifStatement")

        self.eat("if")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")

        if self.tokenizer.peek() == "else":
            self.eat("else")
            self.eat("{")
            self.compileStatements()
            self.eat("}")

        self.closeTag("ifStatement")


    def compileExpression(self) -> None:
        self.openTag("expression")

        self.compileTerm()

        while self.tokenizer.peek() in OPS:
            self.eat()
            self.compileTerm()

        self.closeTag("expression")


    def compileTerm(self) -> None:
        self.openTag("term")

        next_token = self.tokenizer.peek()

        if next_token is None:
            raise ValueError("Unexpected end of input in term")

        if next_token.isdigit():
            self.eat()
        elif next_token.startswith('"'):
            self.eat()
        elif next_token in KEYWORD_CONSTANTS:
            self.eat()

        elif next_token == "(":
            self.eat("(")
            self.compileExpression()
            self.eat(")")

        elif next_token in UNARY_OPS:
            self.eat()
            self.compileTerm()

        else:
            self.eat()

            if self.tokenizer.peek() == "[":
                self.eat("[")
                self.compileExpression()
                self.eat("]")
            elif self.tokenizer.peek() == "(":
                self.eat("(")
                self.compileExpressionList()
                self.eat(")")
            elif self.tokenizer.peek() == ".":
                self.eat(".")
                self.eat()
                self.eat("(")
                self.compileExpressionList()
                self.eat(")")

        self.closeTag("term")


    def compileExpressionList(self) -> None:
        self.openTag("expressionList")

        if self.tokenizer.peek() != ")":
            self.compileExpression()
            while self.tokenizer.peek() == ",":
                self.eat(",")
                self.compileExpression()

        self.closeTag("expressionList")
    

    def compileTokens(self) -> None:
        self.write("<tokens>")
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            token_type = self.tokenizer.tokenType()

            if token_type == "KEYWORD":
                tag = "keyword"
                value = self.tokenizer.keyWord()
            elif token_type == "SYMBOL":
                tag = "symbol"
                value = self.tokenizer.symbol()
            elif token_type == "IDENTIFIER":
                tag = "identifier"
                value = self.tokenizer.identifier()
            elif token_type == "INT_CONST":
                tag = "integerConstant"
                value = str(self.tokenizer.intVal())
            elif token_type == "STRING_CONST":
                tag = "stringConstant"
                value = self.tokenizer.stringVal()
            else:
                raise ValueError(f"Unknown token type: {token_type}")

            self.write(f"<{tag}> {self.escape(value)} </{tag}>")

        self.write("</tokens>")