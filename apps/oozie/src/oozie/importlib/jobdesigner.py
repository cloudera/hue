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

from jobsub.models import OozieMapreduceAction, OozieStreamingAction, OozieJavaAction

from oozie.models import Mapreduce, Java, Streaming


LOG = logging.getLogger(__name__)


def get_root_action(design):
  root = design.root_action
  if root is None:
    return None
  if root.action_type == OozieMapreduceAction.ACTION_TYPE:
    return root.ooziemapreduceaction
  elif root.action_type == OozieStreamingAction.ACTION_TYPE:
    return root.ooziestreamingaction
  elif root.action_type == OozieJavaAction.ACTION_TYPE:
    return root.ooziejavaaction

  LOG.error("Oozie action type '%s' is not valid (jobsub_oozieaction.id %s)" % (root.action_type, root.id))
  return None


def convert_jobsub_design(jobsub_design):
  """Creates an oozie action from a jobsub design"""
  action = get_root_action(jobsub_design)
  if action is None:
    return None
  if action.action_type == OozieMapreduceAction.ACTION_TYPE:
    action = _convert_jobsub_mapreduce_action(action)
  elif action.action_type == OozieStreamingAction.ACTION_TYPE:
    action = _convert_jobsub_streaming_action(action)
  elif action.action_type == OozieJavaAction.ACTION_TYPE:
    action = _convert_jobsub_java_action(action)
  else:
    return None
  action.name = jobsub_design.name
  action.description = jobsub_design.description
  return action

VARIABLE_NAME_REGEX = re.compile('(?<!\$)\$(\w+)')
def _translate_jobsub_contents(contents):
  return VARIABLE_NAME_REGEX.sub(r'${\1}', contents)

def _convert_jobsub_mapreduce_action(jobsub_action):
  action = Mapreduce(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    jar_path=_translate_jobsub_contents(jobsub_action.jar_path),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties))
  action.node_type = Mapreduce.node_type
  return action

def _convert_jobsub_streaming_action(jobsub_action):
  action = Streaming(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties),
    mapper=_translate_jobsub_contents(jobsub_action.mapper),
    reducer=_translate_jobsub_contents(jobsub_action.reducer))
  action.node_type = Streaming.node_type
  return action

def _convert_jobsub_java_action(jobsub_action):
  action = Java(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    jar_path=_translate_jobsub_contents(jobsub_action.jar_path),
    main_class=_translate_jobsub_contents(jobsub_action.main_class),
    args=_translate_jobsub_contents(jobsub_action.args),
    java_opts=_translate_jobsub_contents(jobsub_action.java_opts),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties))
  action.node_type = Java.node_type
  return action
