# -*- coding: utf-8 -*-

# lazy import reporters to minimize startup time


def HostedGraphiteReporter(*args, **kwargs):
    from .hosted_graphite_reporter import HostedGraphiteReporter as cls
    return cls(*args, **kwargs)


def CarbonReporter(*args, **kwargs):
    from .carbon_reporter import CarbonReporter as cls
    return cls(*args, **kwargs)


def UdpCarbonReporter(*args, **kwargs):
    from .carbon_reporter import UdpCarbonReporter as cls
    return cls(*args, **kwargs)


def ConsoleReporter(*args, **kwargs):
    from .console_reporter import ConsoleReporter as cls
    return cls(*args, **kwargs)


def CsvReporter(*args, **kwargs):
    from .csv_reporter import CsvReporter as cls
    return cls(*args, **kwargs)
