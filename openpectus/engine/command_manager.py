from __future__ import annotations
import logging
from typing import Callable
from uuid import UUID

from openpectus.engine.internal_commands import create_internal_command, get_running_internal_command
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import EngineError
from openpectus.lang.exec.runlog import RuntimeInfo, RuntimeRecord
from openpectus.lang.exec.tags import TagCollection, TagValueCollection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase


logger = logging.getLogger(__name__)
frontend_logger = logging.getLogger(__name__ + ".frontend")

TagsAccessor = Callable[[], TagCollection]
RuntimeInfoAccessor = Callable[[], RuntimeInfo]

# TODO:
# If we're going to add command_manager, we should also move this here from engine:
# - executing cmd requests, currently engine.cmd_executing
# - engine._cancel_command_exec_ids
# - engine.execute_commands should only do two things:
#   - move cmds from cmd_queue to manager
#   - call manager.execute_tick() that handles everything else

class CommandManager:
    """ Runs commands and manages their life-time states"""
    def __init__(self, runtimeinfo_accessor: RuntimeInfoAccessor, tags_accessor: TagsAccessor,
                 uod: UnitOperationDefinitionBase) -> None:
        self.runtimeinfo_accessor = runtimeinfo_accessor
        self.tags_accessor = tags_accessor
        self.uod = uod

    def tags_as_readonly(self) -> TagValueCollection:
        return self.tags_accessor().as_readonly()

    @property
    def runtimeinfo(self) -> RuntimeInfo:
        return self.runtimeinfo_accessor()

    def execute_command(self, cmd_request: CommandRequest, cmds_done: set[CommandRequest],
                        executing: list[CommandRequest], cancel_command_exec_ids: set[UUID],
                        tick_time: float, tick_number: int, runstate_started: bool):
        """ Execute a tick of the requested command and update cmds_done. """
        logger.debug("Executing command: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            # Note - could be cleaner to just raise
            frontend_logger.error("Cannot execute command with empty name")
            cmds_done.add(cmd_request)
            return

        if EngineCommandEnum.has_value(cmd_request.name):
            self._execute_internal_command(cmd_request, cmds_done, tick_time, tick_number, runstate_started)
        else:
            self._execute_uod_command(cmd_request, executing, cmds_done, cancel_command_exec_ids, tick_time, tick_number)

    def _execute_internal_command(self, cmd_request: CommandRequest, cmds_done: set[CommandRequest],
                                  tick_time: float, tick_number: int, runstate_started: bool):

        if not runstate_started and cmd_request.name not in [EngineCommandEnum.START, EngineCommandEnum.RESTART]:
            logger.warning(f"Command {cmd_request.name} is invalid when Engine is not running")
            cmds_done.add(cmd_request)
            return

        # get the runtime record to use for tracking if possible
        record = RuntimeRecord.null_record()
        if cmd_request.exec_id is not None:
            # record is None for all commands not originating from interpreter
            # record is None during restart
            # should not be None otherwise
            record = self.runtimeinfo.get_exec_record(cmd_request.exec_id)

        # an existing, long running engine_command is running. other commands must wait
        # Note: we could use a priority mechanism - even Stop is waiting here. Maybe just allow Stop to bypass
        # the wait
        command = get_running_internal_command()
        if command is not None:
            if cmd_request.name == command.name:
                if not command.is_finalized():
                    command.tick()
                if command.has_failed():
                    cmds_done.add(cmd_request)
                    if record is not None:
                        record.add_state_failed(tick_time, tick_number, self.tags_as_readonly())
                    else:
                        logger.error(f"Failed to record failed state for command {cmd_request}")
                elif command.is_finalized():
                    cmds_done.add(cmd_request)
                    if record is not None:
                        record.add_state_completed(tick_time, tick_number, self.tags_as_readonly())
                    else:
                        logger.error(f"Failed to record completed state for command {cmd_request}")
            return

        # no engine command is running - start one
        try:
            command = create_internal_command(cmd_request.name)
            args = cmd_request.get_args()
            if args is not None:
                try:
                    command.init_args(args)
                    logger.debug(f"Initialized command {cmd_request.name} with arguments {args}")
                except Exception:
                    raise EngineError(
                        f"Failed to initialize arguments '{args}' for command '{cmd_request.name}'",
                        "same"
                    )
            else:
                logger.debug(f"Skip init step for command {cmd_request.name} with arguments None")

        except ValueError:
            raise EngineError(
                f"Unknown internal engine command '{cmd_request.name}'",
                f"Unknown command '{cmd_request.name}'")

        if record is not None:
            record.add_state_started(tick_time, tick_number, self.tags_as_readonly())
            command.tick()
            if command.has_failed():
                record.add_state_failed(tick_time, tick_number, self.tags_as_readonly())
                cmds_done.add(cmd_request)
            elif command.is_finalized():
                record.add_state_completed(tick_time, tick_number, self.tags_as_readonly())
                cmds_done.add(cmd_request)
        else:
            logger.error(f"Runtime record is None for command {cmd_request}, this should not occur")


    def _execute_uod_command(self, cmd_request: CommandRequest, executing: list[CommandRequest],
                             cmds_done: set[CommandRequest], cancel_command_exec_ids: set[UUID],
                             tick_time: float, tick_number: int):
        """ Execute a tick of the command and update completed commands """

        cmd_name = cmd_request.name
        assert self.uod.has_command_name(cmd_name), f"Expected Uod to have command named '{cmd_name}'"
        assert cmd_request.exec_id is not None, f"Expected uod command request '{cmd_name}' to have exec_id"

        if not self.uod.hwl.is_connected:
            raise EngineError(
                f"The hardware is disconnected. The command '{cmd_name}' was not allowed to start.",
                "same")

        cancel_this = False

        # cancel any pending cancels (per user request)
        for c in executing:
            if c.command_exec_id in cancel_command_exec_ids:
                cmds_done.add(c)
                cancel_command_exec_ids.remove(c.command_exec_id)
                if c.name == cmd_name:
                    cancel_this = True
                cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                if cmd_record is not None:
                    command, c_record = cmd_record
                    command.cancel()
                    c_record.add_command_state_cancelled(
                        c.command_exec_id, tick_time, tick_number, self.tags_as_readonly())
                    logger.info(f"Running command {c.name} cancelled per user request")
                else:
                    logger.error(f"Cannot cancel command {c}. No runtime record found with {c.exec_id=}" +
                                 f" and {c.command_exec_id=}")
        # if cmd_request.command_exec_id in cancel_command_exec_ids:
        #     cancel_command_exec_ids.remove(cmd_request.command_exec_id)
        #     cancel_this = True

        # cancel any existing instance with same name
        for c in [_c for _c in executing if _c not in cmds_done]:
            if c.name == cmd_name and not c == cmd_request:
                cmds_done.add(c)
                assert c.command_exec_id is not None, f"command_exec_id should be set for command '{cmd_name}'"
                cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                assert cmd_record is not None
                command, c_record = cmd_record
                command.cancel()
                c_record.add_command_state_cancelled(
                    c.command_exec_id, tick_time, tick_number, self.tags_as_readonly())
                logger.debug(f"Running command {c.name} cancelled because another was started")

        # cancel any overlapping instance
        for c in [_c for _c in executing if _c not in cmds_done]:
            if not c == cmd_request:
                for overlap_list in self.uod.overlapping_command_names_lists:
                    if c.name in overlap_list and cmd_name in overlap_list:
                        cmds_done.add(c)
                        assert c.command_exec_id is not None, f"command_exec_id should be set for command '{c.name}'"
                        cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                        assert cmd_record is not None
                        command, c_record = cmd_record
                        command.cancel()
                        c_record.add_command_state_cancelled(
                            c.command_exec_id, tick_time, tick_number, self.tags_as_readonly())
                        logger.info(
                            f"Running command {c.name} cancelled because overlapping command " +
                            f"'{cmd_name}' was started")
                        break

        if cancel_this:
            # don't start command again that was just cancelled
            return

        record = self.runtimeinfo.get_exec_record(cmd_request.exec_id)
        if record is None:
            logger.error(f"Failed to get record for command {cmd_request}")
            return

        # create or get command instance
        if not self.uod.has_command_instance(cmd_name):
            uod_command = self.uod.create_command(cmd_name)
            cmd_request.command_exec_id = record.add_state_uod_command_set(
                uod_command, tick_time, tick_number, self.tags_as_readonly())
        else:
            uod_command = self.uod.get_command(cmd_name)

        assert uod_command is not None, f"Failed to get uod_command for command '{cmd_name}'"

        logger.debug(f"Parsing arguments '{cmd_request.unparsed_args}' for uod command {cmd_name}")
        parsed_args = uod_command.parse_args(cmd_request.unparsed_args or "")

        if parsed_args is None:
            logger.error(f"Invalid argument string: '{cmd_request.unparsed_args}' for command '{cmd_name}'")
            cmds_done.add(cmd_request)
            raise ValueError(f"Invalid arguments for command '{cmd_name}'")

        # execute command state flow
        try:
            logger.debug(
                f"Executing uod command: '{cmd_request.name}' with parsed args '{parsed_args}', " +
                f"iteration {uod_command._exec_iterations}")
            if uod_command.is_cancelled():
                if not uod_command.is_finalized():
                    cmds_done.add(cmd_request)
                    uod_command.finalize()

            if not uod_command.is_initialized():
                uod_command.initialize()
                logger.debug(f"Command {cmd_request.name} initialized")

            if not uod_command.is_execution_started():
                assert cmd_request.command_exec_id is not None
                record.add_command_state_started(
                    cmd_request.command_exec_id,
                    tick_time, tick_number,
                    self.tags_as_readonly())
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command._exec_iterations}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed another iteration {uod_command._exec_iterations}")

            if uod_command.is_execution_complete() and not uod_command.is_finalized():
                assert cmd_request.command_exec_id is not None
                record.add_command_state_completed(
                    cmd_request.command_exec_id, tick_time, tick_number, self.tags_as_readonly())
                cmds_done.add(cmd_request)
                uod_command.finalize()
                logger.debug(f"Command {cmd_request.name} finalized")

        except Exception as ex:
            if cmd_request in executing:
                cmds_done.add(cmd_request)
            assert cmd_request.command_exec_id is not None
            record.add_command_state_failed(
                cmd_request.command_exec_id, tick_time, tick_number, self.tags_as_readonly())
            cmd_record = self.runtimeinfo.get_uod_command_and_record(cmd_request.command_exec_id)
            if cmd_record is not None:
                assert cmd_record[1].exec_id == record.exec_id
                command = cmd_record[0]
                if command is not None and not command.is_cancelled():
                    command.cancel()
                    logger.info(f"Cleaned up failed command {cmd_name}")

            logger.error(
                f"Uod command execution failed. Command: '{cmd_request.name}', " +
                f"argument string: '{cmd_request.unparsed_args}'", exc_info=True)
            raise ex
