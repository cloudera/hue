import time
from threading import Thread, Event
from ..registry import global_registry, get_qualname


class Reporter(object):

    def create_thread(self):
        # noinspection PyAttributeOutsideInit
        self._loop_thread = Thread(target=self._loop, name="pyformance reporter {0}".format(get_qualname(type(self))))
        self._loop_thread.setDaemon(True)

    def __init__(self, registry=None, reporting_interval=30, clock=None):
        self.registry = registry or global_registry()
        self.reporting_interval = reporting_interval
        self.clock = clock or time
        self._stopped = Event()
        self.create_thread()

    def start(self):
        if self._stopped.is_set():
            return False

        r = str(self._loop_thread)
        if "stopped" in r:
            # has to be recreated in a celery worker
            self.create_thread()
        elif "started" in r:
            # already started
            return False

        self._loop_thread.start()
        return True

    def stop(self):
        self._stopped.set()

    def _loop(self):
        while not self._stopped.is_set():
            self.report_now(self.registry)
            time.sleep(self.reporting_interval)
        # self._stopped.clear()

    def report_now(self, registry=None, timestamp=None):
        raise NotImplementedError(self.report_now)
