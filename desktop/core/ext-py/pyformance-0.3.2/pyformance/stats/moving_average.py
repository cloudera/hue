import math
import time


class ExpWeightedMovingAvg(object):

    """
    An exponentially-weighted moving average.
    """
    INTERVAL = 5.0  # seconds
    SECONDS_PER_MINUTE = 60.0

    def __init__(self, period, interval=INTERVAL, clock=time):
        """
        Create a new EWMA with a specific smoothing constant.

        :type period: C{int}
        :param period: the time in minutes it takes to reach a given significance level
        :type interval: C{int}
        :param interval: the expected tick interval, defaults to 5s
        """
        super(ExpWeightedMovingAvg, self).__init__()
        self.clock = clock
        self.uncounted = 0.0
        self.interval = interval
        self.rate = -1
        self.period = period * ExpWeightedMovingAvg.SECONDS_PER_MINUTE
        self.last_tick = self.clock.time()

    def get_rate(self):
        if self.clock.time() - self.last_tick >= self.interval:
            self.tick()
        if self.rate >= 0:
            return self.rate
        return 0

    def add(self, value):
        self.uncounted += value

    def tick(self):
        """
        Mark the passage of time and decay the current rate accordingly.
        """
        prev = self.last_tick
        now = self.clock.time()
        interval = now - prev
        if interval <= 0:
            return

        instant_rate = self.uncounted / interval
        self.uncounted = 0.0

        if self.rate >= 0:
            self.rate += (self._alpha(interval) * (instant_rate - self.rate))
        else:
            self.rate = instant_rate

        self.last_tick = now

    def _alpha(self, interval):
        """
        Calculate the alpha based on the time since the last tick. This is
        necessary because a single threaded Python program loses precision  
        under high load, so we can't assume a consistant I{EWMA._interval}.

        :type interval: C{float}
        :param interval: the interval we use to calculate the alpha
        """
        return 1 - math.exp(-interval / self.period)
