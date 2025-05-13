from __future__ import annotations
from dataclasses import dataclass
import logging
import re

from openpectus.lang.model.ast import NodeIdGenerator, Position
import openpectus.lang.model.ast as p


logger = logging.getLogger(__name__)


def create_method_parser(method: ParserMethod, uod_command_names: list[str] = []) -> PcodeParser:
    """ Create the default parser that applies line ids to nodes. """
    return PcodeParser(id_generator=MethodLineIdGenerator(method), uod_command_names=uod_command_names)

def create_inject_parser(uod_command_names: list[str] = []) -> PcodeParser:
    """ Create a parser that applies negative ids to nodes. Used for injecting pcode into a method. """
    return PcodeParser(id_generator=NegativeIdGenerator(), uod_command_names=uod_command_names)


@dataclass
class ParserMethodLine:
    id: str
    content: str


class ParserMethod:
    empty: ParserMethod

    def __init__(self, lines: list[ParserMethodLine]):
        self.version = 0
        self.lines: list[ParserMethodLine] = lines
        # TODO add version and author - we should keep a version number so we can easily detect
        # multiple concurrent editors and bail out quick in that case

    def __str__(self) -> str:
        lines = [str(line) for line in self.lines]
        return f'{self.__class__.__name__}(lines={lines})'

    @staticmethod
    def create_empty() -> ParserMethod:
        return ParserMethod(lines=[])

    def is_empty(self) -> bool:
        return self.lines == 0

    @staticmethod
    def from_pcode(pcode: str) -> ParserMethod:
        method = ParserMethod.create_empty()
        line_num: int = 1
        for line in pcode.splitlines():
            method.lines.append(ParserMethodLine(id=f"id_{line_num}", content=line))
            line_num += 1
        return method

    def as_pcode(self) -> str:
        pcode = '\n'.join([line.content for line in self.lines])
        return pcode


ParserMethod.empty = ParserMethod.create_empty()


class IncrementalIdGenerator(NodeIdGenerator):
    def __init__(self):
        super().__init__()
        self.next_id = 1

    def create_id(self, node: p.Node):
        id = self.next_id
        self.next_id += 1
        return str(id)


class MethodLineIdGenerator(NodeIdGenerator):
    """ Generates node ids from line ids in source method """
    def __init__(self, method: ParserMethod):
        super().__init__()
        self.method = method

    def create_id(self, node: p.Node) -> str:
        """ find source line for the node in method """
        if isinstance(node, p.ProgramNode):
            return "root"
        line = self.method.lines[node.position.line]
        return line.id

class NegativeIdGenerator(NodeIdGenerator):
    """ Generates incremental negative ids for use with injected code lines. """
    def __init__(self):
        super().__init__()
        self.id = -1

    def create_id(self, node):
        id = self.id
        self.id -= 1
        return str(id)


def count_leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip())

def count_trailing_spaces(s: str) -> int:
    return len(s) - len(s.rstrip())


class Grammar:
    indent_re = r'(?P<indent>\s+)?'
    threshold_re = r'((?P<threshold>\d+(\.\d+)?)\s)?'
    instruction_re = r'(?P<instruction_name>\b[a-zA-Z_0-9][^:#]*)'
    argument_re = r'(: (?P<argument>[^#]+))?'
    comment_re = r'(\s*(?P<has_comment>#)\s*(?P<comment>.*$))?'

    full_line_re = indent_re + threshold_re + instruction_re + argument_re + comment_re
    # fallback is used to capture the command name, even if the command is not parsable
    #re_fallback_inst = r'(?P<indent>\s+)?((?P<threshold>\d+(\.\d+)?)\s)?(?P<instruction_name>[^:#]+\b) :? \s*#\s*(?P<comment>.*$))?'  # noqa E501'

    instruction_line_pattern = re.compile(full_line_re)

    operators = ['<', '<=', '>', '>=', '==', '=', '!=']
    operators_1char = ['<', '>', '=']
    operators_2char = ['<=', '>=', '==', '!=']
    # condition_op_re = "\\s*(?P<op>" + "|".join(op for op in operators) + ")\\s*"

    float_re = r'(?P<float>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)'
    unit_re = r'(?P<unit>[a-zA-Z%\/23\*]+)'

    condition_rhs_re = '^' + float_re + '\\s*' + unit_re + '$'
    condition_rhs_pattern = re.compile(condition_rhs_re)
    condition_rhs_no_unit_re = '^' + float_re + '\\s*$'
    condition_rhs_no_unit_pattern = re.compile(condition_rhs_no_unit_re)


class LspParseResult:
    def __init__(self, indentation: str, threshold: str, instruction_name: str, argument: str):
        self.indentation: str = indentation
        self.threshold: str = threshold
        self.instruction_name: str = instruction_name
        self.argument: str = argument


def lsp_parse_line(pcode_query: str) -> LspParseResult | None:
    """ Provides a fast one-line parse for lsp completions. """
    if "\r\n" in pcode_query:
        pcode_query, remainder = pcode_query.split("\r\n", maxsplit=1)
        assert len(remainder) == 0
    match = Grammar.instruction_line_pattern.match(pcode_query)
    if match is None:
        return None
    else:
        match_groups = match.groupdict()
        indent = match_groups.get("indent")
        threshold = match_groups.get("threshold")
        instruction_name = match_groups.get("instruction_name", "") or ""
        argument = match_groups.get("argument", "")
        return LspParseResult(indent or "", threshold or "", instruction_name, argument or "")


class PcodeParser:
    def __init__(self, id_generator: NodeIdGenerator = IncrementalIdGenerator(), uod_command_names: list[str] = []):
        self.id_generator: NodeIdGenerator = id_generator
        self.instruction_name_map = self._inspect_instruction_node_types()
        self.uod_command_names = uod_command_names

    def parse_pcode(self, pcode: str) -> p.ProgramNode:
        method = ParserMethod.from_pcode(pcode)
        return self.parse_method(method)

    def parse_method(self, method: ParserMethod) -> p.ProgramNode:  # noqa C901
        program = p.ProgramNode(position=Position(0, 0)).with_id(self.id_generator)

        # first parse all lines individually in one fast pass, ignoring indentation and parent
        nodes: list[p.Node] = []
        line_no = 0
        for line in method.lines:
            node = self._parse_line(line.content, line_no=line_no)
            nodes.append(node)
            line_no += 1

        # match indentations with node types to match nested instructions with their parent
        prev_indent = 0
        prev_node: p.Node | None = None
        parent_node: p.NodeWithChildren = program
        increment_required = False
        for line_no, node in enumerate(nodes):
            # incr_indent_allowed = prev_node is not None and isinstance(prev_node, p.NodeWithChildren)
            # decr_indent_allowed = parent_node.position.character > 0 and len(parent_node.children) > 0
            node_error = False
            is_whitespace_node = isinstance(node, p.WhitespaceNode)

            if node.indent_error:
                parent_node.append_child(node)
                node_error = True
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    pass


            elif node.position.character > prev_indent and not increment_required:
                parent_node.append_child(node)
                node.indent_error = True
                node_error = True
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    increment_required = False

            elif node.position.character == prev_indent:  # indentation unchanged
                if increment_required:
                    # what to do here - the node is in error but the parent may also be
                    logger.error("Expected increment")
                parent_node.append_child(node)
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    increment_required = False

            elif node.position.character == parent_node.position.character + 4 and not isinstance(parent_node, p.ProgramNode):  # indentation increased one level
                # TODO fail if not valid increment
                if not increment_required and not is_whitespace_node:
                    node.indent_error = True
                    node_error = True
                parent_node.append_child(node)
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    increment_required = False

            elif node.position.character > prev_indent + 4:  # indentation increased multiple levels
                node.indent_error = True
                node_error = True

            elif node.position.character < prev_indent:  # indentation decreased one or more levels
                if not is_whitespace_node:
                    outdent_levels = int((prev_indent - node.position.character) / 4)
                    for _ in range(outdent_levels):
                        if parent_node.parent is None:
                            node_error = True
                            node.indent_error = True
                            break
                        else:
                            parent_node = parent_node.parent

                parent_node.append_child(node)
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    increment_required = False

            else:
                parent_node.append_child(node)

            if not node_error:
                prev_node = node
                if not is_whitespace_node:
                    prev_indent = prev_node.position.character

            if increment_required and not isinstance(node, (p.ProgramNode, p.WatchNode, p.AlarmNode, p.MacroNode, p.BlockNode,)) and not node_error:
                increment_required = False

        return program

    def _parse_line(self, line: str, line_no: int) -> p.Node:
        line_stripped = line.strip()
        if line_stripped == "":
            return p.BlankNode(
                position=Position(line=line_no, character=len(line))
            ).with_id(self.id_generator)
        elif line_stripped.startswith("#"):
            return p.CommentNode(
                position=Position(line=line_no, character=line.index("#"))
            ).with_id(self.id_generator).with_line(line)

        match = Grammar.instruction_line_pattern.match(line)
        if not match:
            return p.ErrorInstructionNode(
                position=Position(line=line_no, character=0)
            ).with_id(self.id_generator).with_line(line)

        match_groups = match.groupdict()
        indent = match_groups.get("indent")
        threshold = match_groups.get("threshold")
        instruction_name = match_groups.get("instruction_name", "") or ""
        argument = match_groups.get("argument", "")
        has_comment = match_groups.get("has_comment", "") == "#"
        comment = match_groups.get("comment", "")
        
        has_argument = ":" in line_stripped.split("#")[0]

        node = self._create_node(instruction_name.strip(), line, line_no).with_id(self.id_generator)
        node.threshold_part = threshold or ""
        node.instruction_part = instruction_name
        node.instruction_range = p.Range(
            start=Position(
                line=line_no,
                character=match.start("instruction_name")+count_leading_spaces(node.instruction_part),
            ),
            end=Position(
                line=line_no,
                character=match.end("instruction_name")-count_trailing_spaces(node.instruction_part),
            )
        )
        node.arguments_part = (argument or "")
        if len(node.arguments_part) > 0:
            node.arguments_range = p.Range(
                start=Position(
                    line=line_no,
                    character=match.start("argument")+count_leading_spaces(node.arguments_part),
                ),
                end=Position(
                    line=line_no,
                    character=match.end("argument")-count_trailing_spaces(node.arguments_part),
                )
            )
        node.has_argument = has_argument
        node.arguments = node.arguments_part.strip()  # convenience cleanup, hard to do in regex
        node.has_comment = has_comment
        node.comment_part = comment or ""

        character = 0 if indent is None or indent == "" else len(indent)
        node.position = Position(line=line_no, character=character)
        node.threshold = None if threshold is None else float(threshold)

        if node.position.character % 4 != 0:
            node.indent_error = True

        # could leave this out initially to speed up parsing
        if isinstance(node, p.NodeWithCondition):
            self._parse_condition(node)

        return node

    @staticmethod
    def _parse_condition(node: p.NodeWithCondition):  # noqa C901
        node.condition_part = node.arguments_part
        node.condition = p.Condition()

        c = node.condition
        c.range = node.arguments_range

        # check operator existence
        for op2 in Grammar.operators_2char:
            if op2 in node.condition_part:
                c.op = op2
                break
        if c.op == "":
            for op1 in Grammar.operators_1char:
                if op1 in node.condition_part:
                    c.op = op1
                    break
        if c.op == "":
            c.lhs = node.arguments_part.strip()
            c.lhs_range = node.arguments_range
            c.tag_name = c.lhs
            return

        try:
            op_start = node.condition_part.index(c.op)
            leading_spaces = count_leading_spaces(node.condition_part)
            trailing_spaces = count_trailing_spaces(node.condition_part)
            [lhs, rhs] = node.condition_part.split(c.op)
            c.lhs = lhs.strip()
            c.lhs_range = p.Range(
                start=c.range.start,
                end=Position(
                    line=c.range.start.line,
                    character=c.range.start.character + op_start - 1 - trailing_spaces)
            )

            c.op_range = p.Range(
                start=Position(
                    line=c.range.start.line,
                    character=c.range.start.character + op_start - leading_spaces),
                end=Position(
                    line=c.range.start.line,
                    character=c.range.start.character + op_start - leading_spaces + len(c.op)),
            )
            c.rhs = rhs.strip()
            c.rhs_range = p.Range(
                start=Position(
                    line=c.range.start.line,
                    character=c.op_range.end.character + 1),
                end=Position(
                    line=c.range.start.line,
                    character=c.op_range.end.character + len(rhs) - trailing_spaces)
                )

        except Exception:
            return

        # lhs must be a tag but we cannot validate this at parse time. This is done later in an analyzer
        if c.lhs != "":
            c.tag_name = c.lhs
        else:
            return

        # rhs must be a number possibly followed by a unit. At parse time
        # we can only check the number constraint
        if c.rhs == "":
            return

        match = re.search(Grammar.condition_rhs_pattern, c.rhs)
        if match:  # float with unit
            c.tag_value = match.group('float')
            c.tag_value_numeric = float(c.tag_value or "")
            c.tag_unit = match.group('unit')
            c.error = False
        else:
            match = re.search(Grammar.condition_rhs_no_unit_pattern, c.rhs)

            if match:  # float without unit
                c.tag_value = match.group('float')
                c.tag_value_numeric = float(c.tag_value or "")
                c.error = False
            else:  # str
                c.tag_value = c.rhs
                c.error = False
        node.condition.error = False

    # consider caching this, we only need to load once per process
    def _inspect_instruction_node_types(self) -> dict[str, type[p.Node]]:
        """ Build 'instruction_name => node constructor' map based on Node sub classes
        and their instruction_names class field. """
        import inspect
        map = {}
        for _, node_type in inspect.getmembers(p, inspect.isclass):
            if issubclass(node_type, p.Node):
                for inst_name in node_type.instruction_names:
                    if inst_name is not None and inst_name != "":
                        map[inst_name] = node_type
        return map

    def _create_node(self, instruction_name: str, line: str, line_number: int) -> p.Node:
        factory = self.instruction_name_map.get(instruction_name, None)
        if factory is not None:
            try:
                return factory(position=Position(line_number, 0))
            except Exception:
                logger.error(f"Factory failed, {instruction_name=}")
        else:
            if instruction_name in self.uod_command_names:
                return p.UodCommandNode(
                    position=Position(line_number, 0)
                    ).with_id(self.id_generator)

        return p.ErrorInstructionNode(
            position=Position(line_number, 0)
        ).with_id(self.id_generator).with_line(line)
