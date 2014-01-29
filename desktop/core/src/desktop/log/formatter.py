import logging
import os

from pytz import timezone, datetime


class Formatter(logging.Formatter):
  def formatTime(self, record, datefmt=None):
    try:
      tz = timezone(os.environ['TZ'])
      ct = datetime.datetime.fromtimestamp(record.created, tz=tz)
    except:
      try:
        ct = datetime.datetime.fromtimestamp(record.created)
      except:
        # Fallback to original.
        return super(Formatter, self).formatTime(record, datefmt=datefmt)

    if datefmt:
      s = ct.strftime(datefmt)
    else:
      t = ct.strftime("%Y-%m-%d %H:%M:%S")
      s = "%s,%03d" % (t, record.msecs)
    return s
