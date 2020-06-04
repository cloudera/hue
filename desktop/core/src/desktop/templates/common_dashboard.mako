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
  from desktop import conf
  from django.utils.translation import ugettext as _

  from dashboard.conf import HAS_REPORT_ENABLED, USE_GRIDSTER, USE_NEW_ADD_METHOD
  from desktop.views import _ko
%>

<%def name="import_layout(with_deferred=False)">
  <link rel="stylesheet" href="${ static('dashboard/css/common_dashboard.css') }">
  <script src="${ static('desktop/js/ko.common-dashboard.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/ko.droppable.fix.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/clipboard.min.js') }"></script>

  %if with_deferred:
  <script type="text/javascript">
    if (ko.options) {
      ko.options.deferUpdates = true;
    }
  </script>
  %endif
</%def>

<%def name="layout_toolbar()">

<div class="card card-toolbar">
  %if not hasattr(caller, "skipLayout"):
  <div style="float: left" data-bind="visible: columns().length == 0 && isEditing">
    <div class="toolbar-label">${_('LAYOUT')}</div>
    % if not USE_GRIDSTER.get():
    <a href="javascript: magicSearchLayout(searchViewModel)" title="${ _('Dynamic dashboard: multiple interconnected widgets') }" onmouseover="searchViewModel.previewColumns('magic')" onmouseout="searchViewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 24px"></div>
        <div class="layout-box" style="width: 72px; margin-left: 4px"><i class="fa fa-line-chart"></i></div>
      </div>
    </a>
    <a href="javascript: fullLayout(searchViewModel)" title="${ _('Empty dashboard that can be used as a starting point') }" onmouseover="searchViewModel.previewColumns('full')" onmouseout="searchViewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 100px;"></div>
      </div>
    </a>
    % else:
    <a href="javascript: queryBuilderSearchLayout(searchViewModel)" onmouseover="searchViewModel.previewColumns('dashboard')" onmouseout="searchViewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box layout-box-text">${ _("Analytics") }</div>
      </div>
    </a>
    <a href="javascript: textSearchLayout(searchViewModel, true)" onmouseover="searchViewModel.previewColumns('search')" onmouseout="searchViewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box layout-box-text">${ _("Search") }</div>
      </div>
    </a>
    % endif
  </div>
  %endif

  % if not USE_NEW_ADD_METHOD.get():
  <!-- ko if: columns().length > 0 && isToolbarVisible -->
  <div>
    %if hasattr(caller, "results"):
    <div style="float: left; margin-left: 20px">
      <div class="toolbar-label">${_('DISPLAY')}</div>
      ${caller.results()}
    </div>
    %endif

    %if hasattr(caller, "widgets"):
    <div class="card-toolbar-content" style="float: left; margin-left: 20px">
      %if hasattr(caller, "widgetSectionName"):
        <div class="toolbar-label">${caller.widgetSectionName()}</div>
      %else:
        <div class="toolbar-label margin-left-20">${_('ANALYTICS')}</div>
      %endif
      ${caller.widgets()}
    </div>
    %endif
  </div>
  <!-- /ko -->
  % endif
  <div class="clearfix"></div>
</div>

</%def>

<%def name="layout_skeleton(suffix='')">
  <!-- ko hueSpinner: { spin: isEditing() && columns().length == 0 && previewColumns() == '', center: true, size: 'xlarge' } --><!-- /ko -->

  % if USE_NEW_ADD_METHOD.get():
  <!-- ko if: $root.isGridster -->
  <div class="initial-hint empty-dashboard-plus" data-bind="fadeVisible: columns().length > 0 && showPlusButtonHint() && !showPlusButtonHintShownOnce(), click: function(){ showPlusButtonHint(false); }">

    <div class="initial-hint-text">${_('Drag the top plus button or any field from the right assistant into your dashboard')}</div>
    <img src="${ static('desktop/art/hint_arrow.svg') }" alt="${ _('Hint arrow') }" style="width: 90px" />
    <img src="${ static('desktop/art/hint_arrow.svg') }" alt="${ _('Hint arrow') }" style="width: 90px; margin-left: 80px; position: absolute; transform: rotate(33deg);" />
  </div>
  <!-- /ko -->
  % endif


  <div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0, css: {'with-top-margin': isEditing()}">
    <div class="container-fluid">

      <div class="row-fluid" data-bind="visible: previewColumns() == 'full'">
        <div class="span12 preview-row">
          <div style="font-size: 80px; padding-top: 120px">${ _('Blank') }</div>
        </div>
      </div>

      <div class="row-fluid" data-bind="visible: previewColumns() == 'magic'">
        <div class="span2 preview-row" style="font-size: 120px;">
          <i class="fa fa-pie-chart" style="padding-top: 10px"></i>
        </div>
        <div class="span10">
          <div class="preview-row" style="font-size: 120px; min-height: 50px !important;">
            <i class="fa fa-filter"></i>
          </div>
          <div class="preview-row" style="margin-top: 40px; padding-top: 40px; padding-bottom: 0; min-height: 200px !important;">
            <i class="fa fa-line-chart" style="font-size: 120px"></i><br/>
            <div style="font-size: 80px; padding-top: 20px">${ _('Dashboard') }</div>
          </div>
        </div>
      </div>

      <div class="row-fluid" data-bind="visible: previewColumns() == 'dashboard'">
        <div class="span12">
          <div class="preview-row" style="font-size: 120px; min-height: 50px !important;">
            <i class="fa fa-square"></i>
            <i class="fa fa-square" style="margin-left: 20px"></i>
            <i class="fa fa-superscript" style="margin-left: 20px"></i>
          </div>
          <div class="preview-row" style="margin-top: 40px; padding-top: 40px; padding-bottom: 0; min-height: 200px !important;">
            <i class="fa fa-table" style="font-size: 120px"></i><br/>
            <div style="font-size: 40px; padding-top: 20px; line-height: 48px">${ _('Compute and calculate metrics') }</div>
          </div>
        </div>
      </div>

      <div class="row-fluid" data-bind="visible: previewColumns() == 'search'">
        <div class="span12">
          <div class="preview-row" style="font-size: 80px; ">
            <i class="fa fa-search" style="font-size: 120px; padding-top: 100px"></i><br/>
            <div style="font-size: 40px; padding-top: 20px; line-height: 48px">${ _('Retrieve and display records of data') }</div>
          </div>
        </div>
      </div>

    </div>
  </div>

<div class="dashboard dashboard-flex" data-bind="css: {'with-top-margin': isEditing()}">
  <div class="container-fluid">
  <!-- ko if: $root.isGridster -->
    <div class="gridster" data-bind="click: function(){ showPlusButtonHint(false); }">
      <!-- ko if: typeof gridItems !== 'undefined' -->
      <ul class="unstyled" data-bind="css: { 'is-adding': $root.isToolbarVisible }, gridster: { items: gridItems, template: 'widget-template-gridster${ suffix }' }"></ul>
      <!-- /ko -->
    </div>
  <!-- /ko -->

  <!-- ko ifnot: $root.isGridster -->
    <!-- ko if: $root.selectedQDefinition() != null -->
    <div class="row-fluid">
      <div class="card card-additional card-home span12" style="background-color: #F5F5F5">
        <strong data-bind="editable: $root.selectedQDefinition().name, editableOptions: { enabled: true, placement: 'right' }"></strong>
        <!-- ko if: $root.selectedQDefinition().hasChanged() -->
        &nbsp;&nbsp;
        <a class="pointer" data-bind="click: $root.collection.reloadQDefinition" title="${ _('Reload this definition') }"><i class="fa fa-undo"></i></a> <a class="pointer" data-bind="click: $root.collection.updateQDefinition" title="${ _('Update the definition') }"><i class="fa fa-save"></i></a>
        <!-- /ko -->
        &nbsp;&nbsp;
        <a class="pointer" data-bind="click: $root.collection.unloadQDefinition" title="${ _('Close this definition') }"><i class="fa fa-times"></i></a>
      </div>
    </div>
    <!-- /ko -->
    <div class="row-fluid" data-bind="template: { name: 'column-template${ suffix }', foreach: columns}">
    </div>
    <div class="clearfix"></div>
  <!-- /ko -->
  </div>
</div>

<script id="widget-template-gridster${ suffix }" type="text/html">
  <li>
    <!-- ko ifnot: widget -->
    <div class="empty-gridster-widget card card-widget" data-bind="draggable: { data: $data, isEnabled: $root.isGridster(), options: getDraggableOptions({ data: $data, parent: $data }) }">
      <h2 class="card-heading simple" title="${ _('Drag to move') }">
        ${ _('Empty widget') }
        <div class="inline pull-right margin-right-10">
          <a href="javascript:void(0)" class="remove-widget" data-bind="publish: { 'gridster.remove': $data }"><i class="fa fa-times"></i></a>
        </div>
      </h2>
      <div class="empty-content" data-bind="droppable: { data: function(w) { huePubSub.publish('gridster.empty.drop', { widget: w, target: $data }); }, options: { disabled: $root.hasNewAdd(), greedy: true, hoverClass: 'droppable-hover', drop: function(){ huePubSub.publish('gridster.added.widget'); } }}, css: { 'query-builder': $root.isQueryBuilder }">
        % if USE_NEW_ADD_METHOD.get():
        <!-- ko with: emptyProperties -->
        <div class="edit-dimensions">
          <div class="badge dimensions-badge-container dimensions-badge-container-add is-adding">
            <div class="action-icon" data-bind="click: function(){ isAdding(true); }"><i class="fa fa-plus"></i> ${ _('Add') }</div>
            <div class="metric-form empty-widget-form" data-bind="visible: isAdding">
                <a href="javascript:void(0)" data-bind="toggle: isAdding" class="pull-right"><i class="fa fa-times inactive-action"></i></a>
                <select data-bind="selectize: fieldOperations, optionsText: 'label', optionsValue: 'value', value: fieldOperation" class="input-small"></select>
                <select data-bind="selectize: $root.collection.template.filteredModalFields().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), value: fieldName, optionsValue: 'name', optionsText: 'name', optionsCaption: '${ _ko('Field...') }'" class="hit-options input-small" style="margin-bottom: 0"></select>
                <!-- ko if: fieldName -->
                <a class="inactive-action context-popover-icon" href="javascript:void(0);" data-bind="sqlContextPopover: { sourceType: 'solr', namespace: $root.collection.activeNamespace(), compute: $root.collection.activeCompute(), path: 'default.' + $root.collection.name() + '.' + fieldName()  }">
                  <i class="fa fa-fw fa-info" title="${_('Show Details')}"/>
                </a>
                <!-- /ko -->
                <!-- ko ifnot: fieldName  -->
                  <i class="fa fa-fw"/>
                <!-- /ko -->


                <div class="clearfix"></div>
                <br>

                <div class="facet-field-cnt">
                  <span class="facet-field-label facet-field-label-fixed-width">${ _('Visualization') }</span>
                  <div class="dropdown inline-block">
                    <a class="dropdown-toggle" href="javascript: void(0)" data-toggle="dropdown" title="${ _('Change widget visualization') }">
                      <!-- ko switch: fieldViz -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.COUNTER --><i class="fa fa-superscript fa-fw"></i> ${_('Counter')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.TEXTSELECT --><i class="fa fa-sort-amount-asc fa-fw"></i> ${_('Text select')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.BARCHART --><i class="hcha hcha-bar-chart fa-fw"></i> ${_('Bars')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.PIECHART --><i class="hcha hcha-pie-chart fa-fw"></i> ${_('Pie')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.TIMELINECHART --><i class="fa fa-fw fa-line-chart"></i> ${_('Timeline')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.GRADIENTMAP --><i class="hcha fa-fw hcha-map-chart chart-icon"></i> ${_('Gradient Map')}<!-- /ko -->
                        <!-- ko case: window.HUE_CHARTS.TYPES.MAP --><i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}<!-- /ko -->
                      <!-- /ko -->
                    </a>
                    <ul class="dropdown-menu">
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.COUNTER); }">
                          <i class="fa fa-superscript fa-fw"></i> ${_('Counter')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.TEXTSELECT); }">
                          <i class="fa fa-sort-amount-asc fa-fw"></i> ${_('Text select')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.BARCHART); }">
                          <i class="hcha hcha-bar-chart fa-fw"></i> ${_('Bars')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.PIECHART); }">
                          <i class="hcha hcha-pie-chart fa-fw"></i> ${_('Pie')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.TIMELINECHART); }">
                          <i class="fa fa-fw fa-line-chart"></i> ${_('Timeline')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.GRADIENTMAP); }">
                          <i class="hcha fa-fw hcha-map-chart chart-icon"></i> ${_('Gradient Map')}
                        </a>
                      </li>
                      <li>
                        <a href="javascript:void(0)"
                           data-bind="click: function(){ fieldViz(window.HUE_CHARTS.TYPES.MAP); }">
                          <i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>

                <div class="facet-field-cnt">
                  <span class="facet-field-label facet-field-label-fixed-width">${ _('Sorting') }</span>
                  <a href="javascript: void(0)" title="${ _('Toggle sort order') }" data-bind="click: loopThroughSorts">
                    <i class="fa fa-fw" data-bind="css: { 'fa-caret-down': fieldSort() == 'desc', 'fa-caret-up': fieldSort() == 'asc', 'fa-sort': fieldSort() == 'default' }"></i>
                    <span data-bind="visible: fieldSort() == 'desc'">${_('descending')}</span>
                    <span data-bind="visible: fieldSort() == 'asc'">${_('ascending')}</span>
                    <span data-bind="visible: fieldSort() == 'default'">${_('default')}</span>
                  </a>
                </div>


                <a data-bind="visible: fieldName(), click: function() { huePubSub.publish('gridster.empty.add', { widget: $root.draggableBucket(), target: $parent }); }" class="pull-right margin-top-10" href="javascript:void(0)">
                  <i class="fa fa-plus"></i> ${ _('Add') }
                </a>
                <div class="pull-right margin-top-10 muted" data-bind="visible: !fieldName()">
                  <i class="fa fa-plus"></i> ${ _('Add') }
                </div>
            </div>
          </div>
        </div>
        <!-- /ko -->
        % endif
      </div>
      <div class="clearfix"></div>
    </div>
  <!-- /ko -->
  <!-- ko with: widget -->
    <div data-bind="template: 'widget-template${ suffix }', css: { 'query-builder': $root.isQueryBuilder }"></div>
    <div class="clearfix"></div>
  <!-- /ko -->
  </li>
</script>


<script type="text/html" id="column-template${ suffix }">
  <div data-bind="css: klass">
    <div class="pull-right margin-right-10" data-bind="visible: $root.isEditing()">
      <a href="javascript:void(0)" data-bind="visible: size() > 2, click: shrinkColumn" title="${ _('Make column smaller') }"><i class="fa fa-step-backward"></i></a>
      <a href="javascript:void(0)" data-bind="visible: size() < 12, click: expandColumn" title="${ _('Make column larger') }"><i class="fa fa-step-forward"></i></a>
      <a href="javascript:void(0)" data-bind="visible: $parent.columns().length < 2, click: addColumnRight" title="${ _('Add a column to the right') }"><i class="fa fa-plus"></i></a>
      <a href="javascript:void(0)" data-bind="visible: true, click: removeColumn" title="${ _('Remove this column') }"><i class="fa fa-times"></i></a>
    </div>
    <div class="pull-left margin-left-10" data-bind="visible: $root.isEditing()">
      <a href="javascript:void(0)" data-bind="visible: $index() == 0 && $parent.columns().length > 1, click: function() { moveRight($index()) }" title="${ _('Move column to the right') }"><i class="fa fa-arrow-right"></i></a>
      <a href="javascript:void(0)" data-bind="visible: $parent.columns().length < 2, click: addColumnLeft" title="${ _('Add a column to the left') }"><i class="fa fa-plus"></i></a>
      <a href="javascript:void(0)" data-bind="visible: $index() > 0, click: function() { moveLeft($index()) }" title="${ _('Move column to the left') }"><i class="fa fa-arrow-left"></i></a>
    </div>
    <div class="clearfix"></div>
    <div class="container-fluid" data-bind="visible: $root.isEditing()">
      <div data-bind="click: function(){$data.addEmptyRow(true)}, css: {'add-row': true, 'is-editing': $root.isEditing}, droppable: { data: function() { $root.collection.dropOnEmpty($data, true) }, options:{ greedy:true }}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(true); _r.addWidget(widget);$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)}); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'add-row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"></div>
    </div>
    <div data-bind="template: { name: 'row-template${ suffix }', foreach: rows}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isEditing() && rows().length > 0">
      <div data-bind="click: function(){$data.addEmptyRow()}, css: {'add-row': true, 'is-editing': $root.isEditing}, droppable: { data: function() { $root.collection.dropOnEmpty($data, false) }, options:{ greedy:true }}, sortable: { data: drops, isEnabled: $root.isEditing, 'afterMove': function(event){var widget=event.item; var _r = $data.addEmptyRow(); _r.addWidget(widget);$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)}); columnDropAdditionalHandler(widget)}, options: {'placeholder': 'add-row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"></div>
    </div>
  </div>
</script>

<script type="text/html" id="row-template${ suffix }">
  <div class="emptyRow" data-bind="visible: widgets().length == 0 && $index() == 0 && $root.isEditing() && $parent.size() > 4 && $parent.rows().length == 1">
    <img src="${ static('desktop/art/hint_arrow.svg') }" style="float:left; margin-right: 10px" alt="${ _('Hint arrow') }" class="flip-both"/>
    <div style="float: left; text-align: center; width: 260px">${_('Drag any of the widgets inside your empty row')}</div>
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
        sortable: { template: 'widget-template${ suffix }', data: widgets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.card-body').slideUp('fast'); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
            dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});widgetDraggedAdditionalHandler(widget, $data)}}">
    </div>
    <div class="container-fluid" data-bind="visible: $root.isNested() && columns().length > 0" style="border: 1px solid #e5e5e5; border-top: none; background-color: #F3F3F3;">
      <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing}">
        <div data-bind="template: { name: 'column-template${ suffix }', foreach: columns}">
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="widget-template${ suffix }">
  <div data-bind="attr: { 'id': 'wdg_'+ id() }, css: klass,
      draggable: {
         data: $data,
         isEnabled: $root.isGridster(),
         options: getDraggableOptions({ data: $data, parent: $parent })
      },
      droppable: {
        data: function() {
          $root.collection.dropOnWidget(id())
        },
        options: {
          greedy:true,
          drop: function(event, ui) {
            huePubSub.publish('dashboard.drop.on.page', { event: event, ui: ui })
          }
        }
      }">
    <h2 class="card-heading simple" data-bind="attr: { title: $root.isGridster() ? '${ _ko('Drag to move') }' : '' }">
      <!-- ko ifnot: $root.isGridster -->
      <span data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
        <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
        &nbsp;
      </span>
      <!-- /ko -->
      <!-- ko if: $root.collection && $root.collection.getFacetById(id()) -->
      <span data-bind="with: $root.collection.getFacetById(id())">
        <span data-bind="editable: label, editableOptions: { enabled: true, placement: 'right' }" title="${ _('Click to change the widget title') }"></span>
      </span>
      <!-- /ko -->
      <!-- ko if: typeof $root.collection == 'undefined' || $root.collection.getFacetById(id()) == null -->
        <span data-bind="editable: name, editableOptions: { enabled: true, placement: 'right' }" title="${ _('Click to change the widget title') }"></span>
      <!-- /ko -->
      <div class="inline pull-right margin-right-10" data-bind="visible: !$root.hasNewAdd() || ($root.hasNewAdd() && widgetType() !== 'resultset-widget' && widgetType() !== 'filter-widget')">
        <a href="javascript:void(0)" class="remove-widget" data-bind="click: $root.removeWidget"><i class="fa fa-times"></i></a>
      </div>
    </h2>
    <div class="card-body" style="padding: 5px;">
      <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>
      <div class="clearfix"></div>
    </div>
  </div>
</script>
</%def>


<%def name="import_bindings()">
  <link rel="stylesheet" href="${ static('desktop/css/freshereditor.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/codemirror.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-timepicker.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-spinedit.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/bootstrap-slider.css') }">

  <script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/bootstrap-timepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-spinedit.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/bootstrap-slider.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/freshereditor.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/codemirror-3.11.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/codemirror-xml.js') }" type="text/javascript" charset="utf-8"></script>

  <script src="${ static('desktop/ext/js/less-1.7.0.min.js') }" type="text/javascript" charset="utf-8"></script>


  <script type="text/javascript">
    KO_DATERANGEPICKER_LABELS = {
      START: "${_('Start')}",
      END: "${_('End')}",
      INTERVAL: "${_('Interval')}",
      CUSTOM_FORMAT: "${_('Switch to custom format')}",
      DATE_PICKERS: "${_('Switch to date pickers')}",
      CUSTOM_POPOVER_TITLE: "${_('e.g.')}",
      CUSTOM_POPOVER_CONTENT: "${_('Start')}: NOW-5DAYS<br/>${_('End')}: NOW<br/>${_('Interval')}: +1HOURS<br/><a href='http://lucene.apache.org/solr/4_10_2/solr-core/org/apache/solr/util/DateMathParser.html' target='_blank'>${_('Read more...')}</a>"
    };
  </script>
</%def>
