import sys
from pathlib import Path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def compile_jack_file(input_path):
    tokenizer = JackTokenizer(input_path)
    output_path = Path(input_path).with_suffix(".vm")

    with open(output_path, "w", encoding="utf-8") as out:
        engine = CompilationEngine(tokenizer, out)
        engine.compileClass()


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py <input file or directory>")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file():
        if path.suffix != ".jack":
            raise ValueError("Input file must end with .jack")
        compile_jack_file(path)
    elif path.is_dir():
        for jack_file in sorted(path.glob("*.jack")):
            compile_jack_file(jack_file)
    else:
        raise ValueError("Input path does not exist")


if __name__ == "__main__":
    main()