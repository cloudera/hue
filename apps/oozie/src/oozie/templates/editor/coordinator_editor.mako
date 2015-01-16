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
from desktop.views import commonheader, commonfooter, commonshare
from django.utils.translation import ugettext as _
%>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="utils" file="../utils.inc.mako" />
<%namespace name="coordinator_utils" file="coordinator_utils.mako" />

${ commonheader(_("Coordinator Editor"), "Oozie", user) | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("coordinator") > -1) {
      location.href = "/oozie/editor/coordinator/edit/?" + window.location.hash.substr(1);
    }
  }
</script>


<div id="editor">

<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: showSubmitPopup, css: {'btn': true}, visible: coordinator.id() != null">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}, visible: canEdit">
      <i class="fa fa-pencil"></i>
    </a>
    
    &nbsp;&nbsp;&nbsp;

    <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsModal" data-bind="css: {'btn': true}, visible: canEdit">
      <i class="fa fa-cog"></i>
    </button>
    
    &nbsp;&nbsp;&nbsp;

    <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" 
        data-bind="click: $root.save, css: {'btn': true}, visible: canEdit">
      <i class="fa fa-save"></i>
    </button>
    
    <a class="share-link btn" rel="tooltip" data-placement="bottom" data-bind="click: openShareModal,
        attr: {'data-original-title': '${ _("Share") } ' + name},
        css: {'isShared': isShared(), 'btn': true},
        visible: coordinator.id() != null && canEdit()">
      <i class="fa fa-users"></i>
    </a>    
    
    &nbsp;&nbsp;&nbsp;

    <a class="btn" href="${ url('oozie:new_coordinator') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-file-o"></i>
    </a>
    <a class="btn" href="${ url('oozie:list_editor_coordinators') }" title="${ _('Coordinators') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-tags"></i>
    </a>

  </div>

  <form class="form-search">
    <div class="inline object-name">
      <span data-bind="editable: $root.coordinator.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
    </div>
  </form>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12 coordinator">

      <div class="card card-home">
        <h1 class="card-heading simple">${ _('Which workflow to schedule?') }</h1>

        <div class="card-body">
          <a class="pointer" data-bind="visible: ! coordinator.properties.workflow(), click: showChooseWorkflow">${ _('Choose a workflow...') }</a>
          <!-- ko if: coordinator.properties.workflow -->
            <a class="pointer" data-bind="click: showChooseWorkflow, text: getWorkflowById(coordinator.properties.workflow()).name"></a>
            
            <a data-bind="attr: { href: '${ url('oozie:edit_workflow') }?workflow=' + coordinator.properties.workflow() }" target="_blank" title="${ _('Open') }">
             <i class="fa fa-external-link-square"></i>
            </a>            
          <!-- /ko -->
        </div>
      </div>

      <div class="card card-home" data-bind="visible: coordinator.properties.workflow">
        <h1 class="card-heading simple">${ _('How often?') }</h1>

        <div class="card-body">
          
          <div class="controls">
            <div class="row-fluid">
              <div class="span9">
                <a data-bind="visible: coordinator.properties.cron_advanced" href="http://quartz-scheduler.org/api/2.0.0/org/quartz/CronExpression.html" class="pull-right" target="_blank">
                  &nbsp;<i class="fa fa-question-circle" title="${ _('Check syntax ?') }"></i>
                </a>
                <input data-bind="visible: coordinator.properties.cron_advanced" id="coord-frequency" data-bind="value: coordinator.properties.cron_frequency" name="cron_frequency" class="pull-right"/>
                <span data-bind="visible: coordinator.properties.cron_advanced" class="pull-right" style="padding-right:20px">
                  ${ _('Crontab') }
                </span>
              </div>
              <div class="span3">
              </div>
            </div>
          </div>          
                    
          <div data-bind="visible: coordinator.showAdvancedFrequencyUI" style="padding-left: 20px">
            Start
            <input data-bind="value: coordinator.properties.start" />
            End
            <input data-bind="value: coordinator.properties.end" />
            Timezone
            <input data-bind="value: coordinator.properties.timezone" />
              
            <label class="checkbox" style="display: inline-block">
               <input type="checkbox" name="coordinator.properties.cron_advanced" data-bind="checked: coordinator.properties.cron_advanced" /> ${ _('Advanced Cron syntax') }
            </label>
          </div>
          
          <a href="#" data-bind="click: function() { $root.coordinator.showAdvancedFrequencyUI(! $root.coordinator.showAdvancedFrequencyUI()) }">
            <i class="fa fa-sliders"></i>
          </a>          
        </div>
      </div>

      <div class="card card-home" data-bind="visible: coordinator.properties.workflow">
        <h1 class="card-heading simple">${ _('Workflow Parameters') }</h1>

        <div class="card-body">
          <ul data-bind="foreach: coordinator.variables" class="unstyled">
            <li>
              <input data-bind="value: workflow_variable"/>
              <select data-bind="options: $parent.coordinator.workflowParameters, optionsText: 'name'"></select>

              <div class="btn-group">
                <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                        aria-expanded="false">
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

              <div data-bind="visible: show_advanced" style="padding-left: 20px">
                Done flag 
                <input type="checkbox" data-bind="checked: use_done_flag" />
                <input data-bind="value: done_flag, visible: use_done_flag"/>
                
                Same start
                <input type="checkbox" data-bind="checked: same_start" />                
                <input data-bind="value: start, visible: ! same_start()" />
                
                Same timezone
                <input type="checkbox" data-bind="checked: same_timezone" />
                <input data-bind="value: timezone, visible: ! same_timezone()" />
                
                <div class="control-group">
                  <label class="control-label">${ _('Instance') }</label>

                  <div class="controls">
                    <div class="btn-group" data-toggle="buttons-radio">
                      <button id="default-btn" type="button" class="btn"
                              data-bind="click: function() { instance_choice('default'); }, css: { active: instance_choice() == 'default' }">
                        ${ _('Default') }
                      </button>
                      <button id="single-btn" type="button" class="btn"
                              data-bind="click: function() { instance_choice('single'); }, css: { active: instance_choice() == 'single' }">
                        ${ _('Single') }
                      </button>
                      <button id="range-btn" type="button" class="btn"
                              data-bind="click: function() { instance_choice('range'); }, css: { active: instance_choice() == 'range' }">
                        ${ _('Range') }
                      </button>
                    </div>
                    <span class="help-block">instance_choice.help_text</span>

                    <div data-bind="visible: $.inArray(instance_choice(), ['single', 'range']) != -1">
                      <span class="span1">${ _('Start') }</span>
                      <input name="instance_start" type="number"
                             data-bind="value: start_instance, enable: ! is_advanced_start_instance()"/>
                      <label style="display: inline">
                        &nbsp;
                        <input type="checkbox" data-bind="checked: is_advanced_start_instance">
                        ${ _('(advanced)') }
                      </label>
                      <input type="text" data-bind="value: advanced_start_instance, visible: is_advanced_start_instance()"
                             class="span4"/>
                      <span class="help-block">advanced_start_instance.help_text </span>
                    </div>
                    <div data-bind="visible: instance_choice() == 'range'">
                      <span class="span1">${ _('End') }</span>
                      <input name="instance_end" type="number"
                             data-bind="value: end_instance, enable: ! is_advanced_end_instance()"/>
                      <label style="display: inline">
                        &nbsp;
                        <input type="checkbox" data-bind="checked: is_advanced_end_instance">
                        ${ _('(advanced)') }
                      </label>
                      <input type="text" data-bind="value: advanced_end_instance, visible: is_advanced_end_instance()"
                             class="span4"/>
                      <span class="help-block">advanced_end_instance.help_text</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- /ko -->
              <a href="#" data-bind="click: function(){ $root.coordinator.variables.remove(this); }">
                <i class="fa fa-minus"></i>
              </a>              
            </li>
          </ul>

          <a class="pointer" data-bind="click: coordinator.addVariable">
            <i class="fa fa-plus"></i> ${ _('Add a parameter') }
          </a>
        </div>
      </div>


    </div>
  </div>
</div>

<div id="chooseWorkflowDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 10px;text-align: center">
      <input type="text" data-bind="clearable: $root.workflowModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter workflows')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.filteredModalWorkflows().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.filteredModalWorkflows().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li data-bind="click: selectWorkflow">
          <span class="badge badge-info">
            <span data-bind="text: name(), attr: {'title': uuid()}"></span>
          </span>
          <a data-bind="attr: { href: '${ url('oozie:edit_workflow') }?workflow=' + uuid() }" target="_blank" title="${ _('Open') }">
            <i class="fa fa-external-link-square"></i>
          </a>
        </li>        
      </ul>
      <div class="alert alert-info inline" data-bind="visible: $root.filteredModalWorkflows().length == 0" style="margin-left: 250px;margin-right: 50px; height: 42px;line-height: 42px">
        ${_('There are no workflows matching your search term.')}
      </div>
    </div>
  </div>
</div>

<div id="settingsModal" class="modal hide fade">
  <div class="modal-header" style="padding-bottom: 2px">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3 id="myModalLabel">${ _('Coordinator Settings') }</h3>
  </div>
  <div class="modal-body">
      <h4>${ _('Submission Parameters') }</h4>
      <ul data-bind="foreach: coordinator.properties.parameters" class="unstyled">
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.coordinator.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.coordinator.properties.parameters.push({'name': '', 'value': ''}); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>

      <h4>${ _('Timeout') }</h4>
      <input data-bind="value: coordinator.properties.timeout"/>

      <h4>${ _('Concurrency') }</h4>
      <input data-bind="value: coordinator.properties.concurrency"/>
      
      <h4>${ _('Execution') }</h4>
      <input data-bind="value: coordinator.properties.execution"/>

      <h4>${ _('Throttle') }</h4>
      <input data-bind="value: coordinator.properties.throttle"/>

      <h4>${ _('SLA Configuration') }</h4>
      <div class="sla-form" data-bind="with: $root.coordinator.properties">
        ${ utils.slaForm() }
      </div>
  </div>
</div>


<div id="submit-coord-modal" class="modal hide"></div>


</div>

<div id="exposeOverlay"></div>

<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/oozie/static/css/common-editor.css">
<link rel="stylesheet" href="/oozie/static/css/coordinator-editor.css">

<link href="/static/css/jqCron.css" rel="stylesheet" type="text/css" />
<script src="/static/js/jqCron.js" type="text/javascript"></script>

${ dashboard.import_layout() }

${ commonshare() | n,unicode }

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/share.vm.js"></script>

${ dashboard.import_bindings() }


<script src="/oozie/static/js/coordinator-editor.ko.js" type="text/javascript" charset="utf-8"></script>


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
        lang: 'i18n'
      })
      .jqCronGetInstance();

  var viewModel = new CoordinatorEditorViewModel(${ coordinator_json | n,unicode }, ${ credentials_json | n,unicode }, ${ workflows_json | n,unicode }, ${ can_edit_json | n,unicode });
  ko.applyBindings(viewModel, $("#editor")[0]);

  viewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status

  var shareViewModel = setupSharing("#documentShareModal");
  shareViewModel.setDocId(${ doc1_id });

  function showChooseWorkflow() {
    $("#chooseWorkflowDemiModal").modal("show");
  }

  function selectWorkflow(wf) {
    viewModel.coordinator.properties.workflow(wf.uuid());
    $("#chooseWorkflowDemiModal").modal("hide");
  }
  
  $(document).on("showSubmitPopup", function(event, data){
    $('#submit-coord-modal').html(data);
    $('#submit-coord-modal').modal('show');
  });

  $(document).ready(function() {
    $("#chooseWorkflowDemiModal").modal({
      show: false
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
