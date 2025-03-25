import logging
from openpectus.lang.exec.pinterpreter import PInterpreter
from openpectus.lang.exec.units import as_int
import openpectus.protocol.models as Mdl
from openpectus.lang.model.parser import Method, MethodLine, create_method_parser, create_inject_parser
import openpectus.lang.model.ast as p

logger = logging.getLogger(__name__)



class MethodModel:

    def __init__(self, uod_command_names: list[str]):
        self._uod_command_names = uod_command_names
        self._method = Method.empty
        self._program = p.ProgramNode.empty()

    @property
    def method(self) -> Method:
        return self._method

    @property
    def program(self) -> p.ProgramNode:
        return self._program

    def save_method(self, method: Mdl.Method):
        """ User saved a modified method"""
        # concurrency check: aggregator performs the version check and aborts on error

        # convert method from protocol api
        _method = Method(lines=[MethodLine(line.id, line.content) for line in method.lines])
        existing_state = self._program.extract_tree_state()

        # TODO consider engine state - if we're in running state, we should probably pause before modifying the method
        # TODO consider MethodState - will that automatically be correct when state changes are applied?

        logger.debug(f"Existing tree state size: {len(existing_state.keys())}")
        logger.debug(f"existing state: {str(existing_state)}")
        self._method = _method
        parser = create_method_parser(_method, self._uod_command_names)
        self._program = parser.parse_method(_method)
        try:
            self._program.apply_tree_state(existing_state)
        except Exception:
            logger.error("Failed to apply tree state")

    def parse_inject_code(self, pcode: str) -> p.ProgramNode:
        # TODO - fix poor cohesion here - engine should not deal with ast and pass it to interpreter for injection
        # should MethodModel know about the current instruction - which is where interpreter injects it ??
        # We shold probably move interpreter in here so engine only has this class as interface to method/interpreter
        parser = create_inject_parser(self._uod_command_names)
        return parser.parse_pcode(pcode)

    def get_method_state(self) -> Mdl.MethodState:
        all_nodes = self._program.get_all_nodes()
        method_state = Mdl.MethodState.empty()
        for node in all_nodes:
            if node.completed:
                method_state.executed_line_ids.append(node.id)
            elif node.started:
                method_state.started_line_ids.append(node.id)
            # injected node ids are created as negative integers
            id_int = as_int(node.id)
            if id_int is not None and id_int < 0:
                method_state.injected_line_ids.append(node.id)
        return method_state
