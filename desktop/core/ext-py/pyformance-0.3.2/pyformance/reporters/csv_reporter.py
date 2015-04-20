# -*- coding: utf-8 -*-
import sys
import os
import datetime
from .reporter import Reporter


class CsvReporter(Reporter):

    """
    Show metrics in comma-separated-files.
    Each metrics gets its own file
    """

    def __init__(self, registry=None, reporting_interval=30, path=None, separator="\t", clock=None):
        super(CsvReporter, self).__init__(
            registry, reporting_interval, clock)
        self.path = path or os.getcwd()
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.separator = separator
        self.files = {}

    def report_now(self, registry=None, timestamp=None):
        self._save_metrics(registry or self.registry, timestamp)

    def _save_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        dt = datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(seconds=timestamp)
        date = dt.strftime("%Y-%m-%d %H:%M:%S")
        metrics = registry.dump_metrics()
        for key in metrics.keys():
            values = metrics[key]
            value_keys = list(sorted(values.keys()))
            target = os.path.join(self.path, "%s.csv" % key)
            f = self.files.get(target, None)
            if f is None:
                if not os.path.exists(target):
                    f = open(target, "w")
                    f.write("%s\n" % self.separator.join(["timestamp"] + value_keys))
                else:
                    f = open(target, "a")
                self.files[target] = f
            cols = [date]
            for vk in value_keys:
                cols.append(values[vk])
            f.write("%s\n" % self.separator.join(map(str, cols)))
            f.flush()
