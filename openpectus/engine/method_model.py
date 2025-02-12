import logging
from typing import Callable
from uuid import UUID
from openpectus.lang.exec.runlog import RuntimeInfo
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PNode, PProgram
import openpectus.protocol.models as Mdl

logger = logging.getLogger(__name__)

def parse_pcode(pcode: str) -> PProgram:
    p = PGrammar()
    p.parse(pcode)
    return p.build_model()


class MethodModel:
    """ Manages the mutable method state and its changes.

    Method state is mutated by engine as the program runs, e.g. executed lines are updated
    Method state is mutated by aggregator, e.g. by the user changing program code lines on injecting code
    """
    def __init__(self,
                 on_method_init: Callable[[], None] | None = None,
                 on_method_error: Callable[[Exception], None] | None = None) -> None:

        self._method = Mdl.Method.empty()
        self._method_state: Mdl.MethodState = Mdl.MethodState.empty()
        self._program: PProgram = PProgram()
        self._pcode: str = ""
        self._map_line_num_to_line_id: dict[int, str] = {}
        self._map_line_id_to_line_num: dict[str, int] = {}
        self._map_line_num_to_node_id: dict[int, UUID] = {}
        self._map_node_id_to_line_num: dict[UUID, int] = {}
        self._method_init_callback: Callable[[], None] | None = on_method_init
        self._method_error_callback: Callable[[Exception], None] | None = on_method_error

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(program="{self.get_program()}")'

    def set_method(self, method: Mdl.Method):
        # initialize new method
        self._method = method
        self._pcode = '\n'.join(line.content for line in method.lines)
        try:
            self._program = parse_pcode(pcode=self._pcode)
        except Exception as ex:
            logger.error(f"Parse error, pcode:\n{self._pcode}", exc_info=True)
            if self._method_error_callback is not None:
                self._method_error_callback(ex)

            # TODO: Figure out whether we need to raise here - how is error callback used
            raise

        # fill mapping between line_num and line_id
        line_num: int = 1
        for line in method.lines:
            self._map_line_num_to_line_id[line_num] = line.id
            self._map_line_id_to_line_num[line.id] = line_num
            line_num += 1

        # fill mapping bewteen line_num and node_id
        def map_node(node: PNode):
            if node is not PProgram:
                assert node.line is not None
                self._map_line_num_to_node_id[node.line] = node.id
                self._map_node_id_to_line_num[node.id] = node.line
        self._program.iterate(map_node)

        if self._method_init_callback is not None:
            self._method_init_callback()

    def get_program(self) -> PProgram:
        return self._program

    def get_code_lines(self) -> list[Mdl.MethodLine]:
        return list([line for line in self._method.lines])

    def calculate_method_state(self, runtimeinfo: RuntimeInfo) -> Mdl.MethodState:
        method_state = Mdl.MethodState.empty()
        if self._pcode != "":
            for record in runtimeinfo.records:
                if not isinstance(record.node, PProgram):
                    assert record.node is not None, "node is None"
                    if record.node.line is not None:  # Note: injected nodes have no line numbers
                        line_num = record.node.line
                        line_id = self._map_line_num_to_line_id[line_num]
                        method_state.started_line_ids.append(line_id)
                        if record.visit_end_time != -1:
                            method_state.executed_line_ids.append(line_id)
        return method_state
