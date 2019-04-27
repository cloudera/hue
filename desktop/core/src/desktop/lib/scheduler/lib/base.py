

from desktop.lib.scheduler.lib.beat import CeleryBeatApi
from desktop.lib.scheduler.lib.oozie import OozieApi


def get_api(request, interface):

  if interface == 'beat':
    return CeleryBeatApi(user=request.user)
  elif interface == 'oozie':
    return OozieApi(user=request.user)
  else:
    raise PopupException(_('Scheduler connector interface not recognized: %s') % interface)


class Api():

  def get_schedule():
    return JsonResponse({
    })

  def submit_schedule():
    return
