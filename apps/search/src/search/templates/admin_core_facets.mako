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
    <h1>${_('Search Admin - ')}${hue_core.label}</h1>
  </%def>
  <%def name="navigation()">
    ${ layout.sidebar(hue_core.name, 'facets') }
  </%def>
  <%def name="content()">
    <form method="POST" class="form-horizontal" data-bind="submit: submit">

      <div class="section">
        <div class="alert alert-info">
          <div class="pull-right">
            <label>
              <input type='checkbox' data-bind="checked: isEnabled" style="margin-top: -2px; margin-right: 4px"/> ${_('Enabled') }
            </label>
          </div>         
          <h4>${_('Facets')}</h4>
        </div>
      </div>

      <div class="section">
        <div class="alert alert-info" style="margin-top: 60px"><h4>${_('Field Facets')}</h4></div>
        <div data-bind="visible: fieldFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no field Facets defined.')}</em>
        </div>
        <div data-bind="foreach: fieldFacets">
          <div class="bubble">
            <strong><span data-bind="text: field"></span></strong>
            <a class="btn btn-small" data-bind="click: $root.removeFieldFacet"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select id="select-field-facet" data-bind="options: fields, value: selectedFieldFacet"></select>
          <a class="btn" data-bind="click: $root.addFieldFacet"><i class="icon-plus"></i> ${_('Add field')}</a>
          &nbsp;<span id="field-facet-error" class="label label-important hide">${_('The field you are trying to add is already in the list.')}</span>
        </div>
      </div>

      <div class="section">
        <div class="alert alert-info" style="margin-top: 60px"><h4>${_('Range Facets')}</h4></div>
        <div data-bind="visible: rangeFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Range Facets defined.')}</em>
        </div>
        <div data-bind="foreach: rangeFacets">
          <div class="bubble">
            <strong><span data-bind="text: field"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: start"></span> <i class="icon-double-angle-right"></i> <span data-bind="text: end"></span>,
              <i class="icon-resize-horizontal"></i> <span data-bind="text: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeRangeFacet"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: fields, value: selectedRangeFacet"></select>
          &nbsp;${_('Start')}
          <input type="number" data-bind="value: selectedRangeStartFacet" class="input-mini" />
          &nbsp;${_('End')}
          <input type="number" data-bind="value: selectedRangeEndFacet" class="input-mini" />
          &nbsp;${_('Gap')}
          <input type="number" data-bind="value: selectedRangeGapFacet" class="input-mini" />
          <a class="btn" data-bind="click: $root.addRangeFacet"><i class="icon-plus"></i> ${_('Add field')}</a>
        </div>
      </div>

      <div class="section">
        <div class="alert alert-info" style="margin-top: 60px"><h4>${_('Date Facets')}</h4></div>
        <div data-bind="visible: dateFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Date Facets defined.')}</em>
        </div>
        <div data-bind="foreach: dateFacets">
          <div class="bubble">
            <strong><span data-bind="text: field"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: start"></span> <i class="icon-double-angle-right"></i> <span data-bind="text: end"></span>,
              <i class="icon-resize-horizontal"></i> <span data-bind="text: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeDateFacet"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: fields, value: selectedDateFacet"></select>
          &nbsp;${_('Start')}
          <input id="dp-start" class="input-small" type="text" data-bind="value: selectedDateStartFacet" />
          &nbsp;${_('End')}
          <input id="dp-end" class="input-small" type="text" data-bind="value: selectedDateEndFacet" />
          &nbsp;${_('Gap')}
          <input type="number" data-bind="value: selectedDateGapFacet" class="input-mini" />
          <a class="btn" data-bind="click: $root.addDateFacet"><i class="icon-plus"></i> ${_('Add field')}</a>
        </div>
      </div>


      <div class="form-actions" style="margin-top: 80px">
        <button type="submit" class="btn btn-primary" id="save-facets">${_('Save')}</button>
      </div>
    </form>
  </%def>
</%layout:skeleton>

<link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  var DATE_FORMAT = "mm-dd-yyyy";

  var Facet = function (type, field, start, end, gap) {
    return {
      type: type,
      field: field,
      start: start,
      end: end,
      gap: gap
    }
  }

  var FieldFacet = function (field) {
    return new Facet("field", field);
  }

  var RangeFacet = function (field, start, end, gap) {
    return new Facet("range", field, start, end, gap);
  }

  var DateFacet = function (field, start, end, gap) {
    return new Facet("date", field, start, end, gap);
  }

  function ViewModel() {
    var self = this;
    self.fields = ko.observableArray(${ hue_core.fields | n,unicode });

    self.isEnabled = ko.observable(${ hue_core.facets.data | n,unicode }.properties.is_enabled);

    self.fieldFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.fields, function (obj) {
      return new FieldFacet(obj.field);
    }));

    self.rangeFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.ranges, function (obj) {
      return new RangeFacet(obj.field, obj.start, obj.end, obj.gap);
    }));

    self.dateFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.dates, function (obj) {
      return new DateFacet(obj.field, obj.start, obj.end, obj.gap);
    }));

    self.selectedFieldFacet = ko.observable();
    self.selectedRangeFacet = ko.observable();
    self.selectedRangeStartFacet = ko.observable("");
    self.selectedRangeEndFacet = ko.observable("");
    self.selectedRangeGapFacet = ko.observable("");
    self.selectedDateFacet = ko.observable();
    self.selectedDateStartFacet = ko.observable("");
    self.selectedDateEndFacet = ko.observable("");
    self.selectedDateGapFacet = ko.observable("");

    self.removeFieldFacet = function (facet) {
      self.fieldFacets.remove(facet);
    };

    self.removeRangeFacet = function (facet) {
      self.rangeFacets.remove(facet);
    };

    self.removeDateFacet = function (facet) {
      self.dateFacets.remove(facet);
    };

    self.addFieldFacet = function () {
      var found = false;
      ko.utils.arrayForEach(self.fieldFacets(), function(facet) {
        if (facet.field == self.selectedFieldFacet()){
          found = true;
        }
      });
      if (!found){
        self.fieldFacets.push(new FieldFacet(self.selectedFieldFacet()));
      }
      else {
        $("#field-facet-error").show();
      }
    };

    self.addRangeFacet = function () {
      self.rangeFacets.push(new RangeFacet(self.selectedRangeFacet(), self.selectedRangeStartFacet(), self.selectedRangeEndFacet(), self.selectedRangeGapFacet()));
      self.selectedRangeStartFacet("");
      self.selectedRangeEndFacet("");
      self.selectedRangeGapFacet("");
    };

    self.addDateFacet = function () {
      self.dateFacets.push(new DateFacet(self.selectedDateFacet(), self.selectedDateStartFacet(), self.selectedDateEndFacet(), self.selectedDateGapFacet()));
      self.selectedDateStartFacet("");
      self.selectedDateEndFacet("");
      self.selectedDateGapFacet("");
    };

    self.submit = function () {
      $.ajax("${ url('search:admin_core_facets', core=hue_core.name) }", {
        data: {
          'properties': ko.utils.stringifyJson({'is_enabled': self.isEnabled()}),
          'fields': ko.utils.stringifyJson(self.fieldFacets),
          'ranges': ko.utils.stringifyJson(self.rangeFacets),
          'dates': ko.utils.stringifyJson(self.dateFacets)
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $.jHueNotify.info("${_('Facets updated')}");
        },
        error: function (data) {
          $.jHueNotify.error("${_('Error: ')}" + data);
        },
        complete: function() {
          $("#save-facets").button('reset');
        }
      });
    };
  };

  var viewModel = new ViewModel();

  $(document).ready(function () {
    $(".btn-primary").button("reset");
    ko.applyBindings(viewModel);
    $("#select-field-facet").click(function(){
      $("#field-facet-error").hide();
    });
    $("#dp-start").datepicker({
      format: DATE_FORMAT
    }).on("changeDate", function(e){
      viewModel.selectedDateStartFacet($(this).val());
    });
    $("#dp-end").datepicker({
      format: DATE_FORMAT
    }).on("changeDate", function(e){
      viewModel.selectedDateEndFacet($(this).val());
    });
  });
</script>

${ commonfooter(messages) | n,unicode }

