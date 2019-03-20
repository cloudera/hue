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
<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

% if not is_embeddable:
${ commonheader(_("Bundle Editor"), "Oozie", user, request) | n,unicode }
% endif

<div id="oozie_bundleComponents">

<%def name="buttons()">
  <div class="pull-right" style="padding-right: 10px">

    <div data-bind="visible: bundle.isDirty() || bundle.id() == null" class="pull-left muted" style="padding-top: 12px; padding-right: 8px">
      ${ _('Unsaved') }
    </div>

    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true, 'disabled': bundle.isDirty()}, visible: bundle.id() != null">
      <i class="fa fa-play"></i>
    </a>

    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}, visible: canEdit">
      <i class="fa fa-pencil"></i>
    </a>

    <a type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true, 'disabled': $root.isSaving()}, visible: canEdit() && bundle.coordinators().length > 0">
      <i class="fa fa-save"></i>
    </a>


    <div class="dropdown pull-right margin-left-10">
      <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
        <i class="fa fa-fw fa-ellipsis-v"></i>
      </a>
      <ul class="dropdown-menu">
        <li>
          <a href="javascript: void(0)" data-bind="hueLink: '${ url('oozie:new_bundle') }'">
            <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
          </a>
        </li>
        %if is_embeddable:
          <li>
            <a href="javascript: void(0)" data-bind="publish: { 'assist.show.documents': 'oozie-bundle2' }">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> ${ _('Bundles') }
            </a>
          </li>
        %endif
        <li class="divider"></li>
        <li data-bind="visible: canEdit">
          <a class="pointer" data-toggle="modal" data-target="#settingsModal">
            <i class="fa fa-fw fa-cog"></i> ${ _('Settings') }
          </a>
        </li>
        <li data-bind="visible: bundle.id() != null && canEdit()">
          <a class="pointer share-link" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal, css: {'isShared': isShared()}">
            <i class="fa fa-fw fa-users"></i> ${ _("Share") }
          </a>
        </li>
      </ul>
    </div>
  </div>
</%def>

${ layout.menubar(section='bundles', is_editor=True, pullright=buttons, is_embeddable=is_embeddable) }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("bundle") > -1) {
      var url = "/oozie/editor/bundle/edit/?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
      % if is_embeddable:
        huePubSub.publish('open.link', url);
      % else:
        location.href = url;
      % endif
    }
  }
</script>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12 bundle">

      <div class="card card-home" style="padding-bottom: 10px">
        <h1 class="card-heading simple" style="border-bottom: none"><span data-bind="editable: $root.bundle.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span></h1>
        <div class="card-body muted" style="margin-top: 2px" data-bind="visible: $root.isEditing() || (! $root.isEditing() && $root.bundle.properties.description)">
          <span data-bind="editable: $root.bundle.properties.description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_ko('Add a description...')}'}"></span>
        </div>
      </div>

      <div class="card card-home" style="margin-top: 20px; margin-bottom: 20px; padding-bottom: 10px" data-bind="visible: isEditing">
        <h1 class="card-heading simple">${ _('Which schedules to bundle?') }</h1>

        <div class="card-body">
          <span class="muted" data-bind="visible: bundle.coordinators().length == 0 && ! isEditing()">${ _('This bundle has no defined coordinators.') }</span>
          <a class="pointer" data-bind="click: function() { showChooseCoordinator(); }, visible: $root.isEditing">
            <i class="fa fa-plus"></i> ${ _('Add a coordinator') }
          </a>
        </div>
      </div>

      <div data-bind="foreach: bundle.coordinators">
        <div class="card card-home" style="margin-bottom: 20px; padding-bottom: 10px">
          <h1 class="card-heading simple">
            <a class="pointer" data-bind="click: function() { showChooseCoordinator(this); }, text: $root.getCoordinatorById(coordinator()).name"></a>
            <a data-bind="hueLink: '${ url('oozie:edit_coordinator') }?coordinator=' + $root.getCoordinatorById(coordinator()).id()" title="${ _('Open') }">
              <i class="fa fa-external-link-square"></i>
            </a>
            <a class="pointer pull-right" data-bind="click: function() { $root.bundle.coordinators.remove(this); }, visible: $root.isEditing">
              <i class="fa fa-times"></i>
            </a>
          </h1>

          <div class="card-body">
            <ul data-bind="foreach: properties" class="unstyled with-margin">
              <li data-bind="visible: ! $root.isEditing()">
                <strong data-bind="text: name"></strong>
                <em data-bind="text: value"></em>
              </li>
              <li data-bind="visible: $root.isEditing">
                <input data-bind="value: name" type="text" class="no-margin-bottom"/>
                <div class="controls inline-block">
                  <input data-bind="value: value, filechooser: value" type="text" class="input-xlarge filechooser-input"/>
                  <!-- ko template: { name: 'calendar-dropdown' } --><!-- /ko -->
                </div>
                <a href="#" data-bind="click: function(){ $parent.properties.remove(this); }">
                  <i class="fa fa-minus"></i>
                </a>
              </li>
            </ul>

            <a class="pointer" data-bind="click: function(){ $data.properties.push({'name': '', 'value': ''}); }, visible: $root.isEditing">
              <i class="fa fa-plus"></i> ${ _('Add a parameter') }
            </a>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>


<div id="chooseCoordinatorDemiModal" class="${ is_embeddable and 'modal' or 'demi-modal' } fade" data-backdrop="${ is_embeddable and 'true' or 'false' }">
  %if is_embeddable:
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Choose a coordinator') }</h2>
    </div>
  %endif
  <div class="modal-body">
    %if not is_embeddable:
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    %endif
    <div style="float: left; margin-right: 10px;text-align: center">
      <input type="text" data-bind="clearable: $root.coordinatorModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter coordinators')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.filteredModalCoordinators().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.filteredModalCoordinators().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li style="${ not is_embeddable and 'line-height: 30px' or ''}">
          <span data-bind="click: selectCoordinator" class="badge badge-info"><span data-bind="text: name(), attr: {'title': uuid()}"></span>
          </span>
          <a data-bind="hueLink: '${ url('oozie:edit_coordinator') }?uuid=' + uuid()" title="${ _('Open') }">
            <i class="fa fa-external-link-square"></i>
          </a>
        </li>
      </ul>
      <div class="label inline" data-bind="visible: $root.filteredModalCoordinators().length == 0" style="line-height: 30px">
        ${_('There are no coordinators matching your search term.')}
      </div>
    </div>
  </div>
  %if not is_embeddable:
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
  %endif
</div>


<div id="settingsModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 id="myModalLabel" class="modal-title">${ _('Settings') }</h2>
  </div>
  <div class="modal-body">
      <h4>${ _('Kick off time') }</h4>
      <div class="controls">
        <input data-bind="value: bundle.properties.kickoff" type="text" class="no-margin-bottom"/>
        <!-- ko template: { name: 'calendar-dropdown' } --><!-- /ko -->
      </div>

      <h4>${ _('Submission Parameters') }</h4>
      <ul data-bind="foreach: bundle.properties.parameters" class="unstyled">
        <!-- ko if: ['oozie.use.system.libpath', 'start_date', 'end_date'].indexOf(typeof name == 'function' ? name() : name) == -1 -->
        <li>

          <input data-bind="value: name" type="text" class="no-margin-bottom"/>
          <div class="controls inline-block">
            <input data-bind="value: value, filechooser: value" type="text" class="filechooser-input"/>
            <!-- ko template: { name: 'calendar-dropdown' } --><!-- /ko -->
          </div>
          <a href="#" data-bind="click: function(){ $root.bundle.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
        <!-- /ko -->
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.bundle.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>
  </div>
</div>


<div class="submit-modal modal hide"></div>


</div>

<script type="text/html" id="calendar-dropdown">
<div class="btn-group">
  <a class="btn btn-default dropdown-toggle" data-toggle="dropdown">
    <i class="fa fa-calendar"></i>
    <span class="caret"></span>
  </a>
  <ul class="dropdown-menu pull-right" role="menu">
    <li>
      <a class="pointer now-link">
        ${ _('Now') }
      </a>
      <a class="pointer calendar-link">
        ${ _('Calendar') }
      </a>
    </li>
  </ul>
</div>
</script>


<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('oozie/css/common-editor.css') }">
<link rel="stylesheet" href="${ static('oozie/css/coordinator-editor.css') }">

${ dashboard.import_layout() }

%if not is_embeddable:
${ commonshare() | n,unicode }
%endif

% if not is_embeddable:
<script src="${ static('desktop/js/share2.vm.js') }"></script>
%endif

${ dashboard.import_bindings() }

<script src="${ static('oozie/js/bundle-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>

${ utils.submit_popup_event() }

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>


<script type="text/javascript">
  var viewModel = new BundleEditorViewModel(${ bundle_json | n,unicode }, ${ coordinators_json | n,unicode }, ${ can_edit_json | n,unicode });
  ko.applyBindings(viewModel, $("#oozie_bundleComponents")[0]);

  viewModel.bundle.tracker().markCurrentStateAsClean();

  % if not is_embeddable:
  var shareViewModel = initSharing("#documentShareModal");
  % endif
  shareViewModel.setDocUuid('${ doc_uuid }');

  var tempCoordinator = null;
  function showChooseCoordinator(coord) {
    if (typeof coord != "undefined"){
      tempCoordinator = coord;
    }
    $("#chooseCoordinatorDemiModal").modal("show");
  }

  function selectCoordinator(coord) {
    if (tempCoordinator != null){
      tempCoordinator.coordinator(coord.uuid());
      tempCoordinator = null;
    }
    else  {
      viewModel.addBundledCoordinator(coord.uuid());
    }
    $("#chooseCoordinatorDemiModal").modal("hide");
  }

  $(document).ready(function() {
    $("#chooseCoordinatorDemiModal").modal({
      show: false
    });
    $(window).bind("keydown", "esc", function () {
      if (window.location.pathname.indexOf('/oozie/editor/bundle') > -1) {
        if ($(".demi-modal.fade.in").length > 0) {
          $(".demi-modal.fade.in .demi-modal-chevron").click();
        }
      }
    });

    $(document).on("click", ".now-link", function () {
      if (window.location.pathname.indexOf('/oozie/editor/bundle') > -1) {
        $(this).parents(".controls").find("input[type='text']").val(moment().format("YYYY-MM-DD[T]HH:mm[Z]"));
      }
    });

    $(document).on("click", ".calendar-link", function () {
      if (window.location.pathname.indexOf('/oozie/editor/bundle') > -1) {
        var DATE_FORMAT = "YYYY-MM-DD";
        var _el = $(this).parents(".controls").find("input[type='text']");
        _el.off("keyup");
        _el.on("keyup", function () {
          _el.data("lastValue", _el.val());
        });
        _el.data("lastValue", _el.val());
        _el.datepicker({
          format: DATE_FORMAT.toLowerCase()
        }).on("changeDate", function () {
          _el.datepicker("hide");
        }).on("hide", function () {
          var _val = _el.data("lastValue") ? _el.data("lastValue") : _el.val();
          if (_val.indexOf("T") == -1) {
            _el.val(_el.val() + "T00:00Z");
          }
          else if (_el.val().indexOf("T") == "-1") {
            _el.val(_el.val() + "T" + _val.split("T")[1]);
          }
        });
        _el.datepicker('show');
        huePubSub.subscribeOnce('hide.datepicker', function () {
          _el.datepicker('hide');
        });
      }
    });

    huePubSub.subscribe('submit.popup.return', function (data) {
      if (data.type == 'bundle') {
        $.jHueNotify.info('${_('Bundle submitted.')}');
        huePubSub.publish('open.link', '/jobbrowser/#!id=' + data.job_id);
        huePubSub.publish('browser.job.open.link', data.job_id);
        $('.submit-modal').modal('hide');
        $('.modal-backdrop').hide();
      }
    }, 'oozie');
  });
</script>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
