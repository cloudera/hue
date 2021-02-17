import cmf.monitor.generic.adapter
import hue_adapters

class AdapterFactory(object):
  """
  Factory for making monitoring Adapter classes.
  """

  def make_adapter(self, service_type, role_type, safety_valve, daemon = None):
    """
    Makes an Adapter for the input role type.
    """
    if service_type == "HUE" and role_type == "HUE_SERVER":
      return hue_adapters.HueServerAdapter(safety_valve)
    else:
      return cmf.monitor.generic.adapter.Adapter(service_type, role_type, safety_valve)
