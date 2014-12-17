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
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Coordinator Editor"), "Oozie", user) | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("coordinator") > -1) {
      location.href = "/oozie/editor/coordinator/edit/?" + window.location.hash.substr(1);
    }
  }
</script>





<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Gen XML') }" rel="tooltip" data-placement="bottom" data-bind="click: gen_xml, css: {'btn': true}">
      <i class="fa fa-file-code-o"></i>
    </a>
    <a title="${ _('Import coordinators') }" rel="tooltip" data-placement="bottom" data-bind="click: import_coordinators, css: {'btn': true}">
      <i class="fa fa fa-download"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal" data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: $root.save, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <a class="btn" href="${ url('oozie:new_coordinator') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </a>
      <a class="btn" href="${ url('oozie:list_editor_coordinators') }" title="${ _('Coordinators') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-tags"></i>
      </a>
    % endif
  </div>

  <form class="form-search" style="margin: 0">
    <strong>${_("Name")}</strong>
    <input data-bind="value: $root.coordinator.name"/>
    
    &nbsp;&nbsp;&nbsp;
    1
    2
    3
    4
    Scrollspy?
  </form>
</div>

<div>
  <div>     
    <h1>1 Which workflow to schedule?</h1> 

    <select data-bind="options: workflows,
                       optionsText: 'name',
                       optionsValue: 'uuid',
                       value: coordinator.properties.workflow,
                       optionsCaption: 'Choose...'">
    </select>
  </div>
  
  <div data-bind="visible: coordinator.properties.workflow">
    <h1>2 How often?</h1>
    
    [hourly] [daily] [weekly] [monthly]
    <input data-bind="value: coordinator.properties.cron_frequency"/>
    
  </div>
  
  <div data-bind="visible: coordinator.properties.workflow">
    <h1>3 Workflow Parameters</h1>    

    <ul data-bind="foreach: coordinator.variables">
      <li>
        <input data-bind="value: workflow_variable"/>
		<div class="btn-group">
		  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
		      <!-- ko if: dataset_type() == 'parameter' -->
              ${ _('Parameter') }
              <!-- /ko -->
              <!-- ko if: dataset_type() == 'input_path' -->
              ${ _('Input Path') }
              <!-- /ko -->
              <!-- ko if: dataset_type() == 'output_path' -->
              ${ _('Output Path') }
              <!-- /ko --> <span class="caret"></span>
		  </button>
		  <ul class="dropdown-menu" role="menu" data-bind="foreach: $parent.coordinator.variablesUI">
		    <!-- ko if: $data != $parent.dataset_type() -->
		    <li>
		      <a href="#" data-bind="click: function() { $parent.dataset_type($data) } ">
		      <!-- ko if: $data == 'parameter' -->
		      ${ _('Parameter') }
		      <!-- /ko -->
              <!-- ko if: $data == 'input_path' -->
              ${ _('Input Path') }
              <!-- /ko -->
              <!-- ko if: $data == 'output_path' -->
              ${ _('Output Path') }
              <!-- /ko -->
		      </a>
		    </li>
		    <!-- /ko -->
		  </ul>
		</div>        
        <input data-bind="value: dataset_variable"/>
        
        <!-- ko if: dataset_type() == 'input_path' || dataset_type() == 'output_path' -->
          [hourly] [daily] [weekly] [monthly]
          <a href="#" data-bind="click: function() { show_advanced(! show_advanced()) }">
            <i class="fa fa-sliders"></i>
          </a>
          
          <span data-bind="visible: show_advanced">            
            Done flag <input data-bind="value: done_flag"/>
            Range

			<div class="control-group">
			  <label class="control-label">${ _('Instance') }</label>
			  <div class="controls">
			      <div class="btn-group" data-toggle="buttons-radio">
			          <button id="default-btn" type="button" class="btn" data-bind="click: function() { instance_choice('default'); }, css: { active: instance_choice() == 'default' }">
			            ${ _('Default') }
			          </button>
			          <button id="single-btn" type="button" class="btn" data-bind="click: function() { instance_choice('single'); }, css: { active: instance_choice() == 'single' }">
			            ${ _('Single') }
			          </button>
			          <button id="range-btn" type="button" class="btn" data-bind="click: function() { instance_choice('range'); }, css: { active: instance_choice() == 'range' }">
			            ${ _('Range') }
			          </button>
			      </div>
			      <span class="help-block">instance_choice.help_text</span>
			
			      <div data-bind="visible: $.inArray(instance_choice(), ['single', 'range']) != -1">
			          <span class="span1">${ _('Start') }</span>
			          <input name="instance_start" type="number" data-bind="value: start_instance, enable: ! is_advanced_start_instance()"/>
			          <label style="display: inline">
			              &nbsp;
			              <input type="checkbox" data-bind="checked: is_advanced_start_instance">
			              ${ _('(advanced)') }
			          </label>
			          <input type="text" data-bind="value: advanced_start_instance, visible: is_advanced_start_instance()" class="span4"/>
			          <span class="help-block">advanced_start_instance.help_text </span>
			      </div>
			      <div data-bind="visible: instance_choice() == 'range'">
			          <span class="span1">${ _('End') }</span>
			          <input name="instance_end" type="number" data-bind="value: end_instance, enable: ! is_advanced_end_instance()" />
			          <label style="display: inline">
			              &nbsp;
			              <input type="checkbox" data-bind="checked: is_advanced_end_instance">
			              ${ _('(advanced)') }
			          </label>
			          <input type="text" data-bind="value: advanced_end_instance, visible: is_advanced_end_instance()" class="span4"/>
			          <span class="help-block">advanced_end_instance.help_text</span>
			      </div>
			  </div>
			</div

          </span>          
        <!-- /ko -->
                
        <a href="#" data-bind="click: function(){ $root.coordinator.variables.remove(this); }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>

    <button data-bind="click: coordinator.addVariable">
      <i class="fa fa-plus"></i>
    </button>

  </div>
</div>


<div id="settingsDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 30px; text-align: center; line-height: 28px">

      ${ _('Throttle') }
      <input data-bind="value: coordinator.properties.throttle"/>
      <br/>

      ${ _('Oozie Parameters') }
      <ul data-bind="foreach: coordinator.properties.properties">
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.coordinator.properties.properties.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <button data-bind="click: function(){ $root.coordinator.properties.properties.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i>
      </button>

      <br/>
      <div class="control-group">
        <label class="control-label">${ _('SLA Configuration') }</label>
        <div class="controls" data-bind="with: $root.coordinator.properties">
          ${ utils.slaForm() }
        </div>
      </div>
    </div>
  </div>
</div>


<div id="submit-coord-modal" class="modal hide"></div>

<div id="exposeOverlay"></div>

<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/oozie/static/css/coordinator-editor.css">


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>


<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>


<script src="/oozie/static/js/coordinator-editor.ko.js" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript">
  ${ utils.slaGlobal() }

  var viewModel = new CoordinatorEditorViewModel(${ coordinator_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflows_json | n,unicode });
  ko.applyBindings(viewModel);

  function showAddActionDemiModal(widget) {
    newAction = widget;
    $("#addActionDemiModal").modal("show");
  }

  function addActionDemiModalFieldPreview(field) {
    if (newAction != null) {
      viewModel.coordinator.addNode(newAction);
      $("#addActionDemiModal").modal("hide");
    }
  }

  function addActionDemiModalFieldCancel() {
    viewModel.removeWidgetById(newAction.id());
  }
  
  $(document).on("showSubmitPopup", function(event, data){
    $('#submit-coord-modal').html(data);
    $('#submit-coord-modal').modal('show');
  });  
</script>

${ commonfooter(messages) | n,unicode }
