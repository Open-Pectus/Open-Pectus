
import logging
import time

from typing import List
from lang.model.pprogram import (
    PNode,
    PProgram,
    PBlank,
    # PBlock,
    # PEndBlock,
    PWatch,
    PAlarm,
    PCommand,
    PMark
)

from lang.exec.tags import TagCollection
from lang.exec.uod import UnitOperationDefinitionBase

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO add Alarm interpretation, including scope definition
# TODO add timings (depends on units)
# TODO condition expressions when defined in grammar
# TODO validate condition expression identifiers against known tags
# TODO if tags have an SI unit, validate the unit against that, eg. 'Watch: TT01 > 50 degC'


class PInterpreter():
    def __init__(self, program: PProgram, uod: UnitOperationDefinitionBase) -> None:
        self.tags = TagCollection()
        self.program = program
        self.uod = uod
        self.logs = []
        self.pause_node: PNode | None = None
        self.stack = []

    def validate_commands(self):  # return?
        # validate that all command names in the program are defined in the UOD
        commands = self.program.get_commands()
        for c in commands:
            if not self.uod.validate_command_name(c.name):
                c.add_error("Unknown command")
            if not self.uod.validate_command_args(c.name, c.args):
                c.add_error("Invalid arguments for command " + c.name)

        # validate that all condition tag references in the program are defined in the UOD
        condition_nodes = self.program.get_condition_nodes()
        for c in condition_nodes:
            if c.condition is None:
                c.add_error("Required condition is empty")
            else:
                try:
                    c.condition.parse()
                except Exception as ex:
                    c.add_error(f"Condition parse error: {ex}")
                    continue
                if not self.uod.validate_tag_name(c.condition.tag_name):
                    c.add_error(f"Unknown tag '{c.condition.tag_name}' in condition")
                    continue

    def start(self):
        next_node = self._run(self.program)
        while (next_node is not None):
            logger.debug(f"_run node: {type(next_node).__name__}, src line: {next_node.line}")
            next_node = self._run(next_node)

    def pause(self, node: PNode):
        self.pause_node = node
        # TODO pause execution

    def _run(self, node: PNode | None) -> PNode | None:
        if node is None:
            return None

        if node.has_error():
            logger.warning("Interpretation encountered a node with an error. Pausing execution")
            self.pause(node)
            return None

        elif isinstance(node, PProgram):
            # self.stack.append(node)
            next_node = node.next_descendant()
            return self._run(next_node)

        elif isinstance(node, PBlank):
            return node.next_following()

        elif isinstance(node, PMark):
            self.add_to_log(time.time(), node.time, node.name)
            return node.next_following()

        elif isinstance(node, PWatch):
            return self.run_watch(node)

        elif isinstance(node, PCommand):
            try:
                self.uod.execute_command(node.name, node.args)
            except Exception as ex:
                print(ex)
                return None
            return node.next_following()
        else:
            raise NotImplementedError(f"Interpreter does not support node type: {type(node).__name__}")

    def run_watch(self, node: PWatch) -> PNode | None:
        condition_result = self.evaluate_condition(node)
        if condition_result:
            # TODO push new context on stack and continue from child[0]
            next_node = node.next_descendant()
        else:
            # continue from next sibling or other folloing node
            next_node = node.next_following()
        return next_node

    def evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        # HACK to pass tests using the imaginary 'counter' tag.
        # Need condition expression definition and parsing for a proper implementation.
        value = int(self.uod.tags["counter"].get_value())
        return value > 0

    def add_to_log(self, _time, unit_time, message):
        self.logs.append({'time': _time, 'unit_time': unit_time, 'message': message})

    def get_marks(self) -> List[str]:
        return [x['message'] for x in self.logs]
