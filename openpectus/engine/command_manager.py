import logging
from typing import Iterator, Set
from queue import Empty, Queue

from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import EngineError
from openpectus.lang.exec.pinterpreter import Tracking
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand
from openpectus.engine.internal_commands import InternalCommandsRegistry, InternalEngineCommand


logger = logging.getLogger(__name__)
frontend_logger = logging.getLogger(__name__ + ".frontend")  # will this work or use that of engine?

priority_command_names = ['Start', 'Stop', 'Unhold', 'Unpause']

class CommandManager():

    def __init__(
            self,
            tracking: Tracking,
            uod: UnitOperationDefinitionBase,
            registry: InternalCommandsRegistry,
            restart_request_pending: CommandRequest | None = None):
        self.tracking = tracking
        self.uod = uod
        self.registry = registry

        self.cmd_queue: Queue[CommandRequest] = Queue()
        """ Commands to execute, coming from interpreter and from aggregator """
        self.cmd_executing: list[CommandRequest] = []
        """ Uod commands currently being excuted """
        self.cmd_executing_done: Set[CommandRequest] = set()
        """ Uod commands completed in current tick """
        self.in_executing_loop = False
        """ Whether the executing tick loop is active. Changes to self.cmd_executing cannot occur in this
        phase but must be scheduled using and then committed with self._commit_commands_done()"""
        self.tick_time: float = 0.0
        self.tick_number: int = -1

        self.restart_request_pending: CommandRequest | None = None
        """ Restart command request to pass to next command manager instance during restart """

        logger.warning(f"CommandManager instance {id(self)} created")
        if restart_request_pending is not None:
            logger.debug("New CommandManager instance, picking up Restart command")
            self.cmd_executing.append(restart_request_pending)

    @property
    def currently_executing(self) -> Iterator[CommandRequest]:
        """ Iterate over cmd_executing but skip commands already marked as done """
        for cmd_request in self.cmd_executing:
            if cmd_request not in self.cmd_executing_done:
                yield cmd_request

    def schedule(self, req: CommandRequest):
        self.cmd_queue.put_nowait(req)

    def _get_command_instance(self, name: str) -> InternalEngineCommand | UodCommand | None:
        cmd = self.registry.get_running_command(name)
        if cmd is not None:
            return cmd
        if self.uod.has_command_instance(name):
            return self.uod.get_command(name)

    def tick(self, tick_time: float, tick_number: int):
        # FIXME: clean up
        self.tick_time = tick_time
        self.tick_number = tick_number
        # run a tick
        if len(self.cmd_executing_done) > 0:
            # Possibly an error rather than a warning. In any case, it is often followed by a duplicate state error
            cmds = ", ".join([str(cmd) for cmd in self.cmd_executing_done])
            logger.warning(f"Executing_done is non-empty. Completed command(s) not comitted: {cmds}")

        # priority 1 - a hign priority command is running
        # - just let it run as is

        # priority 2 - a hign priority command is queued - start it immediately
        # TODO
        queue_items: list[CommandRequest] = list(self.cmd_queue.queue)
        for queue_req in queue_items:
            if queue_req.name in priority_command_names:
                logger.warning("Priority command in queue: " + str(queue_req))
        self.execute_commands()

    def execute_commands(self):
        done = False
        # add command requests from incoming queue to self.cmd_executing
        while self.cmd_queue.qsize() > 0 and not done:
            try:
                engine_command = self.cmd_queue.get()
                # Note: New commands are inserted at the beginning of the list.
                # This allows simpler cancellation of identical/overlapping commands
                self.cmd_executing.insert(0, engine_command)
                logger.debug(f"Queued command {engine_command} moved to executing list")
            except Empty:
                done = True

        # Execute a tick of each running command
        self.cmd_executing_done.clear()
        latest_cmd = "(none)"
        try:
            self.in_executing_loop = True
            for c in self.currently_executing:
                latest_cmd = c.name
                # Note: Executing one command may cause other commands to be cancelled (by identical or overlapping
                # commands) Rather than modify self.cmd_executing (while iterating over it), cancelled/completed
                # commands are added to the cmds_done set.
                self._execute_command(c)
        except ValueError as ve:
            logger.error(f"Error executing command: '{latest_cmd}'. Command failed with error: {ve}", exc_info=True)
            frontend_logger.error(f"Command '{latest_cmd}' failed: {ve}")
            raise
        except Exception:
            logger.error(f"Error executing command: '{latest_cmd}'", exc_info=True)
            frontend_logger.error(f"Error executing command: '{latest_cmd}'")
            raise
        finally:
            self.in_executing_loop = False
            # commit removal of completed commands to self.cmd_executing
            self._commit_commands_done()

    def _execute_command(self, cmd_request: CommandRequest):
        """ Execute a tick of the requested command, creating the command instance if needed """

        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            frontend_logger.error("Cannot execute command with empty name")
            self._executing_command_done(cmd_request)
            return

        try:
            if EngineCommandEnum.has_value(cmd_request.name):
                self._execute_internal_command(cmd_request)
            else:
                self._execute_uod_command(cmd_request)
        except Exception:
            self.tracking.mark_failed(cmd_request)
            logger.error(f"Error running command '{cmd_request.name}'", exc_info=True)
            raise


    def _execute_internal_command(self, cmd_request: CommandRequest):  # noqa C901
        # FIXME: consider how this engine state can be accessed
        # if not self._runstate_started and cmd_request.name not in [EngineCommandEnum.START, EngineCommandEnum.RESTART]:
        #     logger.warning(f"Command '{cmd_request.name}' is invalid when Engine is not running")
        #     self._remove_executing_command_request(cmd_request)
        #     return

        # an existing, long running engine_command is running. other commands must wait
        # Note: we need a priority mechanism - even Stop is waiting here
        # The reason for this is that Pause/Hold block interpreter ticks using
        # engine._runstate_paused and engine._runstate_holding. So interpreter cant
        # schedule more commands
        logger.debug(f"Executing internal command request: {cmd_request}, tick_number {self.tick_number}")
        command = self.registry.get_running_command(cmd_request.name)
        if command is not None:
            if cmd_request.name == command.name:
                if command.is_cancelled():
                    if not command.is_finalized():
                        self._finalize_command(cmd_request, command)
                elif not command.is_finalized():
                    command.tick()
                if command.has_failed():
                    self._executing_command_done(cmd_request)
                    self.tracking.mark_failed(cmd_request)
                    # missing finalize/dispose?
                elif command.is_finalized():
                    self._executing_command_done(cmd_request)
                    self.tracking.mark_completed(cmd_request)
            return

        # no engine command is running - start one
        try:
            command = self.registry.create_internal_command(cmd_request.name, cmd_request.instance_id)
            args = cmd_request.arguments
            if args is not None:
                try:
                    command.validate_arguments(args)
                    logger.debug(f"Initialized command {cmd_request.name} with arguments '{args}'")
                except Exception:
                    raise EngineError(
                        f"Failed to initialize arguments '{args}' for command '{cmd_request.name}'",
                        "same"
                    )
        except ValueError:
            raise EngineError(
                f"Unknown internal engine command '{cmd_request.name}'",
                f"Unknown command '{cmd_request.name}'")

        if command.name == EngineCommandEnum.RESTART:
            self.restart_request_pending = cmd_request

        self.tracking.mark_internal_command_started(command)
        command.tick()
        if command.has_failed():
            self._executing_command_done(cmd_request)
            self.tracking.mark_failed(command)
        elif command.is_finalized():
            self._executing_command_done(cmd_request)
            self.tracking.mark_completed(command)

    def _execute_uod_command(self, cmd_request: CommandRequest):  # noqa C901
        assert self.uod.has_command_name(cmd_request.name), f"Expected Uod to have command named '{cmd_request.name}'"

        # if self._runstate_stopping:
        #     logger.debug(f"Skipping uod command '{cmd_name}', run is restarting")
        #     return

        # if not self.uod.hwl.is_connected:
        #     raise EngineError(
        #         f"The hardware is disconnected. The command '{cmd_name}' was not allowed to start.",
        #         "same")

        logger.debug(f"Executing uod command request: {cmd_request}, tick_number {self.tick_number}")
        # cancel any existing instance with same name
        for c in self.currently_executing:
            if c.name == cmd_request.name and c != cmd_request:
                self._cancel_command(c)
                logger.info(f"Running command request '{c}' cancelled because a new instance was requested '{cmd_request}'")

        # cancel any overlapping instance
        for c in self.currently_executing:
            if c != cmd_request:
                for overlap_list in self.uod.overlapping_command_names_lists:
                    if c.name in overlap_list and cmd_request.name in overlap_list:
                        self._cancel_command(c)
                        logger.info(
                            f"Running command request '{c}' cancelled because overlapping command " +
                            f"'{cmd_request}' was requested")

        # create or get command instance
        if not self.uod.has_command_instance(cmd_request.name):
            uod_command = self.uod.create_command(cmd_request.name, cmd_request.instance_id)
        else:
            uod_command = self.uod.get_command(cmd_request.name)

        assert uod_command is not None, f"Failed to get uod_command for command '{cmd_request.name}'"

        logger.debug(f"Parsing arguments '{cmd_request.arguments}' for uod command {cmd_request.name}")
        parsed_args = uod_command.parse_args(cmd_request.arguments)

        if parsed_args is None:
            logger.error(f"Invalid argument string: '{cmd_request.arguments}' for command '{cmd_request.name}'")
            # TODO possible more: tracking, node, command?
            self._executing_command_done(cmd_request)
            raise ValueError(f"Invalid arguments for command '{cmd_request.name}'")

        # execute command state flow
        try:
            logger.debug(
                f"Executing uod command: '{cmd_request.name}' with parsed args '{parsed_args}', " +
                f"iteration {uod_command._exec_iterations}")
            if uod_command.is_cancelled():
                if not uod_command.is_finalized():
                    self._finalize_command(cmd_request, uod_command)
                return

            if not uod_command.is_initialized():
                uod_command.initialize()
                logger.debug(f"Command {cmd_request.name} initialized")

            if not uod_command.is_execution_started():
                self.tracking.mark_uod_command_started(uod_command)
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command.get_iteration_count()}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed another iteration {uod_command.get_iteration_count()}")

            if uod_command.is_execution_complete() and not uod_command.is_finalized():
                self.tracking.mark_completed(cmd_request)
                self._finalize_command(cmd_request, uod_command)
                logger.debug(f"Command {cmd_request.name} finalized")

        except Exception:
            # handle error locally because we need specific command cleanup
            if not uod_command.is_cancelled():
                self._cancel_command(cmd_request)
                logger.info(f"Cleaned up failed command {cmd_request.name}")

            logger.error(f"Uod command execution failed. Command: '{cmd_request}'", exc_info=True)
            raise

    def _executing_command_done(self, cmd_request: CommandRequest, commit=False):
        if cmd_request in self.cmd_executing:
            self.cmd_executing_done.add(cmd_request)
            logger.debug(f"Command request {cmd_request} marked as done")
        if commit:
            self._commit_commands_done()

    def _commit_commands_done(self):
        assert not self.in_executing_loop
        for cmd_request in self.cmd_executing_done:
            if cmd_request in self.cmd_executing:
                self.cmd_executing.remove(cmd_request)
        self.cmd_executing_done.clear()

    def _cancel_command(self, cmd_request: CommandRequest, finalize=True):
        """ Cancel the command request.

        If finalize is False, the command is cancelled with command.cancel() and tracking, but no clean up is performed.
        This means the command has a few ticks to cancel its work and set its is_execution_complete to True.
        Currently - this is not implemented except when Stop or Restart cancels other commands

        If finalize if True, both cancel() and finalize() is called without delay"""
        try:
            cmd = self._get_command_instance(cmd_request.name)
            if cmd is not None:
                if not cmd.is_execution_complete():
                    cmd.cancel()
                    self.tracking.mark_cancelled(cmd_request)
                else:
                    logger.warning(f"Cannot cancel command {cmd_request} because it is already completed")
                if finalize:
                    self._finalize_command(cmd_request, cmd)
            else:
                # maybe this should not be a warning
                logger.warning(f"Could not cancel command request '{cmd_request}'. No command instance was found")
        except Exception:
            # Note: Consider making this method safer and idempotent. If this error occurs we should do it
            logger.error("An error occurred during command cancellation", exc_info=True)

    def _finalize_command(self, cmd_request: CommandRequest, cmd: InternalEngineCommand | UodCommand):
        if cmd.is_finalized():
            logger.warning(f"Command is already finalized: {cmd_request}")
        try:
            cmd.finalize()
        finally:
            self._executing_command_done(cmd_request)

    def _get_executing_command_request(self, command_name: str) -> CommandRequest | None:
        for cmd_request in self.currently_executing:
            if cmd_request.name == command_name:
                return cmd_request

    def _get_executing_command_request_by_instance(self, instance_id: str) -> CommandRequest | None:
        for cmd_request in self.cmd_executing:
            if cmd_request.instance_id == instance_id:
                return cmd_request
    # ----------
    # API for outside calls. These are
    # - cancel_instruction, force_instruction: called from aggregator in other thread.

    def cancel_instruction(self, instance_id: str):
        assert not self.in_executing_loop
        if not self.tracking.has_instance_id(instance_id):
            raise ValueError(f"Cannot cancel instruction {instance_id=}, no runtime record found")
        else:
            logger.info(f"Cancel instruction {instance_id=} accepted")
            # use instead of tracking self._get_executing_command_request_by_instance(instance_id)
            record = self.tracking.get_record_by_instance_id(instance_id)
            assert record is not None
            command = self.tracking.get_command(instance_id)
            if command is not None:
                cmd_request = self._get_executing_command_request(command.name)
                if cmd_request is not None:
                    self._cancel_command(cmd_request)
                else:
                    # best effort cleanup when request is not available
                    logger.warning(f"Command cancel clean up error. Command '{command.name}' had no cmd request")
                    command.cancel()
                    self.tracking.mark_cancelled(command)
                    if not command.is_finalized():
                        command.finalize()
            else:
                node = self.tracking.get_known_node_by_id(record.node_id)
                assert node is not None
                self.tracking.mark_cancelled(node)
        self._commit_commands_done()

    def force_instruction(self, instance_id: str):
        assert not self.in_executing_loop
        if not self.tracking.has_instance_id(instance_id):
            logger.error(f"Cannot force instruction {instance_id=}, no runtime record found")
        else:
            logger.info(f"Force instruction {instance_id=} accepted")
            record = self.tracking.get_record_by_instance_id(instance_id)
            assert record is not None
            command = self.tracking.get_command(instance_id)
            if command is not None:
                command.force()
                self.tracking.mark_forced(command)
            else:
                node = self.tracking.get_known_node_by_id(record.node_id)
                assert node is not None
                self.tracking.mark_forced(node)
        self._commit_commands_done()

    # ----------
    # API for other commands. These should not commit because they are called while in_executing_loop==True
    #  - cancel_commands, finalize_commands: called from other commands via engine

    def cancel_commands(self, source_command_name: str, finalize=False):
        """ Cancel all commands except the source to prepare for stop/restart """
        reqs = list(self.cmd_executing)
        for cmd_request in reqs:
            if cmd_request.name == source_command_name:
                continue
            self._cancel_command(cmd_request, finalize)

        if finalize:  # warn if we missed some
            cmds_still_running = []
            for name in self.registry.get_running_command_names():
                if name != source_command_name:
                    cmds_still_running.append(name)
            for name, _ in self.uod.command_instances.items():
                cmds_still_running.append(name)
            if any(cmds_still_running):
                logger.error("All commands should be cancelled but these are still not finalized: " +
                             ", ".join(cmds_still_running))

    def finalize_commands(self, source_command_name: str):
        """ Finalize all commands except the source to prepare for stop/restart """
        cmds: list[InternalEngineCommand | UodCommand] = []
        reqs = []
        for cmd_request in self.cmd_executing.copy():
            if cmd_request.name == source_command_name:
                continue
            reqs.append(cmd_request)
            command = self._get_command_instance(cmd_request.name)
            if command is not None:
                cmds.append(command)
        for command in cmds:
            if command is not None and not command.is_finalized():
                command.finalize()
        for cmd_request in reqs:
            self._executing_command_done(cmd_request, commit=True)

        # warn if we missed some
        cmds_still_running = []
        for name in self.registry.get_running_command_names():
            if name != source_command_name:
                cmds_still_running.append(name)
        for name, _ in self.uod.command_instances.items():
            cmds_still_running.append(name)
        if any(cmds_still_running):
            logger.error("All commands should be finalized but these are still not finalized: " +
                         ", ".join(cmds_still_running))
