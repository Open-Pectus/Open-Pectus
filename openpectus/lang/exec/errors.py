
from openpectus.lang.model.pprogram import PNode


class EngineNotInitializedError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)


class UodValidationError(Exception):
    """ Raised when a UnitOperationDefinition definition/configuration error occurs. """
    pass


class InterpretationError(Exception):
    """ Raised by interpreter when a general error occurs """
    def __init__(self, message: str, exception: Exception | None = None, *args: object) -> None:
        self.message: str = message
        self.exception = exception
        super().__init__(*args)


class NodeInterpretationError(InterpretationError):
    """ Raised by interpreter when an instruction specific error occurs """
    def __init__(self, node: PNode, message: str, exception: Exception | None = None, *args: object) -> None:
        self.node = node
        self.message: str = message
        self.exception = exception
        base_message = f"An error occurred in instruction '{node.display_name}': {message}"
        super().__init__(base_message, exception, *args)

class InterpretationInternalError(InterpretationError):
    """ Raised by interpreter if an internal error occurs """
    def __init__(self, message: str, exception: Exception | None = None, *args: object) -> None:
        self.message: str = message
        self.exception = exception
        base_message = f"An internal error occurred. Interpretation cannot continue: {message}"
        super().__init__(base_message, exception, *args)
