#!/usr/bin/env python
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
"""
Upgrades a configuration from a mapping file.

Mapping files have a series of search/replace instructions in the form
s/<old_value>/<new_value>/
This will rewrite the configurations if any changes are required.
"""
import logging

import os, glob, string
import desktop.conf
import desktop.log
from desktop.lib.paths import get_desktop_root
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
  help = _('Upgrades the Hue configuration with a mapping file.')
  def add_arguments(self, parser):
    parser.add_argument('--mapping_file', help=_('Location of the mapping file.'))

  """Upgrades a configuration."""
  def handle(self, *args, **options):
    required = ("mapping_file",)
    for r in required:
      if not options.get(r):
        raise CommandError(_("--%(param)s is required.") % {'param': r})
  
    # Pull out all the mappings  
    mapping_file = options["mapping_file"]
    mapping_handle = open(mapping_file, 'r')
    mappings = []
    for mapping in mapping_handle:
      map_parts = mapping.strip().lstrip('s/')
      map_parts = map_parts.rstrip('/')
      map_parts = map_parts.split('/')
      if len(map_parts) != 2:
        raise CommandError(_("Invalid mapping %(mapping)s in %(file)s.") % {'mapping': mapping.strip(), 'file': mapping_file})
      mappings.append(map_parts)

    config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))
    for conf_file in glob.glob(os.path.join(config_dir, '*.ini')):
      LOG.info("Upgrading %s" % conf_file)
      conf_handle = open(conf_file, 'r')
      data = []
      for line in conf_handle:
        # Pull apart any variables so we don't overwrite config settings
        data.append(line.split('=', 1))

      # Iterate over mappings to perform
      for line in data:
          for mapping in mappings:
            old_value = mapping[0]
            new_value = mapping[1]

            if old_value in line[0]:
              LOG.info("Replacing %s with %s in line %s" % 
                  (old_value, new_value, '='.join(line),)) 
              line[0] = line[0].replace(old_value, new_value)
            
      
      # Rewrite file with replacements made
      conf_handle.close()
      conf_handle = open(conf_file, 'w')
      data_to_write = ''.join([ '='.join(split) for split in data ])
      conf_handle.write(data_to_write)

