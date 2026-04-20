class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}

        self.counts = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0,
        }


    def startSubroutine(self) -> None:
        self.subroutine_scope = {}
        self.counts["ARG"] = 0
        self.counts["VAR"] = 0


    def define(self, name, type, kind) -> None:
        index = self.counts[kind]
        entry = {
            "type": type,
            "kind": kind,
            "index": index,
        }

        if kind == "STATIC" or kind == "FIELD":
            self.class_scope[name] = entry
        elif kind == "ARG" or kind == "VAR":
            self.subroutine_scope[name] = entry
        else:
            raise ValueError(f"Unknown kind: {kind}")

        self.counts[kind] += 1


    def varCount(self, kind) -> int:
        return self.counts[kind]


    def kindOf(self, name) -> str:
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["kind"]
    
        if name in self.class_scope:
            return self.class_scope[name]["kind"]
        return None


    def typeOf(self, name) -> str:
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["type"]

        if name in self.class_scope:
            return self.class_scope[name]["type"]


    def indexOf(self, name) -> int:
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]["index"]
        
        if name in self.class_scope:
            return self.class_scope[name]["index"]
