
from io import StringIO
import openpectus.lang.model.ast as p
from openpectus.lang.model.parser import ParserMethod, create_method_parser


def print_program(program: p.ProgramNode,
                  show_line_numbers: bool = False,
                  show_errors: bool = False,
                  show_blanks: bool = False):
    """ Print program to stdout using the provided options. """
    opts = FormattingOptions()
    opts.line_numbers = show_line_numbers
    opts.errors = show_errors
    opts.blanks = show_blanks
    out = ProgramFormatter(opts).format(program)
    print()
    print(out)
    print()

def print_parsed_program(pcode: str,
                         show_line_numbers: bool = False,
                         show_errors: bool = False,
                         show_blanks: bool = False):
    """ Parse pcode and print program to stdout using the provided options. """
    method = ParserMethod.from_pcode(pcode)
    parser = create_method_parser(method)
    program = parser.parse_method(method)
    return print_program(program, show_line_numbers=show_line_numbers, show_errors=show_errors, show_blanks=show_blanks)


class FormattingOptions():
    def __init__(self) -> None:
        self.indent: int = 4
        self.blanks: bool = False
        self.line_numbers: bool = False
        self.errors: bool = False



class ProgramFormatter():
    def __init__(self, opts: FormattingOptions = FormattingOptions()) -> None:
        self.opts = opts
        self.out = StringIO()

    def format(self, program: p.ProgramNode) -> str:
        def print_node(node: p.Node, indent: int):
            if not self.opts.blanks and isinstance(node, p.BlankNode):
                return
            self.out.write("".join(" " for _ in range(indent)))
            self.out.write(type(node).__name__)
            if self.opts.errors:
                err = node.errors[0].message if node.has_error() else ""
                self.out.write(f" | Err: {err}")
            if self.opts.line_numbers:
                self.out.write(f" | Line: {node.position.line}")

            self.out.write("\n")
            if isinstance(node, p.NodeWithChildren):
                for child in node.get_child_nodes():
                    print_node(child, indent + self.opts.indent)

        print_node(program, 0)
        return self.out.getvalue().strip()
