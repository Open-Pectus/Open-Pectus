
import logging
import re
from typing import Sequence


from openpectus.lsp.new_parser.grammar import Grammar
from openpectus.lsp.new_parser.program import Position, Range
import openpectus.lsp.new_parser.program as p


logger = logging.getLogger(__name__)


class PcodeParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.program = p.ProgramNode()
        self.cur_parent: p.Node = self.program

    def parseline(self, line: str, line_no: int, lines: Sequence[str]) -> p.Node:
        if line.strip() == "":
            return p.BlankNode(position=Position(line=line_no, character=0))

        match = Grammar.instruction_line_pattern.match(line)
        if not match:
            return p.ErrorInstructionNode(position=Position(line=line_no, character=0))

        match_groups = match.groupdict()
        indent = match_groups.get("indent")
        threshold = match_groups.get("threshold")
        instruction_name = match_groups.get("instruction_name", "")
        argument = match_groups.get("argument", "")
        comment = match_groups.get("comment", "")

        if instruction_name is None or instruction_name.strip() == "":
            return p.ErrorInstructionNode(position=Position(line=line_no, character=0))

        # grammar operates as node factory
        node = self.grammar.create_node(instruction_name)
        node.threshold_part = threshold or ""
        node.name_part = instruction_name
        node.arguments_part = (argument or "").rstrip()  # convenience cleanup, hard to do in regex
        node.comment_part = comment or ""

        node.position = Position(line=line_no, character=0 if indent is None else len(indent))
        node.threshold = None if threshold is None else float(threshold)

        if node.position.character % 4 != 0:
            node.indent_error = True

        return node

    def parse_program(self, lines: Sequence[str]) -> p.ProgramNode:
        self.program = p.ProgramNode()
        self.program.position = Position(0, 0)

        nodes: list[p.Node] = []
        # first parse all lines individually in one fast pass, ignoring indentation and parent
        line_no = 0
        for line in lines:
            node = self.parseline(line, line_no=line_no, lines=lines)
            nodes.append(node)
            line_no += 1

        # match indentations with node types to match nested instructions with their parent
        prev_indent = 0
        prev_node: p.Node | None = None
        parent_node: p.NodeWithChildren = self.program
        increment_required = False
        for line_no, node in enumerate(nodes):
            incr_indent_allowed = prev_node is not None and isinstance(prev_node, p.NodeWithChildren)
            decr_indent_allowed = parent_node.position.character > 0 and len(parent_node.children) > 0
            node_error = False

            if node.position.character == prev_indent:  # indentation unchanged
                if increment_required:
                    # what to do here - the node is in error but the parent may also be
                    logger.error("Expected increment")
                parent_node.append_child(node)
                if isinstance(node, p.NodeWithChildren):
                    parent_node = node
                    increment_required = True
                else:
                    increment_required = False

            elif node.position.character == prev_indent + 4:  # indentation increased one level
                # TODO fail if not valid increment
                if not increment_required:
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
                outdent_levels = int((prev_indent - node.position.character) / 4)
                for _ in range(outdent_levels):
                    if parent_node.parent is None:
                        node_error = True
                        node.indent_error = True
                        break
                    else:
                        parent_node = parent_node.parent

                parent_node.append_child(node)

            if not node_error:
                prev_node = node
                prev_indent = prev_node.position.character

        return self.program
