import logging
import time
import unittest
import multiprocessing
import asyncio
import asyncua
from openpectus.engine.hardware import Register, RegisterDirection, HardwareLayerException
from openpectus.engine.opcua_hardware import OPCUA_Hardware, OPCUA_Types

logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
logger = logging.getLogger("openpectus.engine.opcua_hardware.OPCUA_Hardware")
logger.setLevel(logging.DEBUG)

opcua_host = "opc.tcp://127.0.0.1:48401/"


async def opcua_test_server_task(registers: list[Register],
                                 callback_output_queue: multiprocessing.Queue,
                                 stop_event: multiprocessing.Event,
                                 is_started_event: multiprocessing.Event):
    post_write_callback_queue = multiprocessing.Queue()
    server = asyncua.Server()
    await server.init()
    server.set_endpoint(opcua_host)
    server.set_server_name("Open Pectus OPC-UA Test Server")
    server.set_security_policy([asyncua.ua.SecurityPolicyType.NoSecurity,])
    uri = "https://github.com/Open-Pectus/Open-Pectus/"

    idx = await server.register_namespace(uri)
    objects = server.nodes.objects

    for r in registers:
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

    while not post_write_callback_queue.empty():
        write_value = post_write_callback_queue.get()
        node = server.get_node(write_value.NodeId)
        node_path_list = await node.get_path(as_string=True)
        # ["0:Root", "0:Objects", 2:"node_name"] -> "Objects/2:node_name"
        node_path = "/".join(node_path_list[1:])[2:]
        tag_value = write_value.Value.Value.Value
        callback_output_queue.put((node_path, tag_value,))


def sync_opcua_test_server_task(*args, **kwargs):
    asyncio.run(opcua_test_server_task(*args, **kwargs))


class OPCUATestServer():
    """ Context manager which launches OPC-UA test server. """
    def __init__(self, registers=None):
        self.callback_output_queue = multiprocessing.Queue()
        self.server_write_events = []
        self.registers = []
        if registers:
            self.registers = registers

    def __enter__(self):
        self.stop_event = multiprocessing.Event()  # Signal to OPC-UA test server that it should stop
        self.is_started_event = multiprocessing.Event()  # Signal from OPC-UA test server that it has started
        self.process = multiprocessing.Process(target=sync_opcua_test_server_task,
                                               args=(self.registers,
                                                     self.callback_output_queue,
                                                     self.stop_event,
                                                     self.is_started_event)
                                               )
        self.process.start()
        # Block until OPC-UA server is started
        while not self.is_started_event.is_set():
            time.sleep(0.1)

    def __exit__(self, type, value, traceback):
        self.stop_event.set()
        self.process.join()
        # Gather queue before closing the process to avoid corruption
        while not self.callback_output_queue.empty():
            self.server_write_events.append(self.callback_output_queue.get())
        self.process.close()


class TestOPCUAHardware(unittest.TestCase):
    def test_can_connect(self):
        test_server = OPCUATestServer()
        with test_server:
            hwl = OPCUA_Hardware(host=opcua_host)
            try:
                hwl.connect()
                hwl.disconnect()
            except HardwareLayerException:
                self.fail()

    def test_reconnect(self):
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = [
            FT01
        ]

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers

        # Connect and read
        with OPCUATestServer(registers=registers):
            hwl.connect()
            self.assertEqual(0.0, hwl.read(FT01))
        # Sever connection to server and read again
        with self.assertRaises(HardwareLayerException):
            hwl.read(FT01)
        # Re-onnect and read
        with OPCUATestServer(registers=registers), hwl:
            self.assertEqual(0.0, hwl.read(FT01))

    def test_connection_left_connected_does_not_hang(self):
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = [
            FT01
        ]
        test_server = OPCUATestServer(registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers
        with test_server:
            hwl.connect()  # Connection is opened but not closed subsequently

    def test_can_read_register(self):
        FT01 = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01")
        registers = [
            FT01
        ]
        test_server = OPCUATestServer(registers=registers)

        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        with test_server, hwl:
            self.assertEqual(0.0, hwl.read(FT01))

    def test_can_write_register(self):
        PU01 = Register("PU01", RegisterDirection.Both, path="Objects/2:PU01", safe_value=0.0)
        registers = [
            PU01
        ]
        test_server = OPCUATestServer(registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers
        with test_server, hwl:
            hwl.write(10.2, PU01)
        self.assertIn((PU01.options["path"], 10.2,), test_server.server_write_events)

    def test_can_read_multiple_registers(self):
        registers = [Register(f"{i:02d}", RegisterDirection.Read, path=f"Objects/2:readable_{i:02d}") for i in range(100)]
        test_server = OPCUATestServer(registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers
        with test_server, hwl:
            values = hwl.read_batch(registers)
            for value in values:
                self.assertEqual(0.0, value)

    def test_can_write_multiple_registers(self):
        registers = [Register(f"{i:02d}",
                     RegisterDirection.Both,
                     path=f"Objects/2:writable_{i:02d}",
                     safe_value=0.0) for i in range(100)]
        test_server = OPCUATestServer(registers=registers)
        values_to_write = [float(i) for i in range(len(registers))]

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers
        with test_server, hwl:
            hwl.write_batch(values_to_write, registers)
        for register, value_to_write in zip(registers, values_to_write):
            self.assertIn((register.options["path"], value_to_write,), test_server.server_write_events)

    def test_does_help_user_fix_path_typo(self):
        FT01_totalizer_1_total_with_typo = Register("FT01",
                                                    RegisterDirection.Read,
                                                    path="Objects/2:FT01/2:Totalizer/2:Totaal 1")
        FT01_totalizer_1_total_proper = Register("FT01",
                                                 RegisterDirection.Read,
                                                 path="Objects/2:FT01/2:Totalizer/2:Total 1")
        test_server = OPCUATestServer(registers=[FT01_totalizer_1_total_proper])

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = [FT01_totalizer_1_total_with_typo]
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException) as context:
                hwl.read(FT01_totalizer_1_total_with_typo)
            self.assertIn("Objects/2:FT01/2:Totalizer/2:Totaal 1 cannot be found", str(context.exception))

    def test_can_read_write_registers_with_type(self):
        OPCUA_Types
        bool_register = Register("Bool",
                                 RegisterDirection.Both,
                                 path="Objects/2:Boolean value",
                                 type=OPCUA_Types.Boolean,
                                 safe_value=False)
        float_register = Register("Float",
                                  RegisterDirection.Both,
                                  path="Objects/2:Float value",
                                  type=OPCUA_Types.Float,
                                  safe_value=0.0)
        uint16_register = Register("Uint16",
                                   RegisterDirection.Both,
                                   path="Objects/2:Uint16 value",
                                   type=OPCUA_Types.UInt16,
                                   safe_value=0)
        registers = [
            bool_register,
            float_register,
            uint16_register,
        ]
        test_server = OPCUATestServer(registers=registers)

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = registers

        with test_server, hwl:
            hwl.write_batch([1, 1, 1], registers)
            values = hwl.read_batch(registers)

        self.assertIn((bool_register.options["path"], True), test_server.server_write_events)
        self.assertIn((float_register.options["path"], 1.0), test_server.server_write_events)
        self.assertIn((uint16_register.options["path"], 1), test_server.server_write_events)
        self.assertEqual(values, [True, 1.0, 1,])

    def test_illegal_register_type_is_detected(self):
        FT01_type_not_ok = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01", type=bool)
        FT01_type_ok = Register("FT01", RegisterDirection.Read, path="Objects/2:FT01", type=OPCUA_Types.Boolean)
        test_server = OPCUATestServer(registers=[FT01_type_ok])

        hwl = OPCUA_Hardware(host=opcua_host)
        hwl.registers = [FT01_type_not_ok]
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException):
                hwl.read(FT01_type_not_ok)


if __name__ == "__main__":
    unittest.main()
