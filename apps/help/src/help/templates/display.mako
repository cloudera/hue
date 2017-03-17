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
from desktop.views import commonheader, commonfooter

def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

%if not is_embeddable:
${ commonheader("Hue Help", "help", user, request, "40px") | n,unicode }
%endif

<style type="text/css">
  .card h1, .card h2, .card h3, .card h4 {
    color: #777777;
  }

  .card h1 {
    font-size: 28px;
    font-weight: 500;
  }

  .card h2 {
    border-bottom: 1px solid #E5E5E5;
    font-size: 24px;
    font-weight: 300;
    margin-top: 30px;
  }

  .card h3 {
    font-size: 20px;
    font-weight: 300;
    margin-top: 20px;
  }

</style>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
            % for app in apps:
              <li class="${is_selected(app.name, current)}"><a href="${url("help.views.view", app=app.name, path="/")}">${app.nice_name}</a></li>
            % endfor
        </ul>
      </div>
    </div>
    <div class="span10 card card-small">
      <div class="card-body">
        <p>
          ${content|n}
        </p>
      </div>
    </div>
  </div>
</div>

<script>
  $(document).ready(function () {
    $.jHueScrollUp();
  });
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
