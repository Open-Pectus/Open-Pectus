
import threading
import time
from typing import Any, Callable


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
    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

class OneThreadTimer(EngineTimer):
    """ Single threaded (1 extra thread) timer.

    This allows controlled multithreading.
    """
    def __init__(self, interval: float, tick: Callable[[], Any]) -> None:
        """ Initialize a new timer.

        Parameters:
        - interval: float   Interval in seconds between ticks
        - tick: function    The tick function to call when interval has passed
        """
        self.interval = interval
        self.tick = tick
        self.running = False
        self.paused = False

    def get_interval(self) -> float:
        """ Get interval in seconds """
        return self.interval

    def start(self):
        self.running = True
        self.thread = threading.Thread(
            target=self.ticker,
            name="OneThreadTimer",
            daemon=True)
        self.thread.start()

    def ticker(self):
        deadline = time.monotonic()
        while self.running:
            deadline += self.interval
            if not self.paused:
                self.tick()
            delay = deadline - time.monotonic()
            if delay > 0 and self.running:
                time.sleep(delay)
            elif delay <= 0:
                print("Negative timer delay - work must have take too long")

    def stop(self):
        self.running = False
        # self.thread.join()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False


class NullTimer(EngineTimer):
    pass
