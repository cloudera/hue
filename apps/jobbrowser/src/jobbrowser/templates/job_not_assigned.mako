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

<%namespace name="comps" file="jobbrowser_components.mako" />

<%!
  from desktop.views import commonheader, commonfooter

  from django.template.defaultfilters import urlencode
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('Job'), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<link href="${ static('jobbrowser/css/jobbrowser.css') }" rel="stylesheet">

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Job ID')}</li>
          <li class="white truncate-text" title="${ jobid }">${ jobid }</li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_('Loading...')}</h1>
          <div class="card-body">
            <p>

              ${ _('The application might not be running yet or there is no Node Manager or Container available.') }
              <strong>${ _('This page will be automatically refreshed.') }</strong>

              <br/>
              <br/>

              <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
            </p>
      </div>
    </div>
  </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {

    function checkStatus() {
      $.getJSON("${ url('jobbrowser.views.job_not_assigned', jobid=jobid, path=path) }?format=json", function (data) {
        if (data.status == 1) {
          window.setTimeout(checkStatus, 1000);
        } else if (data.status == 0) {
          window.location.replace("${ path }");
        } else {
          // info js popup
          window.setTimeout(checkStatus, 1000);
        }
      });
    }

    checkStatus();
  });
</script>

${ commonfooter(request, messages) | n,unicode }
