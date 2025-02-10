
import threading
import time
from typing import Callable


TickConsumer = Callable[[float, float], None]
""" Tick function. It is called by the timer on each tick with arguments:
- tick_time: float          Time of the tick in seconds
- increment_time: float     Time since last tick_time

Will be called on all ticks, even tick 0 where `increment_time` is zero.

On pause/resume, will also be called on the first tick after resume where `increment_time` is also zero.
"""

class EngineTimer():

    def set_tick_fn(self, tick_fn: TickConsumer):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class NullTimer(EngineTimer):
    pass


class OneThreadTimer(EngineTimer):
    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle thread
        del state["thread"]
        return state

    def __setstate(self, state):
        self.__dict__.update(state)
        if self._thread_started:
            self.start()
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
        self.running = False            # flag to allow shut down by exiting the ticker loop method
        self._thread_started = False

    def set_tick_fn(self, tick_fn: TickConsumer):
        self.tick = tick_fn

    def start(self):
        """ Start timer """
        if self.tick is None:
            raise ValueError("Timer cannot start when no tick_fn has been set")
        self.running = True
        self.thread = threading.Thread(
            target=self.ticker,
            name=self.__class__.__name__,
            daemon=True)
        self.thread.start()
        self._thread_started = True

    def ticker(self):
        assert self.tick is not None, "No tick function has been set"

        tick_number = 0
        last_tick_time_mon = 0.0
        increment = 0.0

        while self.running:
            tick_time = time.time()
            tick_time_mon = time.monotonic()
            if tick_number > 0:
                increment = tick_time_mon - last_tick_time_mon

            self.tick(tick_time, increment)

            tick_number += 1
            last_tick_time_mon = tick_time_mon
            tick_time_mon = time.monotonic()
            elapsed = tick_time_mon - last_tick_time_mon
            deadline = self.interval - elapsed
            if deadline > 0.0:
                time.sleep(deadline)
        self._thread_started = False

    def stop(self):
        self.running = False
