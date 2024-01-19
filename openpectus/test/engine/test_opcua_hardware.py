import logging
import time
import unittest
import multiprocessing
import contextlib
from openpectus.engine.hardware import Register, RegisterDirection, HardwareLayerException
from openpectus.engine.opcua_hardware import OPCUA_Hardware, OPCUA_Types

logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
logger = logging.getLogger("openpectus.engine.opcua_hardware.OPCUA_Hardware")
logger.setLevel(logging.DEBUG)


import asyncio, asyncua

async def opcua_test_server_task(
    registers: list[Register],
    callback_output_queue: multiprocessing.Queue,
    stop_event: multiprocessing.Event,
    is_started_event: multiprocessing.Event
    ):
    modify_callback_queue = multiprocessing.Queue()
    server = asyncua.Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:48401/")
    server.set_server_name("Open Pectus OPC-UA Test Server")
    server.set_security_policy(
        [
            asyncua.ua.SecurityPolicyType.NoSecurity,
        ]
    )
    uri = "https://github.com/Open-Pectus/Open-Pectus/"
    idx = await server.register_namespace(uri)
    objects = server.nodes.objects
    
    for r in registers:
        # Objects/2:parent_node/2:node_name -> [2:parent_node,]
        objects_prior_to_variable = r.options["path"].split("/")[1:-1]
        obj = objects
        if objects_prior_to_variable:
            for part in objects_prior_to_variable:
                idx, name = part.split(":")
                idx = int(idx)
                obj = await obj.add_object(idx, name)
        idx, name = r.options["path"].split("/")[-1].split(":")
        idx = int(idx)
        if 'type' in r.options:
            node = await obj.add_variable(idx, name, asyncua.ua.Variant([], r.options["type"]))
        else:
            node = await obj.add_variable(idx, name, 0.0)
        if RegisterDirection.Write in r.direction:
            await node.set_writable()
    
    await server.start()
    
    def opcua_modify_callback(event, dispatcher):
        for write_value in event.request_params.NodesToWrite:
            modify_callback_queue.put(write_value)
    server.subscribe_server_callback(asyncua.common.callback.CallbackType.PostWrite, opcua_modify_callback)
    
    while not stop_event.is_set():
        await asyncio.sleep(0.1)
        if not is_started_event.is_set():
            is_started_event.set()
    
    while not modify_callback_queue.empty():
        write_value = modify_callback_queue.get()
        node = server.get_node(write_value.NodeId)
        node_path_list = await node.get_path(as_string=True)
        # ['0:Root', '0:Objects', 2:'node_name'] -> Objects/2:node_name
        node_path = "/".join(node_path_list[1:])[2:]
        tag_value = write_value.Value.Value.Value
        callback_output_queue.put((node_path, tag_value,))

def sync_opcua_test_server_task(
    registers: list[Register],
    callback_output_queue: multiprocessing.Queue,
    stop_event: multiprocessing.Event,
    is_started_event: multiprocessing.Event
    ):
    asyncio.run(opcua_test_server_task(registers, callback_output_queue, stop_event, is_started_event))

class OPCUATestServer():
    def __init__(self, registers=None):
        self.callback_output_queue = multiprocessing.Queue()
        self.server_write_events = []
        self.registers = []
        if registers:
            self.registers = registers
    def __enter__(self):
        self.stop_event = multiprocessing.Event()
        self.is_started_event = multiprocessing.Event()
        self.process = multiprocessing.Process(target=sync_opcua_test_server_task, args=(self.registers, self.callback_output_queue, self.stop_event, self.is_started_event))
        self.process.start()
        while not self.is_started_event.is_set():
            time.sleep(0.1)
    def __exit__(self, type, value, traceback):
        self.stop_event.set()
        self.process.join()
        while not self.callback_output_queue.empty():
            self.server_write_events.append(self.callback_output_queue.get())
        self.process.close()

class TestOPCUAHardware(unittest.TestCase):
    def test_can_connect(self):
        test_server = OPCUATestServer()
        with test_server:
            hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
            try:
                hwl.connect()
                hwl.disconnect()
            except HardwareLayerException:
                self.fail()

    def test_can_read_register(self):
        FT01 = Register("FT01", RegisterDirection.Both, path="Objects/2:FT01")
        registers = [
            FT01
        ]
        test_server = OPCUATestServer(registers=registers)
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        with test_server, hwl:
            self.assertEqual(0.0, hwl.read(FT01))
    
    def test_can_write_register(self):
        PU01 = Register("PU01", RegisterDirection.Both, path="Objects/2:PU01")
        registers = [
            PU01
        ]
        test_server = OPCUATestServer(registers=registers)
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        with test_server, hwl:
            hwl.write(10.2, PU01)
        self.assertIn((PU01.options["path"], 10.2,), test_server.server_write_events)
    def test_can_read_multiple_registers(self):
        registers = [Register(f"{i:02d}", RegisterDirection.Read, path=f"Objects/2:readable_{i:02d}") for i in range(100)]
        test_server = OPCUATestServer(registers=registers)
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        with test_server, hwl:
            values = hwl.read_batch(registers)
            for value in values:
                self.assertEqual(0.0, value)
    
    def test_can_write_multiple_registers(self):
        registers = [Register(f"{i:02d}", RegisterDirection.Both, path=f"Objects/2:writable_{i:02d}") for i in range(100)]
        test_server = OPCUATestServer(registers=registers)
        values_to_write = [float(i) for i in range(len(registers))]
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        with test_server,hwl:
            values = hwl.write_batch(values_to_write, registers)
        for register, value_to_write in zip(registers, values_to_write):
            self.assertIn((register.options["path"], value_to_write,), test_server.server_write_events)
    
    def test_does_help_user_fix_path_typo(self):
        FT01_totalizer_1_total_with_typo = Register("FT01", RegisterDirection.Both, path="Objects/2:FT01/2:Totalizer/2:Totaal 1")
        FT01_totalizer_1_total_proper = Register("FT01", RegisterDirection.Both, path="Objects/2:FT01/2:Totalizer/2:Total 1")
        test_server = OPCUATestServer(registers=[FT01_totalizer_1_total_proper])
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = [FT01_totalizer_1_total_with_typo]
        with test_server, hwl:
            with self.assertRaises(HardwareLayerException) as context:
                hwl.read(FT01_totalizer_1_total_with_typo)
            self.assertTrue("Node at register Register(name=FT01) path Objects/2:FT01/2:Totalizer/2:Totaal 1 cannot be found. The closest parent node is 'Objects/2:FT01/2:Totalizer/2:Totaal 1' with children: 2:Total 1" in str(context.exception))
    
    def test_can_read_write_registers_with_type(self):
        OPCUA_Types
        bool_register = Register("Bool", RegisterDirection.Both, path="Objects/2:Boolean value", type=OPCUA_Types.Boolean)
        float_register = Register("Float", RegisterDirection.Both, path="Objects/2:Float value", type=OPCUA_Types.Float)
        uint16_register =  Register("Uint16", RegisterDirection.Both, path="Objects/2:Uint16 value", type=OPCUA_Types.UInt16)
        registers = [
            bool_register,
            float_register,
            uint16_register,
        ]
        test_server = OPCUATestServer(registers=registers)
        
        hwl = OPCUA_Hardware(host="opc.tcp://127.0.0.1:48401/")
        hwl.registers = registers
        
        with test_server, hwl:
            hwl.write_batch([1,1,1], registers)
            values = hwl.read_batch(registers)
        
        self.assertIn((bool_register.options["path"], True), test_server.server_write_events)
        self.assertIn((float_register.options["path"], 1.0), test_server.server_write_events)
        self.assertIn((uint16_register.options["path"], 1), test_server.server_write_events)
        self.assertEqual(values, [True, 1.0, 1,])
if __name__ == "__main__":
    unittest.main()