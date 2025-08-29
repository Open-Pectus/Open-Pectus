
import logging

from openpectus.lang.exec.analyzer import WhitespaceCheckAnalyzer
from openpectus.lang.exec.errors import MethodEditError
from openpectus.lang.exec.pinterpreter import InterpreterContext, PInterpreter
from openpectus.lang.exec.units import as_int
from openpectus.lang.model.parser import (
    ParserMethodLine, ParserMethod, create_inject_parser, create_method_parser
)
import openpectus.lang.model.ast as p
import openpectus.protocol.models as Mdl


logger = logging.getLogger(__name__)


class MethodManager:
    def __init__(self, uod_command_names: list[str], interpreter_context: InterpreterContext):
        self._uod_command_names = uod_command_names
        self._interpreter_context = interpreter_context
        self._method = ParserMethod.empty
        self._program = p.ProgramNode.empty()
        self._inject_parser = create_inject_parser(self._uod_command_names)
        self._interpreter: PInterpreter = self._create_interpreter(self._program)

    def _create_interpreter(self, program: p.ProgramNode) -> PInterpreter:
        return PInterpreter(program, self._interpreter_context)

    @property
    def interpreter(self) -> PInterpreter:
        return self._interpreter

    @property
    def program(self) -> p.ProgramNode:
        return self._program

    @property
    def program_is_started(self) -> bool:
        """ Determine whether the method is started, i.e. the first non-ProgramNode has started executing. """
        return self._program.active_node is not None

    def set_method(self, method: Mdl.Method):
        """ User saved method. The new method just replaces the existing method. Use when
        no run is active. """
        # concurrency check: aggregator performs the version check and aborts on error

        # convert method from protocol api and apply the new method
        assert not self.program_is_started, "Program has already started, use merge_method() instead of set_method()"
        _method = ParserMethod(lines=[ParserMethodLine(line.id, line.content) for line in method.lines])
        self._method = _method
        parser = create_method_parser(_method, self._uod_command_names)
        self._program = parser.parse_method(_method)

        self._apply_analysis(self._program)
        self._interpreter = self._create_interpreter(self._program)

    def reset_interpreter(self):
        # re-parse the method to reset all runtime state. self._program.reset_runtime_state() is not sufficient
        # because some nodes maintain some state to support method merge
        parser = create_method_parser(self._method, self._uod_command_names)
        self._program = parser.parse_method(self._method)
        self._apply_analysis(self._program)
        self._interpreter = self._create_interpreter(self._program)

    def merge_method(self, _new_method: Mdl.Method):
        assert self.program_is_started, "Program has not yet started, use set_method() rather that merge_method()"
        try:
            new_method, new_program = self._merge_method(_new_method)
        except MethodEditError:
            logger.error("merge_method failed")
            raise
        except Exception as ex:
            logger.error("merge_method failed", exc_info=True)
            raise MethodEditError(f"Merging the new method failed: Ex: {ex}", ex)

        self._apply_analysis(new_program)

        try:
            # create new interpreter instance with the new method and whose
            # state is fast-forwarded to the same instruction as before
            interpreter = self.interpreter.with_edited_program(new_program)
        except MethodEditError:
            logger.error("Preparing new interpreter failed", exc_info=True)
            raise
        except Exception as ex:
            logger.error("Preparing new interpreter failed", exc_info=True)
            raise MethodEditError(f"Preparing new interpreter failed: Ex: {ex}", ex)

        # finally commit the "transaction"
        self._interpreter = interpreter
        self._method = new_method
        self._program = new_program

    def _merge_method(self, new_method: Mdl.Method) -> tuple[ParserMethod, p.ProgramNode]:  # noqa C901
        """ User saved method while a run was active. The new method is replacing an existing method
        whose state should be merged over. """
        # concurrency check: aggregator performs the version check and aborts on error

        old_method = self._method
        old_program = self._program

        # validate that the content of the new method does not conflict with the state of the running method
        # this state is based off of Node.started and Node.completed. It does not consider Node.action_history
        method_state = self._get_method_state(old_program)
        for new_line in new_method.lines:
            if new_line.id in method_state.executed_line_ids or new_line.id in method_state.started_line_ids:
                cur_line = next((line for line in old_method.lines if line.id == new_line.id), None)
                if cur_line is not None and cur_line.content != new_line.content:
                    raise MethodEditError(
                        f"The line '{new_line.content}' with id {new_line.id} may not be edited, because it " +
                        "has already started")

        # extract state for existing method
        existing_state = old_program.extract_tree_state()

        # convert new method from protocol api and parse it
        _new_method = ParserMethod(lines=[ParserMethodLine(line.id, line.content) for line in new_method.lines])

        parser = create_method_parser(_new_method, self._uod_command_names)
        new_program = parser.parse_method(_new_method)

        # validate that macros that have started executing are not modified
        for old_macro_node in old_program.macros.values():
            if old_macro_node.run_started_count > 0:
                new_macro_node = new_program.get_child_by_id(old_macro_node.id)
                if new_macro_node is None:
                    raise MethodEditError(
                        f"The macro '{old_macro_node.name}' that has already started executing may not be deleted.")
                elif not isinstance(new_macro_node, p.MacroNode):
                    raise MethodEditError(
                        f"The macro '{old_macro_node.name}' that has already started executing has been changed " +
                        "to another instruction type. This is not allowed. ")
                else:
                    if not old_macro_node.matches_source(new_macro_node, logger):
                        raise MethodEditError(
                            f"The macro '{old_macro_node.name}' has already started executing may not be modified")

        # more validation and action history cleanup
        assert old_program.active_node is not None, "Active node is None. This should not occur during method merge"
        assert not isinstance(old_program.active_node, p.ProgramNode)
        target_node_id: str = old_program.active_node.id
        target_node = new_program.get_child_by_id(target_node_id, include_self=True)
        if target_node is None:
            logger.error(f"Edit aborted because the active node, id {target_node_id} was not found in updated method")
            raise MethodEditError(f"Edit aborted. The active instruction '{old_program.active_node.instruction_name}' " +
                                  f"on line {old_program.active_node.position.line} was deleted from the method.")
        logger.info(f"Active node, source: {old_program.active_node}, target: {target_node}")
        if target_node.completed:
            logger.error(f"Internal error. Target node {target_node} is already completed")
            raise Exception(f"Internal error. Target node {target_node} is already completed")

        # allow a started node that awaits its threshold to be changed to anything but clear history to start over
        # clearing history will disable importing state from source
        if self.interpreter._is_awaiting_threshold(old_program.active_node):
            logger.debug("Source active node is awaiting threshold - clearing its history to start over")
            target_node.action_history.clear()
        # allow any whitespace node to be changed, but clear its history to start over
        for old_node in self._program.get_all_nodes():
            if isinstance(old_node, p.WhitespaceNode):
                node = new_program.get_child_by_id(old_node.id, include_self=True)
                if node is not None:
                    logger.debug(f"Clearing history of target node {node} because its source was whitespace")
                    node.action_history.clear()

        debug_enabled = True  # logger.isEnabledFor(logging.DEBUG)
        logger.info("Merging existing method state into modified method")
        try:
            new_program.apply_tree_state(existing_state)
            new_program.revision = old_program.revision + 1
            logger.debug(f"Updating method revision from {old_program.revision} to {new_program.revision}")

            if debug_enabled:
                print(f"\n----- Old method, rev {old_program.revision}: -----\n{old_method.as_pcode_w_id()}\n")
                print(f"\n----- New method, rev {new_program.revision}: -----\n{_new_method.as_pcode_w_id()}\n")
                debug_state = {
                    "old export state": existing_state,
                    "new_patched_state": new_program.extract_tree_state()
                }
                out = self._serialize(debug_state)
                logger.debug("Tree debugging state:\n\n" + out + "\n")

        except Exception as ex:
            logger.error("Failed to apply tree state", exc_info=True)
            debug_state = {
                "old export state": existing_state,
                "new_patched_state": new_program.extract_tree_state()
            }
            out = self._serialize(debug_state)
            logger.debug("Tree debugging state:\n\n" + out + "\n")
            raise MethodEditError("Failed to apply tree state to updated method", ex)

        return _new_method, new_program

    def parse_inject_code(self, pcode: str) -> p.ProgramNode:
        return self._inject_parser.parse_pcode(pcode)

    def get_method_state(self) -> Mdl.MethodState:
        return self._get_method_state(self._program)

    def _get_method_state(self, program: p.ProgramNode) -> Mdl.MethodState:
        all_nodes = program.get_all_nodes()
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

    def _apply_analysis(self, program: p.ProgramNode):
        # TODO improve this. may need additional analyzers which also
        # require access to tags/commands
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)

    def _serialize(self, obj) -> str:
        """ Serialize data for debugging """
        import json
        from collections import abc

        def serialize_dict_values(obj):
            if isinstance(obj, abc.ValuesView):
                return list(obj)
            raise TypeError("Type %s is not serializable" % type(obj))

        return json.dumps(obj, default=serialize_dict_values)
