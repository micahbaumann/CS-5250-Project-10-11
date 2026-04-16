from pathlib import Path
import re

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

    
    def tokenize(self, text) -> list:
        clean_text = re.sub(r"//.*", "", text)
        clean_text = re.sub(r"/\*.*?\*/", "", clean_text, flags=re.DOTALL)

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
                temp_token = ""
                while clean_text[i] != "\"":
                    temp_token += clean_text[i]
                    i += 1
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
                while i < len(clean_text) and (clean_text[i].isalpha() or clean_text[i] == "_"):
                    temp_token += clean_text[i]
                    i += 1
                tokens.append(temp_token)
                continue
        
        return tokens


    def hasMoreTokens(self) -> bool:
        pass


    def advance(self) -> None:
        pass


    def tokenType(self) -> str:
        pass


    def keyWord(self) -> str:
        pass


    def symbol(self) -> str:
        pass


    def identifier(self) -> str:
        pass


    def intVal(self) -> int:
        pass


    def stringVal(self) -> str:
        pass