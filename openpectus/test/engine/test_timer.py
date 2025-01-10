import time
import unittest

from openpectus.lang.exec.timer import OneThreadTimer


@unittest.skip("Slow")
class TimerTest(unittest.TestCase):

    def test_one_thread_timer(self):
        def tick(tick_time: float, increment_time: float):
            print('tick: {:.4f}'.format(tick_time))
            time.sleep(0.3)  # simulate work

        timer = OneThreadTimer(1.0, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(5.5)
        timer.stop()
        print('timer.stopped')

    def test_one_thread_timer_drift(self):
        def tick(tick_time: float, increment_time: float):
            print("tick_time", tick_time)
            time.sleep(0.07)  # simulate safe work amount
            # time.sleep(0.09)  # simulate unsafe work amount - will print warnings

        interval = .1
        timer = OneThreadTimer(interval, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(3)
        timer.stop()
        print('timer.stopped')

    def test_one_thread_timer_can_restart(self):
        def tick(tick_time: float, increment_time: float):
            print("tick_time", tick_time)
            time.sleep(0.8 * interval)  # simulate work

        interval = 0.3
        timer = OneThreadTimer(interval, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(5 * interval + .1)
        timer.stop()
        print('timer stopped')

        time.sleep(3 * interval + .1)

        timer.start()
        print('timer restarted')

        time.sleep(5 * interval + .1)
        timer.stop()
        print('timer stopped again')


if __name__ == "__main__":
    unittest.main()
