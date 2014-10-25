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

<%namespace name="dashboard" file="/common_dashboard.mako" />

${ commonheader(_("Workflow Editor"), "Oozie", user) | n,unicode }


<%dashboard:layout_toolbar>
  <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableHiveAction(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Hive Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true},
                    draggable: {data: draggablePigAction(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                        'stop': function(event, ui){$('.card-body').slideDown('fast'); }}}"
         title="${_('Pig Script')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><img src="/oozie/static/art/icon_pig_48.png" class="app-icon"></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableJavaAction(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Java program')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableMapReduceAction(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('MapReduce job')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-file-code-o"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableSubworkflowAction(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Sub workflow')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-code-fork"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true }" rel="tooltip" data-placement="top">
          
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableForkNode(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Fork')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-share-alt"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableDecisionNode(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Decision')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-question"></i></a>
    </div>

    <div data-bind="css: { 'draggable-widget': true },
                    draggable: {data: draggableStopNode(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Kill')}" rel="tooltip" data-placement="top">
         <a class="draggable-icon"><i class="fa fa-stop"></i></a>
    </div>
</%def>
</%dashboard:layout_toolbar>


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">    
    <a title="${ _('Gen XML') }" rel="tooltip" data-placement="bottom" data-bind="click: gen_xml, css: {'btn': true}">
      <i class="fa fa-file-code-o"></i>
    </a>
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>    
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Workspace') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-folder-open"></i>
      </button>      
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <a class="btn" href="${ url('oozie:new_workflow') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </a>
      <a class="btn" href="${ url('oozie:list_editor_workflows') }" title="${ _('Workflows') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-tags"></i>
      </a>
    % endif
  </div>

  <form class="form-search" style="margin: 0">
    <strong>${_("Name")}</strong>
    <input data-bind="value: $root.workflow.name"/>    
  </form>
</div>


${ dashboard.layout_skeleton() }


<script type="text/html" id="start-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      Start
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="end-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="hive-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Hive') }</a></li>
        <li><a href="#files" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <img src="/oozie/static/art/icon_beeswax_48.png" class="app-icon">
        </div>
        <div class="tab-pane" id="files">
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="pig-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Pig') }</a></li>
        <li><a href="#files" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <img src="/oozie/static/art/icon_pig_48.png" class="app-icon">
          <input type="text" data-bind="value: properties.script_path" />
          </br>
	      ${ _('Variables') }   
	      <ul data-bind="foreach: properties.arguments">
	        <li>
	          <input data-bind="value: value"/>
	          <a href="#" data-bind="click: function(){ $parent.properties.arguments.remove(this); }">
	            <i class="fa fa-minus"></i>
	          </a>
	        </li>
	      </ul>
          <button data-bind="click: function(){ properties.arguments.push({'value': ''}); }">
            <i class="fa fa-plus"></i>
          </button>	      
        </div>
        <div class="tab-pane" id="files">
          prepares <input type="text" data-bind="value: properties.prepares" /></br>
          job_xml <input type="text" data-bind="value: properties.job_xml" /></br>
          proeperties <input type="text" data-bind="value: properties.properties" /></br>
          parameters <input type="text" data-bind="value: properties.parameters" /></br>
          files <input type="text" data-bind="value: properties.files" /></br>
          archives <input type="text" data-bind="value: properties.archives" /></br>
          sla <input type="text" data-bind="value: properties.sla" /></br>
          credentials <input type="text" data-bind="value: properties.credentials" /></br>
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="java-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Java') }</a></li>
        <li><a href="#files" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <input type="text" data-bind="value: properties.jar_path" />
        </div>
        <div class="tab-pane" id="files">
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="subworkflow-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#action" data-toggle="tab">${ _('Java') }</a></li>
        <li><a href="#files" data-toggle="tab">${ _('Files') }</a></li>
        <li><a href="#sla" data-toggle="tab">${ _('SLA') }</a></li>
        <li><a href="#credentials" data-toggle="tab">${ _('Credentials') }</a></li>
        <li><a href="#transitions" data-toggle="tab">${ _('Transitions') }</a></li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane active" id="action">
          <input type="text" data-bind="value: properties.jar_path" />
        </div>
        <div class="tab-pane" id="files">
        </div>
        <div class="tab-pane" id="sla">
        </div>
        <div class="tab-pane" id="credentials">
        </div>
        <div class="tab-pane" id="transitions">
          OK --> []
          KO --> []
        </div>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="fork-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="decision-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="enkill-widget">
  <!-- ko if: $root.workflow.getNodeById(id()) -->
  <div class="row-fluid" data-bind="with: $root.workflow.getNodeById(id())">
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <input type="text" data-bind="value: id" />
      <input type="text" data-bind="value: name" />
    </div>

    <div>
      End
    </div>
  </div>
  <!-- /ko -->
</script>


<div id="addActionDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" data-bind="click: addActionDemiModalFieldCancel" class="pull-right"><i class="fa fa-times"></i></a>
    
    <ul data-bind="foreach: addActionProperties">
      <li>
        <span data-bind="text: label"></span>
        <input data-bind="value: value"/>
      </li>
    </ul>
    
    <!-- ko if: addActionWorkflows().length > 0 -->
      <select data-bind="options: addActionWorkflows, optionsText: 'name'"></select>
    <!-- /ko -->        
    
    <br/>
    <a data-bind="click: addActionDemiModalFieldPreview">
      Add
    </a>
  </div>
</div>


<div id="settingsDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 30px; text-align: center; line-height: 28px">
      
      ${ _('Oozie Parameters') }   
      <ul data-bind="foreach: $root.workflow.properties.parameters">
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.workflow.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <button data-bind="click: function(){ $root.workflow.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i>
      </button>

      <br/>
      ${_("Workspace")}
      <input data-bind="value: $root.workflow.properties.deployment_dir"/>

    </div>
  </div>
</div>


<div id="submit-wf-modal" class="modal hide"></div>


<link rel="stylesheet" href="/oozie/static/css/workflow-editor.css">
<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">


${ dashboard.import_layout() }


<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }

<script src="/oozie/static/js/workflow-editor.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  var viewModel = new WorkflowEditorViewModel(${ layout_json | n,unicode }, ${ workflow_json | n,unicode });
  ko.applyBindings(viewModel);

  viewModel.init();


  function columnDropAdditionalHandler(widget) {
    widgetDraggedAdditionalHandler(widget);
  }

  function widgetDraggedAdditionalHandler(widget) {
    viewModel.workflow.newNode(widget);
    showAddActionDemiModal(widget);
  }


  $(document).on("showSubmitPopup", function(event, data){
    $('#submit-wf-modal').html(data);
    $('#submit-wf-modal').modal('show');
  });

  
  var newAction = null;

  function showAddActionDemiModal(widget) {
    newAction = widget;
    $("#addActionDemiModal").modal("show");
  }

  function addActionDemiModalFieldPreview(field) {    
    if (newAction != null) {
      viewModel.workflow.addNode(newAction);
      $("#addActionDemiModal").modal("hide");
    }
  }

  function addActionDemiModalFieldCancel() {
    viewModel.removeWidgetById(newAction.id());
  }
</script>

${ commonfooter(messages) | n,unicode }
