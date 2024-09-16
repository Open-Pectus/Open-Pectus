import time
import unittest

from openpectus.lang.exec.timer import ZeroThreadTimer, OneThreadTimer


#@unittest.skip("Slow")
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

        time.sleep(5.5)
        timer.stop()
        print('timer.stopped')

    def test_one_thead_timer_drift(self):        
        counter = 0
        last_tick = 0
        last_last_tick = 0

        def tick():
            nonlocal counter, last_tick, last_last_tick
            _time = time.time()
            #print('tick: {:.4f}'.format(_time))
            time.sleep(0.9)  # simulate work
            if counter % 3 == 0 and last_last_tick > 0 :
                #print("Diff", _time - last_tick)
                print("Diff", _time - last_last_tick)
            counter += 1
            last_last_tick = last_tick
            last_tick = _time

        timer = OneThreadTimer(1.0, tick)
        timer.start()
        print('timer.start() returned')

        time.sleep(10)
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
