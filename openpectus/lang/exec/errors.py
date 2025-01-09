
from typing import Literal
from openpectus.lang.model.pprogram import PNode


class EngineNotInitializedError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        return self.message or type(self).__name__


class EngineError(Exception):
    def __init__(self, message: str, user_message: str | Literal["same"] | None = None, *args) -> None:
        self.message = message
        if user_message == "same":
            self.user_message = message
        else:
            self.user_message = user_message
        super().__init__(*args)

    def __str__(self) -> str:
        return self.message or self.user_message or type(self).__name__


class UodValidationError(Exception):
    """ Raised when a UnitOperationDefinition definition/configuration error occurs. """
    pass

    def __str__(self) -> str:
        return type(self).__name__


class InterpretationError(Exception):
    """ Raised by interpreter when a general error occurs """
    def __init__(self,
                 message: str,
                 user_message: str | Literal["same"] | None = "same",
                 exception: Exception | None = None, *args: object
                 ) -> None:
        self.message: str = message
        if user_message == "same":
            self.user_message = message
        else:
            self.user_message = user_message
        self.exception = exception
        super().__init__(*args)

    def __str__(self) -> str:
        return self.message or self.user_message or type(self).__name__


class NodeInterpretationError(InterpretationError):
    """ Raised by interpreter when an instruction specific error occurs """
    def __init__(self, node: PNode, message: str, user_message: str | Literal["same"] | None = "same",
                 exception: Exception | None = None, *args: object) -> None:
        self.node = node
        self.message: str = message
        self.exception = exception
        if user_message == "same":  # avoid using base message for user messages
            user_message = message
        base_message = f"An error occurred in instruction '{node.display_name}': {message}"
        super().__init__(base_message, user_message, exception, *args)

    def __str__(self) -> str:
        return self.message or self.user_message or type(self).__name__

class InterpretationInternalError(InterpretationError):
    """ Raised by interpreter if an internal error occurs """
    def __init__(self, message: str, exception: Exception | None = None, *args: object) -> None:
        self.message: str = message
        self.exception = exception
        base_message = f"An internal error occurred. Interpretation cannot continue: {message}"
        super().__init__(base_message, "Internal error", exception, *args)

    def __str__(self) -> str:
        return self.message or self.user_message or type(self).__name__
