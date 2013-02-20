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

<%namespace name="layout" file="layout.mako" />
<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }

<%layout:skeleton>
  <%def name="title()">
    <h1>${_('Search Admin - ')}${hue_core.name}</h1>
  </%def>
  <%def name="navigation()">
    ${ layout.sidebar(hue_core.name, 'facets') }
  </%def>
  <%def name="content()">
    <form method="POST" id="facets" data-bind="submit: submit">

    <div class="well"><h3>${_('Field Facets')}</h3></div>

    <table class="table table-striped">
      <thead data-bind="visible: fieldsFacets().length == 0">
      <tr>
        <td colspan="3">
          <div class="alert">
          ${_('There are currently no field Facets defined. Please add at least one from the bottom.')}
          </div>
        </td>
      </tr>
      </thead>
      <tbody id="fields" data-bind="foreach: fieldsFacets">
      <tr data-bind="attr: {'data-field': $data}">
        <td><span data-bind="text: $data"></span></td>
        <td width="30"><a class="btn btn-small" data-bind="click: $root.removeFieldsFacets"><i class="icon-trash"></i></a></td>
      </tr>
      </tbody>
      <tfoot>
      <tr style="padding-top: 20px">
        <td><select data-bind="options: fields, value: selectedField" style="width:100%"></select></td>
        <td width="30"><a class="btn btn-small" data-bind="click: $root.addFieldsFacets"><i class="icon-plus"></i></a></td>
      </tr>
      </tfoot>
    </table>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary btn-large" id="save-facets">${_('Save Facets')}</button>
    </div>
    </form>
  </%def>
</%layout:skeleton>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function () {
    function ViewModel() {
      var self = this;
      self.fields = ko.observableArray(${ hue_core.fields | n,unicode });
      self.fieldsFacets = ko.observableArray(${ hue_core.facets.data | n,unicode }.fields
    )
      ;
      self.selectedField = ko.observable();

      self.removeFieldsFacets = function (facet) {
        self.fieldsFacets.remove(facet);
      };

      self.addFieldsFacets = function () {
        self.fieldsFacets.push(self.selectedField());
      };

      self.submit = function () {
        $.ajax("${ url('search:admin_core_facets', core=hue_core.name) }", {
          data: {'fields': ko.utils.stringifyJson(self.fieldsFacets)},
          contentType: 'application/json',
          type: 'POST',
          complete: function (data) {
            location.reload();
          }
        });
      };
    };

    ko.applyBindings(new ViewModel());

  });
</script>

${ commonfooter(messages) | n,unicode }

