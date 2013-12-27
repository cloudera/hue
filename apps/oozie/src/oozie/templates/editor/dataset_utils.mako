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
%>

## How to use:
## <%include file="dataset_utils.mako"/>
## <%include file="dataset_utils.mako" args="base_id='#id_create-'"/>

<%page args="base_id='#id_edit-'"/>


<div class="control-group">
  <label class="control-label">${ _('Instance') }</label>
  <div class="controls">
      <div class="btn-group" data-toggle="buttons-radio">
          <button id="default-btn" type="button" class="btn" data-bind="click: setDefault, css: { active: instance_choice() == 'default' }">${ _('Default') }</button>
          <button id="single-btn" type="button" class="btn" data-bind="click: setSingle, css: { active: instance_choice() == 'single' }">${ _('Single') }</button>
          <button id="range-btn" type="button" class="btn" data-bind="click: setRange, css: { active: instance_choice() == 'range' }">${ _('Range') }</button>
      </div>
      <span class="help-block">${ dataset_form['instance_choice'].help_text }</span>

      <div data-bind="visible: $.inArray(instance_choice(), ['single', 'range']) != -1">
          <span class="span1">${ _('Start') }</span>
          <input name="instance_start" type="number" data-bind="value: start_instance, enable: ! is_advanced_start_instance()"/>
          <label style="display: inline">
              &nbsp;
              <input type="checkbox" data-bind="checked: is_advanced_start_instance">
              ${ _('(advanced)') }
          </label>
          <input type="text" data-bind="value: advanced_start_instance, visible: is_advanced_start_instance()" class="span4"/>
          <span class="help-block">${ dataset_form['advanced_start_instance'].help_text }</span>
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
          <span class="help-block">${ dataset_form['advanced_end_instance'].help_text }</span>
      </div>
  </div>
</div>

<div class="hide">
    ${ dataset_form['instance_choice'] | n,unicode }
    ${ dataset_form['advanced_start_instance'] | n,unicode }
    ${ dataset_form['advanced_end_instance'] | n,unicode  }
</div>

<script type="text/javascript">
  $(document).ready(function(){
    window.viewModel.updateInstance = function() {
      $("${ base_id }instance_choice").val(window.viewModel.instance_choice());

      if (window.viewModel.is_advanced_start_instance()) {
        $("${ base_id }advanced_start_instance").val(window.viewModel.advanced_start_instance());
      } else {
        $("${ base_id }advanced_start_instance").val(window.viewModel.start_instance());
      }

      if (window.viewModel.is_advanced_end_instance()) {
        $("${ base_id }advanced_end_instance").val(window.viewModel.advanced_end_instance());
      } else {
        $("${ base_id }advanced_end_instance").val(window.viewModel.end_instance());
      }
    }

    window.viewModel.instance_choice = ko.observable('${ dataset.instance_choice }');

    window.viewModel.start_instance = ko.observable(${ dataset.start_instance });
    window.viewModel.advanced_start_instance = ko.observable('${ (dataset.is_advanced_start_instance and dataset.advanced_start_instance) or "${coord:current(%s)}" % dataset.start_instance }');
    window.viewModel.is_advanced_start_instance = ko.observable(${ dataset.is_advanced_start_instance and 'true' or 'false' });

    window.viewModel.end_instance = ko.observable(${ dataset.end_instance });
    window.viewModel.advanced_end_instance = ko.observable('${ (dataset.is_advanced_end_instance and dataset.advanced_end_instance) or "${coord:current(%s)}" % dataset.end_instance }');
    window.viewModel.is_advanced_end_instance = ko.observable(${ dataset.is_advanced_end_instance and 'true' or 'false' });


    window.viewModel.setDefault = function() {
      window.viewModel.instance_choice('default');
    };
    window.viewModel.setSingle = function() {
      window.viewModel.instance_choice('single');
    };
    window.viewModel.setRange = function() {
      window.viewModel.instance_choice('range');
    };

    window.viewModel.reset = function() {
      window.viewModel.instance_choice('default');
      window.viewModel.start_instance('0');
      window.viewModel.advanced_start_instance('${"${"}coord:current(0)}');
      window.viewModel.is_advanced_start_instance(false);
      window.viewModel.end_instance('0');
      window.viewModel.advanced_end_instance('${"${"}coord:current(0)}');
      window.viewModel.is_advanced_end_instance(false);
    }
  });
</script>
