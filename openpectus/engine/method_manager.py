
import logging

from openpectus.lang.exec.analyzer import WhitespaceCheckAnalyzer
from openpectus.lang.exec.errors import MethodEditError
from openpectus.lang.exec.units import as_int
from openpectus.lang.model.parser import (
    ParserMethodLine, ParserMethod, create_inject_parser, create_method_parser
)
import openpectus.lang.model.ast as p
import openpectus.protocol.models as Mdl


logger = logging.getLogger(__name__)


class MethodManager:
    def __init__(self, uod_command_names: list[str]):
        self._uod_command_names = uod_command_names
        self._method = ParserMethod.empty
        self._program = p.ProgramNode.empty()
        self._inject_parser = create_inject_parser(self._uod_command_names)

    def to_model_method(self) -> Mdl.Method:
        return Mdl.Method(lines=[Mdl.MethodLine(id=line.id, content=line.content) for line in self._method.lines])

    @property
    def program(self) -> p.ProgramNode:
        return self._program

    def set_method(self, method: Mdl.Method):
        """ User saved method. The new method just replaces the existing method. Use when
        no run is active. """
        # concurrency check: aggregator performs the version check and aborts on error

        # convert method from protocol api and apply the new method
        _method = ParserMethod(lines=[ParserMethodLine(line.id, line.content) for line in method.lines])
        self._method = _method
        parser = create_method_parser(_method, self._uod_command_names)
        self._program = parser.parse_method(_method)

        self._apply_analysis()

    def merge_method(self, method: Mdl.Method):
        """ User saved method while a run was active. The new method is replacing an existing method
        whose state should be merged over. """
        # concurrency check: aggregator performs the version check and aborts on error

        # validate that the content of the new method does not conflict with the state of the running method
        method_state = self.get_method_state()
        for new_line in method.lines:
            if new_line.id in method_state.executed_line_ids or new_line.id in method_state.started_line_ids:
                cur_line = next((line for line in self._method.lines if line.id == new_line.id))
                if cur_line is not None and cur_line.content != new_line.content:
                    raise MethodEditError(
                        f"The line '{new_line.content}' may not be edited, because it is already started")

        # extract state for existing method
        # existing_state = self._program.extract_tree_state(skip_started_nodes=True)
        existing_state = self._program.extract_tree_state(skip_started_nodes=False)

        # convert method from protocol api and apply the new method
        _method = ParserMethod(lines=[ParserMethodLine(line.id, line.content) for line in method.lines])
        self._method = _method
        parser = create_method_parser(_method, self._uod_command_names)
        self._program = parser.parse_method(_method)

        logger.info("Merging existing ast state into modified method ast")
        logger.debug(f"Existing tree state size: {len(existing_state.keys())}, values:")
        for v in existing_state.values():
            logger.debug(v)

        try:
            self._program.apply_tree_state(existing_state)
            self._program.revision = self._program.revision + 1
            logger.debug(f"Updating method revision to {self._program.revision}")

        except Exception as ex:
            logger.error("Failed to apply tree state", exc_info=True)
            raise MethodEditError("Failed to apply tree state", ex)

        self._apply_analysis()

    def parse_inject_code(self, pcode: str) -> p.ProgramNode:
        return self._inject_parser.parse_pcode(pcode)

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

    def _apply_analysis(self):
        # TODO improve this. may need additional analyzers which also
        # requires access to tags/commands
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(self._program)
