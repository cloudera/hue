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


<%def name="key_value_field(label, help_text, javascript_attrs={})">
  <div id="${ javascript_attrs['name'] }" class="control-group ko-${ javascript_attrs['name'] }" rel="popover"
      data-original-title="${ label }" data-content="${ help_text }">
    <label class="control-label">${ label }</label>

    <div class="controls">
      <table class="table-condensed designTable" data-bind="visible: ${ javascript_attrs['name'] }().length > 0" style="text-align: left;">
        <thead>
          <tr>
            <th>${ _('Name') }</th>
            <th>${ _('Value') }</th>
            <th/>
          </tr>
        </thead>
        <tbody data-bind="foreach: ${ javascript_attrs['name'] }">
          <tr>
            <td><input type="text" class="required" data-bind="value: name" /></td>
            <td><input type="text" class="required" data-bind="value: value" /></td>
            <td><a class="btn btn-small" href="#" data-bind="click: function(data, event) { ${ javascript_attrs['remove'] }.call($root, data, event) }">${ _('Delete') }</a></td>
          </tr>
        </tbody>
      </table>

      <button class="btn" data-bind="click: function(data, event) { ${ javascript_attrs['add'] }.call($root, data, event) }">${ _('Add') }</button>
    </div>
  </div>
</%def>
