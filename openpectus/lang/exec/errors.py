
from typing import Literal
import openpectus.lang.model.ast as p


class EngineNotInitializedError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(message="{self.message}")'


class EngineError(Exception):
    def __init__(
            self,
            message: str,
            user_message: str | Literal["same"] | None = None,
            exception: Exception | None = None,
            *args) -> None:
        self.message = message
        if user_message == "same":
            self.user_message = message
        else:
            self.user_message = user_message
        super().__init__(*args)
        self.exception = exception

    def __str__(self) -> str:
        if self.user_message == self.message:
            return f'{self.__class__.__name__}(message="{self.message}")'
        else:
            return f'{self.__class__.__name__}(message="{self.message}", user_message="{self.user_message}")'


class UodValidationError(Exception):
    """ Raised when a UnitOperationDefinition definition/configuration error occurs. """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(self.args)})'


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
        if self.user_message == self.message:
            return f'{self.__class__.__name__}(message="{self.message}", exception={self.exception})'
        else:
            return (f'{self.__class__.__name__}(message="{self.message}", user_message="{self.user_message}", ' +
                    f'exception={self.exception})')


class NodeInterpretationError(InterpretationError):
    """ Raised by interpreter when an instruction specific error occurs """
    def __init__(self, node: p.Node, message: str, user_message: str | Literal["same"] | None = "same",
                 exception: Exception | None = None, *args: object) -> None:
        self.node = node
        self.message: str = message
        self.exception = exception
        if user_message == "same":  # avoid using base message for user messages
            user_message = message
        base_message = f"An error occurred in instruction '{node.display_name}': {message}"
        super().__init__(base_message, user_message, exception, *args)


class InterpretationInternalError(InterpretationError):
    """ Raised by interpreter if an internal error occurs """
    def __init__(self, message: str, exception: Exception | None = None, *args: object) -> None:
        self.message: str = message
        self.exception = exception
        base_message = f"An internal error occurred. Interpretation cannot continue: {message}"
        super().__init__(base_message, "Internal error", exception, *args)


class MethodError(Exception):
    def __init__(self, message: str, exception: Exception | None = None):
        self.message = message
        self.exception = exception


class MethodEditError(MethodError):
    def __init__(self, message: str, exception: Exception | None = None):
        super().__init__(message, exception)
