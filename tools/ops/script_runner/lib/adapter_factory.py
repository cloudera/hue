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

import cmf.monitor.generic.adapter
import hue_adapters

class AdapterFactory(object):
  """
  Factory for making monitoring Adapter classes.
  """

  def make_adapter(self, service_type, role_type, safety_valve, daemon = None):
    """
    Makes an Adapter for the input role type.
    """
    if service_type == "HUE" and role_type == "HUE_SERVER":
      return hue_adapters.HueServerAdapter(safety_valve)
    else:
      return cmf.monitor.generic.adapter.Adapter(service_type, role_type, safety_valve)
