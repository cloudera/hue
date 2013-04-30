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
  <li><a href="/${ app }${ extra_path }"><i class="icon-double-angle-right"></i> ${ label is not None and label or apps[app].nice_name }</a></li>
</%def>

<div style="position: absolute;top:80px;right:30px"><img src="/static/art/hue-logo-subtle.png"/></div>

<div class="container-fluid">
  <h1>${_('Welcome Home.')}</h1>

  <div class="row-fluid">
    <div class="span12">
      <p>
        ${ _('Hue is a Web UI for Apache Hadoop. Please select an application below.') }
      </p>
    </div>
  </div>

  <div class="row-fluid" style="margin-top: 30px">

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Query')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("beeswax", _('Hive')) }
            ${ app_link("impala", _('Impala')) }
            ${ app_link("pig") }
            ${ app_link("shell", _('Shell')) }
          </ul>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Hadoop')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("filebrowser", _('Files')) }
            ${ app_link("jobbrowser", _('Jobs')) }
            ${ app_link("catalog", _('Tables')) }
            ${ app_link("jobsub", _('Designs')) }
          </ul>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Workflow')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("oozie", _('Dashboard')) }
            ${ app_link("oozie", _('Editor'), "/list_workflows/") }
          </ul>
        </div>
      </div>
    </div>
  </div>

</div>

${ commonfooter(messages) | n,unicode }
