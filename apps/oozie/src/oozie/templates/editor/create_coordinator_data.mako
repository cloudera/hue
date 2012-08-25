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
import re

from django.utils.translation import ugettext as _
%>

<%namespace name="utils" file="../../utils.inc.mako" />


<%def name="print_datasets(label, element, formset, direction)">
  <table id="${element}" class="table-condensed designTable">
    <thead>
      <tr>
        <th>${ _('Name') }</th>
        <th>${ _('Dataset') }</th>
        <th></th>
      </tr>
    </thead>
    <tbody data-bind="foreach: ${ element }">
      % if 'forms' in formset.__dict__:
        % for form in formset.forms:
          <tr>
            <td>${ form['name'] }</td>
            <td>${ form['dataset'] }</td>
            <td><a class="btn btn-small" href="#" data-bind="click: $root.remove_${ element }">${ _('Delete') }</a></td>
          </tr>
        % endfor
        <tr>
          <td>${ formset.empty_form['name'] }</td>
          <td>${ formset.empty_form['dataset'] }</td>
          <td><a class="btn btn-small" href="#" data-bind="click: $root.remove_${ element }">${ _('Delete') }</a></td>
        </tr>
      % else:
        <tr>
          <td>${ formset['name'] }</td>
          <td>${ formset['dataset'] }</td>
          <td><a class="btn btn-small" href="#" data-bind="click: $root.remove_${ element }">${ _('Delete') }</a></td>
        </tr>
      % endif
    </tbody>
  </table>
  % if 'forms' in formset.__dict__:
    % for form in formset.forms:
      % if form.errors:
        <div class="row">
          <div class="alert alert-error">
            ${ unicode(form.errors) | n }
          </div>
        </div>
      % endif
    % endfor
  % else:
    % if formset.errors:
      <div class="row">
        <div class="alert alert-error">
          ${ unicode(formset.errors) | n }
        </div>
      </div>
    % endif
  % endif

  <button type="button" class="btn" data-bind="click: add_${ element }">${ _('Add') }</button>

  <style>
    .designTable th {
      text-align:left;
    }
  </style>

  <script type="text/javascript">
    $(document).ready(function(){
      window.viewModel.${element} = ko.observableArray([]);

      window.viewModel.add_${element} = function() {
        window.viewModel.${element}.push({name: "", dataset: ""});
      };

      window.viewModel.remove_${element} = function(val) {
        window.viewModel.${element}.remove(val);
      };

      var previousSubmit = window.viewModel.submit;
      window.viewModel.submit = function(form) {
        $.post("${ url('oozie:create_coordinator_data', coordinator=coordinator.id, data_type='%s' % direction) }",
          $("#${element} :input").serialize(), function(response) {
            if (response['status'] != 0) {
              $.jHueNotify.error("${ _('Problem: ') }" + response['data']);
            } else {
              window.location.replace(response['data']);
            }
        });

        previousSubmit(form);
      };
    });
  </script>
</%def>
