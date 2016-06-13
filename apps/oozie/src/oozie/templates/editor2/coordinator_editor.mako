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
from desktop.views import commonheader, commonfooter, commonshare, _ko
from django.utils.translation import ugettext as _
%>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="coordinator_utils" file="coordinator_utils.mako" />
<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="scheduler" file="common_scheduler.inc.mako" />

${ commonheader(_("Coordinator Editor"), "Oozie", user) | n,unicode }

<div id="editor">

<%def name="buttons()">
  <div class="pull-right" style="padding-right: 10px">

    <div data-bind="visible: coordinator.isDirty() || coordinator.id() == null" class="pull-left muted" style="padding-top: 12px; padding-right: 8px">
      ${ _('Unsaved') }
    </div>

    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true, 'disabled': coordinator.isDirty()}, visible: coordinator.id() != null">
      <i class="fa fa-play"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}, visible: canEdit">
      <i class="fa fa-pencil"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsModal" data-bind="css: {'btn': true}, visible: canEdit">
      <i class="fa fa-cog"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
        data-bind="click: $root.save, css: {'btn': true, 'disabled': $root.isSaving()}, visible: coordinator.properties.workflow() && canEdit">
      <i class="fa fa-save"></i>
    </a>

    <a class="share-link btn" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal,
        attr: {'data-original-title': '${ _ko("Share") } ' + name},
        css: {'isShared': isShared(), 'btn': true},
        visible: coordinator.id() != null && canEdit()">
      <i class="fa fa-users"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a class="btn" href="${ url('oozie:new_coordinator') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-file-o"></i>
    </a>

  </div>
</%def>

${ layout.menubar(section='coordinators', is_editor=True, pullright=buttons) }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("coordinator") > -1) {
      location.href = "/oozie/editor/coordinator/edit/?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
    }
  }
  var datasetTypeaheadSource = ["/data/${'${'}YEAR}/${'${'}MONTH}/${'${'}DAY}", "${'${'}MINUTE}", "${'${'}HOUR}", "${'${'}DAY}", "${'${'}MONTH}", "${'${'}YEAR}", "${'${'}coord:nominalTime()}", "${'${'}coord:formatTime(coord:nominalTime(), 'yyyyMMdd')}"]

</script>


${ scheduler.import_layout() }


<div class="submit-modal modal hide"></div>

<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
      <div id="filechooser">
      </div>
  </div>
  <div class="modal-footer">
  </div>
</div>


</div>

<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">
<link rel="stylesheet" href="${ static('oozie/css/coordinator-editor.css') }">

<link href="${ static('desktop/css/jqCron.css') }" rel="stylesheet" type="text/css" />
<script src="${ static('desktop/js/jqCron.js') }" type="text/javascript"></script>

<script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/tzdetect.js') }" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">
<script src="${ static('desktop/ext/select2/select2.min.js') }" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_layout() }

${ commonshare() | n,unicode }

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/share2.vm.js') }"></script>

${ dashboard.import_bindings() }

<script src="${ static('oozie/js/coordinator-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/editor2-utils.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>


<script type="text/javascript">
  ${ utils.slaGlobal() }

  ${ utils.cron_js() }

  var coordCron =
    $('#coord-frequency')
      .jqCron({
        texts: {
          i18n: cron_i18n
        },
        enabled_minute: false,
        multiple_dom: true,
        multiple_month: true,
        multiple_mins: true,
        multiple_dow: true,
        multiple_time_hours: true,
        multiple_time_minutes: false,
        default_period: 'day',
        default_value: ${ coordinator_json | n,unicode }.properties.cron_frequency,
        no_reset_button: true,
        lang: 'i18n',
        jquery_container: $('#jqCron-container'),
        jquery_element: $('#jqCron-instance')
      })
      .jqCronGetInstance();

  $('#jqCron-container').on('cron:change', function(e, cron){
    viewModel.coordinator.properties.cron_frequency(cron);
  });

  function zeroPadding(value) {
    return (value < 10 ? '0':'') + value;
  }

  function convertDatasetVariables(path, hasSameStart, customStart, hasSameFrequency, customFrequencyUnit, startInstance, instanceChoice) {
    var _startDate = moment(viewModel.coordinator.start_date.value()).utc();
    if (!hasSameStart) {
      _startDate = moment(customStart).utc();
    }

    var _startDiffObj = {
      qty: 0,
      freq: "minutes"
    };
    if (startInstance != 0 && instanceChoice == "single") {
      _startDiffObj.qty = startInstance;
      if (hasSameFrequency) {
        var _freqs = $.trim(viewModel.coordinator.properties.cron_frequency()).split(" ");
        if (_freqs.length >= 5) {
          if (_freqs[_freqs.length - 1] == "*") {
            _startDiffObj.freq = "years";
          }
          if (_freqs[_freqs.length - 2] == "*") {
            _startDiffObj.freq = "months";
          }
          if (_freqs[_freqs.length - 3] == "*") {
            _startDiffObj.freq = "days";
          }
          if (_freqs[_freqs.length - 4] == "*") {
            _startDiffObj.freq = "hours";
          }
          if (_freqs[_freqs.length - 5] == "*") {
            _startDiffObj.freq = "minutes";
          }
        }
        else {
          _startDiffObj.qty = 0;
        }
      }
      else {
        _startDiffObj.freq = customFrequencyUnit;
      }
    }

    if (_startDate.isValid()) {
      _startDate = _startDate.add(_startDiffObj.qty, _startDiffObj.freq);
      path = path.replace(/\${'$'}{YEAR}/gi, _startDate.year());
      path = path.replace(/\${'$'}{MONTH}/gi, zeroPadding((_startDate.month() + 1)));
      path = path.replace(/\${'$'}{DAY}/gi, zeroPadding(_startDate.date()));
      path = path.replace(/\${'$'}{HOUR}/gi, zeroPadding(_startDate.hours()));
      path = path.replace(/\${'$'}{MINUTE}/gi, zeroPadding(_startDate.minutes()));
    }
    return path;
  }

  var viewModel = new CoordinatorEditorViewModel(${ coordinator_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflows_json | n,unicode }, ${ can_edit_json | n,unicode });

  ko.applyBindings(viewModel, $("#editor")[0]);

  viewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
  viewModel.coordinator.tracker().markCurrentStateAsClean();


  var shareViewModel = initSharing("#documentShareModal");
  shareViewModel.setDocUuid('${ doc_uuid }');

  function showChooseWorkflow() {
    $("#chooseWorkflowDemiModal").modal("show");
  }

  function selectWorkflow(wf) {
    viewModel.coordinator.properties.workflow(wf.uuid());
    $("#chooseWorkflowDemiModal").modal("hide");
  }

  var firstToggled = true;
  $(document).on("editingToggled", function(){
    if (firstToggled){
      firstToggled = false;
      viewModel.coordinator.tracker().markCurrentStateAsClean();
    }
  });

  $(document).ready(function() {
    $("#chooseWorkflowDemiModal").modal({
      show: false
    });
    $(window).bind("keydown", "esc", function () {
      if ($(".demi-modal.fade.in").length > 0) {
        $(".demi-modal.fade.in .demi-modal-chevron").click();
      }
    });
  });
</script>

${ commonfooter(request, messages) | n,unicode }
