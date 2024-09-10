import datetime
import unittest

from openpectus.lang.exec.tags import Tag
from openpectus.lang.exec.tags_impl import format_time_as_clock


class TagTest(unittest.TestCase):

    def test_formatting(self):
        tag = Tag("foo")

        tag.format_fn = format_time_as_clock
        _date = datetime.datetime(year=2000, month=1, day=1, hour=6, minute=46, second=3, microsecond=111)
        tag.value = _date.timestamp()

        t = tag.as_readonly()

        self.assertNotEqual("06:46:03", t.value_formatted)
        self.assertIsNotNone(t.value_formatted)
