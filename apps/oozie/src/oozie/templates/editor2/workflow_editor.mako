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
from desktop import conf
from django.utils.translation import ugettext as _
%>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="workflow" file="common_workflow.mako" />
<%namespace name="layout" file="../navigation-bar.mako" />

${ commonheader(_("Workflow Editor"), "Oozie", user, "40px") | n,unicode }
<div id="editor">

<%def name="buttons()">
  <div class="pull-right" style="padding-right: 10px">

    <div data-bind="visible: workflow.isDirty() || workflow.id() == null" class="pull-left muted" style="padding-top: 12px; padding-right: 8px">
      ${ _('Unsaved') }
    </div>

    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}, visible: canEdit">
      <i class="fa fa-fw fa-pencil"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true, 'disabled': workflow.isDirty()}, visible: workflow.id() != null">
      <i class="fa fa-fw fa-play"></i>
    </a>
    <a title="${ _('Schedule') }" rel="tooltip" data-placement="bottom" data-bind="click: schedule, css: {'btn': true, 'disabled': workflow.isDirty()}, visible: workflow.id() != null">
      <i class="fa fa-fw fa-calendar"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsModal" data-bind="css: {'btn': true}, visible: canEdit">
      <i class="fa fa-fw fa-cog"></i>
    </a>

    <a title="${ _('History') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#historyModal" data-bind="css: {'btn': true}, visible: workflow.id() != null && history().length > 0">
      <i class="fa fa-fw fa-history"></i>
    </a>

    <a title="${ _('Workspace') }" target="_blank" rel="tooltip" data-placement="right"
        data-original-title="${ _('Go upload additional files and libraries to the deployment directory on HDFS') }"
        data-bind="css: {'btn': true}, attr: { href: '/filebrowser/view=' + $root.workflow.properties.deployment_dir() }">
      <i class="fa fa-fw fa-folder-open"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: validateAndSave, css: {'btn': true, 'disabled': $root.isSaving()}, visible: canEdit">
      <i class="fa fa-fw fa-save"></i>
    </a>

    <a class="share-link btn" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal,
        attr: {'data-original-title': '${ _ko("Share") } ' + name},
        css: {'isShared': isShared(), 'btn': true},
        visible: workflow.id() != null && canEdit()">
      <i class="fa fa-users"></i>
    </a>

    &nbsp;&nbsp;&nbsp;

    <a class="btn" href="${ url('oozie:new_workflow') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-fw fa-file-o"></i>
    </a>

  </div>
</%def>

${ layout.menubar(section='workflows', is_editor=True, pullright=buttons) }

<style type="text/css">
  body {
    background-color: #FFFFFF;
  }
</style>

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("workflow") > -1) {
      location.href = "/oozie/editor/workflow/edit/?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
    }
  }
</script>



<%dashboard:layout_toolbar>
  <%def name="skipLayout()"></%def>
  <%def name="widgetSectionName()">${ _('ACTIONS') }</%def>
  <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHiveAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableHiveAction());}}}"
         title="${_('Hive Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="${ static('oozie/art/icon_beeswax_48.png') }" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHive2Action(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableHive2Action());}}}"
         title="${_('HiveServer2 Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="${ static('oozie/art/icon_beeswax_48.png') }" class="app-icon"><sup style="color: #338bb8; margin-left: -4px; top: -14px; font-size: 12px">2</sup></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true},
                    draggable: {data: draggablePigAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggablePigAction());}}}"
         title="${_('Pig Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="${ static('oozie/art/icon_pig_48.png') }" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSparkAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSparkAction());}}}"
         title="${_('Spark program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="${ static('oozie/art/icon_spark_48.png') }" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableJavaAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableJavaAction());}}}"
         title="${_('Java program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSqoopAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSqoopAction());}}}"
         title="${_('Sqoop 1')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="${ static('oozie/art/icon_sqoop_48.png') }" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableMapReduceAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableMapReduceAction());}}}"
         title="${_('MapReduce job')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-archive-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSubworkflowAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSubworkflowAction());}}}"
         title="${_('Sub workflow')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code-fork"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableShellAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableShellAction());}}}"
         title="${_('Shell')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-terminal"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSshAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableSshAction());}}}"
         title="${_('Ssh')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-tty"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableFsAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableFsAction());}}}"
         title="${_('HDFS Fs')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableEmailAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableEmailAction());}}}"
         title="${_('Email')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-envelope-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableStreamingAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableStreamingAction());}}}"
         title="${_('Streaming')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-exchange"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableDistCpAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableDistCpAction());}}}"
         title="${_('Distcp')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-files-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableGenericAction(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableGenericAction());}}}"
         title="${_('Generic')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableKillNode(), isEnabled: true,
                    options: {'refreshPositions': true, 'stop': function(){ $root.isDragging(false); }, 'start': function(event, ui){ $root.isDragging(true); $root.currentlyDraggedWidget(draggableKillNode());}}}"
         title="${_('Kill')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-stop"></i></a>
    </div>
</%def>
</%dashboard:layout_toolbar>


  <div class="container-fluid">
  <div class="row-fluid">
    <div class="span12" data-bind="style:{'marginTop' : $root.isEditing() ? '120px': '50px'}">
    <div class="object-name" style="text-align: center">
      <span data-bind="editable: $root.workflow.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
    </div>
    <div class="object-description" style="text-align: center; margin-top: 10px">
      <span data-bind="editable: $root.workflow.properties.description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_ko('Add a description...')}'}"></span>
    </div>
    </div>
  </div>
</div>




${ workflow.render() }


<div id="addActionDemiModal" class="demi-modal demi-modal-half hide" data-backdrop="false">
  <div class="modal-body">
    <table data-bind="foreach: addActionProperties">
      <tr>
        <td data-bind="text: label" style="width: 1%; padding-right: 10px" class="no-wrap"></td>
        <td>
          <!-- ko if: type() == '' -->
          <input type="text" class="filechooser-input" style="width:80%" data-bind="value: value, valueUpdate:'afterkeydown', filechooser: value, filechooserOptions: globalFilechooserOptions, attr: { placeholder: help_text }">
          <!-- /ko -->
          <!-- ko if: type() == 'text' -->
          <input type="text" data-bind="value: value, valueUpdate:'afterkeydown', attr: { placeholder: help_text }" class="input-xlarge"/>
          <!-- /ko -->
          <!-- ko if: type() == 'textarea' -->
          <textarea data-bind="value: value, valueUpdate:'afterkeydown'" class="input-xlarge" style="resize:both"></textarea>
          <!-- /ko -->
          <!-- ko if: type() == 'workflow' -->
          <select data-bind="options: $root.subworkflows, optionsText: 'name', optionsValue: 'value', value: value"></select>
          <!-- /ko -->

          <!-- ko if: type() == 'distcp' -->
          <ul class="unstyled">
            <li>
              ${ _('Source') }
              <input type="text" class="filechooser-input" data-bind="value: value()[0].value, valueUpdate:'afterkeydown', filechooser: value()[0].value, filechooserOptions: globalFilechooserOptions" placeholder="${ _('e.g. ${nameNode1}/path/to/input.txt') }">
            </li>
            <li>
              ${ _('Destination') }
              <input type="text" class="filechooser-input" data-bind="value: value()[1].value, valueUpdate:'afterkeydown', filechooser: value()[1].value, filechooserOptions: globalFilechooserOptions" placeholder="${ _('e.g. ${nameNode2}/path/to/output.txt') }">
            </li>
          </ul>
          <!-- /ko -->

          <!-- ko if: ['jar_path', 'script_path', 'mapper', 'reducer', 'hive_xml'].indexOf(name()) != -1 &&  value().length > 0 -->
            <span data-bind='template: { name: "common-fs-link", data: {path: value(), with_label: false}}'></span>
          <!-- /ko -->
          <!-- ko if: name() == 'workflow' && $root.getSubWorkflow(value())-->
          <span data-bind="with: $root.getSubWorkflow(value())">
            <a href="#" data-bind="attr: { href: '${ url('oozie:edit_workflow') }' + '?workflow=' + $data.value() }" target="_blank" title="${ _('Open') }">
              <i class="fa fa-external-link-square"></i>
            </a>
          </span>
          <!-- /ko -->
        </td>
      </tr>
    </table>

    <br/>
    <a class="btn btn-primary disable-feedback" data-bind="css: {'disabled': ! addActionPropertiesFilledOut()}, click: function(field){ addActionPropertiesFilledOut() ? addActionDemiModalFieldPreview(field) : void(0) } ">
      ${ _('Add') }
    </a>
  </div>
</div>

<div id="settingsModal" class="modal fade hide">
  <div class="modal-header" style="padding-bottom: 2px">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${ _('Workflow Settings') }</h3>
  </div>
  <div class="modal-body">
      <h4>${ _('Variables') }</h4>
      <ul data-bind="foreach: $root.workflow.properties.parameters" class="unstyled">
        <li>
          <input type="text" data-bind="value: name" placeholder="${ _('Name, e.g. market') }"/>
          <input type="text" data-bind="value: value" placeholder="${ _('Value, e.g. US') }"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.workflow.properties.parameters.push(ko.mapping.fromJS({'name': '', 'value': ''})); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>

      <h4>${_("Workspace")}</h4>
      <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: {value: $root.workflow.properties.deployment_dir, displayJustLastBit: true}, filechooserOptions: globalFilechooserOptions" rel="tooltip"/>
      <span data-bind='template: { name: "common-fs-link", data: {path: $root.workflow.properties.deployment_dir(), with_label: false}}'></span>

	  <h4>${ _('Hadoop Properties') }</h4>
      <ul data-bind="foreach: $root.workflow.properties.properties" class="unstyled">
        <li>
          <input type="text" data-bind="value: name" placeholder="${ _('Name, e.g. mapred.map.tasks') }"/>
          <input type="text" data-bind="value: value" placeholder="${ _('Value, e.g. ${n}') }"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.properties.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer"  data-bind="click: function(){ $root.workflow.properties.properties.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add property') }
      </a>

      <h4>${ _("Show graph arrows") }</h4>
      <input type="checkbox" data-bind="checked: $root.workflow.properties.show_arrows" title="${ _('Toggle arrow showing') }" rel="tooltip" data-placement="bottom" />

      <h4>${ _("Version") }</h4>
      <select class="input-xlarge" data-bind="value: $root.workflow.properties.schema_version, options: $root.workflow.versions"></select>

      <h4>${ _("Job XML") }</h4>
      <input type="text" class="input-xlarge filechooser-input" data-bind="filechooser: $root.workflow.properties.job_xml, filechooserOptions: globalFilechooserOptions" placeholder="${ _('Path to job.xml') }"/>
      <span data-bind='template: { name: "common-fs-link", data: {path: $root.workflow.properties.job_xml(), with_label: false}}'></span>

      <h4>${ _('SLA Configuration') }</h4>
      <div class="sla-form" data-bind="with: $root.workflow.properties">
        ${ utils.slaForm() }
      </div>
  </div>
</div>


<div id="historyModal" class="modal fade hide">
  <div class="modal-header" style="padding-bottom: 2px">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${ _('Submission History') }</h3>
  </div>
  <div class="modal-body">
    <table class="table table-condensed margin-top-20">
      <tr>
        <th width="30%">${ _('Date') }</th>
        <th>${ _('ID') }</th>
        <th width="20">&nbsp;</th>
      </tr>
      <!-- ko foreach: $root.history -->
      <tr>
        <td data-bind="text: $data.date"></td>
        <td><a data-bind="attr:{'href': '/oozie/list_oozie_workflow/' + $data.history.oozie_id() + '/' }, text: $data.history.oozie_id" target="_blank"></a></td>
        <td><a class="pointer" data-bind="click: function(){$data.expanded(!$data.expanded())}"><i class="fa fa-info-circle"></i></a></td>
      </tr>
      <tr data-bind="slideVisible: $data.expanded">
        <td colspan="3" style="padding-left: 20px;border-left: 5px solid #DDD;">
        <dl>
          <!-- ko foreach: Object.keys($data.history.properties) -->
          <dt data-bind="text: $data"></dt>
          <dd>
            <!-- ko if: typeof $parent.history.properties[$data] == 'function' -->
              <!-- ko if: typeof $parent.history.properties[$data]() == 'string' && $parent.history.properties[$data]().indexOf('/') == 0 -->
                <a data-bind="text: $parent.history.properties[$data], attr: { href: '/filebrowser/view=' + $root.workflow.properties.deployment_dir() }" target="_blank"></a>
              <!-- /ko -->
              <!-- ko ifnot: typeof $parent.history.properties[$data]() == 'string' && $parent.history.properties[$data]().indexOf('/') == 0 -->
              <span data-bind="text: $parent.history.properties[$data]"></span>
              <!-- /ko -->
            <!-- /ko -->
          </dd>
          <!-- /ko -->
          </dl>
        </td>
      </tr>
      <!-- /ko -->
    </table>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>


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
<link rel="stylesheet" href="${ static('oozie/css/workflow-editor.css') }">


${ dashboard.import_layout() }

${ commonshare() | n,unicode }

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/share.vm.js') }"></script>
<script src="${ static('desktop/js/jquery.hdfsautocomplete.js') }" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }

<script src="${ static('oozie/js/workflow-editor.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/workflow-editor.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.curvedarrow.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/editor2-utils.js') }" type="text/javascript" charset="utf-8"></script>

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .card-toolbar {
    top: 100px!important;
  }
% endif
</style>

<div id="exposeOverlay"></div>

<script type="text/javascript">
  ${ utils.slaGlobal() }

  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflow_properties_json | n,unicode }, ${ subworkflows_json | n,unicode }, ${ can_edit_json | n,unicode }, ${ history_json | n,unicode });
  ko.applyBindings(viewModel, $("#editor")[0]);

  var shareViewModel = initSharing("#documentShareModal");
  shareViewModel.setDocId(${ doc1_id });

  viewModel.init();
  viewModel.workflow.tracker().markCurrentStateAsClean();
  fullLayout(viewModel);

  var globalFilechooserOptions = {
    skipInitialPathIfEmpty: true,
    showExtraHome: true,
    uploadFile: true,
    createFolder: true,
    extraHomeProperties: {
      label: '${ _('Workspace') }',
      icon: 'fa-folder-open',
      path: viewModel.workflow.properties.deployment_dir()
    },
    deploymentDir: viewModel.workflow.properties.deployment_dir()
  }

  function columnDropAdditionalHandler(widget) {
    widgetDraggedAdditionalHandler(widget);
  }

  function widgetDraggedAdditionalHandler(widget) {
    $("canvas").remove();
    if (viewModel.currentlyDraggedWidget() && viewModel.currentlyDraggedWidget().id() == ""){
      viewModel.workflow.newNode(widget);
      showAddActionDemiModal(widget);
    }
    else {
      if (viewModel.currentlyDraggedOp() == "move"){
        viewModel.workflow.moveNode(widget);
      }
      else { // Copy
        var _sourceNode = viewModel.workflow.getNodeById(viewModel.currentlyDraggedWidget().id());
        viewModel.workflow.newNode(widget, viewModel.workflow.addNode, _sourceNode);
      }
      $(document).trigger("drawArrows");
    }
  }

  function showAddActionDemiModal(widget) {
    viewModel.newAction(widget);
    $("#exposeOverlay").fadeIn(300);
    var _el = $("#wdg_" + widget.id());
    _el.css("zIndex", "1032");
    var lastSeenPosition = _el.position();
    var _width = _el.width();

    _el.css("position", "absolute");
    _el.css({
      "top": (lastSeenPosition.top) + "px",
      "left": lastSeenPosition.left + "px",
      "width": 450
    });
    $("#addActionDemiModal").width(_el.width()).css("top", _el.offset().top + 25).css("left", _el.offset().left).modal("show");
    $("html, body").animate({
      scrollTop: $("#addActionDemiModal").offset().top - 200
    }, 200);
  }

  function addActionDemiModalFieldPreview(field) {
    if (viewModel.newAction() != null) {
      var _el = $("#wdg_" + viewModel.newAction().id());
      _el.css("position", "static");
      _el.css("width", "");
      viewModel.workflow.addNode(viewModel.newAction());
      $("#addActionDemiModal").modal("hide");
      $("#wdg_" + viewModel.newAction().id()).css("zIndex", "0");
      $("#exposeOverlay").fadeOut(300);
      viewModel.newAction(null);
    }
  }

  function addActionDemiModalFieldCancel() {
    $("#exposeOverlay").fadeOut(300);
    $("#addActionDemiModal").modal("hide");
    if (viewModel.newAction()){
      viewModel.removeWidgetById(viewModel.newAction().id());
    }
    viewModel.newAction(null);
  }

  $(document).on("editingToggled", function(){
    $("canvas").remove();
    exposeOverlayClickHandler();
    window.setTimeout(renderChangeables, 100);
  });

  function resizeDrops() {
    $(".drop-target-side").each(function () {
      var _el = $(this);
      _el.height(0);
      window.setTimeout(function(){
        _el.height(_el.parent().parent().innerHeight() - 12);
      }, 20);
    });
  }

  function renderChangeables() {
    resizeDrops();
    if (viewModel.workflow.properties.show_arrows()){
      drawArrows();
    }
    $(".widget-main-section").removeClass("zoom-in");
    $(".widget-main-section").each(function(){
      var $el = $(this);
      if (!$el.is("a") && !$el.is("input") && !$el.is("i") && !$el.is("button")) {
        var w = ko.dataFor($el.parents(".card-widget")[0]);
        if (!w.oozieExpanded() && !w.ooziePropertiesExpanded() && ["start-widget", "end-widget", "fork-widget", "join-widget"].indexOf(w.widgetType()) == -1 && $el.width() < 500){
          $el.addClass("zoom-in");
        }
      }
    });
  }

  var lastSeenPosition = null;
  var lastExpandedWidget = null;
  function setLastExpandedWidget(widget) {
    lastExpandedWidget = widget;
    if (! widget.oozieExpanded() && ["start-widget", "end-widget", "fork-widget", "join-widget"].indexOf(widget.widgetType()) == -1){
      var _el = $("#wdg_" + widget.id());
      _el.find(".widget-main-section").removeClass("zoom-in");
      if (_el.width() < 500){
        _el.css("z-index", "1032");
        lastSeenPosition = _el.position();
        var _width = _el.width();
        _el.parent().css("height", viewModel.isEditing() ? _el.height() : (_el.height() + 17) + "px");
        _el.css("position", "absolute");
        _el.css({
          "top": (lastSeenPosition.top) + "px",
          "left": lastSeenPosition.left + "px",
          "width": _width
        });
        $("#exposeOverlay").fadeIn(300);
        _el.animate({
          "width": "500px"
        }, 200, function(){
          widget.oozieExpanded(true);
          if ($(document).width() > $(window).width()){
            $("html, body").scrollLeft($(document).width() - $(window).width());
          }
        });
      }
      else {
        widget.oozieExpanded(false);
      }
    }
  }

  function exposeOverlayClickHandler() {
    if (lastExpandedWidget) {
      var _el = $("#wdg_" + lastExpandedWidget.id());
      _el.find(".prop-editor").hide();
      _el.removeAttr("style");
      _el.parent().removeAttr("style");
      lastExpandedWidget.ooziePropertiesExpanded(false);
      lastExpandedWidget.oozieExpanded(false);
    }
    addActionDemiModalFieldCancel();
    $("#exposeOverlay").fadeOut(300);
    $(document).trigger("drawArrows");
  }

  function validateAndSave() {
    validateFields();
    if (viewModel.isInvalid() && viewModel.isEditing()) {
      var $firstElWithErrors = $("[validate].with-errors").eq(0);
      if (!$firstElWithErrors.is(":visible")) {
        var widgetId = $firstElWithErrors.parents(".card-widget").attr("id").substr(4);
        viewModel.getWidgetById(widgetId).ooziePropertiesExpanded(true);
      }
      window.setTimeout(function () {
        $("html,body").animate({
          "scrollTop": ($firstElWithErrors.offset().top - 150) + "px"
        }, 500);
      }, 200);
    }

    viewModel.save();
  }

  function validateFields() {
    var _hasErrors = false;
    $("[validate]").each(function () {
      if ($(this).attr("validate") == "nonempty" && $.trim($(this).val()) == "") {
        $(this).addClass("with-errors");
        _hasErrors = true;
      }
      else {
        $(this).removeClass("with-errors");
      }
    });
    viewModel.isInvalid(_hasErrors);
  }

  $(document).ready(function(){
    renderChangeables();

    $(document).on("blur", "[validate]", function() {
      validateFields();
    });

    $("#exposeOverlay").on("click", exposeOverlayClickHandler);

    $(document).keyup(function(e) {
      if (e.keyCode == 27) {
        exposeOverlayClickHandler();
        addActionDemiModalFieldCancel();
        $("#addActionDemiModal").modal("hide");
      }
    });

    var resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        renderChangeables();
      }, 200);
    });

    $(document).on("click", ".widget-main-section", function(e){
      if (! $(e.target).is("a") && ! $(e.target).is("input") && ! $(e.target).is("i") && ! $(e.target).is("button")){
        setLastExpandedWidget(ko.dataFor($(e.target).parents(".card-widget")[0]));
      }
    });

    $.jHueScrollUp();
    $(".custom-popover").popover();
  });

</script>

${ commonfooter(request, messages) | n,unicode }
