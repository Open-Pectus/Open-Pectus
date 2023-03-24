

import unittest
import time
from lang.exec.timer import ZeroThreadTimer, OneThreadTimer


class TimerTest(unittest.TestCase):
    def test_zero_thread_timer(self):
        def tick() -> bool:
            print('tick: {:.4f}'.format(time.time()))
            time.sleep(0.3)  # simulate work
            if time.time() > start_time + 10:
                return False
            return True

        start_time = time.time()
        timer = ZeroThreadTimer(1.0, tick)
        timer.start()
        print('timer.start() returned')

    def test_one_thead_timer(self):
        def tick():
            print('tick: {:.4f}'.format(time.time()))
            time.sleep(0.3)  # simulate work

        timer = OneThreadTimer(1.0, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(10.5)
        timer.stop()
        print('timer.stopped')

    def test_one_thead_timer_can_restart(self):
        def tick():
            print('tick: {:.4f}'.format(time.time()), flush=True)
            time.sleep(0.8 * period)  # simulate work

        period = 0.3
        timer = OneThreadTimer(period, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(5 * period + .1)
        timer.stop()
        print('timer stopped')

        time.sleep(3 * period + .1)

        timer.start()
        print('timer restarted')

        time.sleep(5 * period + .1)
        timer.stop()
        print('timer stopped again')


if __name__ == "__main__":
    unittest.main()
