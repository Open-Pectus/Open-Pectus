

import logging
import re
from typing import Sequence
import openpectus.lsp.new_parser.program as p


logger = logging.getLogger(__name__)


class Grammar:
    indent_re = r'(?P<indent>\s+)?'
    threshold_re = r'((?P<threshold>\d+(\.\d+)?)\s)?'
    instruction_re = r'(?P<instruction_name>\b[a-zA-Z_][^:#]*)'
    #argument_re = r'(: (?P<argument>[^#]+\b))?'
    argument_re = r'(: (?P<argument>[^#]+))?'
    comment_re = r'(\s*#\s*(?P<comment>.*$))?'

    full_line_re = indent_re + threshold_re + instruction_re + argument_re + comment_re
    # fallback is used to capture the command name, even if the command is not parsable
    #re_fallback_inst = r'(?P<indent>\s+)?((?P<threshold>\d+(\.\d+)?)\s)?(?P<instruction_name>[^:#]+\b) :? \s*#\s*(?P<comment>.*$))?'  # noqa E501'

    instruction_line_pattern = re.compile(full_line_re)

    def __init__(self):
        # the test suite shows no apparent perf deficit doing this
        self.instruction_name_map = self._inspect_instruction_node_types()
        # instead of this
        # self.instruction_name_map = {
        #     'Mark': p.MarkNode,
        #     'Block': p.BlockNode,
        # }

    def _inspect_instruction_node_types(self) -> dict[str, type[p.Node]]:
        import inspect
        map = {}
        for _, node_type in inspect.getmembers(p, inspect.isclass):
            if issubclass(node_type, p.Node):
                inst_name = node_type.instruction_name
                if inst_name is not None and inst_name != "":
                    map[inst_name] = node_type
        return map

    def create_node(self, instruction_name: str) -> p.Node:
        factory = self.instruction_name_map.get(instruction_name, None)
        if factory is not None:
            try:
                return factory()
            except Exception:
                logger.error(f"Factory failed, {instruction_name=}")

        return p.ErrorInstructionNode()
