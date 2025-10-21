
import logging
from typing import Callable, Iterator, Set
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
            tracking_accessor: Callable[[], Tracking],
            uod: UnitOperationDefinitionBase,
            registry: InternalCommandsRegistry):
        self._tracking_accessor = tracking_accessor
        self.uod = uod
        self.registry = registry

        self.cmd_queue: Queue[CommandRequest] = Queue()
        """ Commands to execute, coming from interpreter and from aggregator """
        self.cmd_executing: list[CommandRequest] = []
        """ Uod commands currently being excuted """
        self.cmd_executing_done: Set[CommandRequest] = set()
        """ Uod commands completed in current tick """

    @property
    def tracking(self) -> Tracking:
        # until we know how lifetimes should work, we just resolve tracking on every call
        instance = self._tracking_accessor()
        return instance

    @property
    def currently_executing(self) -> Iterator[CommandRequest]:
        """ Iterate over cmd_executing but skip commands already marked as done """
        for cmd_request in self.cmd_executing:
            if cmd_request not in self.cmd_executing_done:
                yield cmd_request

    def schedule(self, req: CommandRequest):
        self.cmd_queue.put_nowait(req)

    def get_command_instance(self, name: str) -> InternalEngineCommand | UodCommand | None:
        cmd = self.registry.get_running_internal_command()
        if cmd is not None and cmd.name == name:
            return cmd
        if self.uod.has_command_instance(name):
            return self.uod.get_command(name)

    def tick(self):
        # run a tick
        self.cmd_executing_done.clear()
        
        # highest priority - a hign priority command is running - let it and only it run
        for cmd_request in self.currently_executing:
            if cmd_request.name in priority_command_names:
                logger.info(f"Priority command '{cmd_request.name}' running")
                self._execute_command(cmd_request)
                # cmd = self.get_command_instance(cmd_request.name)
                # if cmd is not None:
                    
                #     #self.tick_command(cmd)                    
                # else:
                #     logger.error(f"Failed to get priority command '{cmd_request.name}")
                #     self._remove_executing_command_request(cmd_request)
                #     return

        # high priority - a hign priority command is queued - start it and let only it run
        # TODO

        # in high prio cases above, when do we finalize commands already running?
        queue_items: list[CommandRequest] = list(self.cmd_queue.queue)
        queue_item_names = [cmd.name for cmd in queue_items]
        for priority_cmd in priority_command_names:
            if priority_cmd in queue_item_names:
                logger.warning("Priority command in queue: " + priority_cmd)
                # how about other running commands? Do they get any chance to clean up?
                # We should at least (cancel? and) finalize them.
                #return
        # If queue has a priority command (Stop, Unpause or Unhold), that one is started and gets the tick
        # Else, if a command is already running it get's a tick
        # Else, a command is picked from the front of the queue and that is started and gets a tick
        has_ticked_command = False
        # for executing in self.cmd_executing:
        #     if executing.
        self.execute_commands()

    # def tick_command(self, cmd_request: CommandRequest, cmd: InternalEngineCommand | UodCommand):
    #     assert cmd_request.name == cmd.name
    #     assert cmd_request.instance_id == cmd.instance_id
    #     if isinstance(cmd, InternalEngineCommand):
    #         cmd.tick()
    #     elif isinstance(cmd, UodCommand):
    #     # execute uod command state flow
    #         try:
    #             logger.debug(
    #                 f"Executing uod command: '{cmd_request.name}' with parsed args '{parsed_args}', " +
    #                 f"iteration {cmd._exec_iterations}")
    #             if cmd.is_cancelled():
    #                 if not cmd.is_finalized():
    #                     self._remove_executing_command_request(cmd_request)
    #                     cmd.finalize()

    #             if not cmd.is_initialized():
    #                 cmd.initialize()
    #                 logger.debug(f"Command {cmd_request.name} initialized")

    #             if not cmd.is_execution_started():
    #                 self.tracking.mark_uod_command_started(cmd)
    #                 cmd.execute(parsed_args)
    #                 logger.debug(f"Command {cmd_request.name} executed first iteration {cmd._exec_iterations}")
    #             elif not cmd.is_execution_complete():
    #                 cmd.execute(parsed_args)
    #                 logger.debug(f"Command {cmd_request.name} executed another iteration {cmd._exec_iterations}")

    #             if cmd.is_execution_complete() and not cmd.is_finalized():
    #                 self.tracking.mark_completed(cmd_request)
    #                 self._remove_executing_command_request(cmd_request)
    #                 cmd.finalize()
    #                 logger.debug(f"Command {cmd_request.name} finalized")

    #         except Exception:
    #             # handle error locally because we need specific command cleanup
    #             if not cmd.is_cancelled():
    #                 cmd.cancel()
    #                 self.tracking.mark_cancelled(cmd)

    #                 logger.info(f"Cleaned up failed command {cmd.name}")

    #             logger.error(f"Uod command execution failed. Command: '{cmd.name}'", exc_info=True)
    #             raise

    def execute_commands(self):
        done = False
        # add command requests from incoming queue to self.cmd_executing
        while self.cmd_queue.qsize() > 0 and not done:
            try:
                engine_command = self.cmd_queue.get()
                # Note: New commands are inserted at the beginning of the list.
                # This allows simpler cancellation of identical/overlapping commands
                self.cmd_executing.insert(0, engine_command)
            except Empty:
                done = True

        # Execute a tick of each running command
        self.cmd_executing_done.clear()
        latest_cmd = "(none)"
        try:
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
            for c_done in self.cmd_executing_done:
                self.cmd_executing.remove(c_done)

    def _execute_command(self, cmd_request: CommandRequest):
        """ Execute a tick of the requested command, creating the command instance if needed """

        # validate
        logger.debug("Executing command: " + cmd_request.name)
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
        # if not self._runstate_started and cmd_request.name not in [EngineCommandEnum.START, EngineCommandEnum.RESTART]:
        #     logger.warning(f"Command '{cmd_request.name}' is invalid when Engine is not running")
        #     self._remove_executing_command_request(cmd_request)
        #     return

        # an existing, long running engine_command is running. other commands must wait
        # Note: we need a priority mechanism - even Stop is waiting here
        command = self.registry.get_running_internal_command()
        if command is not None:
            if cmd_request.name == command.name:
                if command.is_cancelled():
                    if not command.is_finalized():
                        command.finalize()
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

        self.tracking.mark_internal_command_started(command)
        command.tick()
        if command.has_failed():
            self.tracking.mark_failed(command)
            self._executing_command_done(cmd_request)
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

        # cancel any existing instance with same name
        for c in self.currently_executing:
            if c.name == cmd_request.name and c != cmd_request:
                self._cancel_command(c)
                logger.debug(f"Running command request '{c}' cancelled because a new instance was requested '{cmd_request}'")

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
            self._executing_command_done(cmd_request)
            raise ValueError(f"Invalid arguments for command '{cmd_request.name}'")

        # execute command state flow
        try:
            logger.debug(
                f"Executing uod command: '{cmd_request.name}' with parsed args '{parsed_args}', " +
                f"iteration {uod_command._exec_iterations}")
            if uod_command.is_cancelled():
                if not uod_command.is_finalized():
                    self._executing_command_done(cmd_request)
                    uod_command.finalize()

            if not uod_command.is_initialized():
                uod_command.initialize()
                logger.debug(f"Command {cmd_request.name} initialized")

            if not uod_command.is_execution_started():
                self.tracking.mark_uod_command_started(uod_command)
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command._exec_iterations}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed another iteration {uod_command._exec_iterations}")

            if uod_command.is_execution_complete() and not uod_command.is_finalized():
                self.tracking.mark_completed(cmd_request)
                self._executing_command_done(cmd_request)
                uod_command.finalize()
                logger.debug(f"Command {cmd_request.name} finalized")

        except Exception:
            # handle error locally because we need specific command cleanup
            if not uod_command.is_cancelled():
                self._cancel_command(cmd_request)
                logger.info(f"Cleaned up failed command {cmd_request.name}")

            logger.error(f"Uod command execution failed. Command: '{cmd_request}'", exc_info=True)
            raise

    def _executing_command_done(self, cmd_request: CommandRequest):
        if cmd_request in self.cmd_executing:
            self.cmd_executing_done.add(cmd_request)

    def _cancel_command(self, cmd_request: CommandRequest):
        self._executing_command_done(cmd_request)
        cmd = self.get_command_instance(cmd_request.name)
        if cmd is not None:
            cmd.cancel()
            self.tracking.mark_cancelled(cmd_request)
            if not cmd.is_finalized():
                cmd.finalize()
        else:
            # maybe this should not be a warning
            logger.warning(f"Could not cancel command request '{cmd_request}'. No command instance was found")

    # API for outside calls. These are
    # - cancel_uod_commands, finalize_uod_commands: called from other commands
    # - cancel_instruction, force_instruction: called from aggregator in other thread

    def cancel_instruction(self, instance_id: str):
        if not self.tracking.has_instance_id(instance_id):
            raise ValueError(f"Cannot cancel instruction {instance_id=}, no runtime record found")
        else:
            logger.info(f"Cancel instruction {instance_id=} accepted")
            record = self.tracking.get_record_by_instance_id(instance_id)
            assert record is not None
            command = self.tracking.get_command(instance_id)
            if command is not None:
                command.cancel()
                command.finalize()
                self.tracking.mark_cancelled(command)
                self.tracking.mark_completed(command)
                cmd_request = next((r for r in self.cmd_executing if r.name == command.name), None)
                if cmd_request is not None:
                    self._executing_command_done(cmd_request)
            else:
                node = self.tracking.get_known_node_by_id(record.node_id)
                assert node is not None
                self.tracking.mark_cancelled(node)

    def force_instruction(self, instance_id: str):
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

    # API for commands
    def cancel_uod_commands(self):
        """ Cancel all uod commands to prepare for stop/restart """
        logger.debug("Cancelling all uod commands")
        cmds_to_cancel: list[UodCommand] = []
        for name, command in self.uod.command_instances.items():
            if command.is_cancelled() or command.is_execution_complete() or command.is_finalized():
                logger.debug(f"Skipping command '{name}' that is no longer running")
            else:
                cmds_to_cancel.append(command)

        # call outside the loop because cancel modifies the collection
        for command in cmds_to_cancel:
            command.cancel()
            self.tracking.mark_cancelled(command)

        if any(cmds_to_cancel):
            cmd_names = ",".join([c.name for c in cmds_to_cancel])
            logger.debug(f"Cancelled {len(cmds_to_cancel)} uod commands: {cmd_names}")

    def finalize_uod_commands(self):
        """ Finalize all uod commands to prepare for stop/restart """
        logger.debug("Finalizing uod commands")
        cmds_to_finalize: list[UodCommand] = []
        for command in self.uod.command_instances.values():
            if not command.is_finalized():
                cmds_to_finalize.append(command)

        # call outside the loop because finalize modifies the collection
        for command in cmds_to_finalize:
            command.finalize()
            # remove command request
            for cmd_request in self.cmd_executing.copy():
                if cmd_request.name == command.name:
                    self._executing_command_done(cmd_request)
