import logging
import time
import unittest
from unittest.mock import Mock

from openpectus.lang.exec.events import EventEmitter
from openpectus.lang.exec.tags import Tag


def reset_logging():
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    loggers.append(logging.getLogger())
    for logger in loggers:
        handlers = logger.handlers[:]
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True


reset_logging()


class TestEvents(unittest.TestCase):
    def test_tag_receives_event(self):
        on_start_mock = Mock()
        listener = Mock(on_start=on_start_mock)
        emitter = EventEmitter([listener])
        emitter.emit_on_start("")
        on_start_mock.assert_called()

    def test_emitter_warns_on_slow_Tag_handler(self):

        def onstart_fast(_):
            pass

        def onstart_slow(_):
            time.sleep(0.2)

        # no warning with fast handler on non-tag
        with self.assertNoLogs("openpectus.lang.exec.events"):
            listener = Mock(on_start=onstart_fast)
            emitter = EventEmitter([listener])
            emitter.emit_on_start("")

        # no warning with slow handler on non-tag
        with self.assertNoLogs("openpectus.lang.exec.events", level=logging.WARNING):
            listener = Mock(on_start=onstart_slow)
            emitter = EventEmitter([listener])
            emitter.emit_on_start("")

        # no warning with fast handler on tag
        with self.assertNoLogs("openpectus.lang.exec.events"):
            listener = Tag(name="Foo")
            setattr(listener, "on_start", onstart_fast)
            emitter = EventEmitter([listener])
            emitter.emit_on_start("")

        # warning with slow handler on tag
        with self.assertLogs("openpectus.lang.exec.events", level=logging.WARNING):
            listener = Tag(name="Foo")
            setattr(listener, "on_start", onstart_slow)
            emitter = EventEmitter([listener])
            emitter.emit_on_start("")
