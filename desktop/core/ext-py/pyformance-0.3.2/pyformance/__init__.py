__import__('pkg_resources').declare_namespace(__name__)

from .registry import MetricsRegistry, global_registry, set_global_registry
from .registry import timer, counter, meter, histogram, gauge
from .registry import dump_metrics, clear, count_calls, meter_calls, hist_calls, time_calls
from .meters.timer import call_too_long
