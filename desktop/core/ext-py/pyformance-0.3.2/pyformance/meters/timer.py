import time
try:
    from blinker import Namespace
except ImportError:
    Namespace = None
from .histogram import Histogram, DEFAULT_SIZE, DEFAULT_ALPHA
from .meter import Meter

if Namespace is not None:
    timer_signals = Namespace()
    call_too_long = timer_signals.signal("call_too_long")
else:
    call_too_long = None


class Timer(object):

    """
    A timer metric which aggregates timing durations and provides duration statistics, plus
    throughput statistics via Meter and Histogram.
      
    """

    def __init__(self, threshold=None, size=DEFAULT_SIZE, alpha=DEFAULT_ALPHA, clock=time):
        super(Timer, self).__init__()
        self.meter = Meter(clock=clock)
        self.hist = Histogram(clock=clock)
        self.threshold = threshold

    def get_count(self):
        "get count from internal histogram"
        return self.hist.get_count()

    def get_sum(self):
        "get sum from internal histogram"
        return self.hist.get_sum()

    def get_max(self):
        "get max from internal histogram"
        return self.hist.get_max()

    def get_min(self):
        "get min from internal histogram"
        return self.hist.get_min()

    def get_mean(self):
        "get mean from internal histogram"
        return self.hist.get_mean()

    def get_stddev(self):
        "get stddev from internal histogram"
        return self.hist.get_stddev()

    def get_var(self):
        "get var from internal histogram"
        return self.hist.get_var()

    def get_snapshot(self):
        "get snapshot from internal histogram"
        return self.hist.get_snapshot()

    def get_mean_rate(self):
        "get mean rate from internal meter"
        return self.meter.get_mean_rate()

    def get_one_minute_rate(self):
        "get 1 minut rate from internal meter"
        return self.meter.get_one_minute_rate()

    def get_five_minute_rate(self):
        "get 5 minute rate from internal meter"
        return self.meter.get_five_minute_rate()

    def get_fifteen_minute_rate(self):
        "get 15 rate from internal meter"
        return self.meter.get_fifteen_minute_rate()

    def _update(self, seconds):
        if seconds >= 0:
            self.hist.add(seconds)
            self.meter.mark()

    def time(self, *args, **kwargs):
        """
        Parameters will be sent to signal, if fired.
        Returns a timer context instance which can be used from a with-statement.
        Without with-statement you have to call the stop method on the context
        """
        return TimerContext(self, self.meter.clock, *args, **kwargs)

    def clear(self):
        "clear internal histogram and meter"
        self.hist.clear()
        self.meter.clear()


class TimerContext(object):

    def __init__(self, timer, clock, *args, **kwargs):
        super(TimerContext, self).__init__()
        self.clock = clock
        self.timer = timer
        self.start_time = self.clock.time()
        self.kwargs = kwargs
        self.args = args

    def stop(self):
        elapsed = self.clock.time() - self.start_time
        self.timer._update(elapsed)
        if self.timer.threshold and self.timer.threshold < elapsed and call_too_long is not None:
            call_too_long.send(
                self.timer, elapsed=elapsed, *self.args, **self.kwargs)
        return elapsed

    def __enter__(self):
        pass

    def __exit__(self, t, v, tb):
        self.stop()
