
import inspect
import logging


class Tracer:
    """ Simple tracer that enables logging with automatic class and method details. """
    def __init__(self, logger: logging.Logger, enabled=True):
        self.logger = logger
        self.enabled = enabled

    def trace(self, message: str = ""):
        if not self.enabled:
            return

        func = inspect.currentframe().f_back.f_code  # type: ignore
        qualname = func.co_qualname
        self.logger.debug(f"{qualname} | {message}")
