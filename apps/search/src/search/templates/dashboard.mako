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
from django.utils.dateparse import parse_datetime
from search.api import utf_quoter
import urllib
import math
import time
%>

${ commonheader(_('Search'), "search", user, "70px") | n,unicode }

<style type="text/css">
  .dashboard .container-fluid {
    padding: 10px;
  }

  .row-container {
    width: 100%;
    min-height: 70px;
  }

  .ui-sortable {
    background-color: #F6F6F6;
  }

  .ui-sortable h2 {
    padding-left: 10px!important;
  }

  .ui-sortable h2 ul {
    float: left;
    margin-right: 10px;
    font-size: 14px;
  }

  .ui-sortable:not(.ui-sortable-disabled) h2 {
    cursor: move;
  }

  .ui-sortable-disabled {
    background-color: #FFF;
  }

  .card-column {
    border: none;
    min-height: 400px!important;
  }

  .card-widget {
    margin: 4px!important;
    padding-top: 0;
  }

  .card-toolbar {
    margin: 0;
    padding: 4px;
    padding-top: 10px;
  }

  .row-header {
    background-color: #F6F6F6;
    display: inline;
    padding: 4px;
  }

  #emptyHint {
    position: absolute;
    right: 14px;
    top: 80px;
    color: #666;
    font-size: 20px;
  }

  .preview-row {
    background-color: #DDD;
    min-height: 400px!important;
    margin-top: 30px;
  }

  .draggable-widget {
    width: 100px;
    text-align: center;
    float: left;
    border: 1px solid #CCC;
    margin-top: 10px;
    margin-right: 10px;
    cursor: move;
  }
  .draggable-widget a {
    font-size: 58px;
    line-height: 76px;
    cursor: move;
  }

  .unselectable {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }

</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="pull-right">
        <button type="button" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>
      </div>
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="/search">
              <img src="/search/static/art/icon_search_24.png">
              Collection name
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="card card-toolbar" data-bind="slideVisible: isEditing">
  <div style="float: left">
    <div style="font-weight: bold; color: #999; padding-left: 8px">${_('LAYOUT')}</div>
    <a href="javascript: oneThirdLeftLayout()" onmouseover="viewModel.previewColumns('oneThirdLeft')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_onethirdleft.png" /></a>
    <a href="javascript: halfLayout()" onmouseover="viewModel.previewColumns('half')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_half.png" /></a>
    <a href="javascript: oneThirdRightLayout()" onmouseover="viewModel.previewColumns('oneThirdRight')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_onethirdright.png" /></a>
    <a href="javascript: fullLayout()" onmouseover="viewModel.previewColumns('full')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_full.png" /></a>
  </div>

  <div style="float: left; margin-left: 20px" data-bind="visible: columns().length > 0">
    <div style="font-weight: bold; color: #999; padding-left: 8px">${_('WIDGETS')}</div>
    <div class="draggable-widget" data-bind="draggable: draggableFacet" title="${_('Field Facet')}" rel="tooltip" data-placement="top"><a href="#"><i class="fa fa-filter"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggableResultset" title="${_('Results')}" rel="tooltip" data-placement="top"><a href="#"><i class="fa fa-tasks"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggableBar" title="${_('Bar Chart')}" rel="tooltip" data-placement="top"><a href="#"><i class="fa fa-bar-chart-o"></i></a></div>
  </div>
  <div class="clearfix"></div>
</div>

<div id="emptyHint" data-bind="visible: !isEditing() && columns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${_('Click on the pencil to get started with your dashboard!')}</div>
  <img src="/search/static/art/hint_arrow.png" />
</div>

<div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneThirdLeft'">
      <div class="span3 preview-row"></div>
      <div class="span9 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'half'">
      <div class="span6 preview-row"></div>
      <div class="span6 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneThirdRight'">
      <div class="span9 preview-row"></div>
      <div class="span3 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'full'">
      <div class="span12 preview-row">
      </div>
    </div>
  </div>
</div>

<div data-bind="css: {'dashboard': true, 'unselectable': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="template: { name: 'column-template', foreach: columns}">
    </div>
  </div>
</div>

<script type="text/html" id="column-template">
  <div data-bind="css: klass">
    <div style="height: 30px; text-align: right" data-bind="visible: $root.isEditing">
      <a href="javascript:void(0)" class="btn" style="margin: 4px; margin-right: 10px" data-bind="click: addEmptyRow"><i class="fa fa-plus-circle"></i> Add row</a>
    </div>
    <h4 style="text-align: center" class="muted" data-bind="visible: rows().length == 0">I'm your blank canvas.<br/>Please fill me up with widgets!</h4>
    <div data-bind="template: { name: 'row-template', foreach: rows}">
    </div>
  </div>
</script>

<script type="text/html" id="row-template">
  <div class="container-fluid">
    <div class="row-header" data-bind="visible: $root.isEditing">
      <i class="fa fa-th-list muted"></i>
      <div style="display: inline; margin-left: 60px">
        <a href="javascript:void(0)" data-bind="click: moveDown"><i class="fa fa-chevron-down"></i></a>
        <a href="javascript:void(0)" data-bind="click: moveUp"><i class="fa fa-chevron-up"></i></a>
        <a href="javascript:void(0)" data-bind="click: function(){remove($parent, this)}"><i class="fa fa-trash-o"></i></a>
      </div>
    </div>
    <div class="row-fluid row-container" data-bind="sortable: { template: 'widget-template', data: widgets, isEnabled: $root.isEditing, dragged: tempBarChart}">
    </div>
  </div>
</script>

<script type="text/html" id="widget-template">
  <div data-bind="css: klass">
    <h2 class="card-heading simple">
      <ul class="inline" data-bind="visible: $root.isEditing">
      <li><a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a></li>
      <li><a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a></li>
    </ul>
      <span data-bind="text: name"></span>
    </h2>
    <div class="card-body">
      <p>
        <div data-bind="template: { name: function() { return widgetType(); }, data: properties }"></div>
      </p>
    </div>
  </div>
</script>

<script type="text/html" id="empty-widget">
  Hic sunt leones.
</script>

<script type="text/html" id="facet-widget">
  This is the facet widget
</script>


<script type="text/html" id="resultset-widget">
  This is the resultset widget
</script>

<script type="text/html" id="timeline-widget">
  This is the TIMELINE widget
</script>

<script type="text/html" id="bar-widget">
  This is the bar widget
  <div id="barsample"></div>
</script>

<script type="text/html" id="pie-widget">
  This is the pie widget
</script>

<script type="text/html" id="map-widget">
  This is the map widget
</script>


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.categories.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>

<script type="text/javascript">

  var d1 = [];
  for (var i = 0; i < 14; i += 0.5) {
    d1.push([i, Math.sin(i)]);
  }
  var d6 = [];
  for (var i = 0; i < 14; i += 0.5 + Math.random()) {
    d6.push([i, Math.sqrt(2 * i + Math.sin(i) + 5)]);
  }

  function tempBarChart() {
    window.setTimeout(function () {
      $("#barsample").jHueBlueprint({
        data: d6,
        type: $.jHueBlueprint.TYPES.BARCHART,
        color: $.jHueBlueprint.COLORS.GREEN,
        fill: true
      });
      $("#barsample").jHueBlueprint("add", {
        data: d1,
        type: $.jHueBlueprint.TYPES.BARCHART,
        color: $.jHueBlueprint.COLORS.ORANGE,
        fill: false
      });

    }, 50)
  }


  ko.bindingHandlers.slideVisible = {
    init: function (element, valueAccessor) {
      var value = valueAccessor();
      $(element).toggle(ko.unwrap(value));
    },
    update: function (element, valueAccessor) {
      var value = valueAccessor();
      ko.unwrap(value) ? $(element).slideDown(100) : $(element).slideUp(100);
    }
  };


  var DashBoardViewModel = function () {
    var self = this;
    self.previewColumns = ko.observable("");
    self.columns = ko.observableArray([]);
    self.isEditing = ko.observable(true);
    self.draggableFacet = ko.observable(new Widget(12, "Facet", "facet-widget"));
    self.draggableResultset = ko.observable(new Widget(12, "Results", "resultset-widget"));
    self.draggableBar = ko.observable(new Widget(12, "Bar Chart", "bar-widget"));
    self.toggleEditing = function () {
      self.isEditing(!self.isEditing());
    };
  }

  var Column = function (size, rows) {
    var self = this;
    self.size = ko.observable(size);
    self.rows = ko.observableArray(rows);
    self.klass = ko.computed(function () {
      return "card card-home card-column span" + self.size();
    });
    self.addEmptyRow = function () {
      self.addRow();
    };
    self.addRow = function (row) {
      if (typeof row == "undefined" || row == null) {
        row = new Row([]);
      }
      self.rows.push(row);
    };
  }

  var Row = function (widgets) {
    var self = this;
    self.widgets = ko.observableArray(widgets);

    self.addWidget = function (widget) {
      self.widgets.push(widget);
    };

    self.move = function (from, to) {
      try {
        viewModel.columns()[to].addRow(self);
        viewModel.columns()[from].rows.remove(self);
      }
      catch (exception) {
      }
    }

    self.moveDown = function () {

    }

    self.moveUp = function () {

    }

    self.remove = function (col, row) {
      col.rows.remove(row);
      console.log(row);
    }
  }

  var Widget = function (size, name, widgetType, properties, offset) {
    var self = this;
    self.size = ko.observable(size);
    self.name = ko.observable(name);
    self.widgetType = ko.observable(typeof widgetType != "undefined" && widgetType != null ? widgetType : "empty-widget");
    self.properties = ko.observable(typeof properties != "undefined" && properties != null ? properties : {});
    self.offset = ko.observable(typeof offset != "undefined" && offset != null ? offset : 0);

    self.klass = ko.computed(function () {
      return "card card-widget span" + self.size() + (self.offset() > 0 ? " offset" + self.offset() : "");
    });

    self.expand = function () {
      self.size(self.size() + 1);
    }
    self.compress = function () {
      self.size(self.size() - 1);
    }

    self.moveLeft = function () {
      self.offset(self.offset() - 1);
    }
    self.moveRight = function () {
      self.offset(self.offset() + 1);
    }
  }

  Widget.prototype.clone = function () {
    return new Widget(this.size(), this.name(), this.widgetType());
  };

  var viewModel = new DashBoardViewModel()
  ko.applyBindings(viewModel);


  function fullLayout() {
    setLayout([12]);
  }

  function halfLayout() {
    setLayout([6, 6]);
  }

  function oneThirdLeftLayout() {
    setLayout([3, 9]);
  }

  function oneThirdRightLayout() {
    setLayout([9, 3]);
  }

  function setLayout(colSizes) {
    // save previous widgets
    var _allRows = [];
    $(viewModel.columns()).each(function (cnt, col) {
      _allRows = _allRows.concat(col.rows());
    });

    var _cols = [];
    var _highestCol = {
      idx: -1,
      size: -1
    };
    $(colSizes).each(function (cnt, size) {
      _cols.push(new Column(size, []));
      if (size > _highestCol.size) {
        _highestCol.idx = cnt;
        _highestCol.size = size;
      }
    });
    if (_allRows.length > 0 && _highestCol.idx > -1) {
      _cols[_highestCol.idx].rows(_allRows);
    }
    viewModel.columns(_cols);
  }

  $(document).ready(function () {
    var _wid = [];
    _wid.push(new Widget(4, "Hello world", "timeline-widget"));
    _wid.push(new Widget(4, "Hello world 2 ", "resultset-widget"));

    ##    leftColumnLayout();
    ##    viewModel.columns()[0].addRow(new Row([new Widget(12, "moo")]));
    ##
    ##
    ##    viewModel.columns()[1].addRow();
    ##    viewModel.columns()[1].rows()[0].widgets(_wid);


  });
</script>

${ commonfooter(messages) | n,unicode }
