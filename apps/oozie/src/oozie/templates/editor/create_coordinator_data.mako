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
from django.utils.safestring import mark_safe

%>

<%namespace name="utils" file="../../utils.inc.mako" />


<%def name="print_datasets(label, element, formset, direction, show_headers=True)">
  <div id="${element}">
    <table class="table-condensed dataTable" data-missing="#${element}_missing">
      % if show_headers:
      <thead
        % if not formset.forms:
          data-bind="visible: ${element}().length > 0"
        % endif
        >
        <tr>
          <th>${ _('Name') }</th>
          <th>${ _('Dataset') }</th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      % endif
      <tbody data-bind="foreach: ${ element }">
        <tr>
          <td width="10%" data-bind="html: name"></td>
          <td width="10%" data-bind="html: dataset"></td>
          <td data-bind="html: error_message"></td>
          <td width="1%"><a class="btn btn-small" href="#" data-bind="click: $root.remove_${ element }">${ _('Delete') }</a></td>
        </tr>
      </tbody>
    </table>

  <button type="button" class="btn" data-bind="click: add_${ element }">${ _('Add') }</button>

  ${ formset.management_form | n,unicode }

  </div>

  <style type="text/css">
    .dataTable th {
      text-align:left;
    }
  </style>

  <script type="text/javascript">
    $(document).ready(function(){
      var initial = ${ [{'name': str(form['name']), 'dataset': str(form['dataset']), 'error_message': str(form.errors) } for form in formset.forms]  | n,unicode };
      var nameHTML = '${ str(formset.empty_form["name"]).replace("\r", "").replace("\n", "").replace("\s", "") | n,unicode }';
      var datasetHTML = '${ str(formset.empty_form["dataset"]).replace("\r", "").replace("\n", "").replace("\s", "") | n,unicode }';
      var count = initial.length;
      var root = $('#${element}');
      var table = root.find('table');
      var totalFormsEl = root.find('input[type=hidden]').filter(function() {
        return this.name.indexOf('TOTAL_FORMS') != -1;
      });
      totalFormsEl.val(initial.length);

      window.viewModel.${element} = ko.observableArray(initial);

      $(table.attr('data-missing')).trigger('register', function() {
        return window.viewModel.${element}().length == 0;
      });

      window.viewModel.add_${element} = function() {
        var newNameHTML = nameHTML.replace(new RegExp("__prefix__", 'g'), count);
        var newDatasetHTML = datasetHTML.replace(new RegExp("__prefix__", 'g'), count++);
        window.viewModel.${element}.push({name: newNameHTML, dataset: newDatasetHTML, error_message: ""});

        totalFormsEl.val(window.viewModel.${element}().length);

        $(table.attr('data-missing')).trigger('initOff', table);
      };

      window.viewModel.remove_${element} = function(val) {
        window.viewModel.${element}.remove(val);

        // The following logic is to manage formsets dynamically
        // Replace __prefix__ with '0', '1', '2' and update management table of formset
        var els = root.find(':input').filter(function() {
          return !!$(this).attr('name') && $(this).attr('name').search(/\-\d+\-/) != -1;
        });
        var count = 0;
        for (var i = 0; i < els.length; i++) {
          var el = $(els[i]);
          var name = el.attr('name').replace(/\-\d+\-/g, '-' + count + '-');
          var id = el.attr('id').replace(/\-\d+\-/g, '-' + count + '-');
          el.attr('name', name);
          el.attr('id', id);
          if (i % 2 == 1) {
            count++;
          }
        }

        totalFormsEl.val(window.viewModel.${element}().length);

        $(table.attr('data-missing')).trigger('reinit', table);
      };
    });
  </script>
</%def>
