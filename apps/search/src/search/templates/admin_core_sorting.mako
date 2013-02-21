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
    <form method="POST" class="form-horizontal" data-bind="submit: submit">
      <div class="section">
        <div class="alert alert-info"><h4>${_('Sorting Fields')}</h4></div>
        <div data-bind="visible: sortingFields().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Sorting Fields defined. Please add at least one from the bottom.')}</em>
        </div>
        <div data-bind="foreach: sortingFields">
          <div class="bubble">
            <strong><span data-bind="text: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span> <i class="icon-arrow-up" data-bind="visible: asc == true"></i><i class="icon-arrow-down" data-bind="visible: asc == false"></i> )
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeSortingField"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: fields, value: newFieldSelect"></select>
          &nbsp;${_('Label')}
          <input type="text" data-bind="value: newFieldLabel" class="input" />
          &nbsp;${_('Sorting')}
          <div class="btn-group" style="display: inline">
            <button id="newFieldAsc" type="button" data-bind="css: {'active': newFieldAscDesc() == 'asc', 'btn': true}"><i class="icon-arrow-up"></i></button>
            <button id="newFieldDesc" type="button" data-bind="css: {'active': newFieldAscDesc() == 'desc', 'btn': true}"><i class="icon-arrow-down"></i></button>
          </div>
          &nbsp;&nbsp;<a class="btn" data-bind="click: $root.addSortingField"><i class="icon-plus"></i> ${_('Add field to Sorting Fields')}</a>
        </div>
      </div>

      <div class="form-actions" style="margin-top: 80px">
        <button type="submit" class="btn btn-primary">${_('Save Sorting')}</button>
        <a class="btn" href="${ url('search:admin') }"><i class="icon-list"></i> ${ _('Return to Core list') }</a>
        <a class="btn" href="${ url('search:index') }"><i class="icon-search"></i> ${ _('Back to Search') }</a>
      </div>
    </form>
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

  var SortingField = function (field, label, asc) {
    return {
      field:field,
      label: label,
      asc: asc
    }
  }

  function ViewModel() {
    var self = this;
    self.fields = ko.observableArray(${ hue_core.fields | n,unicode });

    self.sortingFields = ko.observableArray(ko.utils.arrayMap([], function (obj) {
      return new SortingField(obj.field, obj.label, obj.asc);
    }));

    self.newFieldSelect = ko.observable();
    self.newFieldLabel = ko.observable("");
    self.newFieldAscDesc = ko.observable("asc");

    self.removeSortingField = function (field) {
      self.sortingFields.remove(field);
    };

    self.addSortingField = function () {
      if (self.newFieldLabel() == ""){
        self.newFieldLabel(self.newFieldSelect());
      }
      self.sortingFields.push(new SortingField(self.newFieldSelect(), self.newFieldLabel(), self.newFieldAscDesc()=="asc"));
      self.newFieldLabel("");
      self.newFieldAscDesc("asc");
    };

    self.submit = function () {
      ##TODO: the sorting fields are in self.sortingFields
      console.log(ko.utils.stringifyJson(self.sortingFields));
    };
  };

  var viewModel = new ViewModel();

  $(document).ready(function () {

    ko.applyBindings(viewModel);

    $("#newFieldAsc").click(function(){
      viewModel.newFieldAscDesc("asc");
    });

    $("#newFieldDesc").click(function(){
      viewModel.newFieldAscDesc("desc");
    });

  });
</script>


${ commonfooter(messages) | n,unicode }
