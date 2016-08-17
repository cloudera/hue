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
<%
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="require" file="/require.mako" />

${ commonheader("Job Browser", "jobbrowser", user) | n,unicode }

${ require.config() }


<div class="navbar navbar-inverse navbar-fixed-top nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="currentApp">
              <a href="/${app_name}">
                <img src="${ static('jobbrowser/art/icon_jobbrowser_48.png') }" class="app-icon"/>
                ${ _('Job Browser') }
              </a>
            </li>
          </ul>
          % if not hiveserver2_impersonation_enabled:
            <div class="pull-right alert alert-warning" style="margin-top: 4px">${ _("Hive jobs are running as the 'hive' user") }</div>
          % endif
        </div>
      </div>
    </div>
</div>


<div class="container-fluid">

  ${_('Username')} <input id="userFilter" type="text" class="input-medium search-query" placeholder="${_('Search for username')}" value="${ user_filter or '' }">
  &nbsp;&nbsp;${_('Text')} <input id="textFilter" type="text" class="input-xlarge search-query" placeholder="${_('Search for id, name, status...')}" value="${ text_filter or '' }">

  <span class="btn-group">
    <a class="btn btn-status" data-value="completed">${ _('Jobs') }</a>
    <a class="btn btn-status" data-value="running">${ _('Batches') }</a>
    <a class="btn btn-status" data-value="killed">${ _('Schedules') }</a>
  </span>

  <div class="card card-small">

  <table id="jobsTable" class="datatables table table-condensed">
    <thead>
    <tr>
      <th>${_('Logs')}</th>
      <th>${_('Id')}</th>
      <th>${_('Name')}</th>
      <th>${_('Type')}</th>
      <th>${_('Status')}</th>
      <th>${_('User')}</th>
      <th>${_('Cluster')}</th>
      <th>${_('Progress')}</th>
      <th>${_('Duration')}</th>
      <th>${_('Submitted')}</th>
    </tr>
    </thead>
    <tbody data-bind="foreach: apps">
      <tr>
        <td></td>
        <td data-bind="text: id"></td>
        <td data-bind="text: name"></td>
        <td data-bind="text: type"></td>
        <td data-bind="text: status"></td>
        <td data-bind="text: user"></td>
        <td data-bind="text: cluster"></td>
        <td data-bind="text: progress"></td>
        <td data-bind="text: duration"></td>
        <td data-bind="text: submitted"></td>
      </tr>
    </tbody>
  </table>
    </div>
</div>


<script type="text/javascript" charset="utf-8">
  require([
    "knockout",
    "ko.charts",
    "desktop/js/apiHelper",
    "notebook/js/notebook.ko",
    "knockout-mapping",
    "knockout-sortable",
    "ko.editable",
    "ko.hue-bindings"
  ], function (ko, charts, ApiHelper, EditorViewModel) {

    var Job = function (vm, job) {
      var self = this;

      self.id = ko.observable(typeof job.id != "undefined" && job.id != null ? job.id : null);
      self.name = ko.observable(typeof job.name != "undefined" && job.name != null ? job.name : null);
      self.type = ko.observable(typeof job.type != "undefined" && job.type != null ? job.type : null);
      self.status = ko.observable(typeof job.status != "undefined" && job.status != null ? job.status : null);
      self.user = ko.observable(typeof job.user != "undefined" && job.user != null ? job.user : null);
      self.cluster = ko.observable(typeof job.cluster != "undefined" && job.cluster != null ? job.cluster : null);
      self.progress = ko.observable(typeof job.progress != "undefined" && job.progress != null ? job.progress : null);
      self.duration = ko.observable(typeof job.duration != "undefined" && job.duration != null ? job.duration : null);
      self.submitted = ko.observable(typeof job.submitted != "undefined" && job.submitted != null ? job.submitted : null);
    };

    var JobBrowserViewModel = function (options) {
      var self = this;

      self.apps = ko.observableArray();
      self.loadingApps = ko.observable(false);

      self.fetchJobs = function (callback) {
        self.loadingApps(true);
        $.get("/jobbrowser/api/jobs", {
        }, function(data) {
          var apps = [];
          if (data && data.apps){
            data.apps.forEach(function(job){
              apps.push(new Job(self, job));
            });
          }
          self.apps(apps);
        }).always(function(){
          self.loadingApps(false);
        });
      };
    };

    var viewModel;

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
        }
      }
      viewModel = new JobBrowserViewModel(options);
      ko.applyBindings(viewModel);

      viewModel.fetchJobs();
    });
  });
</script>

${ commonfooter(request, messages) | n,unicode }
