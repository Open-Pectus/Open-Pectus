import random
import time
import unittest

from openpectus.lang.exec.timer import TestTimerClock, ZeroThreadTimer, OneThreadTimer


@unittest.skip("Slow")
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
            #time.sleep(0.09)  # simulate unsafe work amount - will print warnings

        interval = .1
        timer = OneThreadTimer(interval, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(3)
        timer.stop()
        print('timer.stopped')

    def test_one_thead_timer_can_restart(self):
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



    def test_TestTimerClock_increment_is_accurate_real_time(self):
        def tick(tick_time, increment_time):
            print("increment", increment_time)
            self.assertLess(abs(.1 - increment_time), 0.001)

        timer = TestTimerClock(0.1, 1.0, tick)
        timer.start()

        time.sleep(3)
        timer.stop

    def test_TestTimerClock_perceived_time_is_accurate_real_time(self):
        last_tick_time = 0.0

        def tick(tick_time, increment_time):
            nonlocal last_tick_time
            if last_tick_time == 0.0:
                last_tick_time = timer.get_time()
            else:
                perceived_increment = timer.get_time() - last_tick_time
                last_tick_time = timer.get_time()
                print("perceived_increment", perceived_increment, "timer increment", increment_time)
                #self.assertLess(abs(.1 - perceived_increment), 0.001)

        timer = TestTimerClock(0.1, 1.0, tick)
        timer.start()

        time.sleep(3)
        timer.stop

    def test_TestTimerClock_increment_is_accurate_speed_30(self):
        def tick(tick_time, increment_time):
            print("increment", increment_time)
            # with the above print this will sometimes take longer than interval
            # and cause a print warning
            time.sleep(random.random() * .1)
            self.assertLess(abs(3.0 - increment_time), 0.001)

        timer = TestTimerClock(0.1, 30.0, tick)
        timer.start()

        time.sleep(3)
        timer.stop()

    def test_TestTimerClock_perceived_time_is_accurate_speed_30(self):
        last_tick_time = 0.0

        def tick(tick_time, increment_time):
            nonlocal last_tick_time
            if last_tick_time == 0.0:
                last_tick_time = timer.get_time()
            else:
                perceived_increment = timer.get_time() - last_tick_time
                last_tick_time = timer.get_time()
                print("perceived_increment", perceived_increment, "timer increment", increment_time)
                #self.assertLess(abs(.1 - perceived_increment), 0.001)

        timer = TestTimerClock(0.1, 30.0, tick)
        timer.start()

        time.sleep(3)
        timer.stop()


if __name__ == "__main__":
    unittest.main()
