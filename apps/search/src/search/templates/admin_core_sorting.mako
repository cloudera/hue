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
    ${ layout.sidebar(hue_core.name, 'sorting') }
  </%def>
  <%def name="content()">
    <div class="well"><h3>${_('Fields')}</h3></div>

    <table class="table table-striped">
      <thead data-bind="visible: fieldsSorting().length == 0">
        <tr>
          <td colspan="3">
            <div class="alert">
            ${_('There are currently no Sorting fields defined. Please add at least one from the bottom.')}
            </div>
          </td>
        </tr>
      </thead>
      <tbody id="fields" data-bind="foreach: fieldsSorting">
        <tr data-bind="attr: {'data-field': $data}">
          <td width="30"><i class="icon-list"></i></td>
          <td><span data-bind="text: $data"></span></td>
          <td width="30"><a class="btn btn-small" data-bind="click: $root.removeFieldSorting"><i class="icon-trash"></i></a></td>
        </tr>
      </tbody>
      <tfoot>
        <tr style="padding-top: 20px">
          <td colspan="2"><select data-bind="options: fields, value: selectedField" style="width:100%"></select></td>
          <td width="30"><a class="btn btn-small" data-bind="click: $root.addFieldSorting"><i class="icon-plus"></i></a></td>
        </tr>
      </tfoot>
    </table>

    <div class="form-actions">
      <a class="btn btn-primary btn-large" id="save-sorting">${_('Save Sorting')}</a>
    </div>
  </%def>
</%layout:skeleton>

<style type="text/css">
  #fields {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  #fields li {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #E3E3E3;
    height: 30px;
  }

  .placeholder {
    height: 30px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }
</style>


<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js"></script>

<script type="text/javascript">
  $(document).ready(function () {
    function ViewModel() {
      var self = this;
      self.fields = ko.observableArray(${ hue_core.fields | n,unicode });
      self.fieldsSorting = ko.observableArray();

      self.selectedField = ko.observable();

      self.removeFieldSorting = function (sort) {
        self.fieldsSorting.remove(sort);
      };

      self.addFieldSorting = function () {
        self.fieldsSorting.push(self.selectedField());
      };

      self.submit = function () {
        $.ajax("${ url('search:admin_core_sorting', core=hue_core.name) }", {
          data: {'fields': ko.utils.stringifyJson(self.fieldsSorting)},
          contentType: 'application/json',
          type: 'POST',
          complete: function (data) {
            location.reload();
          }
        });
      };
    };

    var viewModel = new ViewModel();
    ko.applyBindings(viewModel);

    $("#fields").sortable({
      placeholder: "placeholder",
      update: function (event, ui) {
        var reorderedFields = [];
        $("#fields tr").each(function () {
          reorderedFields.push($(this).data("field"));
        });
        viewModel.fieldsSorting([]);
        viewModel.fieldsSorting(reorderedFields);
      }
    });
    $("#fields").disableSelection();

    $("#save-sorting").click(function () {
      ##TODO: save sorting
      ## you can access to the fields like this: viewModel.fieldsSorting()
      ## console.log(viewModel.fieldsSorting());
    });

  });
</script>


${ commonfooter(messages) | n,unicode }
