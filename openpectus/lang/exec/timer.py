
import math
import threading
import time
from typing import Any, Callable

from openpectus.lang.exec.clock import Clock


TickConsumer = Callable[[float, float], None]
""" Tick function. It is called by the timer on each tick with arguments:
- tick_time: float          Time of the tick in seconds
- increment_time: float     Time since last tick_time

Will not be called on tick 0 where `increment_time` would be zero.

On pause/resume, will also not be called on the first tick after resume.

So it is safe to assume that `increment_time` represents a valid time increment which should be very
close to the timer interval.

Note:
This is a very important assumption. We could also have the client test for `increment_time > 0.0` but unless we 
discover a use case for it we don't do that.
"""


class ZeroThreadTimer:
    """Single threaded (no extra thread) timer using generator.

    Because there is no extra thread, the tick provided must signal
    when to stop using its return value. """
    def __init__(self, period_s: float, tick: Callable[[], bool]):
        self.running = True
        self.period_s = period_s
        self.tick = tick

    def start(self):
        self.start_time = time.time()
        self.do_every()

    def do_every(self):
        def g_tick():
            t = time.time()
            while True:
                t += self.period_s
                yield max(t - time.time(), 0)

        g = g_tick()

        while self.running:
            time.sleep(next(g))
            self.running = self.tick()


class EngineTimer():

    def set_tick_fn(self, tick_fn: TickConsumer):
        pass

    def start(self):
        pass

    def stop(self):
        pass

class OneThreadTimer(EngineTimer):
    """ Single threaded (1 extra thread) timer.

    This allows controlled multithreading.
    """
    def __init__(self, interval: float, tick: TickConsumer | None = None) -> None:
        """ Initialize a new timer.

        Parameters:
        - interval: float   Interval in seconds between ticks
        - tick: function    The tick function to call when interval has passed
        """
        self.interval = interval
        self.tick = tick
        self.start_time = 0.0
        self.tick_number = 0
        self.tick_time_normal = 0.0
        self.last_tick_time_normal = 0.0
        self.running = False
        self.paused = False

    def set_tick_fn(self, tick_fn: TickConsumer):
        self.tick = tick_fn

    def start(self):
        """ Start timer """
        if self.tick is None:
            raise ValueError("Timer cannot start when no tick_fn has been set")

        self.start_time = time.monotonic()
        self.tick_number = 0
        self.tick_time_normal = self.start_time
        self.last_tick_time_normal = 0
        self.running = True
        self.thread = threading.Thread(
            target=self.ticker,
            name=self.__class__.__name__,
            daemon=True)
        self.thread.start()

    def ticker(self):
        assert self.tick is not None, "No tick function has been set"

        if self.tick_number == 0:
            start = time.monotonic()
            start = math.ceil(start * 1000) / 1000  # round up to whole milisecond to make logs pretty
            self.start_time = start
            print("Timer start time (rounded)", start)
            self.last_tick_time_normal = self.start_time
            self.tick_number = 0

        while self.running:

            # calculate the exact normal time. Should result in a milisond-rounded time. We should be called very close
            # to this time
            self.tick_time_normal = self.last_tick_time_normal + self.interval

            # don't tick on the first iteration where no increment is available
            if self.tick_number == 0:
                self.tick_number += 1
                continue
            else:
                # TODO consider locking. In debug we get weird errors. And also in test_speed_perceived. This is not
                # acceptable. We want to be able to debug and not throw timings off

                # notify tick consumer
                self.tick(self.tick_time_normal, self.tick_time_normal - self.last_tick_time_normal)

                # calculate delay for next tick
                delay = self.tick_time_normal - time.monotonic()

                if delay > self.interval * 1.5:
                    print(f"WARNING: Timer delay {delay} much larger than interval, tick_no: {self.tick_number}")
                elif delay > 0:
                    time.sleep(delay)
                elif delay <= 0:
                    print(f"WARNING: Negative timer delay '{delay}' - work took too long, tick_no: {self.tick_number}")

                self.tick_number += 1
                self.last_tick_time_normal = self.tick_time_normal

    def stop(self):
        self.running = False
        # self.thread.join()


class TestTimerClock(EngineTimer, Clock):
    """ Combined timer and clock that enables precise time and speed control for testing. """

    def __init__(self, interval: float, speed: float, on_tick: TickConsumer | None = None) -> None:
        """ Initialize a new timer.

        Parameters:
        - interval: float       Interval in seconds between ticks
        - speed: float          Speed multiplier for the clock and timer
        - on_tick: function     The tick function to call when interval has passed

        Interval is expected to be a factor of 10 miliseconds as we round tick times to nearest milisecond.
        """
        self.interval = interval
        self.speed = speed
        self.tick = on_tick
        self.tick_number: int = 0
        self.tick_time = 0.0
        self.tick_time_normal = 0.0
        self.last_tick_time = 0.0
        self.last_tick_time_normal = 0.0
        self.running = False

    def set_tick_fn(self, tick_fn: TickConsumer):
        self.tick = tick_fn

    def _tick_internal(self):
        pass

    def start(self):
        """ Start clock and timer """
        if self.tick is None:
            raise ValueError("Timer cannot start when no tick_fn has been set")

        self.start_time = time.monotonic()
        self.tick_number = 0
        self.tick_time = self.start_time
        self.tick_time_normal = self.start_time
        self.last_tick_time = 0
        self.last_tick_time_normal = 0
        self.running = True
        self.thread = threading.Thread(
            target=self.ticker,
            name=self.__class__.__name__,
            daemon=True)
        self.thread.start()

    def ticker(self):
        assert self.tick is not None, "No tick function has been set"

        if self.tick_number == 0:
            start = time.monotonic()
            start = math.ceil(start * 1000) / 1000  # round up to whole milisecond to make logs pretty
            self.start_time = start
            print("Timer start time (rounded)", start)
            self.last_tick_time = self.start_time
            self.last_tick_time_normal = self.start_time
            self.tick_number = 0

        while self.running:

            # calculate the exact normal time. Should result in a milisond-rounded time. We should be called very close
            # to this time
            self.tick_time_normal = self.last_tick_time_normal + self.interval
            # calculate exact time of tick using speed. Should result in a milisond-rounded time
            self.tick_time = self.last_tick_time + self.speed * self.interval

            # don't tick on the first iteration where no increment is available
            if self.tick_number == 0:
                self.tick_number += 1
                continue
            else:
                # TODO consider locking. In debug we get weird errors. And also in test_speed_perceived. This is not
                # acceptable. We want to be able to debug and not throw timings off

                # notify tick consumer
                self.tick(self.tick_time, self.tick_time - self.last_tick_time)

                # calculate delay for next tick
                delay = self.tick_time_normal - time.monotonic()

                if delay > self.interval * 1.5:
                    print(f"WARNING: Timer delay {delay} much larger than interval, tick_no: {self.tick_number}")
                elif delay > 0:
                    time.sleep(delay)
                elif delay <= 0:
                    print(f"WARNING: Negative timer delay '{delay}' - work took too long, tick_no: {self.tick_number}")

                self.tick_number += 1
                self.last_tick_time_normal = self.tick_time_normal
                self.last_tick_time = self.tick_time

    def stop(self):
        self.running = False

    # -- Clock impl ---

    def get_time(self) -> float:
        # calculate increment in normal time since last tick
        increment_normal = time.monotonic() - self.last_tick_time_normal
        # scale up the increment to account for speed
        return self.last_tick_time + self.speed * increment_normal


class NullTimer(EngineTimer):
    pass
