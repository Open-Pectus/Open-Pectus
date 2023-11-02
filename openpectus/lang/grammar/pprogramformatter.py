
from io import StringIO
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import (
    PNode,
    PProgram,
    PBlank
)


def print_program(program: PProgram, show_line_numbers: bool = False, show_errors: bool = False, show_blanks: bool = False):
    """ Print program to stdout using the provided options. """
    opts = FormattingOptions()
    opts.line_numbers = show_line_numbers
    opts.errors = show_errors
    opts.blanks = show_blanks
    out = PProgramFormatter(opts).format(program)
    print(out)


def print_parsed_program(pcode: str, show_line_numbers: bool = False, show_errors: bool = False, show_blanks: bool = False):
    """ Parse pcode and print program to stdout using the provided options. """
    p = PGrammar()
    p.parse(pcode)
    program = p.build_model()
    return print_program(program, show_line_numbers=show_line_numbers, show_errors=show_errors, show_blanks=show_blanks)


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
