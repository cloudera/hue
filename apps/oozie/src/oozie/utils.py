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

import logging
import re

from django.utils.translation import ugettext as _
from jobsub.parameterization import find_variables


LOG = logging.getLogger(__name__)

def model_to_dict(model):
  from django.db import models
  from datetime import datetime
  dictionary = {}
  for field in model._meta.fields:
    try:
      attr = getattr(model, field.name, None)
      if isinstance(attr, models.Model):
        dictionary[field.name] = attr.id
      elif isinstance(attr, datetime):
        dictionary[field.name] = str(attr)
      else:
        dictionary[field.name] = attr
    except Exception, e:
      LOG.debug(_("Could not set field %(field)s: %(exception)s") % {'field': field.name, 'exception': str(e)})
  return dictionary


def workflow_to_dict(workflow):
  workflow_dict = model_to_dict(workflow)
  node_list = [node.get_full_node() for node in workflow.node_list]
  nodes = [model_to_dict(node) for node in node_list]

  for index, node in enumerate(node_list):
    nodes[index]['child_links'] = [model_to_dict(link) for link in node.get_all_children_links()]

  workflow_dict['nodes'] = nodes

  return workflow_dict


def smart_path(path, mapping):
  # Try to prepend home_dir and FS scheme if needed.
  # If path starts by a parameter try to get its value from the list of parameters submitted by the user or the coordinator.
  # This dynamic checking enable the use of <prepares> statements in a workflow scheduled manually of by a coordinator.
  # The logic is a bit complicated but Oozie is not consistent with data paths, prepare, coordinator paths and Fs action.

  if not path.startswith('$') and not path.startswith('/') and not path.startswith('hdfs://'):
    path = '/user/%(username)s/%(path)s' % {'username': '${wf:user()}', 'path': path}

  if path.startswith('$'):
    variables = find_variables(path)
    for var in variables:
      prefix = '${%s}' % var
      if path.startswith(prefix):
        if var in mapping:
          if not mapping[var].startswith('hdfs://') and not mapping[var].startswith('$'):
            path = '%(nameNode)s%(path)s' % {'nameNode': '${nameNode}', 'path': path}
  else:
    if not path.startswith('hdfs://'):
      path = '%(nameNode)s%(path)s' % {'nameNode': '${nameNode}', 'path': path}

  return path


def xml_tag(element):
  return re.sub(r'^\{.+\}', '', element.tag)
