from pathlib import Path

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this",
    "let", "do", "if", "else", "while", "return"
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~")

class JackTokenizer:
    def __init__(self, input_path):
        self.source = Path(input_path).read_text()
        self.tokens = self.tokenize(self.source)
        self.index = -1
        self.current = None
    

    def removeComments(self, text) -> str:
        result = []
        i = 0
        length = len(text)
        in_string = False

        while i < length:
            char = text[i]
            next = text[i + 1] if i + 1 < length else ""

            if in_string:
                result.append(char)
                if char == '"':
                    in_string = False
                i += 1
                continue

            if char == '"':
                in_string = True
                result.append(char)
                i += 1
                continue

            if char == "/" and next == "/":
                i += 2
                while i < length and text[i] != "\n":
                    i += 1
                continue

            if char == "/" and next == "*":
                i += 2
                while i + 1 < length and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
                continue

            result.append(char)
            i += 1

        return "".join(result)

    
    def tokenize(self, text) -> list:
        clean_text = self.removeComments(text)

        tokens = []
        i = 0

        while i < len(clean_text):

            if clean_text[i].isspace():
                i += 1
                continue

            if clean_text[i] in SYMBOLS:
                tokens.append(clean_text[i])
                i += 1
                continue

            if clean_text[i] == "\"":
                i += 1
                temp_token = "\""
                while clean_text[i] != "\"":
                    temp_token += clean_text[i]
                    i += 1
                temp_token += "\""
                tokens.append(temp_token)
                i += 1
                continue

            if clean_text[i].isdigit():
                temp_token = ""
                while i < len(clean_text) and clean_text[i].isdigit():
                    temp_token += clean_text[i]
                    i += 1
                tokens.append(temp_token)
                continue

            if clean_text[i].isalpha() or clean_text[i] == "_":
                temp_token = ""
                while i < len(clean_text) and (clean_text[i].isalnum() or clean_text[i] == "_"):
                    temp_token += clean_text[i]
                    i += 1
                tokens.append(temp_token)
                continue

            raise ValueError(f"Unexpected character: {clean_text[i]!r} at position {i}")
        
        return tokens


    def hasMoreTokens(self) -> bool:
        return self.index + 1 < len(self.tokens)


    def advance(self) -> None:
        self.index += 1
        self.current = self.tokens[self.index]


    def tokenType(self) -> str:
        if self.current in KEYWORDS:
            return "KEYWORD"
        elif self.current in SYMBOLS:
            return "SYMBOL"
        elif self.current.isdigit():
            return "INT_CONST"
        elif self.current.startswith("\""):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyWord(self) -> str:
        if self.tokenType() == "KEYWORD":
            return self.current
        raise ValueError(f"\"{self.current}\" is not a keyword")


    def symbol(self) -> str:
        if self.tokenType() == "SYMBOL":
            return self.current
        raise ValueError(f"\"{self.current}\" is not a symbol")


    def identifier(self) -> str:
        if self.tokenType() == "IDENTIFIER":
            return self.current
        raise ValueError(f"\"{self.current}\" is not a identifier")


    def intVal(self) -> int:
        if self.tokenType() == "INT_CONST":
            return int(self.current)
        raise ValueError(f"\"{self.current}\" is not a integer")


    def stringVal(self) -> str:
        if self.tokenType() == "STRING_CONST":
            return self.current[1:-1]
        raise ValueError(f"\"{self.current}\" is not a string")
    
    
    def peek(self) -> str | None:
        if self.hasMoreTokens():
            return self.tokens[self.index + 1]
    