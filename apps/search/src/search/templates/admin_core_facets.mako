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
          <div class="pull-right" style="margin-top: 10px">
            <label>
              <input type='checkbox' data-bind="checked: properties().isEnabled" style="margin-top: -2px; margin-right: 4px"/> ${_('Enabled') }
            </label>
          </div>
          <h3>${_('Facets')}</h3>
          ${_('Facets provide an intuitive way to filter the results.')}
          ${_('Different types of facets can be added on the following steps.')}
          <span data-bind="visible: !properties().isEnabled()"><strong>${_('Facets are currently disabled.')}</strong></span>
        </div>
      </div>

      <div id="facets" class="section">
        <ul class="nav nav-pills">
          <li class="active"><a href="#step1" class="step">${ _('Step 1: General') }</a></li>
          <li><a href="#step2" class="step">${ _('Step 2: Field Facets') }</a></li>
          <li><a href="#step3" class="step">${ _('Step 3: Range Facets') }</a></li>
          <li><a href="#step4" class="step">${ _('Step 4: Date Facets') }</a></li>
          <li><a href="#step5" class="step">${ _('Step 5: Facets Order') }</a></li>
        </ul>

        <div id="step1" class="stepDetails">
          <div class="control-group">
            <label class="control-label"> ${_('Limit') }</label>
            <div class="controls">
              <input type='number' data-bind="value: properties().limit" class="input-mini"/>
            </div>
          </div>
          <div class="control-group">
            <label class="control-label"> ${_('Mincount') }</label>
            <div class="controls">
              <input type='number' data-bind="value: properties().mincount" class="input-mini"/>
            </div>
          </div>
          <div class="control-group">
            <label class="control-label"> ${_('Sort') }</label>
            <div class="controls">
              <select data-bind="value: properties().sort">
                <option value="count">count</option>
                <option value="index">index</option>
              </select>
            </div>
          </div>
        </div>

        <div id="step2" class="stepDetails hide">
          <div data-bind="visible: fieldFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
            <em>${_('There are currently no field Facets defined.')}</em>
          </div>
          <div data-bind="foreach: fieldFacets">
            <div class="bubble">
              <strong><span data-bind="text: label"></span></strong>
              <span style="color:#666;font-size: 12px">(<span data-bind="text: field"></span>)</span>
              <a class="btn btn-small" data-bind="click: $root.removeFieldFacet"><i class="icon-trash"></i></a>
            </div>
          </div>
          <div class="clearfix"></div>
          <div class="miniform">
            ${_('Field')}
            <select id="select-field-facet" data-bind="options: fieldFacetsList, value: selectedFieldFacet"></select>
            &nbsp;${_('Label')}
            <input type="text" data-bind="value: selectedFieldLabel" class="input" />
            <a class="btn" data-bind="click: $root.addFieldFacet"><i class="icon-plus"></i> ${_('Add')}</a>
            &nbsp;<span id="field-facet-error" class="label label-important hide">${_('The field you are trying to add is already in the list.')}</span>
          </div>
        </div>

      <div id="step3" class="stepDetails hide">
        <div data-bind="visible: rangeFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Range Facets defined.')}</em>
        </div>
        <div data-bind="foreach: rangeFacets">
          <div class="bubble">
            <strong><span data-bind="text: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span>, <span data-bind="text: start"></span> <i class="icon-double-angle-right"></i> <span data-bind="text: end"></span>,
              <i class="icon-resize-horizontal"></i> <span data-bind="text: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeRangeFacet"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: rangeFacetsList, value: selectedRangeFacet"></select>
          &nbsp;${_('Label')}
          <input type="text" data-bind="value: selectedRangeLabel" class="input" />
          &nbsp;${_('Start')}
          <input type="number" data-bind="value: selectedRangeStartFacet" class="input-mini" />
          &nbsp;${_('End')}
          <input type="number" data-bind="value: selectedRangeEndFacet" class="input-mini" />
          &nbsp;${_('Gap')}
          <input type="number" data-bind="value: selectedRangeGapFacet" class="input-mini" />
          <a class="btn" data-bind="click: $root.addRangeFacet"><i class="icon-plus"></i> ${_('Add')}</a>
        </div>
      </div>

      <div id="step4" class="stepDetails hide">
        <div data-bind="visible: dateFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Date Facets defined.')}</em>
        </div>
        <div data-bind="foreach: dateFacets">
          <div class="bubble">
            <strong><span data-bind="text: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span>, <span data-bind="text: start"></span> <i class="icon-double-angle-right"></i> <span data-bind="text: end"></span>,
              <i class="icon-resize-horizontal"></i> <span data-bind="text: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeDateFacet"><i class="icon-trash"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: dateFacetsList, value: selectedDateFacet"></select>
          &nbsp;${_('Label')}
          <input type="text" data-bind="value: selectedDateLabel" class="input" />
          <br/>
          <br/>
          <span>
            ${_('Range from')}
            <span data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[0]}"/>
          </span>
          <span>
            &nbsp;${_('before today until')}
            <span  data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[1]}"/>
          </span>
          <span>
            &nbsp;${_('before today. Goes up by increments of')}
            <span id="scriptTable" data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[2]}"/>
          </span>
          <a class="btn" data-bind="click: $root.addDateFacet"><i class="icon-plus"></i> ${_('Add')}</a>
        </div>
      </div>

      <div id="step5" class="stepDetails hide">
        <div data-bind="visible: sortableFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Facets defined.')}</em>
        </div>
        <div data-bind="sortable: sortableFacets, afterMove: isSaveBtnVisible(true)">
          <div class="bubble" style="float: none;cursor: move">
            <i class="icon-move"></i>
            <strong><span data-bind="text: label"></span></strong>
            <span style="color:#666;font-size: 12px">(<span data-bind="text: field"></span>)</span>
          </div>
        </div>
      </div>

      <script id="scriptDateMath" type="text/html">
        <input class="input-mini" type="number" data-bind="value: frequency" />
        <select class="input-small" data-bind="value: unit">
          <option value="YEAR">YEARS</option>
          <option value="MONTH">MONTHS</option>
          <option value="DAYS">DAYS</option>
          <option value="DATE">DATE</option>
          <option value="HOURS">HOURS</option>
          <option value="MINUTES">MINUTES</option>
          <option value="SECONDS">SECONDS</option>
          <option value="MILLISECONDS">MILLISECONDS</option>
        </select>
      </script>

      </div>

      <div class="form-actions" style="margin-top: 80px">
        <a id="backBtn" class="btn disabled disable-feedback">${ _('Back') }</a>
        <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
        <button type="submit" class="btn btn-primary" data-bind="visible: isSaveBtnVisible()" id="save-facets">${_('Save')}</button>
      </div>
    </form>
  </%def>
</%layout:skeleton>

<link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />
<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js"></script>

<script type="text/javascript">
  var MOMENT_DATE_FORMAT = "MM-DD-YYYY";

  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
  }

  function UUID() {
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
  }

  var Facet = function (args) {
    return {
      uuid: (typeof args['uuid'] !== 'undefined' && args['uuid'] != null) ? args['uuid'] : UUID(),
      type: args['type'],
      field: args['field'],
      label: args['label'],
      start: args['start'],
      end: args['end'],
      gap: args['gap'],
      isVerbatim: false,
      verbatim: ""
    }
  }

  var FieldFacet = function (obj) {
    return new Facet({type: "field", field: obj.field, label: obj.label, uuid: obj.uuid});
  }

  var RangeFacet = function (obj) {
    return new Facet({type: "range", field: obj.field, label: obj.label, start: obj.start, end: obj.end, gap: obj.gap, uuid: obj.uuid});
  }

  var DateFacet = function (obj) {
    return new Facet({type: "date", field: obj.field, label: obj.label, start: obj.start, end: obj.end, gap: obj.gap, uuid: obj.uuid});
  }

  var Properties = function (properties) {
    var self = this;

    self.isEnabled = ko.observable(properties.isEnabled);
    self.limit = ko.observable(properties.limit);
    self.mincount = ko.observable(properties.mincount);
    self.sort = ko.observable(properties.sort);
  }

  var DateMath = function (args) {
    var self = this;

    self.frequency = ko.observable(args['frequency']);
    self.unit = ko.observable(args['unit']);
    self.isVerbatim = ko.observable(typeof args['isVerbatim'] !== 'undefined' ? args['isVerbatim'] : false);
    self.verbatim = ko.observable(args['verbatim']);
    self.isRounded = ko.observable(typeof args['isRounded'] !== 'undefined' ? args['isRounded'] : true);

    self.toString = function() {
      return self.frequency() + ' ' + self.unit();
    };
  }

  function ViewModel() {
    var self = this;

    self.isSaveBtnVisible = ko.observable(false);

    self.fields = ko.observableArray(${ hue_core.fields | n,unicode });

    self.fullFields = {}
    $.each(${ hue_core.fields_data | n,unicode }, function(index, field) {
      self.fullFields[field.name] = field;
    });

    self.properties = ko.observable(new Properties(${ hue_core.facets.data | n,unicode }.properties));

    self.fieldFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.fields, function (obj) {
      return new FieldFacet(obj);
    }));

    // Remove already selected fields
    self.fieldFacetsList = ko.observableArray(${ hue_core.fields | n,unicode });
    $.each(self.fieldFacets(), function(index, field) {
      self.fieldFacetsList.remove(field.field);
    });

    self.rangeFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.ranges, function (obj) {
      return new RangeFacet(obj);
    }));

    // Only ranges
    self.rangeFacetsList = ko.observableArray([]);
    $.each(self.fields(), function(index, field) {
      if (self.fullFields[field] && ['tdate', 'tint', 'long'].indexOf(self.fullFields[field].type) >= 0) {
        self.rangeFacetsList.push(field);
      }
    });

    self.dateFacets = ko.observableArray(ko.utils.arrayMap(${ hue_core.facets.data | n,unicode }.dates, function (obj) {
      return new DateFacet({
          field: obj.field,
          label: obj.label,
          start: new DateMath(obj.start),
          end: new DateMath(obj.end),
          gap: new DateMath(obj.gap),
          uuid: obj.uuid,
      });
    }));
    // Only dates
    self.dateFacetsList = ko.observableArray([]);
    $.each(self.fields(), function(index, field) {
      if (self.fullFields[field] && self.fullFields[field].type == 'tdate') {
        self.dateFacetsList.push(field);
      }
    });

    // List of all facets sorted by UUID
    self.sortableFacets = ko.observableArray(self.fieldFacets().concat(self.rangeFacets()).concat(self.dateFacets()));
    self.sortableFacets.sort(function(left, right) {
      var sorted_ids = ${ hue_core.facets.data | n,unicode }.order;
      return sorted_ids.indexOf(left.uuid) > sorted_ids.indexOf(right.uuid);
    })

    self.selectedFieldFacet = ko.observable();
    self.selectedFieldLabel = ko.observable("");
    self.selectedRangeFacet = ko.observable();
    self.selectedRangeLabel = ko.observable("");
    self.selectedRangeStartFacet = ko.observable(0);
    self.selectedRangeEndFacet = ko.observable(100);
    self.selectedRangeGapFacet = ko.observable(10);

    self.selectedDateFacet = ko.observable();
    self.selectedDateLabel = ko.observable("");

    self.selectedDateDateMaths = ko.observableArray([
        // Same as addDateFacet()
        new DateMath({frequency: 10, unit: 'DAYS'}),
        new DateMath({frequency: 0, unit: 'DAYS'}),
        new DateMath({frequency: 1, unit: 'DAYS'})
    ]);


    self.removeFieldFacet = function (facet) {
      self.fieldFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.fieldFacetsList.push(facet.field);
      self.fieldFacetsList.sort();
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.removeRangeFacet = function (facet) {
      self.rangeFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.removeDateFacet = function (facet) {
      self.dateFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.updateSortableFacets = function () {
      self.isSaveBtnVisible(true);
    };

    self.addFieldFacet = function () {
      var found = false;
      ko.utils.arrayForEach(self.fieldFacets(), function(facet) {
        if (facet.field == self.selectedFieldFacet()){
          found = true;
        }
      });
      if (!found){
        if (self.selectedFieldLabel() == ""){
          self.selectedFieldLabel(self.selectedFieldFacet());
        }
        var newFacet = new FieldFacet({field: self.selectedFieldFacet(), label: self.selectedFieldLabel()});
        self.fieldFacets.push(newFacet);
        self.sortableFacets.push(newFacet);
        self.selectedFieldLabel("");
        self.fieldFacetsList.remove(self.selectedFieldFacet());
        self.properties().isEnabled(true);
        self.updateSortableFacets();
        self.isSaveBtnVisible(true);
      }
      else {
        $("#field-facet-error").show();
      }
    };

    self.addRangeFacet = function () {
      if (self.selectedRangeLabel() == ""){
        self.selectedRangeLabel(self.selectedRangeFacet());
      }
      var newFacet = new RangeFacet({
          field: self.selectedRangeFacet(),
          label: self.selectedRangeLabel(),
          start: self.selectedRangeStartFacet(),
          end: self.selectedRangeEndFacet(),
          gap: self.selectedRangeGapFacet()
       });
      self.rangeFacets.push(newFacet);
      self.sortableFacets.push(newFacet);
      self.selectedRangeLabel("");
      self.selectedRangeStartFacet(0);
      self.selectedRangeEndFacet(100);
      self.selectedRangeGapFacet(10);
      self.properties().isEnabled(true);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.addDateFacet = function () {
      if (self.selectedDateLabel() == ""){
        self.selectedDateLabel(self.selectedDateFacet());
      }
      var newFacet = new DateFacet({
          field: self.selectedDateFacet(),
          label: self.selectedDateLabel(),
          start: self.selectedDateDateMaths()[0],
          end: self.selectedDateDateMaths()[1],
          gap: self.selectedDateDateMaths()[2]
      });
      self.dateFacets.push(newFacet);
      self.sortableFacets.push(newFacet);
      self.selectedDateLabel("");
      self.selectedDateDateMaths([
        new DateMath({frequency: 10, unit: 'DAYS'}),
        new DateMath({frequency: 0, unit: 'DAYS'}),
        new DateMath({frequency: 1, unit: 'DAYS'})
      ]);
      self.properties().isEnabled(true);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.submit = function () {
      $.ajax("${ url('search:admin_core_facets', core=hue_core.name) }", {
        data: {
          'properties': ko.toJSON(self.properties),
          'fields': ko.utils.stringifyJson(self.fieldFacets),
          'ranges': ko.utils.stringifyJson(self.rangeFacets),
          'dates': ko.toJSON(self.dateFacets),
          'order': ko.toJSON(ko.utils.arrayMap(self.sortableFacets(), function (obj) {
                      return obj.uuid;
           }))
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $.jHueNotify.info("${_('Facets updated')}");
          self.isSaveBtnVisible(false);
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
    viewModel.isSaveBtnVisible(false);

    $("#select-field-facet").click(function(){
      $("#field-facet-error").hide();
    });

    var currentStep = "step1";

    routie({
      "step1":function () {
        showStep("step1");
      },
      "step2":function () {
        if (validateStep("step1")) {
          showStep("step2");
        }
      },
      "step3":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step3");
        }
      },
      "step4":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step4");
        }
      },
      "step5":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step5");
        }
      }
    });

      function showStep(step) {
        currentStep = step;
        if (step != "step1") {
          $("#backBtn").removeClass("disabled");
        }
        else {
          $("#backBtn").addClass("disabled");
        }
        if (step != $(".stepDetails:last").attr("id")) {
          $("#nextBtn").removeClass("disabled");
        }
        else {
          $("#nextBtn").addClass("disabled");
        }
        $("a.step").parent().removeClass("active");
        $("a.step[href=#" + step + "]").parent().addClass("active");
        $(".stepDetails").hide();
        $("#" + step).show();
      }

      function showSection(section) {
        $(".section").hide();
        $("#" + section).show();
      }

      function validateStep(step) {
        var proceed = true;
        $("#" + step).find("[validate=true]").each(function () {
          if ($(this).val().trim() == "") {
            proceed = false;
            routie(step);
            $(this).parents(".control-group").addClass("error");
            $(this).parent().find(".help-inline").remove();
            $(this).after("<span class=\"help-inline\"><strong>${ _('This field is required.') }</strong></span>");
          }
        });
        return proceed;
      }

      $("#backBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 - 1);
        if (nextStep >= 1) {
          routie("step" + nextStep);
        }
      });

      $("#nextBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 + 1);
        if (nextStep <= $(".step").length) {
          routie("step" + nextStep);
        }
      });
  });
</script>

${ commonfooter(messages) | n,unicode }
