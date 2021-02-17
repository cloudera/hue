import time
import logging
from django.contrib.auth.models import User
from hue_converters import DocumentConverterHueScripts

LOG = logging.getLogger(__name__)

class DocumentConversionRunner(object):
  """
  Given a user, converts any existing Document objects to Document2 objects
  """

  def __init__(self, usernames, allowdupes=False, startqueryname=None, startuser=None):
    self.usernames = usernames
    self.allowdupes = allowdupes
    self.startqueryname = startqueryname
    self.startuser = startuser


  def runconversions(self):
    if not self.usernames:
      users = User.objects.all()
    else:
      userlist = self.usernames.split(",")
      users = User.objects.filter(username__in = userlist)

    if self.startqueryname or self.startuser:
      processdocs = False
    else:
      processdocs = True

    LOG.info("Converting docs for %s users" % users.count())
    for user in users:

      LOG.info("Converting docs for user: %s" % user.username)
      if user.username == self.startuser:
        processdocs = True

      start = time.time()

      try:
        converter = DocumentConverterHueScripts(user, allowdupes = self.allowdupes, startqueryname = self.startqueryname, startuser = self.startuser, processdocs = processdocs)
        processdocs = converter.convertfailed()
      except:
        LOG.warn("Conversions failed for user: %s" % user.username)
      end = time.time()
      elapsed = (end - start) / 60
      LOG.info("Finished user: %s : elapsed time: %s" % (user.username, elapsed))



