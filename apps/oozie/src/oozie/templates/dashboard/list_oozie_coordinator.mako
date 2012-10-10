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

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='dashboard') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='coordinators') }

  <h1>${ _('Coordinator') } ${ oozie_coordinator.appName }</h1>

    <div class="tab-pane" id="details">
      <div class="container-fluid">
        <div class="row-fluid">
          <div class="span3">${ _('Coordinator') }</div>
          <div class="span6">
              % if coordinator is not None:
                <a href="${ coordinator.get_absolute_url() }">${ oozie_coordinator.appName }</a>
              % else:
                ${ oozie_coordinator.appName }
              % endif
          </div>
        </div>

        <div class="row-fluid">
          <div class="span3">${ _('Submitter') }</div>
          <div class="span6">${ oozie_coordinator.user }</div>
        </div>

        <div class="row-fluid">
          <div class="span3">${ _('Status') }</div>
          <div class="span6"><span class="label ${ utils.get_status(oozie_coordinator.status) }">${ oozie_coordinator.status }</span>&nbsp;</div>
        </div>

        <div class="row-fluid">
          <div class="span3">
            ${ _('Progress') }
          </div>
          <div class="span3">
            ${ oozie_coordinator.get_progress() }%
          </div>
        </div>

        <div class="row-fluid">
          <div class="span3">${ _('Frequency') }</div>
          <div class="span3">${ oozie_coordinator.frequency } ${ oozie_coordinator.timeUnit }</div>
          <div class="span3">${ _('Next Materialized Time') }</div>
          <div class="span3">${ utils.format_time(oozie_coordinator.nextMaterializedTime) }</div>
        </div>


        <div class="row-fluid">
          <div class="span3">${ _('Start time') }</div><div class="span3">${ utils.format_time(oozie_coordinator.startTime) }</div>
          <div class="span3">${ _('End time') }</div><div class="span3">${ utils.format_time(oozie_coordinator.endTime) }</div>
        </div>

        % if coordinator:
          <div class="row-fluid">
            <div class="row-fluid">
              <div class="span3">${ _('Datasets') }</div>
            </div>
            % for dataset in coordinator.dataset_set.all():
              <div class="row-fluid">
                <div class="span3"></div>
                <div class="span6">${ dataset.name } : ${ dataset.uri }</div>
              </div>
            % endfor
          </div>
        % endif

        % if has_job_edition_permission(oozie_coordinator, user):
          <div class="row-fluid">
            <div class="span3">${ _('Manage') }</div>
            <div class="span6">
              <form action="${ url('oozie:resubmit_coordinator', oozie_coord_id=oozie_coordinator.id) }" method="post">
              % if oozie_coordinator.is_running():
                <a title="${_('Kill %(coordinator)s') % dict(coordinator=oozie_coordinator.id)}"
                  id="kill-coordinator"
                  class="btn small confirmationModal"
                  alt="${ _('Are you sure you want to kill coordinator %s?') % oozie_coordinator.id }"
                  href="javascript:void(0)"
                  data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_coordinator.id, action='kill') }"
                  data-message="${ _('The coordinator was killed!') }"
                  data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
                    ${_('Kill')}
                </a>
              % else:
                <button type="submit" class="btn">
                  ${ _('Resubmit') }
                </button>
              % endif
              </form>
            </div>
          </div>
        % endif
      </div>
    </div>

    <ul class="nav nav-tabs">
      <li class="active"><a href="#calendar" data-toggle="tab">${ _('Calendar') }</a></li>
    <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
    <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
    <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
    <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
    </ul>

    <div class="tab-content" style="padding-bottom:200px">
     <div class="tab-pane active" id="calendar">
        <table class="table table-striped table-condensed">
          <thead>
            <tr>
              <th>${ _('Day') }</th>
              <th>${ _('Comment') }</th>
            </tr>
          </thead>
          <tbody>
            % for i, action in enumerate(reversed(oozie_coordinator.get_working_actions())):
              <tr>
                <td>
                  % if action.externalId:
                    <a href="${ url('oozie:list_oozie_workflow', job_id=action.externalId, coordinator_job_id=oozie_coordinator.id) }"
                      data-row-selector="true"/>
                  % endif
                  <span class="label ${ utils.get_status(action.status) }">${ utils.format_time(action.nominalTime) }</span>
                </td>
                <td>${ action.errorMessage or "" } ${action.missingDependencies}</td>
              </tr>
            % endfor
          </tbody>
        </table>
      </div>

      <div class="tab-pane" id="actions">
        <table data-filters="HtmlTable" class="table table-striped table-condensed" cellpadding="0" cellspacing="0">
          <thead>
            <tr>
              <th>${ _('Number') }</th>
              <th>${ _('Nominal Time') }</th>

              <th>${ _('Type') }</th>
              <th>${ _('Status') }</th>

              <th>${ _('Error Message') }</th>
              <th>${ _('Missing Dependencies') }</th>

              <th>${ _('Created Time') }</th>
              <th>${ _('Last modified Time') }</th>

              <th>${ _('Id') }</th>
              <th>${ _('External Id') }</th>
              <th>${ _('Action') }</th>
            </tr>
          </thead>
          <tbody>
            % for i, action in enumerate(oozie_coordinator.get_working_actions()):
              <tr>

                <td>${ action.actionNumber }</td>
                <td>${ utils.format_time(action.nominalTime) }</td>

                <td>${ action.type }</td>
                <td><span class="label ${ utils.get_status(action.status) }">${ action.status }</span></td>

                <td>${action.errorMessage}</td>
                <td>${action.missingDependencies}</td>

                <td>${ utils.format_time(action.createdTime) }</td>
                <td>${ utils.format_time(action.lastModifiedTime) }</td>

                <td>
                  % if action.externalId:
                    <a href="${ url('oozie:list_oozie_workflow', job_id=action.externalId, coordinator_job_id=oozie_coordinator.id) }"
                      data-row-selector="true">${ action.id }</a>
                  % else:
                    ${ action.id }
                  % endif
                </td>
                <td>
                    ${ action.externalId or "-" }
                </td>
              </tr>
            % endfor
          <tbody>
        </table>
      </div>

    <div class="tab-pane" id="configuration">
       ${ utils.display_conf(oozie_coordinator.conf_dict) }
    </div>

    <div class="tab-pane" id="log">
        <pre>${ oozie_coordinator.log | h }</pre>
    </div>

    <div class="tab-pane" id="definition">
        <pre>${ oozie_coordinator.definition | h }</pre>
    </div>
    </div>
  </div>

  <a href="${ url('oozie:list_oozie_coordinators') }" class="btn">${ _('Back') }</a>

</div>

<div id="confirmation" class="modal hide">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3 class="message"></h3>
  </div>
  <div class="modal-footer">
    <a class="btn primary" href="javascript:void(0);">${_('Yes')}</a>
    <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
  </div>
</div>

<script>
  $("a[data-row-selector='true']").jHueRowSelector();

  $(".confirmationModal").click(function(){
    var _this = $(this);
    $("#confirmation .message").text(_this.attr("data-confirmation-message"));
    $("#confirmation").modal("show");
    $("#confirmation a.primary").click(function() {
      _this.trigger('confirmation');
    });
  });

  $("#kill-coordinator").bind('confirmation', function() {
    var _this = this;
    $.post($(this).attr("data-url"),
      { 'notification': $(this).attr("data-message") },
      function(response) {
        if (response['status'] != 0) {
          $.jHueNotify.error("${ _('Problem: ') }" + response['data']);
        } else {
          window.location.reload();
        }
      }
    );
    return false;
  });
</script>

${commonfooter(messages)}
