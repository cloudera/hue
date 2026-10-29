# Hue: upstream line 1 was `__import__('pkg_resources').declare_namespace(__name__)`.
# pyformance is not a namespace package (setup.py declares none), and setuptools 82
# removed pkg_resources, so the line is dropped to allow setuptools >= 83 in the venv.

from .registry import MetricsRegistry, global_registry, set_global_registry
from .registry import timer, counter, meter, histogram, gauge
from .registry import dump_metrics, clear, count_calls, meter_calls, hist_calls, time_calls
from .meters.timer import call_too_long
