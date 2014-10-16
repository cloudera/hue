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

import json
import logging

from django.utils.translation import ugettext as _

from desktop.models import Document2


LOG = logging.getLogger(__name__)


class Workflow():
  
  def __init__(self, data=None, document=None):
    self.document = document

    if document is not None:
      self.data = document.data
    elif data is not None:
      self.data = data
    else:
      self.data = json.dumps({
          'layout': [
              {"size":12,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"}
          ],
           'workflow': {}
      })
      
  def get_json(self):
    _data = self.get_data()

    if self.document is not None:
      _data['workflow']['id'] = self.document.id  

    return json.dumps(_data)
 
  def get_data(self):
    return json.loads(self.data)

