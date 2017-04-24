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
<%!
from django.utils.translation import ugettext as _
%>
    ${_('Configuration files located in')} <code style="color: #0B7FAD">${conf_dir}</code>

    <br/><br/>
    % if error_list:
      <div class="alert alert-warn">${_('Potential misconfiguration detected. Fix and restart Hue.')}</div>
      <br/>
        <table class="table table-condensed">
      % for error in error_list:
        <tr>
            <td width="15%">
                <code>
                ${error['name'] | n}
              </code>
            </td>
            <td>
              ## Doesn't make sense to print the value of a BoundContainer
              % if 'value' in error:
                ${_('Current value:')} <code>${error['value']}</code><br/>
              % endif
              ${error['message'] | n}
            </td>
        </tr>
      % endfor
    </table>
    % else:
      <h5>${_('All OK. Configuration check passed.')}</h5>
    % endif
