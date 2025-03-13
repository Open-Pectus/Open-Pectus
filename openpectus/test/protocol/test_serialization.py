import unittest

import openpectus.protocol.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.serialization import serialize, deserialize


class SerializationTest(unittest.TestCase):
    def test_serialization_RegisterEngineMsg(self):
        reg = EM.RegisterEngineMsg(
            computer_name="foo",
            uod_name="bar",
            uod_author_name="author_name",
            uod_author_email="",
            uod_filename="",
            location="baz",
            engine_version='0.0.1')
        reg_s = serialize(reg)
        self.assertEqual(
            {'_type': 'RegisterEngineMsg', '_ns': 'openpectus.protocol.engine_messages',
             'computer_name': 'foo', 'engine_version': '0.0.1', 'uod_name': 'bar',
             'uod_author_name': 'author_name', 'uod_author_email': '', 'uod_filename': '',
             'location': 'baz', 'secret': '',
             'sequence_number': -2, 'version': 0},
            reg_s)
        self.assertIsNotNone(reg_s)

    def test_round_trip_RegisterEngineMsg(self):
        reg = EM.RegisterEngineMsg(
            computer_name="foo",
            uod_name="bar",
            uod_author_name="author_name",
            uod_author_email="",
            uod_filename="",
            location="baz",
            engine_version='0.0.1')
        reg_s = serialize(reg)
        reg_d = deserialize(reg_s)
        self.assertIsNotNone(reg_d)
        assert isinstance(reg_d, EM.RegisterEngineMsg)
        self.assertEqual(reg.computer_name, reg_d.computer_name)
        self.assertEqual(reg.uod_name, reg_d.uod_name)

    def test_round_trip_AM_MethodMsg(self):
        am_method = AM.MethodMsg(method=Mdl.Method(lines=[Mdl.MethodLine(id='87', content='Foo')]))
        reg_s = serialize(am_method)
        reg_d = deserialize(reg_s)
        self.assertIsNotNone(reg_d)
        assert isinstance(reg_d, AM.MethodMsg)
        self.assertEqual(am_method.method, reg_d.method)

    def test_serialization_TagsUpdatedMsg(self):
        tu = EM.TagsUpdatedMsg(
            tags=[Mdl.TagValue(name="foo", tick_time=0, value="bar", value_formatted=None, value_unit="m")])
        tu_s = serialize(tu)
        self.assertIsNotNone(tu_s)

    def test_round_trip_TagsUpdatedMsg(self):
        tu = EM.TagsUpdatedMsg(
            tags=[Mdl.TagValue(name="foo", tick_time=0, value="bar", value_formatted=None, value_unit=None)]
        )
        tu_s = serialize(tu)
        self.assertIsNotNone(tu_s)

        tu_d = deserialize(tu_s)
        self.assertIsNotNone(tu_d)
        assert isinstance(tu_d, EM.TagsUpdatedMsg)
        self.assertEqual(tu_d.tags[0].name, tu.tags[0].name)


if __name__ == "__main__":
    unittest.main()
