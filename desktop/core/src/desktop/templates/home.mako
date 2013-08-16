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
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('Home'), "home", user) | n,unicode }


<%def name="app_link(app, label=None, extra_path = '')">
  % if app in apps:
  <li>
    <a href="/${ app }/${ extra_path }"  title="${ apps[app].nice_name }" class="app-tooltips">
      <i class="icon-double-angle-right"></i> ${ label }
    </a>
  </li>
  % endif
</%def>

<div style="position: absolute;top:80px;right:30px"><img src="/static/art/hue-logo-subtle.png"/></div>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <h1>${_('Welcome Home.')}</h1>

      <p>
        ${ _('Hue is a Web UI for Apache Hadoop. Select an application below.') }
      </p>
    </div>
  </div>
  <div class="row-fluid" style="margin-top: 30px">

    <div class="span4">
      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('Query')}</h2>

        <div class="card-body">
          <p>
          <ul>
            ${ app_link("beeswax", "Hive") }
            ${ app_link("impala", "Impala") }
            ${ app_link("pig", "Pig") }
            ${ app_link("search", _('Search')) }
            ${ app_link("hbase", _('HBase')) }
            ${ app_link("shell", _('Shell')) }
          </ul>
          </p>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('Hadoop')}</h2>

        <div class="card-body">
          <p>
          <ul>
            ${ app_link("filebrowser", _('Files')) }
            ${ app_link("jobbrowser", _('Jobs')) }
            ${ app_link("metastore", _('Tables')) }
            ${ app_link("sqoop", _('Sqoop 2')) }
            ${ app_link("jobsub", _('Designs')) }
          </ul>
          </p>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="card card-home card-listcontent">
        <h2 class="card-heading simple">${_('Workflow')}</h2>

        <div class="card-body">
          <p>
          <ul>
            ${ app_link("oozie", _('Dashboard')) }
            ${ app_link("oozie", _('Editor'), "list_workflows/") }
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
    $(".app-tooltips").tooltip();
  });
</script>

${ commonfooter(messages) | n,unicode }
