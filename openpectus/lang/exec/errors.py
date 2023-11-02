
class UodValidationError(Exception):
    """ Raised when a UnitOperationDefinition definition/configuration error occurs. """
    pass


class InterpretationError(Exception):
    def __init__(self, message: str, exception: Exception | None = None, *args: object) -> None:
        self.message: str = message
        self.exception = exception
        super().__init__(*args)
