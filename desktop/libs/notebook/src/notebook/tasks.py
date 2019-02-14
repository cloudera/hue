from __future__ import absolute_import, unicode_literals
import os
import django
# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")
django.setup()
from django.conf import settings

from celery import Celery
app = Celery("desktop")
app.config_from_object('django.conf:settings', namespace='CELERY')

import json
import logging

from desktop import conf
from desktop.conf import ENABLE_DOWNLOAD, USE_NEW_EDITOR

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.http import HttpRequest
from django.contrib.auth.models import User

from notebook.connectors.base import get_api, _get_snippet_name
from django.contrib.auth import authenticate

@app.task()
def download(postdict, notebook, snippet, file_format):
    request = HttpRequest()
    request.POST = postdict
    user = authenticate(username="admin",password="admin")
    request.user = user
    response = get_api(request, snippet).download(notebook, snippet, file_format)
    f=open("/tmp/foo","w")
    for data in response.streaming_content:
      f.write(data)
    f.close()
    return 0

if __name__ == '__main__':
    task = download.s(notebook, snippet, file_format).delay()
