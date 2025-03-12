class AggregatorException(Exception):
    def __init__(self, message: str | None = ""):
        self.message = message

class AggregatorCallerException(AggregatorException):
    pass

class AggregatorInternalException(AggregatorException):
    pass
