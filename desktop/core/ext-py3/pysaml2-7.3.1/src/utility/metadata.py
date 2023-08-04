import logging
import os.path
import time
from time import strftime
import urllib


__author__ = "rhoerbe"

logger = logging.getLogger(__name__)


def fetch_metadata(url, path, maxage=600):
    """
    :param url:  metadata remote location
    :param path: metdata file name
    :param maxage: if max age of existing metadata file (s) is exceeded,
     the file will be fetched from the remote location
    """
    fetch = False
    if not os.path.isfile(path):
        fetch = True
        logger.debug("metadata file %s not found", path)
    elif (os.path.getmtime(path) + maxage) < time.time():
        fetch = True
        logger.debug(
            "metadata file %s from %s is more than %s s old",
            path,
            strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path))),
            maxage,
        )
    else:
        logger.debug("metadata file %s is less than %s s old", path, maxage)
    if fetch:
        f = urllib.URLopener()
        try:
            f.retrieve(url, path)
            logger.debug("downloaded metadata from %s into %s", url, path)
        except Exception as e:
            logger.debug("downloaded metadata from %s failed: %s", url, str(e))
