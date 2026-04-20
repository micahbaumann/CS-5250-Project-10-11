from SymbolTable import SymbolTable
from VMWriter import VMWriter

OPS = {"+": "add", "-": "sub", "&": "and", "|": "or", "<": "lt", ">": "gt", "=": "eq"}
UNARY_OPS = {"-": "neg", "~": "not"}
KEYWORD_CONSTANTS = {"true", "false", "null", "this"}

class CompilationEngine:
    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer
        self.vm = VMWriter(output)
        self.symbols = SymbolTable()
        self.class_name = ""
        self.label_counter = 0
    

    def eat(self, expected=None):
        if not self.tokenizer.hasMoreTokens():
            raise ValueError("Unexpected end of input")

        self.tokenizer.advance()

        if expected is not None and self.tokenizer.current != expected:
            raise ValueError(f"Expected '{expected}', got '{self.tokenizer.current}'")

        return self.tokenizer.current

    
    def newLabel(self, prefix: str) -> str:
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label


    def segmentOf(self, kind: str) -> str:
        if kind == "STATIC":
            return "static"
        if kind == "FIELD":
            return "this"
        if kind == "ARG":
            return "argument"
        if kind == "VAR":
            return "local"
        raise ValueError(f"Unknown kind: {kind}")


    def pushVar(self, name: str) -> None:
        kind = self.symbols.kindOf(name)
        index = self.symbols.indexOf(name)
        self.vm.writePush(self.segmentOf(kind), index)


    def popVar(self, name: str) -> None:
        kind = self.symbols.kindOf(name)
        index = self.symbols.indexOf(name)
        self.vm.writePop(self.segmentOf(kind), index)


    def compileClass(self) -> None:
        self.eat("class")
        self.class_name = self.eat()
        self.eat("{")

        while self.tokenizer.peek() in ("static", "field"):
            self.compileClassVarDec()

        while self.tokenizer.peek() in ("constructor", "function", "method"):
            self.compileSubroutine()

        self.eat("}")


    def compileClassVarDec(self) -> None:
        kind = self.eat().upper()
        type = self.eat()
        name = self.eat()

        self.symbols.define(name, type, kind)

        while self.tokenizer.peek() == ",":
            self.eat(",")
            name = self.eat()
            self.symbols.define(name, type, kind)

        self.eat(";")


    def compileSubroutine(self) -> None:
        subroutine_kind = self.eat()
        self.eat()
        subroutine_name = self.eat()

        self.symbols.startSubroutine()

        if subroutine_kind == "method":
            self.symbols.define("this", self.class_name, "ARG")

        self.eat("(")
        self.compileParameterList()
        self.eat(")")

        self.eat("{")

        while self.tokenizer.peek() == "var":
            self.compileVarDec()

        full_name = f"{self.class_name}.{subroutine_name}"
        n_locals = self.symbols.varCount("VAR")
        self.vm.writeFunction(full_name, n_locals)

        if subroutine_kind == "constructor":
            field_count = self.symbols.varCount("FIELD")
            self.vm.writePush("constant", field_count)
            self.vm.writeCall("Memory.alloc", 1)
            self.vm.writePop("pointer", 0)

        elif subroutine_kind == "method":
            self.vm.writePush("argument", 0)
            self.vm.writePop("pointer", 0)

        self.compileStatements()
        self.eat("}")


    def compileParameterList(self) -> None:
        if self.tokenizer.peek() != ")":
            type = self.eat()
            name = self.eat()
            self.symbols.define(name, type, "ARG")

            while self.tokenizer.peek() == ",":
                self.eat(",")
                type = self.eat()
                name = self.eat()
                self.symbols.define(name, type, "ARG")


    def compileVarDec(self) -> None:
        self.eat("var")
        type = self.eat()
        name = self.eat()
        self.symbols.define(name, type, "VAR")

        while self.tokenizer.peek() == ",":
            self.eat(",")
            name = self.eat()
            self.symbols.define(name, type, "VAR")

        self.eat(";")


    def compileStatements(self) -> None:
        while self.tokenizer.peek() in ("let", "if", "while", "do", "return"):
            next = self.tokenizer.peek()
            if next == "let":
                self.compileLet()
            elif next == "if":
                self.compileIf()
            elif next == "while":
                self.compileWhile()
            elif next == "do":
                self.compileDo()
            elif next == "return":
                self.compileReturn()


    def compileDo(self) -> None:
        self.eat("do")
        name = self.eat()
        n_args = 0

        if self.tokenizer.peek() == ".":
            self.eat(".")
            subroutine_name = self.eat()

            kind = self.symbols.kindOf(name)
            if kind is not None:
                type_ = self.symbols.typeOf(name)
                index = self.symbols.indexOf(name)
                self.vm.writePush(self.segmentOf(kind), index)
                full_name = f"{type_}.{subroutine_name}"
                n_args += 1
            else:
                full_name = f"{name}.{subroutine_name}"

        else:
            self.vm.writePush("pointer", 0)
            full_name = f"{self.class_name}.{name}"
            n_args += 1

        self.eat("(")
        n_args += self.compileExpressionList()
        self.eat(")")

        self.vm.writeCall(full_name, n_args)
        self.vm.writePop("temp", 0)
        self.eat(";")


    def compileLet(self) -> None:
        self.eat("let")
        name = self.eat()

        is_array = False
        if self.tokenizer.peek() == "[":
            is_array = True
            self.eat("[")
            self.pushVar(name)
            self.compileExpression()
            self.vm.writeArithmetic("add")
            self.eat("]")

        self.eat("=")
        self.compileExpression()
        self.eat(";")

        if is_array:
            self.vm.writePop("temp", 0)
            self.vm.writePop("pointer", 1)
            self.vm.writePush("temp", 0)
            self.vm.writePop("that", 0)
        else:
            self.popVar(name)


    def compileWhile(self) -> None:
        self.eat("while")

        start_label = self.newLabel("WHILE_EXP")
        end_label = self.newLabel("WHILE_END")

        self.vm.writeLabel(start_label)

        self.eat("(")
        self.compileExpression()
        self.eat(")")

        self.vm.writeArithmetic("not")
        self.vm.writeIf(end_label)

        self.eat("{")
        self.compileStatements()
        self.eat("}")

        self.vm.writeGoto(start_label)
        self.vm.writeLabel(end_label)


    def compileReturn(self) -> None:
        self.eat("return")

        if self.tokenizer.peek() != ";":
            self.compileExpression()
        else:
            self.vm.writePush("constant", 0)

        self.eat(";")
        self.vm.writeReturn()


    def compileIf(self) -> None:
        self.eat("if")

        true_label = self.newLabel("IF_TRUE")
        false_label = self.newLabel("IF_FALSE")
        end_label = self.newLabel("IF_END")

        self.eat("(")
        self.compileExpression()
        self.eat(")")

        self.vm.writeIf(true_label)
        self.vm.writeGoto(false_label)
        self.vm.writeLabel(true_label)

        self.eat("{")
        self.compileStatements()
        self.eat("}")

        if self.tokenizer.peek() == "else":
            self.vm.writeGoto(end_label)
            self.vm.writeLabel(false_label)

            self.eat("else")
            self.eat("{")
            self.compileStatements()
            self.eat("}")

            self.vm.writeLabel(end_label)
        else:
            self.vm.writeLabel(false_label)


    def compileExpression(self) -> None:
        self.compileTerm()

        while self.tokenizer.peek() in OPS or self.tokenizer.peek() in ("*", "/"):
            op = self.eat()
            self.compileTerm()

            if op in OPS:
                self.vm.writeArithmetic(OPS[op])
            elif op == "*":
                self.vm.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vm.writeCall("Math.divide", 2)


    def compileTerm(self) -> None:
        next_token = self.tokenizer.peek()

        if next_token is None:
            raise ValueError("Unexpected end of input in term")

        if next_token.isdigit():
            value = int(self.eat())
            self.vm.writePush("constant", value)

        elif next_token.startswith('"'):
            value = self.eat()[1:-1]
            self.vm.writePush("constant", len(value))
            self.vm.writeCall("String.new", 1)
            for ch in value:
                self.vm.writePush("constant", ord(ch))
                self.vm.writeCall("String.appendChar", 2)

        elif next_token in KEYWORD_CONSTANTS:
            kw = self.eat()
            if kw in ("false", "null"):
                self.vm.writePush("constant", 0)
            elif kw == "true":
                self.vm.writePush("constant", 0)
                self.vm.writeArithmetic("not")
            elif kw == "this":
                self.vm.writePush("pointer", 0)

        elif next_token == "(":
            self.eat("(")
            self.compileExpression()
            self.eat(")")

        elif next_token in UNARY_OPS:
            op = self.eat()
            self.compileTerm()
            self.vm.writeArithmetic(UNARY_OPS[op])

        else:
            name = self.eat()

            if self.tokenizer.peek() == "[":
                self.eat("[")
                self.pushVar(name)
                self.compileExpression()
                self.vm.writeArithmetic("add")
                self.eat("]")
                self.vm.writePop("pointer", 1)
                self.vm.writePush("that", 0)

            elif self.tokenizer.peek() == "(" or self.tokenizer.peek() == ".":
                n_args = 0

                if self.tokenizer.peek() == ".":
                    self.eat(".")
                    subroutine_name = self.eat()

                    kind = self.symbols.kindOf(name)
                    if kind is not None:
                        type_ = self.symbols.typeOf(name)
                        index = self.symbols.indexOf(name)
                        self.vm.writePush(self.segmentOf(kind), index)
                        full_name = f"{type_}.{subroutine_name}"
                        n_args += 1
                    else:
                        full_name = f"{name}.{subroutine_name}"

                else:
                    self.vm.writePush("pointer", 0)
                    full_name = f"{self.class_name}.{name}"
                    n_args += 1

                self.eat("(")
                n_args += self.compileExpressionList()
                self.eat(")")

                self.vm.writeCall(full_name, n_args)

            else:
                self.pushVar(name)


    def compileExpressionList(self) -> None:
        count = 0

        if self.tokenizer.peek() != ")":
            self.compileExpression()
            count += 1

            while self.tokenizer.peek() == ",":
                self.eat(",")
                self.compileExpression()
                count += 1

        return count