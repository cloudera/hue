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
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%namespace name="utils" file="../utils.inc.mako" />

<%def name="import_layout(embedded=False)">

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12 coordinator">

      %if not embedded:
      <div class="card card-home">
        <h1 class="card-heading simple" style="border-bottom: none"><span data-bind="editable: $root.coordinator.name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span></h1>
        <div class="card-body muted" style="margin-top: 2px" data-bind="visible: $root.isEditing() || (! $root.isEditing() && $root.coordinator.properties.description)">
          <span data-bind="editable: $root.coordinator.properties.description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_ko('Add a description...')}'}"></span>
        </div>
      </div>

      <div class="card card-home" style="margin-top: 20px">
        <h1 class="card-heading simple">${ _('Which workflow to schedule?') }</h1>

        <div class="card-body">
          <a class="pointer" data-bind="visible: ! coordinator.properties.workflow(), click: showChooseWorkflow">${ _('Choose a workflow...') }</a>
          <!-- ko if: getWorkflowById(coordinator.properties.workflow()) -->
            <!-- ko if: isEditing -->
            <a class="pointer" data-bind="click: showChooseWorkflow, text: getWorkflowById(coordinator.properties.workflow()).name"></a>

            <a data-bind="hueLink: '${ url('oozie:edit_workflow') }?workflow=' + coordinator.properties.workflow()" title="${ _('Open') }">
             <i class="fa fa-external-link-square"></i>
            </a>
            <!-- /ko -->
            <!-- ko ifnot: isEditing -->
            <span data-bind="text: getWorkflowById(coordinator.properties.workflow()).name"></span>
            <a data-bind="hueLink: '${ url('oozie:edit_workflow') }?workflow=' + coordinator.properties.workflow()" title="${ _('Open') }">
              <i class="fa fa-external-link-square"></i>
            </a>
            <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
      %endif

      <div class="card card-home" data-bind="visible: coordinator.properties.workflow() || coordinator.properties.document()" style="margin-top: 20px">
        <h1 class="card-heading simple">${ _('How often?') }
        </h1>

        <div class="card-body">

          <div class="row-fluid">
            <div class="span12">
              <form class="
              %if not embedded:
              form-horizontal
              %endif
              ">
                <div class="control-group" data-bind="visible: ! coordinator.properties.cron_advanced()">
                  <div class="controls" id="jqCron-container">
                    <div id="jqCron-instance" style="margin-top: 5px; display: inline-block"></div>
                  </div>
                </div>
                <div class="control-group" data-bind="visible: coordinator.properties.cron_advanced">
                  <label class="control-label">${ _('Crontab') }</label>
                  <div class="controls">
                    <input id="coord-frequency" type="text" data-bind="textInput: coordinator.properties.cron_frequency, enable: $root.isEditing, attachViewModelToElementData, tagsNotAllowed" name="cron_frequency"/>
                    <span class="help-inline">
                      <a data-bind="visible: coordinator.properties.cron_advanced" href="http://www.quartz-scheduler.org/documentation/quartz-2.x/tutorials/crontrigger.html" target="_blank">
                      <i class="fa fa-question-circle" title="${ _('Check syntax ?') }"></i></a>
                    </span>
                  </div>
                </div>
                <div class="control-group" style="margin-bottom: 0">
                  <label class="control-label"></label>
                  <div class="controls">
                    <a href="#" data-bind="click: function() { $root.coordinator.showAdvancedFrequencyUI(! $root.coordinator.showAdvancedFrequencyUI()) }">
                      <i class="fa fa-sliders"></i> <span data-bind="visible: ! coordinator.showAdvancedFrequencyUI()">${ _('Options') }</span>
                      <span data-bind="visible: coordinator.showAdvancedFrequencyUI">${ _('Hide') }</span>
                    </a>
                  </div>
                </div>
             </form>
            </div>

          </div>

          <div data-bind="visible: coordinator.showAdvancedFrequencyUI">
            <form class="
            %if not embedded:
            form-horizontal
            %endif
            ">

              <div class="control-group">
                <div class="controls">
                  <label class="checkbox" style="display: inline-block; margin-top: 5px">
                    <input type="checkbox" name="coordinator.properties.cron_advanced" data-bind="checked: coordinator.properties.cron_advanced, enable: $root.isEditing" /> ${ _('Advanced syntax') }
                  </label>
                </div>
              </div>

              <div class="control-group" style="margin-bottom: 20">
                <label class="control-label">${ _('Timezone') }</label>
                <div class="controls">
                  <select data-bind="options: $root.availableTimezones, select2: { placeholder: '${ _ko("Select a Timezone") }', update: coordinator.properties.timezone, readonly: !$root.isEditing()}" style="width: 180px"></select>
                  <span class="help-inline"></span>
                </div>
              </div>

              <div class="control-group">
                <label class="control-label">${ _('From') }</label>
                <div class="controls">
                  <div class="input-prepend input-group">
                    <span class="add-on input-group-addon">
                      <i class="fa fa-calendar"></i>
                    </span>
                    <input type="text" class="input-small" data-bind="value: coordinator.properties.startDateUI, datepicker: {}, enable: $root.isEditing" />
                  </div>
                  <div class="input-prepend input-group">
                    <span class="add-on input-group-addon">
                      <i class="fa fa-clock-o"></i>
                    </span>
                    <input type="text" class="input-mini" data-bind="value: coordinator.properties.startTimeUI, timepicker: {}, enable: $root.isEditing" />
                  </div>
                  <span class="help-inline"></span>
                </div>
              </div>
              <div class="control-group">
                <label class="control-label">${ _('To') }</label>
                <div class="controls">
                  <div class="input-prepend input-group">
                    <span class="add-on input-group-addon">
                      <i class="fa fa-calendar"></i>
                    </span>
                    <input type="text" class="input-small" data-bind="value: coordinator.properties.endDateUI, datepicker: {}, enable: $root.isEditing" />
                  </div>
                  <div class="input-prepend input-group">
                    <span class="add-on input-group-addon">
                      <i class="fa fa-clock-o"></i>
                    </span>
                    <input type="text" class="input-mini" data-bind="value: coordinator.properties.endTimeUI, timepicker: {}, enable: $root.isEditing" />
                  </div>
                  <span class="help-inline"></span>
                </div>
              </div>

            </form>

          </div>


        </div>
      </div>


      <div class="card card-home" data-bind="visible: coordinator.properties.workflow() || coordinator.properties.document()" style="margin-top: 20px; margin-bottom: 20px">
        <h1 class="card-heading simple">${ _('Parameters') }</h1>

        <div class="card-body">
          <span class="muted" data-bind="visible: coordinator.variables().length == 0 && ! isEditing()">${ _('This coordinator has no defined parameters.') }</span>

          <ul data-bind="foreach: coordinator.variables, visible: coordinator.variables().length > 0" class="unstyled">
            <li class="workflow-parameter" style="margin-bottom: 10px">

              %if embedded:
              <a href="#" class="pull-right inactive-action" data-bind="click: function(){ $root.coordinator.variables.remove(this); }, visible: $root.isEditing">
                <i class="fa fa-times"></i>
              </a>
              %endif

              <select data-bind="options: $parent.coordinator.workflowParameters, optionsText: 'name', optionsValue: 'name', select2: { placeholder: '${ _ko("Select a parameter") }', update: workflow_variable, type: 'parameter', readonly: !$root.isEditing()}" style="width: 250px"></select>

              %if embedded:
                <div style="height: 20px"></div>
              %else:
                &nbsp;&nbsp;
              %endif

              <div class="btn-group">
                <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"
                        aria-expanded="false" data-bind="enable: $root.isEditing">
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

              %if embedded:
                <div style="height: 20px"></div>
              %else:
                &nbsp;&nbsp;
              %endif

              <span data-bind="visible: $root.isEditing">
                <input type="text" class="filechooser-input dataset-input" data-bind="value: dataset_variable, valueUpdate:'afterkeydown', filechooser: dataset_variable, attr: { placeholder:
                  dataset_type() == 'input_path' ? '${ _ko("Required data path dependency to start the worklow") }' :
                  dataset_type() == 'output_path' ? '${ _ko("Data path created by the workflow") }' :
                  'e.g. 1, 2, 3, /data/logs, ${"$"}{coord:nominalTime()}' },
                  typeahead: { target: dataset_variable, source: datasetTypeaheadSource, triggerOnFocus: true, multipleValues: true, multipleValuesSeparator: '', multipleValuesExtractors: [' ', '/'] }" style="margin-bottom:0;" />
              </span>

              <span data-bind="text: dataset_variable, visible: ! $root.isEditing()"></span>

              %if not embedded:
              <a href="#" data-bind="click: function(){ $root.coordinator.variables.remove(this); }, visible: $root.isEditing">
                <i class="fa fa-minus"></i>
              </a>
              %endif

              <!-- ko if: dataset_type() == 'input_path' || dataset_type() == 'output_path' -->

                <a href="#" data-bind="click: function() { show_advanced(! show_advanced()) }">
                  <i class="fa fa-sliders"></i>
                </a>

                %if embedded:
                <div style="height: 4px"></div>
                <span class="muted">
                %else:
                <span style="padding-left:100px">
                %endif
                  <span data-bind="visible: dataset_variable().length == 0">
                    e.g. /data/${'$'}{YEAR}/${'$'}{MONTH}/${'$'}{DAY}
                  </span>
                  <span data-bind="visible: dataset_variable().length > 0 && instance_choice() != 'range'">
                    ${ _('Will convert to') }
                    <a data-bind="text: convertDatasetVariables(dataset_variable(), same_start(), start(), same_frequency(), frequency_unit(), start_instance(), instance_choice(), $root), hueLink: '/filebrowser/view=' + convertDatasetVariables(dataset_variable(), same_start(), start(), same_frequency(), frequency_unit(), start_instance(), instance_choice(), $root)"></a>
                  </span>
                  </a>
                </span>

                <div data-bind="visible: show_advanced" style="padding: 20px">
                  <form class="form-horizontal">
                    <div class="control-group">
                      <label class="control-label">${ _('Done flag') }</label>
                      <div class="controls">
                        <input type="checkbox" data-bind="checked: use_done_flag, style: {'margin-top': !use_done_flag() ? '9px' : '-1px'}, enable: $root.isEditing" />
                        <input type="text" data-bind="value: done_flag, visible: use_done_flag, enable: $root.isEditing"/>
                      </div>
                    </div>
                    <div class="control-group">
                      <label class="control-label">${ _('Same frequency') }</label>
                      <div class="controls">
                        <input type="checkbox" data-bind="checked: same_frequency, style: {'margin-top': same_frequency() ? '5px' : '0'}, enable: $root.isEditing" />
                        <span data-bind="visible: ! same_frequency()">
                          ${ _('Every') }
                        </span>
                        <select data-bind="value: frequency_number, visible: ! same_frequency(), enable: $root.isEditing" style="width: 50px">
                          % for i in xrange(0, 60):
                          <option value="${ i }">${ i }</option>
                          % endfor
                        </select>
                        <select data-bind="value: frequency_unit, visible: ! same_frequency(), enable: $root.isEditing" style="width: 100px">
                          <option value="minutes">${ _('Minutes') }</option>
                          <option value="hours">${ _('Hours') }</option>
                          <option value="days" selected="selected">${ _('Days') }</option>
                          <option value="months">${ _('Months') }</option>
                        </select>
                      </div>
                    </div>
                    <div class="control-group">
                      <label class="control-label">${ _('Same start') }</label>
                      <div class="controls">
                        <input type="checkbox" data-bind="checked: same_start, style: {'margin-top': same_start() ? '9px' : '-1px'}, enable: $root.isEditing" />
                        <input type="text" data-bind="value: start, visible: ! same_start(), enable: $root.isEditing"/>
                      </div>
                    </div>
                    <div class="control-group">
                      <label class="control-label">${ _('Same timezone') }</label>
                      <div class="controls">
                        <input type="checkbox" data-bind="checked: same_timezone, style: {'margin-top': same_timezone() ? '5px' : '0'}, enable: $root.isEditing" />
                        <select data-bind="options: $root.availableTimezones, select2: { placeholder: '${ _ko("Select a Timezone") }', update: timezone}, visible: ! same_timezone(), enable: $root.isEditing" style="width: 180px"></select>
                      </div>
                    </div>
                    <div class="control-group">
                      <label class="control-label">${ _('Instance') }</label>
                      <div class="controls">
                        <div class="btn-group" data-toggle="buttons-radio">
                          <button id="default-btn" type="button" class="btn"
                                  data-bind="click: function() { instance_choice('default'); }, css: { active: instance_choice() == 'default' }, enable: $root.isEditing">
                            ${ _('Default') }
                          </button>
                          <button id="single-btn" type="button" class="btn"
                                  data-bind="click: function() { instance_choice('single'); }, css: { active: instance_choice() == 'single' }, enable: $root.isEditing">
                            ${ _('Single') }
                          </button>
                          <button id="range-btn" type="button" class="btn"
                                  data-bind="click: function() { instance_choice('range'); }, css: { active: instance_choice() == 'range' }, enable: $root.isEditing">
                            ${ _('Range') }
                          </button>
                        </div>
                      </div>
                    </div>
                    <div class="control-group" data-bind="visible: $.inArray(instance_choice(), ['single', 'range']) != -1">
                      <label class="control-label">${ _('Start') }</label>
                      <div class="controls">
                        <input name="instance_start" type="number" data-bind="value: start_instance, enable: ! is_advanced_start_instance(), enable: $root.isEditing"/>
                        <label style="display: inline">
                            &nbsp;
                            <input type="checkbox" data-bind="checked: is_advanced_start_instance, enable: $root.isEditing" style="margin-top:0">
                            ${ _('(advanced)') }
                          </label>
                          <input type="text" data-bind="value: advanced_start_instance, visible: is_advanced_start_instance(), enable: $root.isEditing"/>
                      </div>
                    </div>
                    <div class="control-group" data-bind="visible: instance_choice() == 'range'">
                      <label class="control-label">${ _('End') }</label>
                      <div class="controls">
                        <input name="instance_end" type="number" data-bind="value: end_instance, enable: ! is_advanced_end_instance(), enable: $root.isEditing"/>
                        <label style="display: inline">
                            &nbsp;
                            <input type="checkbox" data-bind="checked: is_advanced_end_instance, enable: $root.isEditing" style="margin-top:0">
                            ${ _('(advanced)') }
                          </label>
                          <input type="text" data-bind="value: advanced_end_instance, visible: is_advanced_end_instance(), enable: $root.isEditing"/>
                      </div>
                    </div>
                  </form>
                </div>
              <!-- /ko -->
            </li>
          </ul>

          <a class="pointer" data-bind="click: function() { coordinator.addVariable() }, visible: isEditing">
            <i class="fa fa-plus"></i> ${ _('Add parameter') }
          </a>

        </div>

      </div>

      %if not embedded:
      <div class="card card-home" data-bind="visible: coordinator.id() == null && coordinator.properties.workflow()">
        <div class="card-body">
          <a href type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
            data-bind="click: $root.save, css: {'btn': true}">
            ${ _('Save') }
          </a>
        </div>
      </div>
      %endif

    </div>
  </div>
</div>

</%def>

<%def name="import_modals()">

<div id="chooseWorkflowDemiModal" class="${ is_embeddable and 'modal' or 'demi-modal' } fade" data-backdrop="${ is_embeddable and 'true' or 'false' }">
  %if is_embeddable:
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 id="myModalLabel" class="modal-title">${_('Choose a workflow')}</h2>
  </div>
  %endif
  <div class="modal-body">
    %if not is_embeddable:
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    %endif
    <div style="float: left; margin-right: 10px;text-align: center">
      <input type="text" data-bind="clearable: $root.workflowModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter workflows')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.filteredModalWorkflows().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.filteredModalWorkflows().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li style="${ not is_embeddable and 'line-height: 30px' or ''}">
          <span class="badge badge-info" data-bind="click: selectWorkflow">
            <span data-bind="text: name(), attr: {'title': uuid()}"></span>
          </span>
          <a data-bind="hueLink: '${ url('oozie:edit_workflow') }?workflow=' + uuid()" title="${ _('Open') }">
            <i class="fa fa-external-link-square"></i>
          </a>
        </li>
      </ul>
      <div class="label inline" data-bind="visible: $root.filteredModalWorkflows().length == 0" style="line-height: 30px">
        ${_('There are no workflows matching your search term.')}
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
    <h2 id="myModalLabel" class="modal-title">${_('Coordinator Settings')}</h2>
  </div>
  <div class="modal-body">
      <h4>${ _('Submission Parameters') }</h4>
      <ul data-bind="foreach: coordinator.properties.parameters" class="unstyled">
        <!-- ko if: ['oozie.use.system.libpath', 'start_date', 'end_date'].indexOf(name()) == -1 -->
        <li>
          <input data-bind="value: name"/>
          <input data-bind="value: value"/>
          <a href="#" data-bind="click: function(){ $root.coordinator.properties.parameters.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
        <!-- /ko -->
      </ul>
      <a class="pointer" data-bind="click: function(){ $root.coordinator.properties.parameters.push(ko.mapping.fromJS({'name': '', 'value': ''})); }">
        <i class="fa fa-plus"></i> ${ _('Add parameter') }
      </a>

      <h4>${ _('Timeout') }</h4>
      <input data-bind="value: coordinator.properties.timeout" type="number"/>

      <h4>${ _('Concurrency') }</h4>
      <select data-bind="options: availableSettings, value: coordinator.properties.concurrency"></select>

      <h4>${ _('Execution') }</h4>
      <select data-bind="value: coordinator.properties.execution">
    <option value="FIFO">${ _("FIFO (oldest first)") }</option>
    <option value="LIFO">${ _("LIFO (newest first)") }</option>
    <option value="LAST_ONLY">${ _("LAST_ONLY (discards all older materializations)") }</option>
      </select>

      <h4>${ _('Throttle') }</h4>
      <select data-bind="options: availableSettings, value: coordinator.properties.throttle"></select>

      <h4>${ _('SLA Configuration') }</h4>
      <div class="sla-form" data-bind="with: $root.coordinator.properties">
        ${ utils.slaForm() }
      </div>
  </div>
</div>
</%def>


<%def name="import_js()">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-timepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-spinedit.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-slider.css') }">

  <script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/bootstrap-timepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-spinedit.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-slider.js') }" type="text/javascript" charset="utf-8"></script>
  <link href="${ static('desktop/css/jqCron.css') }" rel="stylesheet" type="text/css" />
  <script src="${ static('desktop/js/jqCron.js') }" type="text/javascript"></script>

  <script type="text/javascript">
    function showChooseWorkflow() {
    }
  </script>
</%def>


<%def name="import_sla_cron(coordinator_json)">
  <script type="text/javascript">
  var datasetTypeaheadSource = ["/data/${'${'}YEAR}/${'${'}MONTH}/${'${'}DAY}", "${'${'}MINUTE}", "${'${'}HOUR}", "${'${'}DAY}", "${'${'}MONTH}", "${'${'}YEAR}", "${'${'}coord:nominalTime()}", "${'${'}coord:formatTime(coord:nominalTime(), 'yyyyMMdd')}"]

  function zeroPadding(value) {
    return (value < 10 ? '0':'') + value;
  }

  function convertDatasetVariables(path, hasSameStart, customStart, hasSameFrequency, customFrequencyUnit, startInstance, instanceChoice, vm) {
    var _startDate = moment(vm.coordinator.start_date.value()).utc();
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

  ${ utils.slaGlobal() }
  ${ utils.cron_js() }

  var coordCron = {
    enable: function () {
    },
    disable: function () {
    }
  };

  function renderJqCron() {
    if (typeof coordCron.getSettings === 'undefined') {
      coordCron = $('#coord-frequency').jqCron({
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
        }).jqCronGetInstance();

      function waitForVm() {
        var _vm = $('#coord-frequency').data('__ko_vm');
        if (typeof _vm.coordinator !== 'undefined' && typeof _vm.coordinator.properties !== 'undefined') {
          if (_vm.coordinator.properties.cron_advanced() || !_vm.isEditing()) {
            coordCron.disable();
          }
          else {
            coordCron.enable();
          }
        }
        else {
          window.setTimeout(waitForVm, 100)
        }
      }

      waitForVm();

      $('#jqCron-container').on('cron:change', function(e, cron){
        $('#coord-frequency').data('__ko_vm').coordinator.properties.cron_frequency(cron);
      });
    }
  }

  </script>
</%def>
