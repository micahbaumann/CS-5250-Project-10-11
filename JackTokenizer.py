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

        
        
        return []


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