import unittest

import openpectus.lang.model.ast as p

class TestNode(unittest.TestCase):

    def test_ctor_position(self):
        # test weird error that pyright does not catch:
        # in Node subclasses constructor:
        #   def __init__(self, position=Position.empty, id=""):
        # instead of
        # #   def __init__(self, position=Position.empty(), id=""):
        # may even work but is certainly not intended
        node = p.Node()
        assert isinstance(node.position, p.Position)

        alarm = p.AlarmNode()
        self.assertIsInstance(alarm.position, p.Position)

        blank = p.BlankNode()
        self.assertIsInstance(blank.position, p.Position)

    def test_class_name(self):
        node = p.Node()
        self.assertEqual(node.class_name, "Node")

        alarm = p.AlarmNode()
        self.assertEqual(alarm.class_name, "AlarmNode")

        blank = p.BlankNode()
        self.assertEqual(blank.class_name, "BlankNode")

    def test_is_class_of(self):
        node = p.Node()
        alarm = p.AlarmNode()

        self.assertEqual(True, p.Node.is_class_of(node))
        self.assertEqual(False, p.Node.is_class_of(alarm))  # has super class check. add a flag if we need that

        self.assertEqual(False, p.AlarmNode.is_class_of(node))
        self.assertEqual(True, p.AlarmNode.is_class_of(alarm))
