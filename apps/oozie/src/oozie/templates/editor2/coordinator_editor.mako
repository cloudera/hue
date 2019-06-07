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
from django.utils.translation import ugettext as _
from desktop.views import commonheader, commonfooter, commonshare, _ko
%>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="coordinator_utils" file="coordinator_utils.mako" />
<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="scheduler" file="common_scheduler.inc.mako" />

%if not is_embeddable:
${ commonheader(_("Coordinator Editor"), "Oozie", user, request) | n,unicode }
%endif

<div id="oozie_coordinatorComponents">

<%def name="buttons()">
  <div class="pull-right" style="padding-right: 10px">

    <div data-bind="visible: coordinator.isDirty() || coordinator.id() == null" class="pull-left muted" style="padding-top: 12px; padding-right: 8px">
      ${ _('Unsaved') }
    </div>

    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true, 'disabled': coordinator.isDirty()}, visible: coordinator.id() != null">
      <i class="fa fa-play"></i>
    </a>

    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}, visible: canEdit">
      <i class="fa fa-pencil"></i>
    </a>

    <a title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
        data-bind="click: $root.save, css: {'btn': true, 'disabled': $root.isSaving()}, visible: coordinator.properties.workflow() && canEdit">
      <i class="fa fa-save"></i>
    </a>

    <div class="dropdown pull-right margin-left-10">
      <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
        <i class="fa fa-fw fa-ellipsis-v"></i>
      </a>
      <ul class="dropdown-menu">
        <li>
          <a href="javascript: void(0)" data-bind="hueLink: '${ url('oozie:new_coordinator') }'">
            <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
          </a>
        </li>
        %if is_embeddable:
          <li>
            <a href="javascript: void(0)" data-bind="publish: { 'assist.show.documents': 'oozie-coordinator2' }">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> ${ _('Schedules') }
            </a>
          </li>
        %endif
        <li class="divider"></li>
        <li data-bind="visible: canEdit">
          <a class="pointer" data-toggle="modal" data-target="#settingsModal">
            <i class="fa fa-fw fa-cog"></i> ${ _('Settings') }
          </a>
        </li>
        <li data-bind="visible: coordinator.id() != null && canEdit()">
          <a class="pointer share-link" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal, css: {'isShared': isShared()}">
            <i class="fa fa-fw fa-users"></i> ${ _("Share") }
          </a>
        </li>
      </ul>
    </div>


  </div>
</%def>

${ layout.menubar(section='coordinators', is_editor=True, pullright=buttons, is_embeddable=is_embeddable) }


<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("coordinator") > -1) {
      var url = "/oozie/editor/coordinator/edit/?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
      % if is_embeddable:
        huePubSub.publish('open.link', url);
      % else:
        location.href = url;
      % endif
    }
  }
</script>

${ scheduler.import_layout() }
${ scheduler.import_modals() }


<div class="submit-modal modal hide"></div>

</div>

<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">
<link rel="stylesheet" href="${ static('oozie/css/coordinator-editor.css') }">

<link href="${ static('desktop/css/jqCron.css') }" rel="stylesheet" type="text/css" />
<script src="${ static('desktop/js/jqCron.js') }" type="text/javascript"></script>

${ dashboard.import_layout() }

%if not is_embeddable:
${ commonshare() | n,unicode }
%endif

% if not is_embeddable:
<script src="${ static('desktop/js/share2.vm.js') }"></script>
%endif


${ dashboard.import_bindings() }

<script src="${ static('oozie/js/coordinator-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>

${ utils.submit_popup_event() }

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>

${ scheduler.import_sla_cron(coordinator_json) }

<script type="text/javascript">

  var viewModel = new CoordinatorEditorViewModel(${ coordinator_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflows_json | n,unicode }, ${ can_edit_json | n,unicode });

  ko.applyBindings(viewModel, $("#oozie_coordinatorComponents")[0]);

  viewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
  viewModel.coordinator.tracker().markCurrentStateAsClean();
  viewModel.coordinator.refreshParameters();

  % if not is_embeddable:
  var shareViewModel = initSharing("#documentShareModal");
  % endif
  shareViewModel.setDocUuid('${ doc_uuid }');

  function showChooseWorkflow() {
    $("#chooseWorkflowDemiModal").removeAttr("disabled");
    $("#chooseWorkflowDemiModal")[0].style.display = "block";
    $("#chooseWorkflowDemiModal").modal("show");
  }

  function selectWorkflow(wf) {
    viewModel.coordinator.properties.workflow(wf.uuid());
    $("#chooseWorkflowDemiModal").attr('disabled','disabled');
    $("#chooseWorkflowDemiModal")[0].style.display = "none";
    $("#chooseWorkflowDemiModal").modal("hide");
  }

  var firstToggled = true;
  $(document).on("editingToggled", function () {
    if (firstToggled && window.location.pathname.indexOf('/oozie/editor/coordinator') > -1) {
      firstToggled = false;
      viewModel.coordinator.tracker().markCurrentStateAsClean();
    }
  });

  $(document).ready(function() {
    renderJqCron();
    $("#chooseWorkflowDemiModal").modal({
      show: false
    });
    $("#chooseWorkflowDemiModal").attr('disabled','disabled');
    $("#chooseWorkflowDemiModal")[0].style.display = "none";

    $(window).bind("keydown", "esc", function () {
      if ($(".demi-modal.fade.in").length > 0) {
        $(".demi-modal.fade.in .demi-modal-chevron").click();
      }
    });

    huePubSub.subscribe('submit.popup.return', function (data) {
      if (data.type == 'schedule') {
        $.jHueNotify.info('${_('Schedule submitted.')}');
        huePubSub.publish('open.link', '/jobbrowser/#!id=' + data.job_id);
        huePubSub.publish('browser.job.open.link', data.job_id);
        $('.submit-modal').modal('hide');
        $('.modal-backdrop').hide();
      }
    }, 'oozie');
  });
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
