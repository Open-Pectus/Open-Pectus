class ProtocolException(Exception):
    """ Exception for errors related to the Aggregator-Engine protocol """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProtocolDeserializationException(ProtocolException):
    """ Raised on deserialization errors. If this error occurs, it indicates an implementation error. """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProtocolNetworkException(Exception):
    """ Raised on errors related to the physical network connection """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
