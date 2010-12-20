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
from desktop.lib.conf import BoundConfig
%>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <title>Hue Configuration Check</title>
</head>

<body>
  <dl>
    <dt><a target="_blank" href="${url("desktop.views.dump_config")}">View configuration</a></dt>
    <dd>Configuration files located in <code>${conf_dir}</code></dd>
  </dl>
  <dl>
    % if error_list:
      <h3>Potential misconfiguration detected. Please fix and restart HUE.</h3>
      <dl>
      % for confvar, error in error_list:
        <dt>
          <code>
            % if isinstance(confvar, str):
              ${confvar | n}
            % else:
              ${confvar.get_fully_qualifying_key()}
            % endif
          </code>
        </dt>
        <dd>
          ## Doesn't make sense to print the value of a BoundContainer
          % if type(confvar) is BoundConfig:
            Current value: <code>${confvar.get()}</code><br/>
          % endif
          ${error | n}
        </dd>
      % endfor
      </dl>
    % else:
      All ok. Configuration check passed!
    % endif
  </dl>
</body>
