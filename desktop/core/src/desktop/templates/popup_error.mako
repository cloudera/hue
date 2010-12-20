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
<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
  </head>
  <body>
    <div class="alert_popup ccs-error-popup" data-filters="CollapsingElements">
        <code>
        ${message}
        </code>
        % if detail:
        <a><div class="collapser">Click for Details</div></a>
        <div id="data_one" class="ccs-hidden collapsible">
          <p>${detail or ""}</p>
          <p><a href="${request.path}" target="_blank"><img src="/static/art/icons/link.png" alt="[Backend Link (debugging)]"></a></p>
        </div>
        % else:
          <p/>
          <p><a href="${request.get_full_path()}" target="_blank"><img src="/static/art/icons/link.png" alt="[Backend Link (debugging)]"></a></p>
        % endif
## TODO(philip): This would be a good place to put a "feedback"/"support"
## link.
    </div>
  </body>
</html>
