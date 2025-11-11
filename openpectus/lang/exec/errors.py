
from typing import Literal
import openpectus.lang.model.ast as p


class EngineNotInitializedError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(message="{self.message}")'


class EngineError(Exception):
    def __init__(self, message: str, user_message: str | Literal["same"] | None = None) -> None:
        self.message = message
        if user_message == "same":
            self.user_message = message
        else:
            self.user_message = user_message
        super().__init__()

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
    def __init__(self, message: str, user_message: str | Literal["same"] | None = "same") -> None:
        super().__init__()
        self.message: str = message
        if user_message == "same":
            self.user_message = message
        else:
            self.user_message = user_message

    def __str__(self) -> str:
        ex_info = self.__cause__ if self.__cause__ else self.__context__ if self.__context__ else None

        if self.user_message == self.message:
            return f'{self.__class__.__name__}(message="{self.message}", exception={ex_info})'
        else:
            return (f'{self.__class__.__name__}(message="{self.message}", user_message="{self.user_message}", ' +
                    f'exception={ex_info})')


class NodeInterpretationError(InterpretationError):
    """ Raised by interpreter when an instruction specific error occurs """
    def __init__(self, node: p.Node, message: str, user_message: str | Literal["same"] | None = "same") -> None:
        self.node = node
        self.message: str = message
        if user_message == "same":  # avoid using base message for user messages
            user_message = message
        base_message = f"An error occurred in instruction '{node}': {message}"
        super().__init__(base_message, user_message)


class InterpretationInternalError(InterpretationError):
    """ Raised by interpreter if an internal error occurs """
    def __init__(self, message: str) -> None:
        self.message: str = message
        base_message = f"An internal error occurred. Interpretation cannot continue: {message}"
        super().__init__(base_message, "Internal error")


class MethodEditError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
