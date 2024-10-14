from enum import StrEnum
from typing import Literal
from openpectus.lang.exec.tags import SystemTagName, TagDirection

SystemTagName = SystemTagName
TagDirection = TagDirection

class EngineCommandEnum(StrEnum):
    START = "Start"
    STOP = "Stop"
    PAUSE = "Pause"
    UNPAUSE = "Unpause"
    HOLD = "Hold"
    UNHOLD = "Unhold"
    WAIT = "Wait"
    RESTART = "Restart"
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return value in EngineCommandEnum.__members__.values()


class SystemStateEnum(StrEnum):
    Running = "Running"
    Paused = "Paused"
    Holding = "Holding"
    Waiting = "Waiting"
    Stopped = "Stopped"
    Restarting = "Restarting"


class MethodStatusEnum(StrEnum):
    OK = "OK"
    ERROR = "Error"


class ConnectionStatusEnum(StrEnum):
    """ Defines status for the connectedness of the Engine-Hardware connection. """
    Disconnected = "Disconnected"
    Connected = "Connected"


EntryDataType = Literal["str"] | Literal["int"] | Literal["float"] | Literal["auto"]
