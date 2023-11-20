from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.messages import RegisterEngineMsg, UodInfoMsg, TagsUpdatedMsg, RunLogMsg, ControlStateMsg, SuccessMessage, ErrorMessage


class MessageHandlers:
    def __init__(self, dispatcher: AggregatorDispatcher):
        dispatcher.set_post_handler(RegisterEngineMsg, self.handle_RegisterEngineMsg)
        dispatcher.set_post_handler(UodInfoMsg, self.handle_UodInfoMsg)
        dispatcher.set_post_handler(TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        dispatcher.set_post_handler(RunLogMsg, self.handle_RunLogMsg)
        dispatcher.set_post_handler(ControlStateMsg, self.handle_ControlStateMsg)

    async def handle_RegisterEngineMsg(self, channel_id: str, register_engine_msg: RegisterEngineMsg) -> SuccessMessage | ErrorMessage:
        """ Registers engine """
        engine_id = Aggregator.create_engine_id(register_engine_msg)
        if channel_id not in self.channel_map.keys():
            logger.error(f"Registration failed for engine_id {engine_id} and channel_id {channel_id}. Channel not found")
            return ErrorMessage(message="Registration failed")

        channel_info = self.channel_map[channel_id]
        if channel_info.engine_id is not None and channel_info.engine_id != engine_id:
            logger.error(
                f"""Registration failed for engine_id {engine_id} and channel_id {channel_id}.
                        Channel already in use by engine_id {channel_info.engine_id}"""
            )
            return ErrorMessage(message="Registration failed")

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - engine_id reused with "same uod" should take over session, else fail as misconfigured client
        # - add machine name + uod secret
        existing_registrations = [x for x in self.channel_map.values() if x.engine_id == engine_id]
        if (
                len(existing_registrations) > 0 and
                any(existing_registration.status != ChannelStatusEnum.Disconnected for
                    existing_registration in existing_registrations)
        ):
            logger.error(
                f"""Registration failed for engine_id {engine_id} and channel_id {channel_id}.
                        Client has other channel"""
            )
            return ErrorMessage(message="Registration failed")

        channel_info.engine_id = engine_id
        channel_info.engine_name = register_engine_msg.computer_name
        channel_info.uod_name = register_engine_msg.uod_name
        channel_info.status = ChannelStatusEnum.Registered
        logger.debug(f"Registration successful of client {engine_id} on channel {channel_id}")

        # initialize client data
        if engine_id not in self.engine_data_map.keys():
            self.engine_data_map[engine_id] = ClientData(engine_id=engine_id)

        return SuccessMessage()

    async def handle_UodInfoMsg(self, channel_id: str, msg: UodInfoMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        client_data.readings = []
        for r in msg.readings:
            rd = ReadingDef(
                label=r.label,
                tag_name=r.tag_name,
                valid_value_units=r.valid_value_units,
                commands=[ReadingCommand(name=c.name, command=c.command) for c in r.commands]
            )
            client_data.readings.append(rd)

        return SuccessMessage()

    async def handle_TagsUpdatedMsg(self, channel_id: str, msg: TagsUpdatedMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got tags update from client: {str(msg)}")
        for ti in msg.tags:
            client_data.tags_info.upsert(ti.name, ti.value, ti.value_unit)
        return SuccessMessage()

    async def handle_RunLogMsg(self, channel_id: str, msg: RunLogMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.runlog = msg
        return SuccessMessage()

    async def handle_ControlStateMsg(self, channel_id: str, msg: ControlStateMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.control_state = msg
        return SuccessMessage()
