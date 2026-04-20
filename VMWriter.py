class VMWriter:
    def __init__(self, output):
        self.out = output


    def writePush(self, segment, index) -> None:
        self.out.write(f"push {segment} {index}\n")


    def writePop(self, segment, index) -> None:
        self.out.write(f"pop {segment} {index}\n")


    def writeArithmetic(self, command) -> None:
        self.out.write(f"{command}\n")


    def writeLabel(self, label) -> None:
        self.out.write(f"label {label}\n")


    def writeGoto(self, label) -> None:
        self.out.write(f"goto {label}\n")


    def writeIf(self, label) -> None:
        self.out.write(f"if-goto {label}\n")


    def writeCall(self, label, nArgs) -> None:
        self.out.write(f"call {label} {nArgs}\n")


    def writeFunction(self, label, nLocals) -> None:
        self.out.write(f"function {label} {nLocals}\n")


    def writeReturn(self) -> None:
        self.out.write("return\n")