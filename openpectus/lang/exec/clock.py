
import time


class Clock:
    def get_time(self) -> float:
        raise NotImplementedError()


class WallClock(Clock):
    def get_time(self) -> float:
        return time.time()
