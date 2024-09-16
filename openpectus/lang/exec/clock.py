
import time


class Clock:
    def get_time(self) -> float:
        raise NotImplementedError()


class WallClock(Clock):
    def get_time(self) -> float:
        return time.time()


class FixedSpeedTestClock(Clock):
    def __init__(self, start_time=time.time(), speed=1.0) -> None:
        self.start_time = start_time
        self.speed = speed

    def get_time(self) -> float:
        return self.start_time + self.speed * (time.time() - self.start_time)
