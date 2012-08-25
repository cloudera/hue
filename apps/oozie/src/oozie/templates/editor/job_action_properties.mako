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

<%namespace name="utils" file="../../utils.inc.mako" />


<%def name="print_key_value(label, element, form, initial_parameters)">
  <div class="control-group ko-${element}">
    <label class="control-label">${ label }</label>
    <div class="controls">
      <table class="table-condensed designTable" data-bind="visible: ${ element }().length > 0">
        <thead>
          <tr>
            <th>${ _('Name') }</th>
            <th>${ _('Value') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ element }">
          <tr>
            <td><input class="required" data-bind="value: name, uniqueName: false" /></td>
            <td><input class="required" data-bind="value: value, uniqueName: false" /></td>
            <td><a class="btn btn-small" href="#" data-bind="click: $root.remove_${ element }">${ _('Delete') }</a></td>
          </tr>
        </tbody>
      </table>
      % if len(form[element].errors):
        <div class="row">
          <div class="alert alert-error">
            ${ unicode(form[element].errors) | n }
          </div>
        </div>
      % endif

      <button class="btn" data-bind="click: add_${ element }">${ _('Add') }</button>
    </div>
  </div>

  <style>
    .designTable th {
      text-align:left;
    }
  </style>

  <script type="text/javascript">
    $(document).ready(function(){
      var ViewModel = function(parameters) {
        var self = this;
        self.parameters = ko.observableArray(parameters);

        self.add_parameters = function() {
          self.parameters.push({name: "", value: ""});
        };

        self.remove_parameters = function(val) {
          self.parameters.remove(val);
        };

        self.submit = function(form) {
          var form = $("#jobForm");

          $("<input>").attr("type", "hidden")
              .attr("name", "parameters")
              .attr("value", ko.utils.stringifyJson(self.parameters))
              .appendTo(form);

          form.submit();
        };
      };

      window.viewModel = new ViewModel(${ initial_parameters });
    });
  </script>
</%def>
