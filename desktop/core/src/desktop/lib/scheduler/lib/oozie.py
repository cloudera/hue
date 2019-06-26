
from desktop.lib.scheduler.lib.api import Api

from oozie.views.editor2 import _submit_coordinator


class OozieApi(Api):

  def submit_schedule(request, coordinator, mapping):
    return _submit_coordinator(request, coordinator, mapping)
