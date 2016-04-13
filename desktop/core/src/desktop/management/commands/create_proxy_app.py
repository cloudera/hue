
# adapted from django-extensions (http://code.google.com/p/django-command-extensions/)
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil
from django.core.management.base import CommandError, BaseCommand
from mako.template import Template

import logging
from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
  help = _("Creates a Hue proxy application directory structure.")
  args = "app_name app_web_url [app_dir]"
  label = _('application name')

  def handle(self, *args, **options):
    if len(args) > 3 or len(args) == 0:
      raise CommandError(_("Expected arguments: app_name app_web_url [app_dir]"))
    app_name = args[0]
    if len(args) == 2:
      app_url = args[1]
      app_dir = os.getcwd()
    elif len(args) == 3:
      app_url = args[1]
      app_dir = args[2]
    else:
      app_url = "http://gethue.com"
      app_dir = os.getcwd()

    app_template = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app_template_proxy'))
    assert os.path.isdir(app_template), _("App template dir missing: %(template)s.") % {'template': app_template}
    app_dir = os.path.join(app_dir, app_name)

    if not os.path.exists(app_template):
      raise CommandError(_("The template path, %(path)r, does not exist.") % {'path': app_template})

    if not re.search(r'^\w+$', app_name):
      raise CommandError(_("%(name)r is not a valid application name. Use only numbers, letters and underscores.") % {'name': app_name})
    try:
      os.makedirs(app_dir)
    except OSError, e:
      raise CommandError(e)

    copy_template(app_template, app_dir, app_name, app_url)

def copy_template(app_template, copy_to, app_name, app_url):
  """copies the specified template directory to the copy_to location"""

  app_name_spaces = " ".join(word.capitalize() for word in app_name.split("_"))
  app_name_camel = "".join(word.capitalize() for word in app_name.split("_"))

  # walks the template structure and copies it
  for directory, subdirs, files in os.walk(app_template):
    relative_dir = directory[len(app_template)+1:].replace('app_name_camel', app_name_camel).replace('app_name',app_name)
    if not os.path.exists(os.path.join(copy_to, relative_dir)):
      os.mkdir(os.path.join(copy_to, relative_dir))
    for f in files:
      if f.endswith('.pyc') or f.startswith("."):
        continue
        
      path_old = os.path.join(directory, f)
      path_new = os.path.join(copy_to, relative_dir, f.replace('app_name_camel', app_name_camel).replace('app_name', app_name))

      LOG.info("Writing %s" % path_new)
      fp_new = open(path_new, 'w')
      if path_old.endswith(".png"):
        shutil.copyfileobj(file(path_old), fp_new)
      else:
        fp_new.write( Template(filename=path_old).render(app_name=app_name, app_name_camel=app_name_camel, app_name_spaces=app_name_spaces, app_url=app_url) )
      fp_new.close()
        
      shutil.copymode(path_old, path_new)
