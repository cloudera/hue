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

from jobbrowser.views import job_single_logs
from oozie.models import Workflow, Pig
from oozie.views.editor import _submit_workflow


LOG = logging.getLogger(__name__)


class Api:
  WORKFLOW_NAME = 'pig-app-hue-script'
  RE_LOGS = re.compile('>>> Invoking Pig command line now >>>'
                       '\n\n\nRun pig script using PigRunner.run\(\) for Pig version .+?\n'
                       '(?P<pig>.*?)'
                       '(<<< Invocation of Pig command completed <<<|<<< Invocation of Main class completed)', re.DOTALL | re.M)
  
  def __init__(self, fs, user):
    self.fs = fs
    self.user = user
    
  def submit(self, pig_script, mapping):    
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.name = Api.WORKFLOW_NAME
    workflow.is_history = True
    workflow.save()
    Workflow.objects.initialize(workflow, self.fs)
    
    script_path = workflow.deployment_dir + '/script.pig'
    self.fs.create(script_path, data=pig_script.dict['script'])
    
    action = Pig.objects.create(name='pig', script_path=script_path, workflow=workflow, node_type='pig')
    action.add_node(workflow.end)
    
    start_link = workflow.start.get_link()
    start_link.child = action
    start_link.save()    
    
    return _submit_workflow(self.user, self.fs, workflow, mapping)
  
  def get_log(self, request, oozie_workflow):    
    logs = {}
  
    for action in oozie_workflow.get_working_actions():
      try:
        if action.externalId:
          log = job_single_logs(request, **{'job': action.externalId})  
          if log:
            logs[action.name] = Api.RE_LOGS.search(log['logs'][1]).group(1)
      except Exception, e:
        LOG.error('An error happen while watching the demo running: %(error)s' % {'error': e})
  
    workflow_actions = []
    
    if oozie_workflow.get_working_actions():
      for action in oozie_workflow.get_working_actions():
        appendable = {
          'name': action.name,
          'status': action.status,
          'logs': logs.get(action.name, '')
        }
        workflow_actions.append(appendable)   
      
    return logs, workflow_actions 
