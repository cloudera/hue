## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

${'<%!'}
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
${'%>'}

${'<%'}def name="menubar(section='')">
  <div class="subnav subnav-fixed">
    <div class="container-fluid">
      <ul class="nav nav-pills">
        <li class="${'$'}{is_selected(section, 'mytab')}"><a href="#">Tab 1</a></li>
        <li class="${'$'}{is_selected(section, 'mytab2')}"><a href="#">Tab 2</a></li>
      </ul>
    </div>
  </div>
${'</%'}def>
