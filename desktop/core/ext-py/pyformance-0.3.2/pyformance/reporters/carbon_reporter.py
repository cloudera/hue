# -*- coding: utf-8 -*-
import socket
import sys

from .reporter import Reporter

DEFAULT_CARBON_SERVER = '0.0.0.0'
DEFAULT_CARBON_PORT = 2003


class CarbonReporter(Reporter):

    """
    Carbon is the network daemon to collect metrics for Graphite
    """

    def __init__(self, registry=None, reporting_interval=5, prefix="",
                 server=DEFAULT_CARBON_SERVER, port=DEFAULT_CARBON_PORT, socket_factory=socket.socket,
                 clock=None):
        super(CarbonReporter, self).__init__(
            registry, reporting_interval, clock)
        self.prefix = prefix
        self.server = server
        self.port = port
        self.socket_factory = socket_factory

    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            # XXX: keep connection open 
            sock = self.socket_factory()
            sock.connect((self.server, self.port))

            if sys.version_info[0] > 2:
                sock.sendall(metrics.encode())
            else:
                sock.sendall(metrics)

            sock.close()

    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))
        metrics = registry.dump_metrics()
        metrics_data = []
        for key in metrics.keys():
            for value_key in metrics[key].keys():
                metricLine = "%s%s.%s %s %s\n" % (
                    self.prefix, key, value_key, metrics[key][value_key], timestamp)
                metrics_data.append(metricLine)
        return ''.join(metrics_data)

    
class UdpCarbonReporter(CarbonReporter):
    
    """
    The default CarbonReporter uses TCP.
    This sub-class uses UDP instead which might be unreliable but it is faster
    """
    
    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            sock = self.socket_factory(socket.AF_INET, socket.SOCK_DGRAM)

            if sys.version_info[0] > 2:
                sock.sendto(metrics.encode(), (self.server, self.port))
            else:
                sock.sendto(metrics, (self.server, self.port))
