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

## Note that this is similar to the config_dump management command.
<%!
from desktop.lib.conf import BoundContainer, is_anonymous
%>
  
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html><head><title>Hue Configuration</title></head>
<body>
<h1>Hue Configuration</h1>
<ul><li>Configuration files located in <code>${conf_dir}</code></li></ul>
<h2>Installed applications</h2>
<ul>
% for app in sorted(apps, key=lambda app: app.name.lower()):
  % if hasattr(app, "urls_imported") and app.urls_imported:
    <li><a href="/${app.name}/">${app.display_name}</a></li>
  % else:
    <li>${app.name}</li>
  % endif
% endfor
</ul>

<h2>Configuration Variables</h2>
<%def name="recurse(config_obj)">
<dl>
  <dt>
  % if is_anonymous(config_obj.config.key):
    <i>(default section)</i>
  % else:
    ${config_obj.config.key}
  % endif
  </dt>
  <dd>
  % if isinstance(config_obj, BoundContainer):
    <p class="dump_config_help"><i>${config_obj.config.help or "No help available."}</i></p>

    % for v in config_obj.get().values():
<%
      # Don't recurse into private variables.
      if v.config.private and not show_private:
        continue
%>
    ${recurse(v)}
    % endfor
  % else:
    <p>${str(config_obj.get())}</p>
    <p class="dump_config_help"><i>${config_obj.config.help or "No help available."}</i></p>
    <p class="dump_config_default">Default: <i>${config_obj.config.default}</i></p>
  % endif
  </dd>
</dl>
</%def>

${recurse(top_level)}

<hr/>

<a href="/accounts/logout">Logout</a>
</body>
</html>
