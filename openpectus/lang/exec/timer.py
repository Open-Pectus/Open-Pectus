
import threading
import time
from typing import Callable


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


class OneThreadTimer():
    """ Single threaded (1 extra thread) timer.

    This allows controlled multithreading.
    """
    def __init__(self, period_s: float, tick: Callable) -> None:
        self.period_s = period_s
        self.tick = tick
        self.running = False

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
            deadline += self.period_s
            self.tick()
            delay = deadline - time.monotonic()
            if delay > 0 and self.running:
                time.sleep(delay)

    def stop(self):
        self.running = False
        # self.thread.join()
