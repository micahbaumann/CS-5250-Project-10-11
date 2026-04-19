import sys
from pathlib import Path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def write_xml(input_path):
    tokenizer = JackTokenizer(input_path)
    output_path = Path(input_path).with_suffix(".xml")
    output_pathT = Path(input_path).with_name(Path(input_path).stem + "T.xml")

    with open(output_path, "w", encoding="utf-8") as out:
        engine = CompilationEngine(tokenizer, out)
        engine.compileClass()

    tokenizer = JackTokenizer(input_path)
    with open(output_pathT, "w", encoding="utf-8") as out:
        engine = CompilationEngine(tokenizer, out)
        engine.compileTokens()


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py <input file or directory>")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file():
        if path.suffix != ".jack":
            raise ValueError("Input file must end with .jack")
        write_xml(path)
    elif path.is_dir():
        for jack_file in sorted(path.glob("*.jack")):
            write_xml(jack_file)
    else:
        raise ValueError("Input path does not exist")


if __name__ == "__main__":
    main()