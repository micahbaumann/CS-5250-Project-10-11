import sys
from pathlib import Path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def analyze_file(path: Path):
    tokenizer = JackTokenizer(path)

    output_path = path.with_suffix(".xml")
    with open(output_path, "w") as out:
        engine = CompilationEngine(tokenizer, out)
        # engine.compileClass()


def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer <file.jack | directory>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if input_path.is_file():
        analyze_file(input_path)
    else:
        for file in input_path.glob("*.jack"):
            analyze_file(file)


if __name__ == "__main__":
    main()