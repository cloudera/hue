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
  ${ layout.dashboard_sub_menubar(section='workflows') }

  <h1>
    % if oozie_coordinator:
      ${ _('Coordinator') } <a href="${ oozie_coordinator.get_absolute_url() }">${ oozie_coordinator.appName }</a> :
    % endif

    ${ _('Workflow') } ${ oozie_workflow.appName }
  </h1>

  <div class="row-fluid">
    <div class="span3">
      ${ _('Workflow') }
    </div>
    <div class="span3">
      %if hue_workflow is not None:
        <a title="${ _('Edit workflow') }" href="${ hue_workflow.get_absolute_url() }">${ hue_workflow }</a>
      % else:
        ${ oozie_workflow.appName }
      %endif
    </div>
  </div>

  % if hue_coord:
  <div class="row-fluid">
    <div class="span3">
      ${ _('Coordinator') }
    </div>
    <div class="span3">
      <a href="${ hue_coord.get_absolute_url() }">${ hue_coord.name }</a>
    </div>
  </div>
  % endif

  <div class="row-fluid">
    <div class="span3">
      ${ _('Submitter') }
    </div>
    <div class="span3">
      ${ oozie_workflow.user }
    </div>
  </div>

  <div class="row-fluid">
    <div class="span3">
      ${ _('Status') }
    </div>
    <div class="span3">
      <span class="label ${ utils.get_status(oozie_workflow.status) }">${ oozie_workflow.status }</span>
    </div>
  </div>

  <div class="row-fluid">
    <div class="span3">
      ${ _('Progress') }
    </div>
    <div class="span3">
      ${ oozie_workflow.get_progress() }%
    </div>
  </div>

  % if parameters:
    <div class="row-fluid">
      <div class="span3">
        ${ _('Variables') }
      </div>
    </div>
    % for var, value in parameters.iteritems():
      <div class="row-fluid">
        <div class="span3"></div>
        <div class="span3">
          ${ var | h }
        </div>
        <div class="span3">
          ${ utils.guess_hdfs_link(var, str(value)) | h }
        </div>
      </div>
    % endfor
  % endif

  % if has_job_edition_permission(oozie_workflow, user):
  <div class="row-fluid">
    <div class="span3">
      ${ _('Manage') }
    </div>
    <div class="span3">
      <form action="${ url('oozie:resubmit_workflow', oozie_wf_id=oozie_workflow.id) }" method="post">
      % if oozie_workflow.is_running():
        <a title="${_('Kill %(workflow)s') % dict(workflow=oozie_workflow.id)}"
          id="kill-workflow"
          class="btn small confirmationModal"
          alt="${ _('Are you sure you want to kill workflow %s?') %  oozie_workflow.id }"
          href="javascript:void(0)"
          data-url="${ url('oozie:manage_oozie_jobs', job_id=oozie_workflow.id, action='kill') }"
          data-message="${ _('The workflow was killed!') }"
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

  <br/><br/>

    <ul class="nav nav-tabs">
      % if hue_workflow:
        <li class="active"><a href="#graph" data-toggle="tab">${ _('Graph') }</a></li>
        <li><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      % else:
        <li class="active"><a href="#actions" data-toggle="tab">${ _('Actions') }</a></li>
      % endif
        <li><a href="#details" data-toggle="tab">${ _('Details') }</a></li>
        <li><a href="#configuration" data-toggle="tab">${ _('Configuration') }</a></li>
        <li><a href="#log" data-toggle="tab">${ _('Log') }</a></li>
        <li><a href="#definition" data-toggle="tab">${ _('Definition') }</a></li>
    </ul>

    <div id="workflow-tab-content" class="tab-content" style="min-height:200px">
     % if hue_workflow:
       <div id="graph" class="tab-pane active">
         % if hue_workflow is not None:
         <%
           from oozie.forms import NodeForm
           from oozie.models import Workflow, Node
           from django.forms.models import inlineformset_factory

           WorkflowFormSet = inlineformset_factory(Workflow, Node, form=NodeForm, max_num=0, can_order=False, can_delete=False)
           forms = WorkflowFormSet(instance=hue_workflow.get_full_node()).forms
         %>

           ${ hue_workflow.get_full_node().gen_status_graph(forms, oozie_workflow.get_working_actions()) }
         % endif
       </div>
     % endif

    <div class="tab-pane ${ utils.if_false(hue_workflow, 'active') }" id="actions">
      % if oozie_workflow.get_working_actions():
        <table class="table table-striped table-condensed selectable">
          <thead>
            <tr>
              <th>${ _('Logs') }</th>
              <th>${ _('Id') }</th>
              <th>${ _('Name') }</th>
              <th>${ _('Type') }</th>
              <th>${ _('Status') }</th>
              <th>${ _('External Id') }</th>

              <th>${ _('Start Time') }</th>
              <th>${ _('End Time') }</th>

              <th>${ _('Retries') }</th>
              <th>${ _('Error Message') }</th>
              <th>${ _('Transition') }</th>

              <th>${ _('Data') }</th>
            </tr>
          </thead>
          <tbody>
            % for i, action in enumerate(oozie_workflow.get_working_actions()):
              <tr>
                <td>
                  % if action.externalId:
                    <a href="${ url('jobbrowser.views.job_single_logs', jobid=action.externalId) }" data-row-selector-exclude="true"><i class="icon-tasks"></i></a>
                  % endif
                </td>
                <td>
                  <a href="${ url('oozie:list_oozie_workflow_action', action=action.id) }" data-row-selector='true'>${ action.id }</a>
                </td>
                <td>
                  % if design_link:
                    <a href="${ design_link }">${ action.name }</a>
                  % else:
                    ${ action.name }
                  % endif
                </td>
                <td>${ action.type }</td>
                <td><span class="label ${ utils.get_status(action.status) }">${ action.status }</span></td>
                <td>
                  % if action.externalId:
                    <a href="${ url('jobbrowser.views.single_job', jobid=action.externalId) }">${ action.externalId }</a>
                  % endif
                </td>

                <td>${ utils.format_time(action.startTime) }</td>
                <td>${ utils.format_time(action.endTime) }</td>

                <td>${ action.retries }</td>
                <td>${ action.errorMessage }</td>
                <td>${ action.transition }</td>

                <td>${ action.data }</td>
              </tr>
            % endfor
          <tbody>
        </table>
        % endif
      </div>

      <div class="tab-pane" id="details">
        <table class="table table-condensed">
          <tbody>
            <tr>
              <td>${ _('Group') }</td>
              <td>${ oozie_workflow.group }</td>
            </tr>
            <tr>
              <td>${ _('External Id') }</td>
              <td>${ oozie_workflow.externalId or "-" }</td>
            </tr>
            <tr>
              <td>${ _('Start Time') }</td>
              <td>${ utils.format_time(oozie_workflow.startTime) }</td>
            </tr>
            <tr>
              <td>${ _('Created Time') }</td>
              <td>${ utils.format_time(oozie_workflow.createdTime) }</td>
            </tr>
            <tr>
              <td>${ _('End Time') }</td>
              <td>${  utils.format_time(oozie_workflow.endTime) }</td>
            </tr>
            <tr>
              <td>${ _('Application Path') }</td>
              <td>${  utils.hdfs_link(oozie_workflow.appPath) }</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="tab-pane" id="configuration">
          ${ utils.display_conf(oozie_workflow.conf_dict) }
      </div>

      <div class="tab-pane" id="log">
          <pre>${ oozie_workflow.log | h }</pre>
      </div>

      <div class="tab-pane" id="definition">
          <pre>${ oozie_workflow.definition | h }</pre>
      </div>
  </div>

  <a class="btn" onclick="history.back()">${ _('Back') }</a>
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

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function() {
    $(".action-link").click(function(){
      window.location = $(this).attr('data-edit');
    });

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.attr("data-confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.primary").click(function() {
        _this.trigger('confirmation');
      });
    });

    $("#kill-workflow").bind('confirmation', function() {
      var _this = this;
      $.post($(this).attr("data-url"),
        { 'notification': $(this).attr("data-message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Error: ') }" + response['data']);
          } else {
            window.location.reload();
          }
        }
      );
      return false;
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${commonfooter(messages)}
