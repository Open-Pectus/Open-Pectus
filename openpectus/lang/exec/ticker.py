from openpectus.lang.exec.timer import OneThreadTimer


class Ticker:
    def tick(self):
        raise NotImplementedError()


class TimerTicker(Ticker):
    def __init__(self, period_s: float) -> None:
        super().__init__()
        self.timer = OneThreadTimer(period_s, self.tick)
        self.running = True
        self.timer.start()

    def tick(self):
        if self.running:
            yield
        else:
            raise StopIteration

    def stop(self):
        self.running = False
