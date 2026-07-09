from __future__ import annotations
from datetime import datetime
import unittest

from openpectus.lang.exec.elementstate import ElementState, HasElementState
from openpectus.lang.exec.tags import Tag


class TestHasElementState(unittest.TestCase):
    # tests of HasElementState as implemented by TestElement and TestTag

    def test_save(self):
        elem = TestElement("foo", "1", "my arg 1")
        state = elem.extract_state()

        assert state["namespace"] == "foo"
        assert state["element_id"] == "1"
        assert state["start_time"] == elem.start_time  # type: ignore

    def test_load(self):
        start_time = datetime.now()
        state = ElementState(namespace="foo", element_id="1")
        state["start_time"] = start_time  # type: ignore

        elem = TestElement("foo", "1", "my arg 1")
        elem.apply_state(state)

        assert elem.start_time == start_time

    def test_load_fails_on_namespace_mismatch(self):
        start_time = datetime.now()
        state = ElementState(namespace="foo", element_id="1")
        state["start_time"] = start_time  # type: ignore

        elem = TestElement("bar", "1", "my arg 1")
        with self.assertRaises(AssertionError):
            elem.apply_state(state)

    def test_load_fails_on_element_id_mismatch(self):
        start_time = datetime.now()
        state = ElementState(namespace="foo", element_id="1")
        state["start_time"] = start_time  # type: ignore

        elem = TestElement("foo", "2", "my arg 1")
        with self.assertRaises(AssertionError):
            elem.apply_state(state)

    def test_load_fails_on_custom_data_missing(self):
        state = ElementState(namespace="foo", element_id="1")
        # skip defining the required custom data
        # state["start_time"] = <some date value>

        elem = TestElement("foo", "1", "my arg 1")
        with self.assertRaises(KeyError):
            elem.apply_state(state)

    def test_load_fails_on_custom_data_invalid(self):
        state = ElementState(namespace="foo", element_id="1")
        # defining the required custom data with invalid data
        state["start_time"] = "not a datetime value"  # type: ignore
        elem = TestElement("foo", "1", "my arg 1")
        with self.assertRaises(TypeError):  # whatever exception the concrete element class raises
            elem.apply_state(state)

    def test_tag_(self):
        tag = TestTag("foo")
        state = tag.extract_state()
        state["my_attribute"] = "baz"  # type: ignore
        tag.my_attribute = "bar"
        tag.apply_state(state)
        assert tag.my_attribute == "baz"


class TestElement(HasElementState):
    # Example test class implementing HasElementState

    def __init__(self, namespace: str, element_id: str, arg1: str, **kwargs):
        super(TestElement, self).__init__(namespace=namespace, element_id=element_id, **kwargs)

        self.arg1 = arg1
        self.start_time = datetime.now()

    def extract_state(self):
        state = super().extract_state()
        state["start_time"] = self.start_time  # type: ignore
        return state

    def apply_state(self, state):
        super().apply_state(state)
        self.start_time = state["start_time"]  # type: ignore
        if not isinstance(self.start_time, datetime):
            raise TypeError("'start_time' value must be of type datetime")


class TestTag(Tag):
    def __init__(self, my_attribute: str):
        Tag.__init__(self, "TestTag")
        self.my_attribute = my_attribute

    def extract_state(self):
        state = super().extract_state()
        state["my_attribute"] = self.my_attribute  # type: ignore
        return state

    def apply_state(self, state):
        super().apply_state(state)
        self.my_attribute = state["my_attribute"]  # type: ignore
