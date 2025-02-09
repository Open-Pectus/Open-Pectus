
import time


class Clock:
    def get_time(self) -> float:
        raise NotImplementedError()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class WallClock(Clock):
    def get_time(self) -> float:
        return time.time()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(time={self.get_time()})'
