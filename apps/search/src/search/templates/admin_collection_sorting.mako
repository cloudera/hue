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

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<%layout:skeleton>
  <%def name="title()">
    <h4>${ _('Sorting for') } <strong>${ hue_collection.name }</strong></h4>
  </%def>

  <%def name="navigation()">
    ${ layout.sidebar(hue_collection, 'sorting') }
  </%def>

  <%def name="content()">

    <link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
    <script src="/static/ext/js/bootstrap-editable.min.js"></script>
    <script src="/static/js/ko.editable.js"></script>

    <form method="POST" class="form-horizontal" data-bind="submit: submit">
      <div class="well">
      <div class="section">
        <div class="alert alert-info">
          <div class="pull-right" style="margin-top: 10px">
            <label>
              <input type='checkbox' data-bind="checked: isEnabled" style="margin-top: -2px; margin-right: 4px"/> ${_('Enabled') }
            </label>
          </div>
          <h3>${_('Sorting')}</h3>
          ${_('Specify on which fields and order the results are sorted by default.')}
          ${_('The sorting is a combination of the "Default sorting" fields, from left to right.')}
          <span data-bind="visible: ! isEnabled()"><strong>${_('Sorting is currently disabled.')}</strong></span>
        </div>
      </div>

      <div class="section" style="padding: 5px">
        <div data-bind="visible: sortingFields().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no fields defined.')}</em>
        </div>
        <div data-bind="sortable: sortingFields">
          <div class="bubble" style="cursor: move">
            <i class="fa fa-arrows"></i>
            <strong><span data-bind="editable: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span> <i class="fa fa-arrow-up" data-bind="visible: asc() == true"></i><i class="fa fa-arrow-down" data-bind="visible: asc() == false"></i> <span data-bind="editable: order"></span>, <input type="checkbox" data-bind="checked: include" style="margin-top:0" /> ${_('Default sorting')} )
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeSortingField"><i class="fa fa-trash-o"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: sortingFieldsList, value: newFieldSelect"></select>
          &nbsp;${_('Label')}
          <input id="newFieldLabel" type="text" data-bind="value: newFieldLabel" class="input" />
          &nbsp;${_('Sorting')}
          <div class="btn-group" style="display: inline">
            <button id="newFieldAsc" type="button" data-bind="css: {'active': newFieldAscDesc() == 'asc', 'btn': true}"><i class="fa fa-arrow-up"></i></button>
            <button id="newFieldDesc" type="button" data-bind="css: {'active': newFieldAscDesc() == 'desc', 'btn': true}"><i class="fa fa-arrow-down"></i></button>
          </div>
          <label class="checkbox" style="display: inline">
            <input id="newFieldInclude" type="checkbox" style="float:none;margin-left:0;margin-top: -2px;margin-right: 4px"  data-bind="checked: newFieldIncludeInSorting" /> ${_('Include in default sorting')}
          </label>
          <br/>
          <br/>
          <a class="btn" data-bind="click: $root.addSortingField"><i class="fa fa-plus-circle"></i> ${_('Add to Sorting')}</a>
        </div>
      </div>

      <div class="form-actions" style="margin-top: 80px">
        <button type="submit" class="btn btn-primary" id="save-sorting">${_('Save')}</button>
      </div>
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

<script src="/search/static/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js"></script>

<script type="text/javascript">

  var SortingField = function (field, label, asc, include) {
    var _field = {
      field: field,
      label: ko.observable(label),
      asc: ko.observable(asc),
      order: ko.observable(asc ? "ASC" : "DESC"),
      include: ko.observable(include)
    };
    _field.label.subscribe(function (newValue) {
      if ($.trim(newValue) == "") {
        _field.label(f.field);
      }
    });
    _field.order.subscribe(function (newValue) {
      if ($.trim(newValue).toUpperCase() == "DESC") {
        _field.asc(false);
      }
      else {
        _field.asc(true);
      }
    });

    return _field;
  }

  function ViewModel() {
    var self = this;
    self.fields = ko.observableArray(${ hue_collection.fields(user) | n,unicode });

    self.isEnabled = ko.observable(${ hue_collection.sorting.data | n,unicode }.properties.is_enabled);

    self.sortingFields = ko.observableArray(ko.utils.arrayMap(${ hue_collection.sorting.data | n,unicode }.fields, function (obj) {
      return new SortingField(obj.field, obj.label, obj.asc, obj.include);
    }));

    var _cleanedFields = ko.utils.arrayFilter(${ hue_collection.fields_data(user) | n,unicode }, function (fieldObj) {
      return fieldObj.type != "multiValued";
    });

    self.sortingFieldsList = ko.observableArray(ko.utils.arrayMap(_cleanedFields, function (fieldObj) {
      return fieldObj.name;
    }));

    self.newFieldSelect = ko.observable();
    self.newFieldSelect.subscribe(function (newValue) {
      $("#newFieldLabel").prop("placeholder", newValue);
    });

    self.newFieldLabel = ko.observable("");
    self.newFieldAscDesc = ko.observable("asc");

    self.newFieldIncludeInSorting = ko.observable(true);

    self.removeSortingField = function (field) {
      self.sortingFields.remove(field);
      self.sortingFieldsList.sort();
      if (self.sortingFields().length == 0) {
        self.isEnabled(false);
      }
    };

    self.addSortingField = function () {
      if (self.newFieldLabel() == ""){
        self.newFieldLabel(self.newFieldSelect());
      }
      self.sortingFields.push(new SortingField(self.newFieldSelect(), self.newFieldLabel(), self.newFieldAscDesc() == "asc", self.newFieldIncludeInSorting()));
      self.newFieldLabel("");
      self.newFieldAscDesc("asc");
      self.newFieldIncludeInSorting(true);
      self.isEnabled(true);
    };

    self.submit = function () {
      $.ajax("${ url('search:admin_collection_sorting', collection_id=hue_collection.id) }", {
        data: {
          'properties': ko.toJSON({'is_enabled': self.isEnabled()}),
          'fields': ko.toJSON(self.sortingFields)
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $(document).trigger("info", "${_('Sorting updated')}");
        },
        error: function (data) {
          $(document).trigger("error", "${_('Error: ')}" + data);
        },
        complete: function() {
          $("#save-sorting").button('reset');
        }
      });
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
