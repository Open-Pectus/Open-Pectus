
from io import StringIO
from lang.model.pprogram import (
    PNode,
    PProgram,
    PBlank
)


class FormattingOptions():
    def __init__(self) -> None:
        self.indent: int = 4
        self.blanks: bool = False
        self.line_numbers: bool = False
        self.errors: bool = False


class PProgramFormatter():
    def __init__(self, opts: FormattingOptions = FormattingOptions()) -> None:
        self.opts = opts
        self.out = StringIO()

    def format(self, program: PProgram) -> str:
        def print_node(node: PNode, indent: int):
            if not self.opts.blanks and isinstance(node, PBlank):
                return
            self.out.write("".join(" " for _ in range(indent)))
            self.out.write(type(node).__name__)
            if self.opts.errors:
                err = node.errors[0].message if node.has_error() else ""  # type: ignore
                self.out.write(f" | Err: {err}")
            if self.opts.line_numbers:
                self.out.write(f" | Line: {node.line}")

            self.out.write("\n")
            for child in node.get_child_nodes():                    
                print_node(child, indent + self.opts.indent)

        print_node(program, 0)
        return self.out.getvalue().strip()
