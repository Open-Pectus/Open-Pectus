
from datetime import datetime, timezone
import logging
from typing import Any, Callable

from openpectus.lang.exec.analyzer import WhitespaceCheckAnalyzer
from openpectus.lang.exec.errors import MethodEditError
from openpectus.lang.exec.hotswap import HotSwapVisitor
from openpectus.lang.exec.interpreter_models import InterpreterState, InterruptState
from openpectus.lang.exec.pinterpreter import InterpreterContext, PInterpreter
from openpectus.lang.exec.runlog import RuntimeInfo
from openpectus.lang.exec.units import as_int
from openpectus.lang.exec.visitor import VisitResult
from openpectus.lang.model.parser import (
    ParserMethodLine, ParserMethod, create_inject_parser, create_method_parser
)
import openpectus.lang.model.ast as p
import openpectus.protocol.models as Mdl


logger = logging.getLogger(__name__)

InterpreterResetHandler = Callable[[PInterpreter], None]


class MethodManager:
    def __init__(self, uod_command_names: list[str], interpreter_context: InterpreterContext,
                 interpreter_reset_handler: InterpreterResetHandler):
        self._uod_command_names = uod_command_names
        self._interpreter_context = interpreter_context
        self._method = ParserMethod.empty()
        self._program = p.ProgramNode()
        self._inject_parser = create_inject_parser(self._uod_command_names)
        # set handler before the initial creation so we get the event right away
        self._interpreter_reset_handler = interpreter_reset_handler
        self._interpreter: PInterpreter = self._create_interpreter(self._program)

    def _create_interpreter(self, program: p.ProgramNode, raise_change_event=True) -> PInterpreter:
        tracking_was_enabled = False
        if hasattr(self, "_interpreter"):
            tracking_was_enabled = self._interpreter.tracking.enabled if self._interpreter is not None else False
        interpreter = PInterpreter(program, self._interpreter_context, RuntimeInfo(), tracking_was_enabled)
        if raise_change_event:
            self._interpreter_reset_handler(interpreter)
        return interpreter

    def _create_interpreter_from_state(self, state: InterpreterState, raise_change_event=True) -> PInterpreter:
        logger.debug(f"Creating new interpreter from state, method version: {state.method.version}")
        
        self._method = state.method
        parser = create_method_parser(self._method, self._uod_command_names)
        self._program = parser.parse_method(self._method)

        self._apply_analysis(self._program)

        instance = self._create_interpreter(self.program, raise_change_event=raise_change_event)

        # Apply the state to all nodes. In case of merge, the state has been patched by the hotswap visitor.
        logger.debug("Applying program state")
        try:
            instance._program.apply_tree_state(state.tree_state)
        except ValueError as ex:
            logger.error(f"Failed to apply state to nodes. This indicates an error in state.tree_state. Ex:{ex}")
            raise

        logger.debug("Applying interpreter state")

        logger.debug(f"Applying interrupt state ({len(state.interrupt_states)})")
        for interrupt_state in state.interrupt_states:
            node = instance._program.get_child_by_id(interrupt_state.node_id)
            if node is None:
                logger.error(f"Interrupt for node_id {interrupt_state.node_id} cannot be recreated. Node was not found")
                continue
            # interrupt_state.sep - what to do?
            if not isinstance(node, p.NodeWithChildren):
                logger.error(f"Interrupt for node_id {interrupt_state.node_id} cannot be recreated." +
                             f" Node has invalid type: {type(node)}")
                continue
            instance._register_interrupt(node, warn_if_exists=False)

        logger.debug(f"Applying macro state ({len(state.macros_registered)})")
        for node_id in state.macros_registered:
            node = instance._program.get_child_by_id(node_id)
            if node is None:
                logger.error(f"Macro for node_id {node_id} cannot be registered. Node was not found")
                continue
            if not isinstance(node, p.MacroNode):
                logger.error(f"Macro with node_id {node_id} cannot be registered." +
                             f" Node has invalid type: {type(node)}")
                continue
            instance._register_macro(node, warn_if_exists=False)

        logger.debug("Completed applying state")
        return instance

    def _get_interpreter_state(self) -> InterpreterState:
        if self.program is None:
            raise ValueError("Program has not been set")
        if self._method is None:
            raise ValueError("Program has not been set")
        
        return InterpreterState(
            export_date=datetime.now(timezone.utc),
            method=self._method.clone(),
            tree_state=self.program.extract_tree_state(),
            main_sep=self.interpreter.sep.clone(),
            interrupt_states=[InterruptState(intr.node.id) for intr in self.interpreter.interrupts],
            macros_registered=[node.id for node in self.program.macros.values()]
        )

    def _create_interpreter_merge_state(self, new_method: ParserMethod) -> InterpreterState:
        assert self._method is not None
        assert self._program is not None
        method = self._method
        program = self.program
        state = self._get_interpreter_state()
        new_program = self._parse(new_method)

        if new_program.revision == 0:
            new_program.revision = program.revision + 1
            logger.debug(f"New method has no version specified, using {new_program.revision} " +
                         "which is the old version incremented by 1")

        if new_program.has_error():
            logger.warning("Target merge method has parse errors")

#         # check method state preconditions: started or completed lines may not be edited
#         # possibly add idle status here
#         method_state = self._get_method_state(program)
#         for new_line in new_method.lines:
#             if new_line.id in method_state.executed_line_ids or new_line.id in method_state.started_line_ids:
#                 cur_line = next((line for line in method.lines if line.id == new_line.id), None)
#                 if cur_line is not None and cur_line.content != new_line.content:
#                     raise MethodEditError(f"""
# Line with id '{new_line.id}' may not be edited, because it has already started
# Original line: '{cur_line.content}'
# Edited line:   '{new_line.content}'
# """)
        self._validate_liveedit_method(new_method)

        logger.debug("Applying hotswap visitor to create merged state")
        swapper = HotSwapVisitor(old_program=program, old_state=state)
        main_generator = swapper.run(new_program)
        while True:
            try:
                main_result = next(main_generator)
                if main_result == VisitResult.IteratorExhausted:
                    break
            except StopIteration:
                # logger.debug("Main generator is exhausted")
                break

        # stich the new state together from values we know and values the swapper knows
        new_state = InterpreterState(
            export_date=datetime.now(timezone.utc),
            method=new_method,
            tree_state=swapper.new_state.tree_state,
            main_sep=swapper.new_state.main_sep,
            interrupt_states=swapper.new_state.interrupt_states,
            macros_registered=swapper.new_state.macros_registered,
        )

        return new_state

    def _to_parser_method(self, method: Mdl.Method) -> ParserMethod:
        return ParserMethod(lines=[ParserMethodLine(line.id, line.content) for line in method.lines])

    def _parse(self, _method: ParserMethod) -> p.ProgramNode:
        parser = create_method_parser(_method, self._uod_command_names)
        return parser.parse_method(_method)

    @property
    def interpreter(self) -> PInterpreter:
        return self._interpreter

    @property
    def program(self) -> p.ProgramNode:
        return self._program

    @property
    def program_is_started(self) -> bool:
        """ Determine whether the method is started, i.e. the first non-ProgramNode has started executing. """
        return self._program.started

    def set_method(self, method: Mdl.Method):
        """ User saved method. The new method just replaces the existing method. Use when
        no run is active. """
        # concurrency check: aggregator performs the version check and aborts on error

        # convert method from protocol api and apply the new method
        assert not self.program_is_started, "Program has already started, use merge_method() instead of set_method()"
        
        self._method = self._to_parser_method(method)
        self._program = self._parse(self._method)

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
        new_method = self._to_parser_method(_new_method)
        new_program = self._parse(new_method)
        try:
            merge_state = self._create_interpreter_merge_state(new_method)
        except MethodEditError:
            logger.error("merge_method failed")
            raise
        except Exception as ex:
            logger.error("merge_method failed", exc_info=True)
            raise MethodEditError(f"Merging the new method failed: Ex: {ex}") from ex

        interpreter = self._create_interpreter_from_state(merge_state, raise_change_event=False)

        # finally commit the "transaction"
        self._interpreter = interpreter
        self._method = new_method
        self._program = new_program

        # and notify that interpreter was renewed
        self._interpreter_reset_handler(interpreter)


    def _validate_liveedit_method(self, new_method: ParserMethod):
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
        
        new_program = self._parse(new_method)

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

        # TODO: some of the below may still be relevant

        # # more validation and action history cleanup
        # assert old_program.active_node is not None, "Active node is None. This should not occur during method merge"
        # assert not isinstance(old_program.active_node, p.ProgramNode)
        # target_node_id: str = old_program.active_node.id
        # target_node = new_program.get_child_by_id(target_node_id, include_self=True)
        # if target_node is None:
        #     logger.error(f"Edit aborted because the active node, id {target_node_id} was not found in updated method")
        #     raise MethodEditError(f"Edit aborted. The active instruction '{old_program.active_node.instruction_name}' " +
        #                           f"on line {old_program.active_node.position.line} was deleted from the method.")
        # logger.info(f"Active node, source: {old_program.active_node}, target: {target_node}")
        # if target_node.completed:
        #     logger.error(f"Internal error. Target node {target_node} is already completed")
        #     raise Exception(f"Internal error. Target node {target_node} is already completed")
        
        # corrections: dict[str, dict[str, Any]] = {}

        # # allow a started node that awaits its threshold to be changed to anything but clear history to start over
        # # clearing history will disable importing state from source
        # if self.interpreter._is_awaiting_threshold(old_program.active_node):
        #     logger.debug("Source active node is awaiting threshold - clearing its history to start over")
        #     if target_node.id not in corrections.keys():
        #         corrections[target_node.id] = {}
        #     corrections[target_node.id]['action_history'] = []

        # for old_node in self._program.get_all_nodes():
        #     # allow any whitespace node to be changed, but clear its history to start over
        #     if isinstance(old_node, p.WhitespaceNode):
        #         node = new_program.get_child_by_id(old_node.id, include_self=True)
        #         assert node is not None
        #         if node.id not in corrections.keys():
        #             corrections[node.id] = {}
        #         corrections[node.id]['action_history'] = []
        #         logger.debug(f"Clear history of target node {node} because its source was whitespace")

        #     # allow a failed node to be modified but clear its history
        #     if old_node.failed:
        #         logger.debug(f"Clear history for source node {old_node} that is a failed instruction")
        #         if old_node.id not in corrections.keys():
        #             corrections[old_node.id] = {}
        #         corrections[old_node.id]['action_history'] = []
        #         corrections[old_node.id]['started'] = False
        #         corrections[old_node.id]['completed'] = False
        #         corrections[old_node.id]['failed'] = False

        # debug_enabled = True  # logger.isEnabledFor(logging.DEBUG)
        # logger.debug("Applying corrections to extracted state")
        # corrected_state = existing_state.copy()
        # for node_id, value_dict in corrections.items():
        #     if node_id in corrected_state.keys():
        #         for key in value_dict.keys():
        #             if key in corrected_state[node_id].keys():
        #                 logger.debug(f"Correcting state for node {node_id}, property '{key}'; changing value " +
        #                              f"'{corrected_state[node_id][key]}' to '{value_dict[key]}'")
        #                 corrected_state[node_id][key] = value_dict[key]
        #             else:
        #                 logger.debug(f"Correcting state for node {node_id}, adding property '{key}' with value " +
        #                              f"'{value_dict[key]}'")
        #                 corrected_state[node_id][key] = value_dict[key]
        #     else:
        #         pass  # we don't need to add state for additional nodes

        # logger.debug("Merging corrected method state into modified method")
        # try:
        #     new_program.apply_tree_state(corrected_state)
        #     new_program.revision = old_program.revision + 1
        #     logger.debug(f"Updating method revision from {old_program.revision} to {new_program.revision}")

        #     if debug_enabled:
        #         print(f"\n----- Old method, rev {old_program.revision}: -----\n{old_method.as_numbered_pcode()}\n")
        #         print(f"\n----- New method, rev {new_program.revision}: -----\n{_new_method.as_numbered_pcode()}\n")
        #         debug_state = {
        #             "old export state": existing_state,
        #             "corrected_old_state": corrected_state,
        #             "new_patched_state": new_program.extract_tree_state()
        #         }
        #         out = self._serialize(debug_state)
        #         logger.debug("Tree debugging state:\n\n" + out + "\n")

        # except Exception as ex:
        #     logger.error("Failed to apply tree state", exc_info=True)
        #     debug_state = {
        #         "old export state": existing_state,
        #         "corrected_old_state": corrected_state,
        #         "new_patched_state": new_program.extract_tree_state()
        #     }
        #     out = self._serialize(debug_state)
        #     logger.debug("Tree debugging state:\n\n" + out + "\n")
        #     raise MethodEditError("Failed to apply tree state to updated method") from ex

        # return _new_method, new_program


    def parse_inject_code(self, pcode: str) -> p.ProgramNode:
        return self._inject_parser.parse_pcode(pcode)

    def get_method_state(self) -> Mdl.MethodState:
        return self._get_method_state(self._program)

    def _get_method_state(self, program: p.ProgramNode) -> Mdl.MethodState:
        all_nodes = program.get_all_nodes()
        method_state = Mdl.MethodState.empty()
        for node in all_nodes:
            if node.failed:
                method_state.failed_line_ids.append(node.id)
            elif node.completed:
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
