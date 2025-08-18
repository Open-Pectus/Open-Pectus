import logging
import unittest
import threading
import queue
import asyncio
import asyncua
import asyncua.ua
import asyncua.common.callback
from typing import Any, Dict
import os
from openpectus.engine.hardware import Register, RegisterDirection, HardwareLayerException
from openpectus.engine.opcua_hardware import OPCUA_Hardware, OPCUA_Types

logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
logger = logging.getLogger("openpectus.engine.opcua_hardware.OPCUA_Hardware")
logger.setLevel(logging.DEBUG)

opcua_host = "opc.tcp://127.0.0.1:484{:02d}"


async def opcua_test_server_task(port_suffix: int,
                                 registers: Dict[str, Register],
                                 callback_output_queue,
                                 stop_event,
                                 is_started_event,
                                 is_finished_event) -> None:
    post_write_callback_queue = queue.Queue()
    server = asyncua.Server()
    await server.init()
    server.set_endpoint(opcua_host.format(port_suffix))
    server.set_server_name("Open Pectus OPC-UA Test Server")
    server.set_security_policy([asyncua.ua.SecurityPolicyType.NoSecurity,])
    uri = "https://github.com/Open-Pectus/Open-Pectus/"

    idx = await server.register_namespace(uri)
    objects = server.nodes.objects

    for r in registers.values():
        # Objects/2:parent_node/2:node_name -> ["Objects", "2:parent_node", "2:node_name"]
        breadcrumbs = r.options["path"].split("/")
        # ["Objects", "2:parent_node", "2:node_name"] -> ["2:parent_node",]
        objects_prior_to_variable = breadcrumbs[1:-1]
        obj = objects
        if objects_prior_to_variable:
            for part in objects_prior_to_variable:
                idx, name = part.split(":")
                obj = await obj.add_object(int(idx), name)
        idx, name = breadcrumbs[-1].split(":")
        node = await obj.add_variable(int(idx),
                                      name,
                                      0.0 if "type" not in r.options else
                                      asyncua.ua.Variant([], r.options["type"])
                                      )
        if RegisterDirection.Write in r.direction:
            await node.set_writable()

    await server.start()

    def post_write_callback(event, dispatcher):
        for write_value in event.request_params.NodesToWrite:
            post_write_callback_queue.put(write_value)
    server.subscribe_server_callback(asyncua.common.callback.CallbackType.PostWrite, post_write_callback)

    while not stop_event.is_set():
        await asyncio.sleep(0.1)
        if not is_started_event.is_set():
            is_started_event.set()
    server.unsubscribe_server_callback(asyncua.common.callback.CallbackType.PostWrite, post_write_callback)

    while not post_write_callback_queue.empty():
        write_value = post_write_callback_queue.get()
        node = server.get_node(write_value.NodeId)
        node_path_list = await node.get_path(as_string=True)
        # ["0:Root", "0:Objects", 2:"node_name"] -> "Objects/2:node_name"
        node_path = "/".join(node_path_list[1:])[2:]
        tag_value = write_value.Value.Value.Value
        callback_output_queue.put((node_path, tag_value,))
    await server.stop()
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    is_finished_event.set()


def sync_opcua_test_server_task(*args, **kwargs):
    asyncio.run(opcua_test_server_task(*args, **kwargs))


class OPCUATestServer():
    """ Context manager which launches OPC-UA test server. """
    def __init__(self, port_suffix: int = 0, registers=None):
        self.port_suffix = port_suffix
        self.callback_output_queue = queue.Queue()
        self.server_write_events: list[tuple[str, Any]] = []
        self.registers = dict()
        if registers:
            self.registers = registers

    def __enter__(self):
        self.stop_event = threading.Event()  # Signal to OPC-UA test server that it should stop
        self.is_started_event = threading.Event()  # Signal from OPC-UA test server that it has started
        self.is_finished_event = threading.Event()  # Signal from OPC-UA test server that it has finished
        self.process = threading.Thread(
            target=sync_opcua_test_server_task,
            args=(
                self.port_suffix,
                self.registers,
                self.callback_output_queue,
                self.stop_event,
                self.is_started_event,
                self.is_finished_event,
            ),
            daemon=True
        )
        self.process.start()
        # Block until OPC-UA server is started
        self.is_started_event.wait()

    def __exit__(self, type, value, traceback):
        self.stop_event.set()
        self.is_finished_event.wait()
        # Gather queue before closing the process to avoid corruption
        while not self.callback_output_queue.empty():
            self.server_write_events.append(self.callback_output_queue.get())
        self.process.join(timeout=2)


@unittest.skipIf(bool(os.environ.get("OPENPECTUS_ENGINE_SKIP_SLOW_TESTS")), reason="Skipping slow tests as configured")
class TestOPCUAHardware(unittest.TestCase):
    def test_can_connect(self):
        port_suffix = 0
        test_server = OPCUATestServer(port_suffix)
        with test_server:
            hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
            try:
                hwl.connect()
                hwl.disconnect()
            except HardwareLayerException:
                self.fail()

    def test_reconnect(self):
        port_suffix = 1
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = {"FT01": FT01}

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers

        # Connect and read
        with OPCUATestServer(port_suffix, registers=registers):
            hwl.connect()
            self.assertEqual(0.0, hwl.read(FT01))
        # Sever connection to server and read again
        with self.assertRaises(HardwareLayerException):
            hwl.read(FT01)
        # Re-onnect and read
        with OPCUATestServer(port_suffix, registers=registers), hwl:
            self.assertEqual(0.0, hwl.read(FT01))

    def test_connection_left_connected_does_not_hang(self):
        port_suffix = 2
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = {"FT01": FT01}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server:
            hwl.connect()  # Connection is opened but not closed subsequently

    def test_can_read_register(self):
        port_suffix = 3
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = {"FT01": FT01}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            self.assertEqual(0.0, hwl.read(FT01))

    def test_can_write_register(self):
        port_suffix = 4
        PU01 = Register("PU01", RegisterDirection.Both, path="Objects/2:PU01")
        registers = {"PU01": PU01}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            hwl.write(10.2, PU01)
        self.assertIn((PU01.options["path"], 10.2,), test_server.server_write_events)

    def test_can_read_multiple_registers(self):
        port_suffix = 5
        registers = {f"Readable {i:02d}": Register(f"{i:02d}",
                                                   RegisterDirection.Read,
                                                   path=f"Objects/2:readable_{i:02d}") for i in range(100)}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            values = hwl.read_batch(list(registers.values()))
            for value in values:
                self.assertEqual(0.0, value)

    def test_can_write_multiple_registers(self):
        port_suffix = 6
        registers = {f"Writable {i:02d}": Register(f"{i:02d}",
                     RegisterDirection.Both,
                     path=f"Objects/2:writable_{i:02d}") for i in range(100)}
        test_server = OPCUATestServer(port_suffix, registers=registers)
        values_to_write = [float(i) for i in range(len(registers))]

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            hwl.write_batch(values_to_write, list(registers.values()))
        for register, value_to_write in zip(registers.values(), values_to_write):
            self.assertIn((register.options["path"], value_to_write,), test_server.server_write_events)

    def test_does_help_user_fix_path_typo(self):
        port_suffix = 7
        FT01_totalizer_1_total_with_typo = Register("FT01",
                                                    RegisterDirection.Read,
                                                    path="Objects/2:FT01/2:Totalizer/2:Totaal 1")
        FT01_totalizer_1_total_proper = Register("FT01",
                                                 RegisterDirection.Read,
                                                 path="Objects/2:FT01/2:Totalizer/2:Total 1")
        test_server = OPCUATestServer(port_suffix, registers={"FT01": FT01_totalizer_1_total_proper})

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = {"FT01": FT01_totalizer_1_total_with_typo}
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException) as context:
                hwl.read(FT01_totalizer_1_total_with_typo)
            self.assertIn("Objects/2:FT01/2:Totalizer/2:Totaal 1 cannot be found", str(context.exception))

    def test_can_read_write_registers_with_type(self):
        port_suffix = 8
        bool_register = Register("Bool",
                                 RegisterDirection.Both,
                                 path="Objects/2:Boolean value",
                                 type=OPCUA_Types.Boolean)
        float_register = Register("Float",
                                  RegisterDirection.Both,
                                  path="Objects/2:Float value",
                                  type=OPCUA_Types.Float)
        uint16_register = Register("Uint16",
                                   RegisterDirection.Both,
                                   path="Objects/2:Uint16 value",
                                   type=OPCUA_Types.UInt16)
        registers = {
            "Bool": bool_register,
            "Float": float_register,
            "Uint16": uint16_register,
        }
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers

        with test_server, hwl:
            hwl.write_batch([1, 1, 1], list(registers.values()))
            values = hwl.read_batch(list(registers.values()))

        self.assertIn((bool_register.options["path"], True), test_server.server_write_events)
        self.assertIn((float_register.options["path"], 1.0), test_server.server_write_events)
        self.assertIn((uint16_register.options["path"], 1), test_server.server_write_events)
        self.assertEqual(values, [True, 1.0, 1,])

    def test_illegal_register_type_is_detected(self):
        port_suffix = 9
        FT01_type_not_ok = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01", type=bool)
        FT01_type_ok = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01", type=OPCUA_Types.Boolean)
        test_server = OPCUATestServer(port_suffix, registers={"FT01": FT01_type_ok})

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = {"FT01": FT01_type_not_ok}
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException):
                hwl.validate_offline()

    def test_type_disparity_is_detected(self):
        port_suffix = 10
        bool_register = Register("Bool",
                                 RegisterDirection.Both,
                                 path="Objects/2:Boolean value",
                                 type=OPCUA_Types.Boolean)
        registers = {
            "Bool": bool_register,
        }
        test_server = OPCUATestServer(port_suffix, registers=registers)

        bool_register = Register("Bool",
                                 RegisterDirection.Both,
                                 path="Objects/2:Boolean value",
                                 type=OPCUA_Types.Float)
        registers = {
            "Bool": bool_register,
        }
        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException):
                hwl.validate_online()

    def test_type_is_inferred(self):
        port_suffix = 11
        uint_register = Register("UInt",
                                 RegisterDirection.Both,
                                 path="Objects/2:Uint value",
                                 type=OPCUA_Types.UInt16)
        registers = {
            "Uint": uint_register,
        }
        test_server = OPCUATestServer(port_suffix, registers=registers)

        uint_register = Register("Uint",
                                 RegisterDirection.Both,
                                 path="Objects/2:Uint value")
        registers = {
            "Uint": uint_register,
        }
        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        values_to_write = [1]
        with test_server, hwl:
            hwl.validate_online()
            hwl.write(1, uint_register)
            hwl.write_batch(values_to_write, list(registers.values()))

    def test_access_level_disparity_is_detected(self):
        port_suffix = 12
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = {"FT01": FT01}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        FT01 = Register("FT01", RegisterDirection.Write, path="Objects/2:FT01")
        registers = {"FT01": FT01}
        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException):
                hwl.validate_online()

    def test_exception_when_attempting_to_access_using_disconnected_client(self):
        port_suffix = 13
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = {"FT01": FT01}
        test_server = OPCUATestServer(port_suffix, registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host.format(port_suffix))
        hwl._registers = registers
        with test_server:
            hwl.connect()
            hwl.read(FT01)
            hwl.disconnect()
            with self.assertRaises(HardwareLayerException) as context:
                hwl.read(FT01)
            self.assertIn("OPC-UA client is closed.", str(context.exception))


def attempt_to_use_hardware():
    registers = {r.name: r for r in
                 [
                    Register("Readable",
                             RegisterDirection.Read,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:Readable",
                             type=OPCUA_Types.Float),
                    Register("Writable",
                             RegisterDirection.Write,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:Writable",
                             type=OPCUA_Types.Float),
                    Register("ReadableAndWritable",
                             RegisterDirection.Both,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:ReadableAndWritable",
                             type=OPCUA_Types.Float),
                    Register("Bool",
                             RegisterDirection.Both,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:UserDataType/4:Bool",
                             type=OPCUA_Types.Boolean),
                    Register("Float",
                             RegisterDirection.Both,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:UserDataType/4:Float",
                             type=OPCUA_Types.Float),
                    Register("Int",
                             RegisterDirection.Both,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:UserDataType/4:Int",
                             type=OPCUA_Types.Int16),
                    Register("Uint",
                             RegisterDirection.Both,
                             path="Objects/3:ServerInterfaces/4:OPCUA/4:UserDataType/4:Uint",
                             type=OPCUA_Types.UInt16),
                 ]
                 }

    hwl = OPCUA_Hardware(host="opc.tcp://192.168.0.1:4840/")
    hwl._registers = registers
    hwl.validate_offline()
    with hwl:
        hwl.validate_online()
        for r in [r for r in hwl.registers.values() if RegisterDirection.Read in r.direction]:
            print(r, hwl.read(r))
        hwl.write(-5.0, registers["Writable"])
        hwl.write(-6.0, registers["ReadableAndWritable"])
        hwl.write(5, registers["Bool"])
        hwl.write(1.02, registers["Float"])
        hwl.write(-54000, registers["Int"])
        hwl.write(-54, registers["Uint"])


if __name__ == "__main__":
    unittest.main()
