## -*- coding: utf-8 -*-
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


#
# Include this in order to use the functions:
# <%namespace name="dashboard" file="common_dashboard.mako" />
#

<%!
  from django.utils.translation import ugettext as _
%>

<%def name="import_layout()">
  <link rel="stylesheet" href="/static/css/common_dashboard.css">
  <script src="/static/js/ko.layout.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
</%def>

<%def name="layout_toolbar()">

<div class="card card-toolbar" data-bind="slideVisible: isEditing">
  <div style="float: left">
    <div class="toolbar-label">${_('LAYOUT')}</div>
    <a href="javascript: oneSixthLeftLayout(viewModel)" onmouseover="viewModel.previewColumns('oneSixthLeft')" onmouseout="viewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 24px"></div>
        <div class="layout-box" style="width: 72px; margin-left: 4px"></div>
      </div>
    </a>
    <a href="javascript: fullLayout(viewModel)" onmouseover="viewModel.previewColumns('full')" onmouseout="viewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 100px;"></div>
      </div>
    </a>
    <a data-bind="visible: columns().length == 0" href="javascript: magicLayout(viewModel)" onmouseover="viewModel.previewColumns('magic')" onmouseout="viewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 100px;"><i class="fa fa-magic"></i></div>
      </div>
    </a>
  </div>
  %if hasattr(caller, "widgets"):
  <div style="float: left; margin-left: 20px" data-bind="visible: columns().length > 0">
    <div class="toolbar-label">${_('WIDGETS')}</div>
    ${caller.widgets()}
  </div>
  %endif
  <div class="clearfix"></div>
</div>

</%def>

<%def name="layout_skeleton()">
  <div id="emptyDashboard" data-bind="fadeVisible: !isEditing() && columns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${ _('Click on the pencil to get started with your dashboard!') }</div>
    <img src="/static/art/hint_arrow.png" />
  </div>

  <div id="emptyDashboardEditing" data-bind="fadeVisible: isEditing() && columns().length == 0 && previewColumns() == ''">
    <div style="float:right; padding-top: 90px; margin-left: 20px; text-align: center; width: 260px">${ _('Pick an index and Click on a layout to start your dashboard!') }</div>
    <img src="/static/art/hint_arrow_horiz_flipped.png" />
  </div>


  <div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0, css:{'with-top-margin': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneSixthLeft'">
      <div class="span2 preview-row"></div>
      <div class="span10 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'full'">
      <div class="span12 preview-row">
      </div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'magic'">
      <div class="span12 preview-row">
        <div style="text-align: center; color:#EEE; font-size: 180px; margin-top: 80px">
          <i class="fa fa-magic"></i>
        </div>
      </div>
    </div>
  </div>
</div>

<div data-bind="css: {'dashboard': true, 'with-top-margin': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="template: { name: 'column-template', foreach: columns}">
    </div>
    <div class="clearfix"></div>
  </div>
</div>

<script type="text/html" id="column-template">
  <div data-bind="css: klass">
    <div class="container-fluid" data-bind="visible: $root.isEditing">
      <div data-bind="click: function(){$data.addEmptyRow(true)}, css: {'add-row': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(true); _r.addWidget(widget);$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)}); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'add-row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"></div>
    </div>
    <div data-bind="template: { name: 'row-template', foreach: rows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing && rows().length > 0">
      <div data-bind="click: function(){$data.addEmptyRow()}, css: {'add-row': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(); _r.addWidget(widget);$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)}); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'add-row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"></div>
    </div>
  </div>
</script>

<script type="text/html" id="row-template">
  <div class="emptyRow" data-bind="visible: widgets().length == 0 && $index() == 0 && $root.isEditing() && $parent.size() > 4 && $parent.rows().length == 1">
    <img src="/static/art/hint_arrow_flipped.png" style="float:left; margin-right: 10px"/>
    <div style="float:left; text-align: center; width: 260px">${_('Drag any of the widgets inside your empty row')}</div>
    <div class="clearfix"></div>
  </div>
  <div class="container-fluid">
    <div class="row-header" data-bind="visible: $root.isEditing">
      <span class="muted">${_('Row')}</span>
      <div style="display: inline; margin-left: 60px">
        <a href="javascript:void(0)" data-bind="visible: $index()<$parent.rows().length-1, click: function(){moveDown($parent, this)}"><i class="fa fa-chevron-down"></i></a>
        <a href="javascript:void(0)" data-bind="visible: $index()>0, click: function(){moveUp($parent, this)}"><i class="fa fa-chevron-up"></i></a>
        <a href="javascript:void(0)" data-bind="visible: $parent.rows().length > 1, click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </div>
    <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
        sortable: { template: 'widget-template', data: widgets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.card-body').slideUp('fast'); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
            dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});widgetDraggedAdditionalHandler(widget)}}">
    </div>
  </div>
</script>

<script type="text/html" id="widget-template">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass">
    <h2 class="card-heading simple">
      <span data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
        <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
        &nbsp;
      </span>
      <!-- ko if: $root.collection && $root.collection.getFacetById(id()) -->
      <span data-bind="with: $root.collection.getFacetById(id())">
        <span data-bind="editable: label, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
      </span>
      <!-- /ko -->
      <!-- ko if: typeof $root.collection == 'undefined' || $root.collection.getFacetById(id()) == null -->
        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
      <!-- /ko -->
      <div class="inline pull-right" data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" data-bind="click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </h2>
    <div class="card-body" style="padding: 5px;">
      <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>
    </div>
  </div>
</script>
</%def>


<%def name="import_bindings()">
  <link rel="stylesheet" href="/static/css/freshereditor.css">
  <link rel="stylesheet" href="/static/ext/css/codemirror.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css">
  <link rel="stylesheet" href="/static/ext/css/bootstrap-timepicker.min.css">
  <link rel="stylesheet" href="/static/css/bootstrap-spinedit.css">
  <link rel="stylesheet" href="/static/css/bootstrap-slider.css">

  <script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/bootstrap-timepicker.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/bootstrap-spinedit.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/bootstrap-slider.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/freshereditor.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/codemirror-3.11.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/codemirror-xml.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/less-1.7.0.min.js" type="text/javascript" charset="utf-8"></script>


  <script type="text/javascript">
    KO_DATERANGEPICKER_LABELS = {
      START: "${_('Start')}",
      END: "${_('End')}",
      INTERVAL: "${_('Interval')}",
      CUSTOM_FORMAT: "${_('Custom Format')}",
      DATE_PICKERS: "${_('Date Pickers')}"
    };
  </script>
  <script src="/static/js/ko.hue-bindings.js" type="text/javascript" charset="utf-8"></script>

</%def>


<%def name="import_charts()">
  <link rel="stylesheet" href="/static/ext/css/leaflet.css">
  <link rel="stylesheet" href="/static/ext/css/nv.d3.min.css">
  <link rel="stylesheet" href="/static/css/nv.d3.css">

  <script src="/static/js/hue.geo.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/hue.colors.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/ext/js/d3.v3.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/nv.d3.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topojson.v1.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topo/world.topo.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/topo/usa.topo.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/js/nv.d3.datamaps.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.legend.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.multiBarWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.lineWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingDiscreteBar.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingDiscreteBarChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingMultiBar.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingMultiBarChart.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingPie.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/js/nv.d3.growingPieChart.js" type="text/javascript" charset="utf-8"></script>

  <script src="/static/js/ko.charts.js" type="text/javascript" charset="utf-8"></script>

</%def>


