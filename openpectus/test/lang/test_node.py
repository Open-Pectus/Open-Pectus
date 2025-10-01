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
