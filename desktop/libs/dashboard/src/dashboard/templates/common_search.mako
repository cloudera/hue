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

from desktop import conf
from desktop.views import commonheader, commonfooter, _ko, commonshare

from dashboard.conf import USE_GRIDSTER, USE_NEW_ADD_METHOD, HAS_REPORT_ENABLED, HAS_WIDGET_FILTER, HAS_TREE_WIDGET
%>

<%namespace name="dashboard" file="common_dashboard.mako" />

<%def name="page_structure(is_mobile=False, is_embeddable=False, is_report=False)">

<script type="text/javascript">
  SLIDER_LABELS = {
    STEP: "${_('Increment')}"
  }
</script>

%if is_mobile:
  <h3 data-bind="text: collection.label" style="text-align: center"></h3>
  <form class="form-search" style="margin: 0; text-align: center" data-bind="submit: searchBtn, visible: columns().length != 0">
    <div class="input-append">
      <!-- ko if: query.qs().length > 0 -->
        <!-- ko with: query.qs()[0] -->
        <input data-bind="clearable: q, valueUpdate:'afterkeydown', typeahead: { target: q, nonBindableSource: queryTypeahead, multipleValues: true, multipleValuesSeparator: ':', extraKeywords: 'AND OR TO', completeSolrRanges: true }" maxlength="4096" type="text">
        <!-- /ko -->
      <!-- /ko -->

      <button type="submit" id="search-btn" class="btn btn-inverse add-on">
        <i class="fa fa-search" data-bind="visible: ! isRetrievingResults()"></i>
        <i class="fa fa-spinner fa-spin" data-bind="visible: isRetrievingResults()"></i>
      </button>

    </div>
  </form>
%else:
<div class="search-bar" data-bind="visible: !$root.isPlayerMode(), event: { mouseover: function(){ if (columns().length && isGridster()) { showPlusButtonHint(true); } } }">
  <div class="search-bar-header">
    <div class="search-bar-logo">
      <div class="app-header">
        <a href="javascript: void(0)" data-bind="hueLink: '${ url('dashboard:new_search') }'">
          <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Dashboard') }
          <!-- ko component: { name: 'hue-favorite-app', params: { app: 'dashboard' }} --><!-- /ko -->
        </a>
      </div>
    </div>
    <div class="search-bar-middle">
      <form class="form-search" data-bind="visible: $root.isEditing() && columns().length === 0, submit: function() { return false }">
        <!-- ko if: $root.collection.engine() == 'solr' -->
        <!-- ko if: columns().length == 0 -->
        <select data-bind="selectize: $root.initial.collections.sort(), value: $root.collection.name, disable: isSyncingCollections, selectizeOptions: { clearable: true }"></select>

        <label class="checkbox" style="display:inline-block; margin-left: 10px">
          <i class="fa fa-spinner fa-spin" data-bind="visible: isSyncingCollections"></i>
        </label>
        <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: $root.collection.engine() != 'solr' -->
        <!-- ko if: columns().length == 0 -->
        <input type="text" class="no-margin" data-bind="hiveChooser: $root.collection.name, skipColumns: true, apiHelperUser: '${ user }', apiHelperType: $root.collection.engine()" placeholder="${ _('Table name or <database>.<table>') }" style="margin-top: 1px">
        <!-- /ko -->
        <!-- /ko -->

        <select data-bind="options: $root.availableDateFields, value: collection.timeFilter.field, optionsValue: 'name', visible: $root.isEditing() && $root.availableDateFields().length > 0" class="input-medium" style="margin-left: 4px"></select>
        <span class="time-filter" data-bind="template: {name: 'time-filter'}, visible: collection.timeFilter.type() == 'rolling'"></span>
        <span class="time-fixed-filter" data-bind="template: {name: 'time-fixed-filter'}, visible: collection.timeFilter.type() == 'fixed'"></span>

        <!-- ko if: $root.collection.engine() == 'solr' -->
        <span data-bind="template: {name: 'nested-document-filter'}"></span>
        <!-- /ko -->
      </form>

      <form class="form-search" style="margin: 0" data-bind="submit: searchBtn, visible: columns().length != 0">
        <div class="search-bar-query-container">
          <div class="search-bar-collection" data-bind="visible: $root.collection.engine() != 'report'">
##             <div class="selectMask">
##               <span data-bind="editable: collection.label, editableOptions: { enabled: true, placement: 'right' }"></span>
##             </div>
            <select data-bind="selectize: $root.initial.collections.sort(), value: $root.collection.name, disable: isSyncingCollections, selectizeOptions: { clearable: true }"></select>
          </div>
          <!-- ko if: $root.collection.engine() !== 'report' -->
          <div class="search-bar-query" data-bind="foreach: query.qs">

            <div data-bind="component: { name: 'hue-simple-ace-editor', params: {
              value: q,
              onExec: $parent.searchBtn,
              placeHolder: $root.collection.engine() === 'solr' ? '${ _ko('Example: field:value, or press CTRL + space') }' : '${ _ko('Example: col = value, or press CTRL + space') }',
              autocomplete: { type: $root.collection.engine() + 'Query', support: { collection: $root.collection } },
              mode: $root.collection.engine(),
              fixedPrefix: $root.collection.engine() !== 'solr' ? function() { return 'SELECT * FROM ' +  $root.collection.name() + ' WHERE '; } : undefined,
              fixedPostfix: $root.collection.engine() !== 'solr' ? function() { return ' GROUP BY 1;' } : undefined,
              namespace: $root.collection.activeNamespace,
              compute: $root.collection.activeCompute,
              database: function () { return $root.collection.name().split('.')[0] },
              singleLine: true }
            }"></div>
##             <input data-bind="clearable: q, valueUpdate:'afterkeydown', typeahead: { target: q, nonBindableSource: queryTypeahead, multipleValues: true, multipleValuesSeparator: ':', extraKeywords: 'AND OR TO', completeSolrRanges: true }, css: {'input-small': $root.query.qs().length > 1, 'flat-left': $index() === 0, 'input-xlarge': $root.collection.supportAnalytics()}" maxlength="4096" type="text" class="search-query">
            <!-- ko if: $index() >= 1 -->
              <a class="btn flat-left" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
            <!-- /ko -->
          </div>
          <!-- /ko -->
          <div class="search-bar-query-operations">
            <!-- ko if: $root.collection.engine() !== 'report' -->
            <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ, css: { 'flat-left': $root.query.qs().length === 1}, style: { 'margin-left': $root.query.qs().length > 1 ? '10px' : '0' }, visible: ! collection.supportAnalytics()">
              <i class="fa fa-plus"></i>
            </a>
            <!-- /ko -->

            <button type="submit" id="search-btn" class="btn btn-primary disable-feedback" style="margin-left:10px; margin-right:10px">
              <i class="fa fa-search" data-bind="visible: ! isRetrievingResults()"></i>
              <i class="fa fa-spinner fa-spin" data-bind="visible: isRetrievingResults()"></i>
              <!-- ko if: $root.collection.async() -->
              <i class="fa fa-stop" clas="red" data-bind="click: cancelAsync, visible: isRetrievingResults()"></i>
              <!-- /ko -->
            </button>
            <span class="time-filter" data-bind="template: {name: 'time-filter'}, visible: collection.timeFilter.type() == 'rolling'"></span>
            <span class="time-fixed-filter" data-bind="template: {name: 'time-fixed-filter'}, visible: collection.timeFilter.type() == 'fixed'"></span>

            <span data-bind="template: {name: 'nested-document-filter'}"></span>
          </div>
        </div>
      </form>
    </div>

    <div class="search-bar-operations">
      <!-- ko if: $root.isGridster() -->
      <div class="btn-group">
        % if USE_NEW_ADD_METHOD.get():
        <a class="btn draggable-plus-button move-cursor" title="${ _('Drag to add a widget') }" data-bind="draggable: {data: $root.collection.supportAnalytics() ? draggableBucket() : draggableBar(), options: getDraggableOptions({ data: $root.collection.supportAnalytics() ? draggableBucket() : draggableBar(), plusButton: true })}, visible: columns().length">
          <i class="fa fa-plus"></i>
        </a>
        % else:
          %if is_report:
            <a class="btn draggable-plus-button move-cursor" title="${ _('Drag to add a widget') }" data-bind="draggable: {data: draggableDocument(), options: getDraggableOptions({ data: draggableDocument(), plusButton: true })}, visible: columns().length">
              <i class="fa fa-fw fa-plus"></i>
            </a>
          % else:
            <a class="btn" title="${ _('Toggle the widget toolbar') }" rel="tooltip" data-placement="bottom" data-bind="visible: columns().length, click: function() { isToolbarVisible(!isToolbarVisible()) }, css: {'btn': true, 'btn-inverse': isToolbarVisible }">
              <i class="fa fa-plus"></i>
            </a>
          %endif
        % endif:
      </div>
      <!-- /ko -->
      <!-- ko ifnot: $root.isGridster -->
      <div class="btn-group">
        <a class="btn pointer" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
          <i class="fa fa-pencil"></i>
        </a>
      </div>
      <!-- /ko -->

      % if is_owner:
        <div class="btn-group" data-bind="visible: columns().length">
          <a class="btn" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: function() { if (canSave()) { save() } else { $('#saveAsModalDashboard').modal('show'); } }, attr: { title: canSave() ? '${ _ko('Save') }' : '${ _ko('Save As') }' }"><i class="fa fa-save"></i></a>
          <!-- ko if: canSave() -->
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
          <ul class="dropdown-menu pull-right">
            <li>
              <a class="pointer" data-bind="click: function() { $('#saveAsModalDashboard').modal('show'); }">
                <i class="fa fa-fw fa-save"></i> ${ _('Save as...') }
              </a>
            </li>
          </ul>
          <!-- /ko -->
        </div>
      % endif

      <div class="dropdown pull-right margin-left-10">
        <a class="btn" data-toggle="dropdown" href="javascript: void(0)" data-bind="click: function() { showPlusButtonHint(false); }">
          <i class="fa fa-fw fa-ellipsis-v"></i>
        </a>
        <ul class="dropdown-menu">
          <li>
            <a href="javascript:void(0)" data-bind="click: newSearch">
              <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0);" data-bind="publish: { 'assist.show.documents': 'search-dashboard' }">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> ${ _('Dashboards') }
            </a>
          </li>
          <li data-bind="visible: columns().length != 0" class="divider"></li>
          <li data-bind="visible: isSaved()">
            <a class="share-link" data-bind="click: prepareShareModal, css: {'isShared': isShared()}">
              <i class="fa fa-fw fa-users"></i> ${ _('Share') }
            </a>
          </li>
          %if not is_embeddable:
            <li>
              <a class="pointer" data-bind="click: function(){ hueUtils.goFullScreen(); $root.isEditing(false); $root.isPlayerMode(true); }">
                <i class="fa fa-fw fa-expand"></i> ${ _('Player mode') }
              </a>
            </li>
          %endif

          <li data-bind="visible: columns().length != 0">
            <a class="pointer" data-toggle="modal" data-target="#settingsDemiModal">
              <i class="fa fa-fw fa-cog"></i> ${ _('Settings') }
            </a>
          </li>
          <li data-bind="visible: columns().length != 0">
            <a class="pointer" data-toggle="modal" data-target="#qdefinitionsDemiModal">
              <i class="fa fa-fw fa-bookmark-o"></i> ${ _('Saved Queries') }
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>


</div>
%endif

% if not is_report:
<%dashboard:layout_toolbar>
  <%def name="skipLayout()"></%def>
  <%def name="results()">
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableResultset(), isEnabled: availableDraggableResultset, options: getDraggableOptions({ data: draggableResultset(), stop: function() { $root.collection.template.isGridLayout(true); checkResultHighlightingAvailability(); } }) }"
         title="${_('Grid')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-table"></i>
         </a>
    </div>

    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableHtmlResultset(),
                    isEnabled: availableDraggableResultset,
                    options: getDraggableOptions({ data: draggableHtmlResultset(), stop: function(){ $root.collection.template.isGridLayout(false); checkResultHighlightingAvailability(); } }) }"
         title="${_('HTML')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-code"></i>
         </a>
    </div>

    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableFilter() },
                    draggable: {data: draggableFilter(), isEnabled: availableDraggableFilter,
                    options: getDraggableOptions({ data: draggableFilter() }) }"
         title="${_('Filter Bar')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableFilter() ? 'move' : 'default' }">
                       <i class="fa fa-filter"></i>
         </a>
    </div>

    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableLeaflet()},
                    draggable: {data: draggableLeafletMap(), isEnabled: availableDraggableLeaflet,
                    options: getDraggableOptions({ data: draggableLeafletMap() }) }"
         title="${_('Marker Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: 'move' }">
             <i class="fa fa-map-marker"></i>
         </a>
    </div>
      </%def>

      <%def name="widgets()">
    <div data-bind="visible: $root.collection.supportAnalytics,
                    css: { 'draggable-widget': true, 'disabled': !hasAvailableFields() },
                    draggable: {data: draggableCounter(), isEnabled: hasAvailableFields,
                    options: getDraggableOptions({ data: draggableCounter()}) }"
         title="${_('Counter')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.hasAvailableFields() ? 'move' : 'default' }">
                       <i class="fa fa-superscript" style="font-size: 110%"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableFacet(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggableFacet() }) }"
         title="${_('Text Facet')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sort-amount-asc"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableTextFacet(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggableTextFacet() }) }"
         title="${_('Value List')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sort-amount-asc"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggablePie(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggablePie() }) }"
         title="${_('Pie Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-pie-chart"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggablePie2(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggablePie2() }) }"
         title="${_('Pie Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-pie-chart"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableBar(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggableBar() }) }"
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': ! availableDraggableChart() },
                    draggable: {data: draggableBucket(), isEnabled: availableDraggableChart,
                    options: getDraggableOptions({ data: draggableBucket() }) }"
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-bar-chart"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableTree(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableTree() }) }"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
    </div>
    % if HAS_TREE_WIDGET.get():
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableTree2(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableTree2() }) }"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
    </div>
    % endif
    <div data-bind="visible: !$root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableHeatmap(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableHeatmap() }) }"
         title="${_('Heatmap')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-th"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram,
                    options: getDraggableOptions({ data: draggableHistogram() }) }"
         title="${_('Timeline')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableHistogram() ? 'move' : 'default' }">
                       <i class="hcha hcha-timeline-chart"></i>
         </a>
    </div>
    <div data-bind="visible: !$root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableDraggableMap() },
                    draggable: {data: draggableMap(), isEnabled: availableDraggableMap,
                    options: getDraggableOptions({ data: draggableMap() }) }"
         title="${_('Gradient Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableMap() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableTimeline() },
                    draggable: {data: draggableTimeline(), isEnabled: availableTimeline,
                    options: getDraggableOptions({ data: draggableTimeline() }) }"
         title="${_('Timeline')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableTimeline() ? 'move' : 'default' }">
                       <i class="fa fa-line-chart"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableDraggableMap() },
                    draggable: {data: draggableGradienMap(), isEnabled: availableDraggableMap,
                    options: getDraggableOptions({ data: draggableGradienMap() }) }"
         title="${_('Gradient Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableMap() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
         </a>
    </div>

      </%def>
</%dashboard:layout_toolbar>
% endif

<div class="player-toolbar" data-bind="visible: $root.isPlayerMode">
  <div class="pull-right pointer" data-bind="visible: $root.isPlayerMode, click: function(){ hueUtils.exitFullScreen(); $root.isPlayerMode(false); }"><i class="fa fa-times"></i></div>
  <img src="${ static('desktop/art/icon_hue_48.png') }" alt="${ _('Hue logo') }" />
  <h4 data-bind="text: collection.label"></h4>
  <form class="form-search" data-bind="submit: searchBtn">
  <span data-bind="foreach: query.qs">
    <input data-bind="clearable: q, valueUpdate:'afterkeydown', typeahead: { target: q, source: $root.collection.template.fieldsNames, multipleValues: true, multipleValuesSeparator: ':', extraKeywords: 'AND OR TO', completeSolrRanges: true }, css:{'input-xlarge': $root.query.qs().length == 1, 'input-medium': $root.query.qs().length < 4, 'input-small': $root.query.qs().length >= 4}" maxlength="4096" type="text" class="search-query">
    <!-- ko if: $parent.query.qs().length > 1 -->
    <div class="pointer muted link" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></div>
    <!-- /ko -->
  </span>
  <div class="pointer muted link" data-bind="click: $root.query.addQ"><i class="fa fa-plus"></i></div>
  <div class="pointer muted link" data-bind="click: $root.searchBtn"><i class="fa fa-search" data-bind="visible: ! isRetrievingResults()"></i></div>
  <i class="fa fa-spinner fa-spin muted" data-bind="visible: isRetrievingResults()"></i>
  </form>
</div>


${ dashboard.layout_skeleton(suffix='search') }

<script type="text/html" id="empty-widget">
  ${ _('This is an empty widget.')}
</script>


<script type="text/html" id="facet-toggle">
  <div class="facet-field-tile">
    <div class="facet-field-cnt">
      <span class="facet-field-label facet-field-label-fixed-width facet-field-label-fixed-width-double facet-field-label-title">${ _('Settings') }</span>
      <i class="fa fa-spinner fa-spin" data-bind="visible: $root.isRetrievingResults()"></i>
    </div>

    <div class="facet-field-cnt" data-bind="visible: properties.canRange">
      <span class="facet-field-label facet-field-label-fixed-width">${ _('Type') }</span>
      <a href="javascript: void(0)" title="${ _('Toggle how to group the values') }" data-bind="click: $root.collection.toggleRangeFacet">
        <i class="fa" data-bind="css: { 'fa-arrows-h': type() == 'range', 'fa-circle': type() == 'field', 'fa-level-up': type() == 'range-up' }, attr: { title: type() == 'field' ? 'Range' : type() == 'range-up' ? 'Range and up' : 'Term' }"></i>
        <span data-bind="visible: type() == 'range'">${_('range')}</span>
        <span data-bind="visible: type() == 'range-up'">${_('range & up')}</span>
        <span data-bind="visible: type() == 'field'">${_('field')}</span>
      </a>
    </div>

    <div class="facet-field-cnt">
      <span class="facet-field-label facet-field-label-fixed-width">${ _('Sorting') }</span>
      <a href="javascript: void(0)" title="${ _('Toggle sort order') }" data-bind="click: $root.collection.toggleSortFacet">
        <i class="fa" data-bind="css: { 'fa-caret-down': properties.sort() == 'desc', 'fa-caret-up': properties.sort() == 'asc' }"></i>
        <span data-bind="visible: properties.sort() == 'desc'">${_('descending')}</span>
        <span data-bind="visible: properties.sort() == 'asc'">${_('ascending')}</span>
      </a>
    </div>

    <!-- ko if: type() == 'pivot' -->
      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">
            ${ _('Limit') }
          </span>
          <input type="text" class="input-medium" data-bind="spinedit: properties.limit"/>
        </span>
      </div>

      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">
            ${ _('Min Count') }
          </span>
          <input type="text" class="input-medium" data-bind="spinedit: properties.mincount"/>
        </span>
      </div>
    <!-- /ko -->

    <!-- ko if: type() == 'range' || type() == 'range-up' || (type() == 'nested' && typeof properties.min != "undefined") -->
      <!-- ko ifnot: properties.isDate() -->
        <div class="slider-cnt" data-bind="slider: {start: properties.min, end: properties.max, gap: properties.initial_gap, min: properties.initial_start, max: properties.initial_end, properties: properties, labels: SLIDER_LABELS}"></div>
      <!-- /ko -->
      <!-- ko if: properties.isDate() && $root.collection.timeFilter && $root.collection.timeFilter.field && $root.collection.timeFilter.field() != field() -->
        <div data-bind="dateRangePicker: {start: properties.start, end: properties.end, gap: properties.initial_gap, relatedgap: properties.gap, min: properties.min, max: properties.max}"></div>
      <!-- /ko -->
    <!-- /ko -->

    <!-- ko if: type() == 'field' -->
      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">
            ${ _('Limit') }
          </span>
          <input type="text" class="input-medium" data-bind="spinedit: properties.limit"/>
        </span>
      </div>
    <!-- /ko -->

    <!-- ko if: widgetType() == 'map-widget' -->
      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">
            ${ _('Scope') }
          </span>
          <select data-bind="selectedOptions: properties.scope" class="input-small">
            <option value="world">${ _("World") }</option>
            <option value="europe">${ _("Europe") }</option>
            <option value="aus">${ _("Australia") }</option>
            <option value="bra">${ _("Brazil") }</option>
            <option value="can">${ _("Canada") }</option>
            <option value="chn">${ _("China") }</option>
            <option value="fra">${ _("France") }</option>
            <option value="deu">${ _("Germany") }</option>
            <option value="ita">${ _("Italy") }</option>
            <option value="jpn">${ _("Japan") }</option>
            <option value="gbr">${ _("UK") }</option>
            <option value="usa">${ _("USA") }</option>
          </select>
        </span>
      </div>
    <!-- /ko -->
    </div>

    <!-- ko if: type() == 'pivot' || type() == 'nested' -->
      <div class="facet-field-tile" data-bind="visible: properties.scope() == 'tree' || (type() == 'pivot' && properties.facets().length == 0) || (type() == 'nested' && properties.facets().length < 3)">
        <div class="facet-field-cnt">
          <span class="facet-field-label facet-field-label-fixed-width facet-field-label-fixed-width-double facet-field-label-title">
            ${ _('Add a dimension') }
          </span>
        </div>

        <div class="facet-field-cnt">
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Field') }
            </span>
            <select data-bind="options: $root.collection.template.fieldsNames, value: properties.facets_form.field, optionsCaption: '${ _ko('Choose...') }', selectize: $root.collection.template.fieldsNames"></select>
          </span>
        </div>

        <!-- ko if: type() == 'nested' -->
        <div class="facet-field-cnt">
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Metric') }
            </span>
            <select data-bind="options: HIT_OPTIONS, optionsText: 'label', optionsValue: 'value', value: properties.facets_form.aggregate"></select>
          </span>
        </div>
        <!-- /ko -->

        <div class="facet-field-cnt">
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Limit') }
            </span>
            <input type="text" class="input-medium" data-bind="spinedit: properties.facets_form.limit"/>
          </span>
        </div>

        <div class="facet-field-cnt">
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Min Count') }
            </span>
            <input type="text" class="input-medium" data-bind="spinedit: properties.facets_form.mincount"/>
            <a class="pull-right" href="javascript: void(0)" data-bind="visible: ko.toJSON(properties.facets_form.field), click: $root.collection.addPivotFacetValue">
              <i class="fa fa-plus"></i>
            </a>
          </span>
        </div>
      </div>
    <!-- /ko -->
    <div class="clearfix"></div>
</script>


<script type="text/html" id="facet-toggle2">
  <div class="pull-left margin-right-20">

    <!-- ko if: $root.isEditing -->
    <div class="facet-field-cnt" data-bind="visible: $root.collection.nested.enabled">
      <span class="spinedit-cnt">
        <span class="facet-field-label">
          ${ _('Domain') }
        </span>
        ${ _('Parent') }
        <select data-bind="selectedOptions: properties.domain.blockParent, options: $root.collection.nestedNames" size="5" multiple="true"></select>
        ${ _('Children') }
        <select data-bind="selectedOptions: properties.domain.blockChildren, options: $root.collection.nestedNames" size="5" multiple="true"></select>

        <input type="text" class="input-medium" data-bind="spinedit: properties.mincount"/>
      </span>
    </div>
    <!-- /ko -->

    <!-- ko if: !$parents[1].isLoading() || widgetType() == 'hit-widget' -->
    <div class="edit-dimensions" data-bind="css: { 'is-editing': isEditing }">
      <div data-bind="sortable: { data: properties.facets, allowDrop: false, options: { axis: 'x', handle: '.move-dimension', tolerance: 'pointer'}}" class="inline-block">
        <div class="badge dimensions-badge-container" data-bind="css: { 'is-editing': isEditing }, click: function(){ $parent.isEditing(true); $parent.isAdding(false); $parent.properties.facets().forEach(function(f){ f.isEditing(false); }); isEditing(true); }" title="${ _('Edit') }">
          <span data-bind="text: getPrettyMetric($data)"></span>
          <span class="badge badge-info dimensions-badge" data-bind="text: field, attr: { 'title': field }"></span>
          <!-- ko if: aggregate.function() != 'field' && aggregate.metrics && $parent.widgetType() != 'hit-widget' -->
            <i class="fa" data-bind="css: { 'fa-long-arrow-down': sort() == 'desc', 'fa-long-arrow-up': sort() == 'asc' }"></i>
          <!-- /ko -->
          <div class="action-icon margin-left-5 move-dimension" data-bind="visible: $parent.properties.facets().length > 1" title="${ _('Move') }">
            <i class="fa fa-bars"></i>
          </div>
          <!-- ko if: isEditing -->
          <div class="metric-form" data-bind="template: { name: 'metric-form' }"></div>
          <!-- /ko -->
        </div>
      </div>
      <div class="badge dimensions-badge-container dimensions-badge-container-add" data-bind="css: { 'is-adding': isAdding }, visible: properties.facets().length < 15 && widgetType() != 'hit-widget'">
        <div class="action-icon" data-bind="click: function(){ isEditing(true); isAdding(true); properties.facets().forEach(function(f){ f.isEditing(false); });  }"><i class="fa fa-plus"></i> ${ _('Add') }</div>
        <!-- ko if: isAdding -->
          <div class="metric-form" data-bind="template: { name: 'metric-form', data: properties.facets_form }"></div>
        <!-- /ko -->
      </div>
      <div class="clearfix"></div>
    </div>
    <!-- /ko -->
  </div>

  <div class="clearfix"></div>
</script>


<script type="text/html" id="facet-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }"></span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'field' -->
        <div data-bind="foreach: $parent.counts">
          <div class="trigger-exclude">
              <!-- ko if: $index() < $parent.properties.limit() -->
                <!-- ko if: !$data.selected -->
                  <a class="exclude pointer" data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id(), 'exclude': true}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                  <div class="hellip">
                    <a class="pointer" dir="ltr" data-bind="html: prettifyDate($data.value), click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }, attr: {'title': $data.value + ' (' + $data.count + ')'}"></a>
                    <span class="pointer counter" dir="rtl" data-bind="text: ' (' + $data.count + ')', click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }"></span>
                  </div>
                <!-- /ko -->
                <!-- ko if: $data.selected -->
                  <span class="pointer" data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }">
                    <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                    <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                    <div class="hellip">
                      <strong data-bind="html: prettifyDate($data.value), attr: {'title': $data.value}"></strong>
                    </div>
                  </span>
                <!-- /ko -->
              <!-- /ko -->
              <!-- ko if: $index() == $parent.properties.limit() -->
                <!-- ko if: $parent.properties.prevLimit == undefined || $parent.properties.prevLimit == $parent.properties.limit() -->
                  <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                    ${ _('Show more...') }
                  </a>
                <!-- /ko -->
                <!-- ko if: $parent.properties.prevLimit != undefined && $parent.properties.prevLimit != $parent.properties.limit() -->
                  <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                    ${ _('Show more') }
                  </a>
                  /
                  <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'down') }">
                    ${ _('less...') }
                  </a>
                <!-- /ko -->
              <!-- /ko -->
          </div>
        </div>
      <!-- /ko -->
      <!-- ko if: type() == 'range' -->
        <div data-bind="foreach: $parent.counts">
          <div class="trigger-exclude">
              <!-- ko if: ! selected -->
                <a class="exclude pointer" data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, 'exclude': true}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                <div class="hellip">
                  <a class="pointer" data-bind="html: $data.is_single_unit_gap ? prettifyDate($data.from, $parent, $data.to) : prettifyDateRange($data.from, $data.to, $parent, false), click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }, attr: {'title': ($data.is_single_unit_gap ? $data.from : $data.from + ' - ' + $data.to) + ' (' + $data.value + ')'}"></a>
                  <span class="pointer counter" data-bind="text: ' (' + $data.value + ')', click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }"></span>
                </div>
              <!-- /ko -->
              <!-- ko if: selected -->
                <span class="pointer" data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }">
                  <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                  <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                  <div class="hellip">
                    <strong data-bind="html: $data.is_single_unit_gap ? prettifyDate($data.from, $parent, $data.to) : prettifyDateRange($data.from, $data.to, $parent, false), attr: {'title': ($data.is_single_unit_gap ? $data.from : $data.from + ' - ' + $data.to) + ' (' + $data.value + ')'}"></strong>
                  </div>
                </span>
              <!-- /ko -->
          </div>
        </div>
      <!-- /ko -->
      <!-- ko if: type() == 'range-up' -->
        <div data-bind="foreach: $parent.counts">
          <div class="trigger-exclude">
              <!-- ko if: ! selected -->
                <a class="exclude pointer" data-bind="click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, 'exclude': true, is_up: $data.is_up}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                <div class="hellip">
                  <a class="pointer" data-bind="html: prettifyDate($data.from, $parent) + ($data.is_up ? ' & Up' : ' & Less'), click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }, attr: {'title': $data.from + ($data.is_up ? ' & Up' : ' & Less') + ' (' + $data.total_counts + ')'}"></a>
                  <span class="pointer counter" data-bind="text: ' (' + $data.total_counts + ')', click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }"></span>
                </div>
              <!-- /ko -->
              <!-- ko if: selected -->
                <span class="pointer" data-bind="click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }">
                  <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                  <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                  <div class="hellip">
                    <strong data-bind="html: prettifyDate($data.from, $parent) + ($data.is_up ? ' & Up' : ' & Less')"></strong>
                  </div>
                </span>
              <!-- /ko -->
          </div>
        </div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="text-facet-widget">
  ## When coming from a widget chart switch
  <!-- ko if: typeof isLoading !== 'undefined' -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
  <!-- /ko -->

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <!-- ko if: typeof $parent.isLoading !== 'undefined' -->
    <div data-bind="visible: $root.isGridster() || $root.isEditing(), with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle2', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>
    <div class="clearfix"></div>
    <!-- /ko -->

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: properties.facets()[0].type() == 'field' -->
        <!-- ko if: properties.facets()[0].multiselect -->
          <div class="text-widget-filter">
            <!-- ko component: {
              name: 'inline-autocomplete',
              params: {
                querySpec: $parent.querySpec,
                facets: [],
                knownFacetValues: {},
                autocompleteFromEntries: $parent.autocompleteFromEntries
              }
            } --><!-- /ko -->
          </div>
          <!-- ko if: $parent.countsFiltered().length -->
          <div data-bind="foreach: $parent.countsFiltered" class="facet-count">
            <div class="trigger-exclude">
                <!-- ko if: $index() < $parent.properties.limit() -->
                  <!-- ko if: !$data.selected -->
                    <a class="exclude pointer" data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id(), 'exclude': true}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                    <div class="hellip">
                      <a class="pointer" dir="ltr" data-bind="html: prettifyDate($data.value), click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }, attr: {'title': $data.value + ' (' + $data.count + ')'}"></a>
                      <span class="pointer counter" dir="rtl" data-bind="text: ' (' + $data.count + ')', click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }"></span>
                    </div>
                  <!-- /ko -->
                  <!-- ko if: $data.selected -->
                    <span class="pointer" data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }">
                      <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                      <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                      <div class="hellip">
                        <strong data-bind="html: prettifyDate($data.value), attr: {'title': $data.value}"></strong>
                      </div>
                    </span>
                  <!-- /ko -->
                <!-- /ko -->
                <!-- ko if: $index() == $parent.properties.limit() -->
                  <!-- ko if: $parent.properties.prevLimit == undefined || $parent.properties.prevLimit == $parent.properties.limit() -->
                    <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                      ${ _('Show more...') }
                    </a>
                  <!-- /ko -->
                  <!-- ko if: $parent.properties.prevLimit != undefined && $parent.properties.prevLimit != $parent.properties.limit() -->
                    <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                      ${ _('Show more') }
                    </a>
                    /
                    <a class="pointer" data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'down') }">
                      ${ _('less...') }
                    </a>
                  <!-- /ko -->
                <!-- /ko -->
            </div>
          </div>
          <!-- /ko -->
          <!-- ko ifnot: $parent.countsFiltered().length -->
            <div class="facet-count">
              <span class="no-results">${ _('No results found.') }</span>
            </div>
          <!-- /ko -->
       <!-- /ko -->
       <!-- ko ifnot: properties.facets()[0].multiselect -->
        <select data-bind="selectize: $parent.counts, optionsText: 'text', optionsValue:'value', value: $parent.countsSelected"/>
       <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: properties.facets()[0].type() == 'range' -->
        <div data-bind="foreach: $parent.counts" class="facet-count">
          <div class="trigger-exclude">
              <!-- ko if: ! selected -->
                <a class="exclude pointer" data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, 'exclude': true}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                <div class="hellip">
                  <a class="pointer" data-bind="html: $data.is_single_unit_gap ? prettifyDate($data.from, $parent, $data.to) : prettifyDateRange($data.from, $data.to, $parent, false), click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }, attr: {'title': ($data.is_single_unit_gap ? $data.from : $data.from + ' - ' + $data.to) + ' (' + $data.value + ')'}"></a>
                  <span class="pointer counter" data-bind="text: ' (' + $data.value + ')', click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }"></span>
                </div>
              <!-- /ko -->
              <!-- ko if: selected -->
                <span class="pointer" data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }">
                  <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                  <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                  <div class="hellip">
                    <strong data-bind="html: $data.is_single_unit_gap ? prettifyDate($data.from, $parent, $data.to) : prettifyDateRange($data.from, $data.to, $parent, false), attr: {'title': ($data.is_single_unit_gap ? $data.from : $data.from + ' - ' + $data.to) + ' (' + $data.value + ')'}"></strong>
                  </div>
                </span>
              <!-- /ko -->
          </div>
        </div>
      <!-- /ko -->
      <!-- ko if: properties.facets()[0].type() == 'range-up' -->
        <div data-bind="foreach: $parent.counts" class="facet-count">
          <div class="trigger-exclude">
              <!-- ko if: ! selected -->
                <a class="exclude pointer" data-bind="click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, 'exclude': true, is_up: $data.is_up}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                <div class="hellip">
                  <a class="pointer" data-bind="html: prettifyDate($data.from, $parent) + ($data.is_up ? ' & Up' : ' & Less'), click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }, attr: {'title': $data.from + ($data.is_up ? ' & Up' : ' & Less') + ' (' + $data.total_counts + ')'}"></a>
                  <span class="pointer counter" data-bind="text: ' (' + $data.total_counts + ')', click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }"></span>
                </div>
              <!-- /ko -->
              <!-- ko if: selected -->
                <span class="pointer" data-bind="click: function(){ $root.query.selectRangeUpFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field, is_up: $data.is_up}) }">
                  <a class="include pointer" data-bind="visible: ! exclude"><i class="fa fa-times"></i></a>
                  <a class="include pointer" data-bind="visible: exclude"><i class="fa fa-plus"></i></a>
                  <div class="hellip">
                    <strong data-bind="html: prettifyDate($data.from, $parent) + ($data.is_up ? ' & Up' : ' & Less')"></strong>
                  </div>
                </span>
              <!-- /ko -->
          </div>
        </div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="resultset-widget">
  <!-- ko if: $root.collection.template.isGridLayout() -->
    <!-- ko with: $root -->
      <!-- ko if: $root.hasRetrievedResults() && $root.response().response -->
      <span data-bind="template: {name: 'data-grid', data: $root.collection}"></span>
      <!-- /ko -->
    <!-- /ko -->
  <!-- /ko -->
</script>


<script type="text/html" id="grid-chart-settings">
<!-- ko if: $parent.widgetType() === 'resultset-widget' || $parent.widgetType() === 'document-widget' -->
  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: [window.HUE_CHARTS.TYPES.TIMELINECHART, window.HUE_CHARTS.TYPES.BARCHART].indexOf(chartSettings.chartType()) >= 0">
    <li class="nav-header">${_('Chart Type')}</li>
  </ul>
  <div data-bind="visible: [window.HUE_CHARTS.TYPES.TIMELINECHART, window.HUE_CHARTS.TYPES.BARCHART].indexOf(chartSettings.chartType()) >= 0">
    <select class="input-medium" data-bind="options: $root.timelineChartTypes,
                 optionsText: 'label',
                 optionsValue: 'value',
                 value: chartSettings.chartSelectorType">
    </select>
  </div>
  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartSettings.chartType() != ''">
    <li data-bind="visible: [window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP, window.HUE_CHARTS.TYPES.PIECHART].indexOf(chartSettings.chartType()) == -1" class="nav-header">${_('x-axis')}</li>
    <li data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('region')}</li>
    <li data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
    <li data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('legend')}</li>
  </ul>
  <div data-bind="visible: chartSettings.chartType() != ''">
    <select data-bind="options: [window.HUE_CHARTS.TYPES.BARCHART, window.HUE_CHARTS.TYPES.PIECHART, window.HUE_CHARTS.TYPES.GRADIENTMAP, window.HUE_CHARTS.TYPES.MAP].indexOf(chartSettings.chartType()) >= 0 ? cleanedMeta : chartSettings.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART ? cleanedDateTimeMeta : cleanedNumericMeta, value: chartSettings.chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartSettings.chartX}" class="input-medium"></select>
  </div>

  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartSettings.chartType() != ''">
    <li data-bind="visible: [window.HUE_CHARTS.TYPES.MAP, , window.HUE_CHARTS.TYPES.PIECHART].indexOf(chartSettings.chartType()) == -1" class="nav-header">${_('y-axis')}</li>
    <li data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
    <li data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('value')}</li>
  </ul>

  <div style="overflow-y: auto; max-height: 220px" data-bind="visible: chartSettings.chartType() != '' && ([window.HUE_CHARTS.TYPES.TIMELINECHART, window.HUE_CHARTS.TYPES.BARCHART, window.HUE_CHARTS.TYPES.LINECHART].indexOf(chartSettings.chartType()) >= 0 )">
    <ul class="unstyled" data-bind="foreach: cleanedNumericMeta">
      <li><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartSettings.chartYMulti" /> <span data-bind="text: name"></span></li>
    </ul>
  </div>
  <div data-bind="visible: [window.HUE_CHARTS.TYPES.PIECHART, window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartSettings.chartType()) >= 0">
    <select data-bind="options: cleanedNumericMeta, value: chartSettings.chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartSettings.chartYSingle}" class="input-medium"></select>
  </div>

  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartSettings.chartType() != '' && chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP && window.HUE_CHARTS.TYPES.GRADIENTMAP">
    <li class="nav-header">${_('label')}</li>
  </ul>
  <div data-bind="visible: chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP">
    <select data-bind="options: cleanedMeta, value: chartSettings.chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartSettings.chartMapLabel}" class="input-medium"></select>
  </div>


  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartSettings.chartType() != '' && [window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartSettings.chartType()) < 0">
    <li class="nav-header">${_('sorting')}</li>
  </ul>
  <div class="btn-group" data-toggle="buttons-radio" data-bind="visible: chartSettings.chartType() != '' && [window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartSettings.chartType()) < 0">
    <a rel="tooltip" data-placement="top" title="${_('No sorting')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSettings.chartSorting() == 'none'}, click: function(){ chartSettings.chartSorting('none'); }"><i class="fa fa-align-left fa-rotate-270"></i></a>
    <a rel="tooltip" data-placement="top" title="${_('Sort ascending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSettings.chartSorting() == 'asc'}, click: function(){ chartSettings.chartSorting('asc'); }"><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
    <a rel="tooltip" data-placement="top" title="${_('Sort descending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSettings.chartSorting() == 'desc'}, click: function(){ chartSettings.chartSorting('desc'); }"><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
  </div>
<!-- /ko -->

</script>

<script type="text/html" id="html-resultset-widget">
  <!-- ko ifnot: $root.collection.template.isGridLayout() -->
    <!-- ko if: isEditing() -->
    <div class="metric-form html-form">
      <a href="javascript:void(0)" data-bind="toggle: isEditing" class="pull-right"><i class="fa fa-times inactive-action"></i></a>
      <div style="margin-bottom: 20px">
        <ul class="nav nav-pills">
          <li class="active"><a href="javascript: void(0)" class="widget-editor-pill">${_('Editor')}</a></li>
          <li><a href="javascript: void(0)" class="widget-html-pill">${_('HTML')}</a></li>
          <li><a href="javascript: void(0)" class="widget-css-pill">${_('CSS & JS')}</a></li>
          <li><a href="javascript: void(0)" class="widget-settings-pill">${_('Sorting')}</a></li>
        </ul>
      </div>

      <div class="widget-section widget-editor-section">
        <div class="row-fluid">
          <div class="span9">
            <div data-bind="fresherEditor: { data: $root.collection.template.template }"></div>
          </div>
          <div class="span3">
            <div class="editor-title">${_('Available Fields')}</div>
            <select data-bind="options: $root.collection.fields, optionsText: 'name', value: $root.collection.template.selectedVisualField" class="input-large chosen-select"></select>
            <button title="${ _('Click on this button to add the field') }" class="btn btn-mini plus-btn" data-bind="click: $root.collection.template.addFieldToVisual">
              <i class="fa fa-plus"></i>
            </button>

            <div class="editor-title margin-top-30">${_('Available Functions')}</div>
            <select id="visualFunctions" data-bind="value: $root.collection.template.selectedVisualFunction" class="input-large chosen-select">
              <option title="${ _('Formats date or timestamp in DD-MM-YYYY') }" value="{{#date}} {{/date}}">{{#date}}</option>
              <option title="${ _('Formats date or timestamp in HH:mm:ss') }" value="{{#time}} {{/time}}">{{#time}}</option>
              <option title="${ _('Formats date or timestamp in DD-MM-YYYY HH:mm:ss') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
              <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
              <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
              <option title="${ _('Formats a Unix timestamp as Ns, Nmin, Ndays... ago') }" value="{{#fromnow}} {{/fromnow}}">{{#fromnow}}</option>
              <option title="${ _('Downloads and embed the file in the browser') }" value="{{#embeddeddownload}} {{/embeddeddownload}}">{{#embeddeddownload}}</option>
              <option title="${ _('Downloads the linked file') }" value="{{#download}} {{/download}}">{{#download}}</option>
              <option title="${ _('Preview file in File Browser') }" value="{{#preview}} {{/preview}}">{{#preview}}</option>
              <option title="${ _('Truncate a value after 100 characters') }" value="{{#truncate100}} {{/truncate100}}">{{#truncate100}}</option>
              <option title="${ _('Truncate a value after 250 characters') }" value="{{#truncate250}} {{/truncate250}}">{{#truncate250}}</option>
              <option title="${ _('Truncate a value after 500 characters') }" value="{{#truncate500}} {{/truncate500}}">{{#truncate500}}</option>
            </select>
            <button title="${ _('Click on this button to add the function') }" class="btn btn-mini plus-btn" data-bind="click: $root.collection.template.addFunctionToVisual">
              <i class="fa fa-plus"></i>
            </button>
            <p class="muted" style="margin-top: 10px"></p>
          </div>
        </div>
      </div>
      <div class="widget-section widget-html-section" style="display: none">
        <div class="row-fluid">
          <div class="span9">
            <textarea data-bind="codemirror: {data: $root.collection.template.template, lineNumbers: true, htmlMode: true, mode: 'text/html', stripScript: true }" data-template="true"></textarea>
          </div>
          <div class="span3">
            <div class="editor-title">${_('Available Fields')}</div>
            <select data-bind="options: $root.collection.fields, optionsText: 'name', value: $root.collection.template.selectedSourceField" class="input-medium chosen-select"></select>
            <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFieldToSource">
              <i class="fa fa-plus"></i>
            </button>

            <div class="editor-title" style="margin-top: 30px">${_('Available Functions')}</div>
            <select id="sourceFunctions" data-bind="value: $root.collection.template.selectedSourceFunction" class="input-medium chosen-select">
              <option title="${ _('Formats a date in the DD-MM-YYYY format') }" value="{{#date}} {{/date}}">{{#date}}</option>
              <option title="${ _('Formats a date in the HH:mm:ss format') }" value="{{#time}} {{/time}}">{{#time}}</option>
              <option title="${ _('Formats a date in the DD-MM-YYYY HH:mm:ss format') }" value="{{#datetime}} {{/datetime}}">{{#datetime}}</option>
              <option title="${ _('Formats a date in the full format') }" value="{{#fulldate}} {{/fulldate}}">{{#fulldate}}</option>
              <option title="${ _('Formats a date as a Unix timestamp') }" value="{{#timestamp}} {{/timestamp}}">{{#timestamp}}</option>
              <option title="${ _('Shows the relative time') }" value="{{#fromnow}} {{/fromnow}}">{{#fromnow}}</option>
              <option title="${ _('Downloads and embed the file in the browser') }" value="{{#embeddeddownload}} {{/embeddeddownload}}">{{#embeddeddownload}}</option>
              <option title="${ _('Downloads the linked file') }" value="{{#download}} {{/download}}">{{#download}}</option>
              <option title="${ _('Preview file in File Browser') }" value="{{#preview}} {{/preview}}">{{#preview}}</option>
              <option title="${ _('Truncate a value after 100 characters') }" value="{{#truncate100}} {{/truncate100}}">{{#truncate100}}</option>
              <option title="${ _('Truncate a value after 250 characters') }" value="{{#truncate250}} {{/truncate250}}">{{#truncate250}}</option>
              <option title="${ _('Truncate a value after 500 characters') }" value="{{#truncate500}} {{/truncate500}}">{{#truncate500}}</option>
            </select>
            <button title="${ _('Click on this button to add the function') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFunctionToSource">
              <i class="fa fa-plus"></i>
            </button>
            <p class="muted" style="margin-top: 10px"></p>
          </div>
        </div>
      </div>
      <div class="widget-section widget-css-section" style="display: none">
        <textarea data-bind="codemirror: {data: $root.collection.template.extracode, lineNumbers: true, htmlMode: true, mode: 'text/html' }"></textarea>
      </div>
      <div class="widget-section widget-settings-section" style="display: none">
        <div style="overflow-x: scroll; min-height: 40px">
          <table>
            <tr class="result-sorting" data-bind="template: {name: 'result-sorting', data: $root.collection}">
            </tr>
          </table>
        </div>
        <br/>
      </div>
    </div>
    <!-- /ko -->


    <div class="result-main html-resultset" style="overflow-x: auto">
      <!-- ko if: $root.isToolbarVisible -->
      <div class="edit-dimensions" style="float: right">
        <div class="badge dimensions-badge-container dimensions-badge-container-add">
          <div class="action-icon" data-bind="click: function(){ isEditing(true);}"><i class="fa fa-pencil"></i> ${ _('Edit template') }</div>
        </div>
        <div class="clearfix"></div>
      </div>
      <!-- /ko -->

      <div data-bind="visible: $root.hasRetrievedResults() && $root.results().length == 0">
        <br/>
        ${ _('Your search did not match any documents.') }
      </div>



      <!-- ko if: $root.response().response && $root.results().length > 0 -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->


      <table class="result-container" data-bind="visible: $root.hasRetrievedResults()" style="margin-top: 0; width: 100%; border-collapse: initial">
        <thead>
          <tr>
            <th>&nbsp;</th>
          </tr>
        </thead>
        <tbody data-bind="foreach: {data: $root.results, as: 'doc'}" class="result-tbody">
          <tr data-bind="style: {'backgroundColor': $index() % 2 == 0 ? '#FFF': '#F6F6F6'}">
            <td><div data-bind="html: content" style="margin-bottom: -20px"></div></td>
          </tr>
          <tr>
            <td class="show-details-icon pointer" data-bind="click: toggleDocDetails">
              <i class="fa" data-bind="css: {'fa-caret-down' : ! doc.showDetails(), 'fa-caret-up': doc.showDetails()}"></i>
            </td>
          </tr>
          <tr data-bind="visible: doc.showDetails" class="show-details">
            <td data-bind="attr: {'colspan': $root.collection.template.fieldsSelected().length > 0 ? $root.collection.template.fieldsSelected().length + 1 : 2}">
              <span data-bind="template: {name: 'document-details', data: $data}"></span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="widget-spinner" data-bind="visible: !$root.hasRetrievedResults()">
        <i class="fa fa-spinner fa-spin"></i>
      </div>
    </div>
  <!-- /ko -->
</script>


<script type="text/html" id="document-details">
  <!-- ko if: $data.details().length == 0 -->
    <i class="fa fa-spinner fa-spin"></i>
  <!-- /ko -->
  <!-- ko if: $data.details().length > 0 -->
    <div class="document-details-actions pull-left" data-bind="visible: $root.collection.idField() || externalLink()">
      <a href="javascript:void(0)" data-bind="visible: ! showEdit(), click: function() { showEdit(true); }" title="${ _('Edit this document') }">
        <i class="fa fa-edit fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: showEdit(), click: function(data, e) { $(e.currentTarget).parent().css('marginTop', '8px'); $root.getDocument($data); showEdit(false); }" title="${ _('Undo changes') }">
        <i class="fa fa-undo fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: showEdit() && originalDetails() != ko.toJSON(details), click: $root.updateDocument" title="${ _('Update this document') }">
        <i class="fa fa-save fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: externalLink(), attr: { href: externalLink }" target="_blank" title="${ _('Show original document') }">
        <i class="fa fa-external-link fa-fw"></i>
      </a>
    </div>
    <div class="document-details pull-left">
      <table class="table table-condensed">
        <tbody data-bind="foreach: details">
          <tr data-bind="css: {'readonly': !$parent.showEdit()}">
             <th class="grid-th" data-bind="text: key"></th>
             <td width="100%">
               <!-- ko if: typeof value() == 'string' && value().match(/^https?:\/\//i) -->
               <a data-bind="attr: { href: hueUtils.escapeOutput(value()) }" target="_blank">
                 <span data-bind="text: value, visible: !$parent.showEdit()"></span>
               </a>
               <!-- /ko -->
               <!-- ko ifnot: typeof value() == 'string' && value().match(/^https?:\/\//i) -->
                 <span data-bind="text: value, visible: !$parent.showEdit()"></span>
               <!-- /ko -->
               <input data-bind="value: value, visible: $parent.showEdit, valueUpdate: 'afterkeydown',
               click: function(detail, e){
                var target = $(e.currentTarget);
                target.parents('.show-details').find('.document-details-actions').animate({
                  'marginTop': (target.position().top - target.parents('table').position().top) + 'px'
                }, 200)
               }" class="input-xxlarge" style="width: 600px" />
             </td>
          </tr>
        </tbody>
      </table>

      <!-- ko if: doc.childDocuments != undefined -->
        <table class="result-container" data-bind="visible: $root.hasRetrievedResults()" style="margin-top: 0; width: 100%; border-collapse: initial">
          <thead>
            <tr data-bind="visible: $root.collection.template.fieldsSelected().length > 0, template: {name: 'result-sorting', data: $root.collection}">
            </tr>
            <tr data-bind="visible: $root.collection.template.fieldsSelected().length == 0">
              <th style="width: 18px">&nbsp;</th>
              <th>${ _('Child Documents') }</th>
            </tr>
          </thead>
          <tbody data-bind="foreach: {data: childDocuments, as: 'doc'}" class="result-tbody">
            <tr class="result-row" data-bind="style: {'backgroundColor': $index() % 2 == 0 ? '#FFF': '#F6F6F6'}">
              <td>
                <a href="javascript:void(0)" data-bind="click: function() { doc.showDetails(! doc.showDetails()); }">
                  <i class="fa" data-bind="css: {'fa-caret-right' : ! doc.showDetails(), 'fa-caret-down': doc.showDetails()}"></i>
                </a>
              </td>
              <!-- ko foreach: row -->
                <td data-bind="html: $data"></td>
              <!-- /ko -->
            </tr>
            <tr data-bind="visible: doc.showDetails" class="show-details">
              <td>&nbsp;</td>
              <td data-bind="attr: {'colspan': $root.collection.template.fieldsSelected().length > 0 ? $root.collection.template.fieldsSelected().length + 1 : 2}">
                <span data-bind="template: {name: 'document-details', data: $data}"></span>
              </td>
            </tr>
          </tbody>
        </table>
      <!-- /ko -->

    </div>
  <!-- /ko -->
</script>


<script type="text/html" id="result-sorting">
  <th style="width: 18px">&nbsp;</th>
  <!-- ko foreach: template.fieldsSelected -->
  <th data-bind="with: $root.collection.getTemplateField($data, $parent.template.fields())" style="white-space: nowrap">
    <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout" title="${ _('Click to sort') }"></span>
    <i class="fa fa-sort inactive-action margin-right-10 margin-left-5" data-bind="click: $root.collection.toggleSortColumnGridLayout, css: { 'blue': sort.direction() != null, 'fa-sort-down': sort.direction() == 'desc', 'fa-sort-up': sort.direction() == 'asc' }" title="${ _('Click to sort') }"></i>
    <!-- ko if: $root.isToolbarVisible() || $root.isEditing() -->
      <!-- ko if: $index() > 0 -->
      <i class="fa fa-caret-left inactive-action" data-bind="click: function(){ $root.collection.translateSelectedField($index(), 'left', $parents[1].template); }" title="${ _('Move to the left') }"></i>
      <!-- /ko -->
      <!-- ko if: $index() < $parents[1].template.fields().length - 1 -->
      <i class="fa fa-caret-right inactive-action" data-bind="click: function(){ $root.collection.translateSelectedField($index(), 'right', $parents[1].template); }" title="${ _('Move to the right') }"></i>
      <!-- /ko -->
    <!-- /ko -->
  </th>
  <!-- /ko -->
</script>


<script type="text/html" id="resultset-pagination">
<div style="text-align: center; margin-top: 4px">
  <a href="javascript: void(0)" title="${ _('Previous') }">
    <span data-bind="click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-chevron-left" data-bind="
        visible: $data.response.start * 1.0 >= ($parent.template ? $parent : $root.collection).template.rows() * 1.0,
        click: function() { $root.query.paginate('prev') }">
    </i>
  </a>

  ${ _('Showing') }
  <span data-bind="text: ($data.response.start + 1)"></span>
  ${ _('to') }
  <!-- ko if: $root.collection.supportAnalytics() && $data.response.start == 0 && $data.response.numFound > ($parent.template ? $parent : $root.collection).template.rows() -->
    <span class="spinedit-cnt">
      <input type="text" data-bind="spinedit: ($parent.template ? $parent : $root.collection).template.rows, valueUpdate:'afterkeydown'" style="text-align: center; margin-bottom: 0" />
    </span>
  <!-- /ko -->
  <!-- ko if: !($root.collection.supportAnalytics() && $data.response.start == 0 && $data.response.numFound > ($parent.template ? $parent : $root.collection).template.rows()) -->
  <span data-bind="text: Math.min(($data.response.start + ($parent.template ? $parent : $root.collection).template.rows()), $data.response.numFound)"></span>
  <!-- /ko -->
  ${ _('of') }
  <span data-bind="text: $data.response.numFound"></span>
  ${ _(' results') }

  <span data-bind="visible: $root.isEditing() && !$root.collection.supportAnalytics()">
    - ${ _('Show') }
    <span class="spinedit-cnt">
      <input type="text" data-bind="spinedit: ($parent.template ? $parent : $root.collection).template.rows, valueUpdate:'afterkeydown'" style="text-align: center; margin-bottom: 0" />
    </span>
    ${ _('results per page') }
  </span>

  <!-- ko if: $parent == $root.collection && $root.collection.engine() == 'solr'-->
  <span data-bind="visible: $root.collection.template.fieldsSelected().length > 0, click: function() {$root.collection.template.moreLikeThis(!$root.collection.template.moreLikeThis()); $root.search(); }" title="${ _('Show similar records based on the selected fields') }">
    - <a href="javascript: void(0)"><span data-bind="text: $root.collection.template.moreLikeThis() ? '${ _ko('Hide') }' : '${ _ko('Show') }'"></span></a> ${ _('More like this') }
  </span>
  <!-- /ko -->

  <a href="javascript: void(0)" title="${ _('Next') }">
    <span data-bind="click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-chevron-right" data-bind="
        visible: (($parent.template ? $parent : $root.collection).template.rows() * 1.0 + $data.response.start * 1.0) < $data.response.numFound,
        click: function() { $root.query.paginate('next') }">
    </i>
  </a>
</div>
</script>


<script type="text/html" id="histogram-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div class="clearfix"></div>

    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px" data-bind="visible: counts().length > 0">
      <span data-bind="with: $root.collection.getFacetById($parent.id())">
        <div data-bind="visible: canZoomIn() || canReset()" class="inline-block">
          <span class="facet-field-label">${ _('Zoom') }</span>
          <i class="fa fa-search-minus"></i>
        </div>
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canZoomIn">
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomIn">${ _('to selection') }</a>
        </div>
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canReset">
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut">${ _('reset') }</a>
        </div>
        <span class="facet-field-label">${ _('Chart Type') }</span>
        <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
        </select>&nbsp;
      </span>
      <span class="facet-field-label" data-bind="visible: $root.query.multiqs().length > 1">${ _('Group by') }</span>
      <select class="input-medium" data-bind="visible: $root.query.multiqs().length > 1, options: $root.query.multiqs, optionsValue: 'id', optionsText: 'label', value: $root.query.selectedMultiq"></select>
    </div>

    <!-- ko if: $root.collection.getFacetById($parent.id()) -->
      <div style="position: relative;">
      <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), enableSelection: true, field: field, label: label(), transformer: timelineChartDataTransformer,
        type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
        hideSelection: true,
        hideStacked: hideStacked,
        selectedSerie: selectedSerie,
        fqs: $root.query.fqs,
        slot: $root.collection.getFacetById($parent.id()).properties.slot,
        onSelectRange: function(from, to){ $root.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
        onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); $root.collection.getFacetById($parent.id()).properties.enableSelection(state.selectionEnabled); },
        onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
        onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false); }}"/>
      <div class="clearfix"></div>
      </div>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="timeline-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <!-- ko with: $root.collection.getFacetById($parent.id()) -->
    <div style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
      <div class="clearfix"></div>
    </div>

    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px">
      <div data-bind="visible: canZoomIn() || canReset()" class="inline-block">
        <span class="facet-field-label">${ _('Zoom') }</span>
        <i class="fa fa-search-minus"></i>
      </div>
      <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canZoomIn">
        <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomIn">${ _('to selection') }</a>
      </div>
      <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canReset">
        <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut">${ _('reset') }</a>
      </div>
      <span data-bind="with: $root.collection.getFacetById($parent.id())">
        <span class="facet-field-label">${ _('Chart Type') }</span>
        <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
        </select>&nbsp;
      </span>
    </div>

    <span data-bind="template: { name: 'data-grid' }"></span>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="bar-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: properties.canRange -->
        <div style="padding-bottom: 10px; text-align: right; padding-right: 20px">
          <span class="facet-field-label">${ _('Zoom') }</span>
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
        </div>
      <!-- /ko -->
    </div>

    <!-- ko if: $root.collection.getFacetById($parent.id()) -->
    <div style="position: relative;">
    <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(),
      fqs: $root.query.fqs,
      enableSelection: true,
      hideSelection: true,
      hideStacked: hideStacked,
      slot: $root.collection.getFacetById($parent.id()).properties.slot,
      transformer: ($data.type == 'range-up' ? barChartRangeUpDataTransformer : barChartDataTransformer),
      onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
      onClick: function(d) {
        if (d.obj.field != undefined) {
          if ($data.type == 'range-up') {
            searchViewModel.query.selectRangeUpFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field, 'exclude': false, is_up: d.obj.is_up});
          } else {
            searchViewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field});
          }
        } else {
          searchViewModel.query.toggleFacet({facet: d.obj, widget_id: d.obj.widget_id});
        }
      },
      onSelectRange: function(from, to){ searchViewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); },
      type: $root.collection.getFacetById($parent.id()).properties.timelineChartType }"
    />
    </div>
    <div class="clearfix"></div>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="data-grid">
  <div class="grid-row">

    <div class="grid-left-bar">
      <div>
        <div style="margin-top: 3px">
          <a class="grid-side-btn active" href="javascript: void(0)"
             data-bind="click: function(collection, event){ template.showChart(false); template.showGrid(true); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-table' } ); }, css: {'active': template.showGrid() }" title="${_('Grid')}">
            <i class="fa fa-th fa-fw"></i>
          </a>
        </div>

        <div class="dropdown">
          <a class="grid-side-btn" style="padding-right:0" href="javascript:void(0)"
             data-bind="css: {'active': template.showChart() }, click: function(collection, event){ template.showChart(true); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate'); }">
            % if HAS_REPORT_ENABLED.get():
            <i class="fa fa-superscript fa-fw" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.COUNTER"></i>
            <i class="fa fa-sort-amount-asc fa-fw" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TEXTSELECT"></i>
            % endif
            <i class="hcha hcha-bar-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.BARCHART"></i>
            <i class="hcha hcha-pie-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART" style="display: none;"></i>
            <i class="fa fa-fw fa-line-chart" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART" style="display: none;"></i>
            <i class="hcha hcha-map-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP" style="display: none;"></i>
            <i class="fa fa-fw fa-map-marker" data-bind="visible: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP" style="display: none;"></i>
          </a>
          <a class="dropdown-toggle grid-side-btn" style="padding:0" data-toggle="dropdown"
             href="javascript: void(0)" data-bind="css: {'active': template.showChart()}">
            <i class="fa fa-caret-down"></i>
          </a>

          <ul class="dropdown-menu">
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.COUNTER}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.COUNTER); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}"
                 class="active">
                <i class="fa fa-superscript fa-fw"></i> ${_('Counter')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TEXTSELECT}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.TEXTSELECT); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}"
                 class="active">
                <i class="fa fa-sort-amount-asc fa-fw"></i> ${_('Text select')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.BARCHART}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.BARCHART); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}"
                 class="active">
                <i class="hcha hcha-bar-chart fa-fw"></i> ${_('Bars')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.PIECHART); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}">
                <i class="hcha hcha-pie-chart fa-fw"></i> ${_('Pie')}
              </a>
            </li>
            ##<!-- ko if: widgetType() != 'resultset-widget' -->
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.TIMELINECHART); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}">
                <i class="fa fa-fw fa-line-chart"></i> ${_('Timeline')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.GRADIENTMAP); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}">
                <i class="hcha fa-fw hcha-map-chart chart-icon"></i> ${_('Gradient Map')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP}, click: function(collection, event){ template.showChart(true); template.chartSettings.chartType(window.HUE_CHARTS.TYPES.MAP); template.showGrid(false); huePubSub.publish('gridster.clean.grid.whitespace', { event: event, lookFor: '.grid-results-chart' }); huePubSub.publish('gridChartForceUpdate');}">
                <i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}
              </a>
            </li>
          </ul>
        </div>

        <div data-bind="visible: template.showGrid() || (template.showChart() && (widgetType() === 'resultset-widget' || widgetType() === 'document-widget'))">
          <a class="grid-side-btn" href="javascript:void(0)" data-bind="click: function(){ template.showFieldList(!template.showFieldList())}, css: { 'blue' : template.showFieldList() }">
            <!-- ko if: template.showFieldList() -->
              <i class="fa fa-fw fa-chevron-left"></i>
            <!-- /ko -->
            <!-- ko ifnot: template.showFieldList() -->
              <i class="fa fa-fw fa-columns"></i>
            <!-- /ko -->
          </a>
        </div>

        <!-- ko if: $root.collection.engine() != 'solr' -->
          <div data-bind="component: { name: 'downloadSnippetResults', params: { gridSideBtn: true, snippet: $data.queryResult(), notebook: {getContext: function() { return {type: $data.queryResult().type(), id: 1}; }} } }" style="display:inline-block;"></div>
        <!-- /ko -->

        <!-- ko if: $root.collection.engine() == 'solr' -->
        <form method="POST" style="display:inline" data-bind="attr: { action: window.HUE_BASE_URL + '${ url("dashboard:download") }' }">
          ${ csrf_token(request) | n,unicode }
          <input type="hidden" name="collection" data-bind="value: ko.mapping.toJSON($root.collection)"/>
          <input type="hidden" name="query" data-bind="value: ko.mapping.toJSON($root.query)"/>
          <input type="hidden" name="download">
          <input type="hidden" name="type" value="">
          ## Similar to isGridLayout
          <!-- ko if: widgetType() != 'resultset-widget' -->
            <input type="hidden" name="facet" data-bind="value: ko.mapping.toJSON($data)">
          <!-- /ko -->
          % if conf.ENABLE_DOWNLOAD.get():
          <div class="dropdown">
            <a class="grid-side-btn dropdown-toggle" style="padding-left:7px" data-toggle="dropdown">
              <i class="fa fa-download fa-fw"></i>
            </a>
            <ul class="dropdown-menu">
              <li>
                <a class="download" href="javascript:void(0)" data-bind="click: function(widget, event){ var $f = $(event.currentTarget).parents('form'); $f.find('[name=\'type\']').val('csv'); $f.submit()}" title="${ _('Download first rows as CSV') }">
                  <i class="hfo hfo-file-csv"></i> ${ _("CSV") }
                </a>
              </li>
              <li>
                <a class="download" href="javascript:void(0)" data-bind="click: function(widget, event){ var $f = $(event.currentTarget).parents('form'); $f.find('[name=\'type\']').val('xls'); $f.submit()}" title="${ _('Download first rows as XLS') }">
                  <i class="hfo hfo-file-xls"></i> ${ _("Excel") }
                </a>
              </li>
              <li>
                <a class="download" href="javascript:void(0)" data-bind="click: function(widget, event){ var $f = $(event.currentTarget).parents('form'); $f.find('[name=\'type\']').val('json'); $f.submit()}" title="${ _('Download first rows as JSON') }">
                  <i class="hfo hfo-file-json"></i> ${ _("JSON") }
                </a>
              </li>
              ##<li>
                ##<a class="download" href="javascript:void(0)" data-bind="click: function(widget, event){ var $f = $(event.currentTarget).parents('form'); $f.find('[name=\'type\']').val('json'); $f.submit()}" title="${ _('Export results to a dataset') }">
                ##  <i class="fa fa-w fa-save"></i> ${_('Export')}
                ##</a>
              ##</li>
            </ul>
          </div>
          % endif
        </form>
        <!-- /ko -->

      </div>
    </div>
  </div>

  <div class="grid-results">
    <span data-bind="visible: $parent.hasRetrievedResults() && $parent.response().response">
      <div data-bind="visible: template.showFieldList() && template.showGrid()" style="float:left; width:200px; margin-right:10px; background-color:#FFF; padding:5px;">
        <input type="text" data-bind="clearable: template.fieldsAttributesFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" style="width:180px; margin-bottom:10px" />
        <div style="margin-bottom: 8px">
          <a href="javascript: void(0)" data-bind="click: function(){template.filteredAttributeFieldsAll(true)}, style: {'font-weight': template.filteredAttributeFieldsAll() ? 'bold': 'normal'}">${_('All')} (<span data-bind="text: template.fieldsAttributes().length"></span>)</a> / <a href="javascript: void(0)" data-bind="click: function(){template.filteredAttributeFieldsAll(false)}, style: {'font-weight': ! template.filteredAttributeFieldsAll() ? 'bold': 'normal'}">${_('Current')} (<span data-bind="text: template.fields().length"></span>)</a>
        </div>
        <div style="border-bottom: 1px solid #CCC; padding-bottom: 4px;margin-left:4px">
          <div class="pull-left hue-checkbox fa" data-bind="click: toggleGridFieldsSelection, css: { 'fa-check': template.fields().length > 0 }"></div>
          <strong>&nbsp;${_('Field Name')}</strong>
        </div>
        <div data-bind="visible: template.filteredAttributeFields().length == 0" style="padding-left:4px; padding-top:5px; color:#CCC">
          ${ _('No matches.') }
        </div>
        <div class="fields-list" data-bind="foreach: { data: template.filteredAttributeFields, afterRender: resizeFieldsListThrottled }">
          <div style="margin-bottom: 3px; white-space: nowrap; position:relative">
            <div class="pull-left hue-checkbox fa" data-bind="multiCheck: '#partitionsTable', value: name, checkedValue: name, hueChecked: $parent.template.fieldsSelected"></div>
            <div data-bind="text: name, css:{'field-selector': true, 'hoverable': $parent.template.fieldsSelected.indexOf(name()) > -1}, click: highlightColumn, attr: {'title': name() + ' (' + type() + ')'}" style="margin-right:10px"></div>
            <i class="fa fa-question-circle muted pointer analysis" data-bind="click: function(data, e) { $root.fieldAnalysesName(name()); $root.showFieldAnalysis(data, e); }, attr: {'title': '${ _ko('Analyze') }'}, visible: type() != 'aggr'" style="position:absolute; left: 168px; background-color: #FFF"></i>
          </div>
        </div>
      </div>

      <div data-bind="visible: template.showFieldList() && template.showChart() && (widgetType() === 'resultset-widget' || widgetType() === 'document-widget')" style="float:left; width:200px; margin-right:10px; background-color:#FFF; padding:5px;">
        <span data-bind="template: {name: 'grid-chart-settings', data: template}"></span>
      </div>
    </span>

      <div class="widget-spinner" data-bind="visible: !$parent.hasRetrievedResults() || !$parent.response().response">
        <i class="fa fa-spinner fa-spin"></i>
      </div>

      <div data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length == 0 && $parent.response().response">
        <br/>
        ${ _('Your search did not match any documents.') }
      </div>

      <div class="grid-results-table" data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length > 0 && template.showGrid()">
        <!-- ko if: $parent.response().response -->
          <div data-bind="template: {name: 'resultset-pagination', data: $parent.response()}" style="padding:8px; color:#666"></div>
        <!-- /ko -->

        <div class="result-main" style="overflow-x: auto">
          <table class="result-container" data-bind="visible: $parent.hasRetrievedResults()" style="margin-top: 0; width: 100%; border-collapse: initial">
            <thead>
              <tr class="result-sorting" data-bind="visible: template.fieldsSelected().length > 0, template: {name: 'result-sorting', afterRender: throttledHeaderScroll}">
              </tr>
              <tr data-bind="visible: template.fieldsSelected().length == 0">
                <th style="width: 18px">&nbsp;</th>
                <th>${ _('Document') }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: {data: $parent.results, as: 'doc'}" class="result-tbody">
              <tr class="result-row" data-bind="style: {'backgroundColor': $index() % 2 == 0 ? '#FFF': '#F6F6F6'}">
                <td>
                  <a href="javascript:void(0)" data-bind="click: toggleDocDetails">
                    <i class="fa" data-bind="css: {'fa-caret-right' : ! doc.showDetails(), 'fa-caret-down': doc.showDetails()}"></i>
                    <!-- ko if: doc.childDocuments != undefined -->
                    &nbsp(<span data-bind="text: doc.numFound || doc.childDocuments().length"></span>)
                    <!-- /ko -->
                  </a>
                </td>
                <!-- ko foreach: row -->
                  <td data-bind="html: $data"></td>
                <!-- /ko -->
              </tr>
              <tr data-bind="visible: doc.showDetails" class="show-details">
                <td>&nbsp;</td>
                <td data-bind="attr: {'colspan': $parent.template.fieldsSelected().length > 0 ? $parent.template.fieldsSelected().length + 1 : 2}">
                  <span data-bind="template: {name: 'document-details', data: $data}"></span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="grid-results-chart" data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length > 0 && template.showChart()">
        <div data-bind="visible: ! template.hasDataForChart()" style="padding: 10px">${ _('Please select the chart parameters on the left.') }</div>
        <div class="grid-chart-container" style="overflow-x: auto">

        <!-- ko if: widgetType() == 'hit-widget' -->
          <!-- ko with: $parent -->
            <!-- ko if: counts().length > 0 && $root.collection.getFacetById($parent.id()) -->
              <span class="big-counter" data-bind="template: { name: 'counter-form', data: {counts: counts(), properties: $root.collection.getFacetById($parent.id()).properties }}"></span>
            <!-- /ko -->
          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'text-facet-widget' -->
          <span data-bind="template: { name: 'text-facet-widget' }"></span>
        <!-- /ko -->

        <!-- ko if: widgetType() == 'bucket-widget' -->
          <!-- ko with: $parent -->

          <!-- ko if: dimension() == 1 -->
            <div data-bind="barChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(),
              fqs: $root.query.fqs,
              enableSelection: true,
              hideSelection: true,
              hideStacked: hideStacked,
              slot: $root.collection.getFacetById($parent.id()).properties.slot,
              transformer: barChartDataTransformer2,
              onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
              onClick: function(d) {
                if (d.obj.field != undefined) {
                  if ($data.type == 'range-up') {
                    searchViewModel.query.selectRangeUpFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field, 'exclude': false, is_up: d.obj.is_up});
                  } else {
                    searchViewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field});
                  }
                } else {
                  searchViewModel.query.toggleFacet({facet: d.obj, widget_id: d.obj.widget_id});
                }
              },
              onSelectRange: function(from, to){ searchViewModel.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
              onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); },
              type: $root.collection.getFacetById($parent.id()).properties.timelineChartType }"
            />
            <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: dimension() == 2 -->
            <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(),
              isPivot: true,
              fqs: $root.query.fqs,
              enableSelection: true,
              hideSelection: true,
              hideStacked: hideStacked,
              slot: $root.collection.getFacetById($parent.id()).properties.slot,
              transformer: pivotChartDataTransformer,
              onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
              onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
              onClick: function(d) {
                $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
              },
              onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); },
              type: $root.collection.getFacetById($parent.id()).properties.timelineChartType }"
            />
            <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: dimension() == 3 -->
          <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
            type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
            fqs: $root.query.fqs,
            enableSelection: true,
            hideSelection: true,
            hideStacked: hideStacked,
            selectedSerie: selectedSerie,
            slot: $root.collection.getFacetById($parent.id()).properties.facets()[0].slot,
            onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
            onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
            onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
            onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false); }}" />
            <div class="clearfix"></div>
          <!-- /ko -->

          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'gradient-map-widget' -->
          <!-- ko with: $parent -->
            <div data-bind="mapChart: {data: {counts: counts(), scope: $parent.properties.scope()},
              transformer: gradientMapChartDataTransformer,
              maxWidth: 750,
              isScale: true,
              onClick: function(d) {
                $root.query.togglePivotFacet({facet: {'fq_fields': d.fields, 'fq_values': d.value}, widget_id: id()});
              },
              onComplete: function(){ var widget = searchViewModel.getWidgetById($parent.id()); if (widget != null) { widget.isLoading(false)}; }}" />
           <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'timeline-widget' -->
          <!-- ko with: $parent -->
          <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
            type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
            fqs: $root.query.fqs,
            enableSelection: true,
            hideSelection: true,
            hideStacked: hideStacked,
            selectedSerie: selectedSerie,
            slot: $root.collection.getFacetById($parent.id()).properties.slot,
            onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
            onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
            onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
            onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false); }}" />
          <div class="clearfix"></div>
          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'pie2-widget' -->
          <!-- ko if: properties.facets()[0].type() == 'range' -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: rangePieChartDataTransformer,
            maxWidth: 250,
            onClick: function(d){ searchViewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
          <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: properties.facets()[0].type() == 'range-up' -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: rangeUpPieChartDataTransformer,
            rangeUp: true,
            maxWidth: 250,
            onClick: function(d){ searchViewModel.query.selectRangeUpFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field, 'exclude': false, is_up: d.data.obj.is_up}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
          <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: properties.facets()[0].type().indexOf('range') == -1 -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: pieChartDataTransformer,
            maxWidth: 250,
            onClick: function(d){ $parent.dimension() == 2 ? $root.query.togglePivotFacet({facet: d.data.obj, widget_id: id()}) : searchViewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
          <div class="clearfix"></div>
          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'document-widget' -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART -->
          <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: $parent.results(), sorting: template.chartSettings.chartSorting(), snippet: $data, widget_id: $parent.id(), chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYSingle}, field: template.chartSettings.chartX, fqs: $root.query.fqs,
                transformer: pieChartDataTransformerGrid, maxWidth: 350, parentSelector: '.chart-container'}" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.BARCHART -->
          <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: $parent.results(), sorting: template.chartSettings.chartSorting(), snippet: $data, widget_id: $parent.id(), chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYMulti}, field: template.chartSettings.chartX, fqs: $root.query.fqs, hideSelection: true, enableSelection: false, hideStacked: template.chartSettings.hideStacked,
                transformer: multiSerieDataTransformerGrid, stacked: false, showLegend: true, type: template.chartSettings.chartSelectorType},  stacked: true, showLegend: true" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.LINECHART -->
          <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: $parent.results(), sorting: template.chartSettings.chartSorting(), snippet: $data, widget_id: $parent.id(), chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYMulti}, field: template.chartSettings.chartX, fqs: $root.query.fqs, hideSelection: true, enableSelection: false,
                transformer: multiSerieDataTransformerGrid, showControls: false}" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP -->
          <div data-bind="attr: {'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: $parent.results(), sorting: template.chartSettings.chartSorting(), snippet: $data, chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYSingle, chartZ: template.chartSettings.chartMapLabel},
                transformer: leafletMapChartDataTransformerGrid, showControls: false, height: 380, forceRedraw: true,
                showMoveCheckbox: false, moveCheckboxLabel: '${ _ko('Search as I move the map') }'}" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART -->
          <div data-bind="attr:{'id': 'timelineChart_'+id()}, timelineChart: {datum: {counts: $parent.results(), sorting: template.chartSettings.chartSorting(), snippet: $data, chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYMulti, widget_id: $parent.id()}, field: template.chartSettings.chartX, fqs: $root.query.fqs, hideSelection: true, enableSelection: false, hideStacked: template.chartSettings.hideStacked,
                transformer: multiSerieDataTransformerGrid, showControls: false}" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP -->
          <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: $parent.results(), scope: template.chartSettings.chartScope(), snippet: $data, widget_id: $parent.id(), chartX: template.chartSettings.chartX, chartY: template.chartSettings.chartYSingle},
              transformer: gradientMapChartDataTransformerGrid, maxWidth: 750, isScale: true}" />
          <!-- /ko -->
          <div class="clearfix"></div>
        <!-- /ko -->

        <!-- ko if: widgetType() == 'resultset-widget' -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.PIECHART -->
          <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                transformer: pieChartDataTransformerGrid, maxWidth: 350, parentSelector: '.chart-container' }" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.BARCHART -->
          <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: $root.collection.template.chartSettings.hideStacked,
                transformer: multiSerieDataTransformerGrid, stacked: false, showLegend: true, type: $root.collection.template.chartSettings.chartSelectorType},  stacked: true, showLegend: true" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.LINECHART -->
          <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data},
                transformer: multiSerieDataTransformerGrid, showControls: false }" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.MAP -->
          <div data-bind="attr: {'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data},
                transformer: leafletMapChartDataTransformerGrid, showControls: false, height: 380, forceRedraw: true}" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART -->
          <div data-bind="attr:{'id': 'timelineChart_'+id()}, timelineChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: $root.collection.template.chartSettings.hideStacked,
                transformer: multiSerieDataTransformerGrid, showControls: false }" class="chart"></div>
          <!-- /ko -->
          <!-- ko if: $root.collection.template.chartSettings.chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP -->
          <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: $root.results(), scope: $root.collection.template.chartSettings.chartScope(), snippet: $data},
              transformer: gradientMapChartDataTransformerGrid, maxWidth: 750, isScale: true}" />
          <div class="clearfix"></div>
          <!-- /ko -->
        <!-- /ko -->
       </div>
     </div>
    </div>
  </div>
</script>


<script type="text/html" id="document-widget">
  ##<div class="widget-spinner" data-bind="visible: isLoading()">
  ##  <i class="fa fa-spinner fa-spin"></i>
  ##</div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <!-- ko with: $root.collection.getFacetById($parent.id()) -->
    <div>
##       <input type="text" class="input-medium" data-bind="value: properties.engine"/>
##       <textarea data-bind="value: properties.statement"></textarea>

      ## Get sub widget by ID
      ## <div data-bind="template: { name: function() { return widgetType(); }}" class="widget-main-section"></div>

      <span data-bind="template: { name: 'data-grid' }"></span>
    </div>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="bucket-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">

    <!-- ko with: $root.collection.getFacetById($parent.id()) -->
    <div>
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
      <div class="pull-right">
        <div data-bind="visible: canZoomIn() || canReset()" class="inline-block">
          <span class="facet-field-label">${ _('Zoom') }</span>
          <i class="fa fa-search-minus"></i>
        </div>
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canZoomIn">
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomIn">${ _('to selection') }</a>
        </div>
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px" data-bind="visible: canReset">
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut">${ _('reset') }</a>
        </div>
        <!-- ko if: properties.canRange -->
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px">
          <span class="facet-field-label">${ _('Chart Type') }</span>
          <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
          </select>
        </div>
        <!-- /ko -->
      </div>
      <div class="clearfix"></div>
    </div>

    <span data-bind="template: { name: 'data-grid' }"></span>
   <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="line-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px" data-bind="visible: counts.length > 0">
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
    </div>
    <div style="position: relative;">
    <div data-bind="lineChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, field: field, label: label(),
      transformer: lineChartDataTransformer,
      onClick: function(d){ searchViewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onSelectRange: function(from, to){ searchViewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); huePubSub.publish('gridster.autoheight'); }}"
    />
    </div>
    <div class="clearfix"></div>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="pie-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'range' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: rangePieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ searchViewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
      <div class="clearfix"></div>
      <!-- /ko -->
      <!-- ko if: type() == 'range-up' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: rangeUpPieChartDataTransformer,
        rangeUp: true,
        maxWidth: 250,
        onClick: function(d){ searchViewModel.query.selectRangeUpFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field, 'exclude': false, is_up: d.data.obj.is_up}) },
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
      <div class="clearfix"></div>
      <!-- /ko -->
      <!-- ko if: type().indexOf('range') == -1 -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: pieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ searchViewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id}) },
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}" />
      <div class="clearfix"></div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="pie2-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">

    <!-- ko with: $root.collection.getFacetById($parent.id()) -->
    <div style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
      <div class="clearfix"></div>
    </div>

    <span data-bind="template: { name: 'data-grid' }"></span>
    <!-- /ko -->
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="tree-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div class="responsive-facet-toggle-section" data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div class="dimensions-header margin-bottom-10" data-bind="visible: $root.isEditing() && $data.properties.facets().length > 0">
        <span class="muted">${ _('Selected dimensions') }</span>
      </div>
      <div data-bind="foreach: $data.properties.facets, visible: $root.isEditing">
        <div class="filter-box">
          <div class="title">
            <a data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }" class="pull-right" href="javascript:void(0)">
              <i class="fa fa-times"></i>
            </a>
            <span data-bind="text: field"></span>
            &nbsp;
          </div>

          <div class="content">
            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Limit') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: limit"/>
              </span>
            </div>

            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Min Count') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: mincount"/>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="clearfix"></div>

      <!-- ko if: properties.scope() == 'tree' -->
        <div data-bind="partitionChart: {datum: {counts: $parent.counts(), widget_id: $parent.id(), label: $parent.label()},
          fqs: $root.query.fqs,
          tooltip: '${ _ko('Click to zoom, double click to select') }',
          transformer: partitionChartDataTransformer,
          onStateChange: function(state){ },
          onClick: function(d) {
            $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
          },
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}"
        />
      <div class="clearfix"></div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="tree2-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div class="responsive-facet-toggle-section" data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: properties.scope() == 'tree' -->
        <div data-bind="partitionChart: {datum: {counts: $parent.counts(), widget_id: $parent.id(), label: $parent.label()},
          fqs: $root.query.fqs,
          tooltip: '${ _ko('Click to zoom, double click to select') }',
          transformer: partitionChartDataTransformer,
          onStateChange: function(state){ },
          onClick: function(d) {
            $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
          },
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}"
        />
      <div class="clearfix"></div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="heatmap-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div class="floating-facet-toggle-section" data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div class="dimensions-header margin-bottom-10" data-bind="visible: $root.isEditing() && $data.properties.facets().length > 0">
        <span class="muted">${ _('Selected dimension') }</span>
      </div>
      <div data-bind="foreach: $data.properties.facets, visible: $root.isEditing">
        <div class="filter-box">
          <div class="title">
            <a data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }" class="pull-right" href="javascript:void(0)">
              <i class="fa fa-times"></i>
            </a>
            <span data-bind="text: field"></span>
            &nbsp;
          </div>

          <div class="content">
            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Limit') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: limit"/>
              </span>
            </div>
            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Min Count') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: mincount"/>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="clearfix"></div>

      <!-- ko if: properties.scope() == 'stack' -->
        <div style="position: relative;">
        <div data-bind="barChart: {datum: {counts: $parent.counts(), widget_id: $parent.id(), label: $parent.label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(),
          isPivot: true,
          enableSelection: true,
          hideSelection: true,
          fqs: $root.query.fqs,
          slot: $root.collection.getFacetById($parent.id()).properties.slot,
          transformer: pivotChartDataTransformer,
          onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
          onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
          onClick: function(d) {
            $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
          },
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false); }}"
        />
        </div>
      <div class="clearfix"></div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="hit-widget">
  <div class="widget-spinner" data-bind="visible: !$root.hasRetrievedResults()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>

      % if HAS_WIDGET_FILTER.get():
      <div class="pull-right">
        <span data-bind="visible: $root.collection.supportAnalytics(), template: { name: 'facet-filter', data: properties.filter }"></span>
        <span data-bind="visible: $root.collection.supportAnalytics() && $root.availableDateFields().length > 0, template: { name: 'facet-compare', data: properties.compare }"></span>
      </div>
      % endif
    </div>

    <!-- ko if: $root.collection.getFacetById($parent.id()) -->
    <span class="big-counter" data-bind="template: { name: 'counter-form', data: {counts: counts(), properties: $root.collection.getFacetById($parent.id()).properties }}"></span>
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="facet-filter">
  <label>
    <input type="checkbox" data-bind="checked: is_enabled"/> ${ _('Filter') }
  </label>

  <!-- ko if: is_enabled -->
  <div class="facet-field-cnt">
    <span class="spinedit-cnt">
      <span class="facet-field-label">
        ${ _('Query') }
      </span>
      <div data-bind="component: { name: 'hue-simple-ace-editor', params: {
        value: query,
        onExec: $parent.searchBtn,
        placeHolder: $root.collection.engine() === 'solr' ? '${ _ko('Example: field:value, or press CTRL + space') }' : '${ _ko('Example: col = value, or press CTRL + space') }',
        autocomplete: { type: $root.collection.engine() + 'Query', support: { collection: $root.collection } },
        mode: $root.collection.engine(),
        fixedPrefix: $root.collection.engine() !== 'solr' ? function() { return 'SELECT * FROM ' +  $root.collection.name() + ' WHERE '; } : undefined,
        fixedPostfix: $root.collection.engine() !== 'solr' ? function() { return ' GROUP BY 1;' } : undefined,
        namespace: $root.collection.activeNamespace,
        compute: $root.collection.activeCompute,
        database: function () { return $root.collection.name().split('.')[0] },
        singleLine: true }
      }"></div>
    </span>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="counter-form">
  <i class="fa" data-bind="visible: properties.compare.is_enabled, css: { 'fa-caret-down': counts < 0, 'fa-caret-up': counts > 0 }"></i>

  <span data-bind="textSqueezer: counts.value, visible: !properties.compare.use_percentage() || properties.compare.show_both()"></span>

  <span data-bind="visible: properties.compare.use_percentage">
    <span data-bind="textSqueezer: counts.percentage"></span> ${ '%' }
  </span>
</script>


<script type="text/html" id="facet-compare">
  <label>
    <input type="checkbox" data-bind="checked: is_enabled"/> ${ _('Compare') }
  </label>

  <!-- ko if: is_enabled -->
  <div class="facet-field-cnt">
    <span class="spinedit-cnt">
      <span class="facet-field-label">
        ${ _('Cohorts') }
      </span>
      <span data-bind="template: {name: 'time-filter-select', data: {gap: gap} }"></span>
      ## <input type="number" class="input-xsmall" data-bind="value: cohort_number"/>
    </span>
  </div>

  <div class="facet-field-cnt">
    <span class="spinedit-cnt">
      <label>
        <span class="facet-field-label">
          ${ _('Percentage') }
        </span>
        <input type="checkbox" data-bind="checked: use_percentage"/>
      </label>
      <label>
        <span class="facet-field-label">
          ${ _('Both values') }
        </span>
        <input type="checkbox" data-bind="checked: show_both, enable: use_percentage"/>
      </label>
    </span>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="metric-form">
    <!-- ko if: typeof isEditing !== 'undefined' && isEditing() -->
    <div>
      <!-- ko if: typeof $parents[0].isAdding === 'undefined' || !$parents[0].isAdding() -->
      <a href="javascript:void(0)" data-bind="toggle: isEditing" class="pull-right"><i class="fa fa-times inactive-action"></i></a>
      <!-- /ko -->
      <!-- ko if: typeof $parents[0].isAdding !== 'undefined' && $parents[0].isAdding() -->
      <a href="javascript:void(0)" data-bind="toggle: $parents[0].isAdding" class="pull-right"><i class="fa fa-times inactive-action"></i></a>
      <!-- /ko -->
      <!-- ko with: aggregate -->
      <select data-bind="selectize: metrics, optionsText: 'label', optionsValue: 'value', value: $data.function, disable: $parents[1].widgetType() != 'hit-widget' && (typeof $index != 'undefined' && $index() == 0)" class="input-small"></select>

      <!-- ko if: $data.function() == 'percentile' -->
      <input type="number" class="input-mini" data-bind="value: percentile"/>
      <!-- /ko -->

      <!-- ko if: $data.function() != 'formula' -->
      <select data-bind="selectize: facetFieldsNames, value: $parent.field, optionsValue: 'name', optionsText: 'name', optionsCaption: '${ _ko('Field...') }'" class="hit-options input-small" style="margin-bottom: 0"></select>
        <!-- ko if: $parent.field -->
        <a class="inactive-action context-popover-icon" href="javascript:void(0);" data-bind="sqlContextPopover: { sourceType: 'solr', namespace: $root.collection.activeNamespace(), compute: $root.collection.activeCompute(), path: 'default.' + $root.collection.name() + '.' + $parent.field()  }">
          <i class="fa fa-fw fa-info" title="${_('Show Details')}"/>
        </a>
        <!-- /ko -->
      <!-- /ko -->

      <div class="clearfix"></div>
      <br/>

      <div data-bind="component: { name: 'hue-simple-ace-editor', params: { value: plain_formula, parsedValue: formula, autocomplete: { type: 'solrFormula', support: { fields: $root.collection.template.fieldsAttributes } }, singleLine: true, mode: $root.collection.engine() } }, visible: $data.function() == 'formula'" class="margin-bottom-10" style="min-width: 300px"></div>

      <!-- ko if: $parents[1].widgetType() != 'hit-widget' -->
        <div class="facet-field-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">${ _('Sorting') }</span>
          <a href="javascript: void(0)" title="${ _('Toggle sort order') }" data-bind="click: function() { $root.collection.toggleSortFacet2($parents[1], $parent); }">
            <i class="fa" data-bind="css: { 'fa-caret-down': $parent.sort() == 'desc', 'fa-caret-up': $parent.sort() == 'asc', 'fa-sort': $parent.sort() == 'default' }"></i>
            <span data-bind="visible: $parent.sort() == 'desc'">${_('descending')}</span>
            <span data-bind="visible: $parent.sort() == 'asc'">${_('ascending')}</span>
            <span data-bind="visible: $parent.sort() == 'default'">${_('default')}</span>
          </a>
        </div>

        <div class="facet-field-cnt" data-bind="visible: $data.function() == 'count' && !$parent.canRange() && $root.collection.engine() == 'solr'">
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Limit') }
            </span>
            <input type="text" class="input-medium" data-bind="spinedit: $parent.limit"/>
          </span>
        </div>

##        <div class="facet-field-cnt" data-bind="visible: $data.function() == 'count'">
##          <span class="spinedit-cnt">
##            <span class="facet-field-label facet-field-label-fixed-width">
##              ${ _('Min Count') }
##            </span>
##            <input type="text" class="input-medium" data-bind="spinedit: $parent.mincount"/>
##          </span>
##        </div>

##        <!-- ko if: $parentContext.$data.type() == 'field' && $parents[1].widgetType() != 'timeline-widget' && $parents[1].widgetType() != 'gradient-map-widget' && $parents[1].widgetType() != 'leafletmap-widget' && $parents[1].widgetType() != 'tree2-widget' -->
##          <div class="facet-field-cnt" data-bind="visible: $parent == $parentContext.$parentContext.$data.properties.facets()[0] && $root.collection.engine() == 'solr'"> <!-- visible on first element only -->
##            <span class="spinedit-cnt">
##              <span class="facet-field-label facet-field-label-fixed-width">
##                ${ _('Other') }
##              </span>
##              <input type="checkbox" data-bind="checked: $parent.missing"/>
##            </span>
##          </div>
##        <!-- /ko -->

        <!-- ko if: $parentContext.$data.type() == 'field' -->
        <div class="facet-field-cnt" data-bind="visible: $parent == $parentContext.$parentContext.$data.properties.facets()[0]"> <!-- visible on first element only -->
          <span class="spinedit-cnt">
            <span class="facet-field-label facet-field-label-fixed-width">
              ${ _('Multi select') }
            </span>
            <input type="checkbox" data-bind="checked: $parent.multiselect"/>
          </span>
        </div>
        <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $parent.widgetType() != 'hit-widget' -->
      <!-- ko if: canRange() -->
        <div class="facet-field-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">${ _('Type') }</span>
          <a href="javascript: void(0)" title="${ _('Toggle how to group the values') }" data-bind="click: $root.collection.toggleRangeFacet2">
            <i class="fa" data-bind="css: { 'fa-arrows-h': type() == 'range', 'fa-circle': type() == 'field', 'fa-level-up': type() == 'range-up' }, attr: { title: type() == 'field' ? 'Range' : type() == 'range-up' ? 'Range and up' : 'Term' }"></i>
            <span data-bind="visible: type() == 'range'">${_('range')}</span>
            <span data-bind="visible: type() == 'range-up'">${_('range & up')}</span>
            <span data-bind="visible: type() == 'field'">${_('field')}</span>
          </a>
        </div>

        <!-- ko ifnot: isDate() -->
          <div class="slider-cnt" data-bind="slider: {start: min, end: max, gap: initial_gap, min: initial_start, max: initial_end, properties: $data, labels: SLIDER_LABELS}"></div>
        <!-- /ko -->

        <!-- ko if: isDate() && $root.collection.timeFilter && $root.collection.timeFilter.field && $root.collection.timeFilter.field() != field() -->
          <div data-bind="dateRangePicker: {start: start, end: end, gap: initial_gap, relatedgap: gap, min: min, max: max}"></div>
        <!-- /ko -->

        <!-- /ko -->
        <!-- /ko -->


        <!-- ko if: typeof $parents[0].isAdding === 'undefined' || !$parents[0].isAdding() -->
        <a href="javascript: void(0)" class="pull-right" data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }, visible: $parent.properties.facets().length > 1">
          <i class="fa fa-trash"></i> ${ _('Remove') }
        </a>
        <!-- /ko -->
        <!-- ko if: typeof $parents[0].isAdding !== 'undefined' && $parents[0].isAdding() -->
        <a data-bind="visible: aggregate.function() != 'formula' || aggregate.formula(), click: function() { $root.collection.addPivotFacetValue2($parents[0]) }" class="pull-right" href="javascript:void(0)">
          <i class="fa fa-plus"></i> ${ _('Add') }
        </a>
        <!-- /ko -->
        <div class="clearfix"></div>
      </div>
    <!-- /ko -->
</script>


<script type="text/html" id="filter-widget">
  <div data-bind="visible: $root.query.fqs().length == 0" style="margin-top: 10px; min-height: 87px">
    ${ _('There are currently no filters applied.') }
  </div>
  <div data-bind="foreach: { data: $root.query.fqs, afterRender: function(){ isLoading(false); } }">
    <!-- ko if: $data.type() == 'field' -->
    <div class="filter-box">
      <div class="title">
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function() { huePubSub.publish('charts.state', { updating: true }); $root.query.removeFilter($data); $root.search(); }">
          <i class="fa fa-times"></i>
        </a>
        <span data-bind="text: $data.field"></span>
        &nbsp;
      </div>
      <div class="content">
        <strong>${_('selected')}</strong>
        <span data-bind="foreach: $data.filter">
          <span class="label label-info" style="margin-left: 4px" data-bind="visible: !$data.exclude(), html: prettifyDate($data.value()), attr: {'title': $data.value()}"></span>
        </span>
        <br/>
        <strong>${_('excluded')}</strong>
        <span data-bind="foreach: $data.filter">
          <span class="label label-important" style="margin-left: 4px" data-bind="visible: $data.exclude(), html: prettifyDate($data.value()), attr: {'title': $data.value()}"></span>
        </span>
      </div>
    </div>
    <!-- /ko -->

    <!-- ko if: $data.type() == 'range' || $data.type() == 'range-up' -->
    <div class="filter-box">
      <div class="title">
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ huePubSub.publish('charts.state', { updating: true }); $root.query.removeFilter($data); $root.search() }">
          <i class="fa fa-times"></i>
        </a>
        <span data-bind="text: $data.field"></span>
        &nbsp;
      </div>
      <div class="content">
        <strong>${_('selected')}</strong>
        <span data-bind="foreach: $data.properties" style="font-weight: normal">
          <!-- ko if: $.grep($parent.filter(), function(f) { return f.value() == $data.from() && ! f.exclude() }).length > 0 -->
          <span class="label label-info">
            <!-- ko if: $parent.type() == 'range' -->
              <span data-bind="html: prettifyDateRange($data.from(), $data.to(), null, true), attr: {'title': $data.from() + ' -> ' + $data.to()}"></span>
            <!-- /ko -->

            <!-- ko if: $parent.type() == 'range-up' -->
              <strong data-bind="visible: !$parent.is_up()">${ _('Until') }</strong>
              <span data-bind="html: prettifyDate($data.from()), attr: {'title': $data.from()}"></span>
              <strong data-bind="visible: $parent.is_up()"> & Up</strong>
            <!-- /ko -->
          </span>
          <!-- /ko -->
        </span>
        <br/>
        <strong>${_('excluded')}</strong>
        <span data-bind="foreach: $data.properties" style="font-weight: normal" class="excluded">
          <!-- ko if: $.grep($parent.filter(), function(f) { return f.value() == $data.from() && f.exclude() }).length > 0 -->
          <span class="label label-important">
            <span data-bind="html: prettifyDateRange($data.from(), $data.to(), null, true), attr: {'title': $data.from() + ' -> ' + $data.to()}"></span>
          </span>
          <!-- /ko -->
        </span>
      </div>
    </div>
    <!-- /ko -->

    <!-- ko if: $data.type() == 'map' -->
    <div class="filter-box">
      <div class="title">
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ huePubSub.publish('charts.state', { updating: true }); $root.query.removeFilter($data); $root.search() }">
          <i class="fa fa-times"></i>
        </a>
        <span data-bind="text: $data.lat"></span>, <span data-bind="text: $data.lon"></span>
        &nbsp;
      </div>
      <div class="content">
        <strong>${_('selected')}</strong>
        <span class="label label-info">
          [
          <span class="label label-info" style="margin-left: 4px" data-bind="text: $data.properties.lat_sw, attr: {'title': '${ _ko('Latitude South West') }'"></span>
          <span class="label label-info" style="margin-left: 4px" data-bind="text: $data.properties.lon_sw, attr: {'title': '${ _ko('Longitude South West') }'"></span>
          ]
          ${ _("TO") }
          [
          <span class="label label-info" style="margin-left: 4px" data-bind="text: $data.properties.lat_ne, attr: {'title': '${ _ko('Latitude North East') }'"></span>
          <span class="label label-info" style="margin-left: 4px" data-bind="text: $data.properties.lon_ne, attr: {'title': '${ _ko('Longitude North East') }'"></span>
          ]
        </span>
      </div>
    </div>
    <!-- /ko -->

  </div>
  <div class="clearfix"></div>
  <div class="widget-spinner" data-bind="visible: isLoading() &&  $root.query.fqs().length > 0">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="map-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <div class="floating-facet-toggle-section">
        <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
        </span>
      </div>
      <div class="dimensions-header margin-bottom-10" data-bind="visible: $root.isEditing() && $data.properties.facets().length > 0">
        <span class="muted">${ _('Selected dimension') }</span>
      </div>
      <div data-bind="foreach: $data.properties.facets, visible: $root.isEditing">
        <div class="filter-box">
          <div class="title">
            <a data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }" class="pull-right" href="javascript:void(0)">
              <i class="fa fa-times"></i>
            </a>
            <span data-bind="text: field"></span>
            &nbsp;
          </div>

          <div class="content">
            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Limit') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: limit"/>
              </span>
            </div>

            <div class="facet-field-cnt">
              <span class="spinedit-cnt">
                <span class="facet-field-label facet-field-label-fixed-width">
                  ${ _('Min Count') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: mincount"/>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="clearfix"></div>
    </div>

    <div class="margin-bottom-10" data-bind="visible: !$root.isEditing()">
      <div data-bind="with: $root.collection.getFacetById($parent.id())">
        <!-- ko if: $data.properties.facets().length == 1 -->
          <div class="margin-bottom-10">
            <span data-bind="text: $data.properties.facets()[0].field"></span>
          </div>
        <!-- /ko -->
      </div>
    </div>

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div data-bind="mapChart: {data: {counts: $parent.counts(), scope: $root.collection.getFacetById($parent.id()).properties.scope()},
        transformer: mapChartDataTransformer,
        maxWidth: 750,
        isScale: true,
        onClick: function(d) {
          $root.query.togglePivotFacet({facet: {'fq_fields': d.fields, 'fq_values': d.value}, widget_id: id()});
        },
        onComplete: function(){ var widget = searchViewModel.getWidgetById($parent.id()); if (widget != null) { widget.isLoading(false)}; } }" />
      <div class="clearfix"></div>
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="gradient-map-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
      <div class="clearfix"></div>
    </div>

    <!-- ko with: $root.collection.getFacetById($parent.id()) -->
      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label facet-field-label-fixed-width">
            ${ _('Scope') }
          </span>
          <select data-bind="selectedOptions: properties.scope" class="input-small">
            <option value="world">${ _("World") }</option>
            <option value="europe">${ _("Europe") }</option>
            <option value="aus">${ _("Australia") }</option>
            <option value="bra">${ _("Brazil") }</option>
            <option value="can">${ _("Canada") }</option>
            <option value="chn">${ _("China") }</option>
            <option value="fra">${ _("France") }</option>
            <option value="deu">${ _("Germany") }</option>
            <option value="ita">${ _("Italy") }</option>
            <option value="jpn">${ _("Japan") }</option>
            <option value="gbr">${ _("UK") }</option>
            <option value="usa">${ _("USA") }</option>
          </select>
        </span>
      </div>

      <div class="margin-bottom-10" data-bind="visible: !$root.isEditing()">
        <!-- ko if: $data.properties.facets().length == 2 -->
          <div class="margin-bottom-10">
            <span data-bind="text: $data.properties.facets()[1].field"></span>
          </div>
        <!-- /ko -->
      </div>

      <span data-bind="template: { name: 'data-grid' }"></span>
    <!-- /ko -->
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="leafletmap-widget">
  <div class="row-fluid">
    <div data-bind="visible: $root.isEditing" style="margin-top: 10px; margin-bottom: 20px;" class="leaflet-align">
      <span class="facet-field-label">${_('Latitude')}</span><div class="break-on-small-column"></div>
      <select data-bind="options: $root.collection.template.sortedGeogFieldsNames, value: $root.collection.template.leafletmap.latitudeField, optionsCaption: '${ _ko('Choose...') }', selectize: $root.collection.template.sortedGeogFieldsNames"></select>
      &nbsp;&nbsp;
      <div class="break-on-small-column"></div>
      <span class="facet-field-label">${_('Longitude')}</span><div class="break-on-small-column"></div>
      <select data-bind="options: $root.collection.template.sortedGeogFieldsNames, value: $root.collection.template.leafletmap.longitudeField, optionsCaption: '${ _ko('Choose...') }', selectize: $root.collection.template.sortedGeogFieldsNames"></select>
      &nbsp;&nbsp;
      <div class="break-on-small-column"></div>
      <span class="facet-field-label">${_('Label')}</span><div class="break-on-small-column"></div>
      <select data-bind="value: $root.collection.template.leafletmap.labelField, optionsCaption: '${ _ko('Choose...') }', selectize: $root.collection.template.fieldsNames"></select>
    </div>

    <div data-bind="leafletMapChart: {showMoveCheckbox: true, moveCheckboxLabel: '${ _ko('Search as I move the map') }', visible: $root.hasRetrievedResults() && $root.collection.template.leafletmapOn(), isLoading: isLoading(), datum: {counts: $root.response()},
      transformer: leafletMapChartDataTransformer,
      onRegionChange: function(bounds){ $root.query.selectMapRegionFacet({widget_id: id(), 'bounds': ko.toJS(bounds, null, 2), lat: $root.collection.template.leafletmap.latitudeField(), lon: $root.collection.template.leafletmap.longitudeField()}); },
      onComplete: function(){ var widget = searchViewModel.getWidgetById(id()); if (widget != null) { widget.isLoading(false)}; } }">
    </div>
    <div class="clearfix"></div>
  </div>

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>
</script>


<script type="text/html" id="analysis-window">
  <!-- ko if: $root.fieldAnalysesName() -->
  <div data-bind="with: $root.getFieldAnalysis()">
    <div class="pull-right">
      <input type="text" data-bind="visible: section() == 'terms', clearable: terms.prefix, valueUpdate:'afterkeydown'" placeholder="${ _('Prefix filter...') }"/>
      <input type="text" data-bind="visible: section() == 'stats', clearable: stats.facet, typeahead: { target: stats.facet, source: $root.fieldsAnalysisAttributesNames, triggerOnFocus: true }" placeholder="${ _('Field name...') }"/>
    </div>
    <ul class="nav nav-tabs" role="tablist">
      <li class="active"><a href="#analysis-terms" role="tab" data-toggle="tab" data-bind="click: function() { section('terms'); }">${ _('Terms') }</a></li>
      <li><a href="#analysis-stats" role="tab" data-toggle="tab" data-bind="click: function() { section('stats'); }">${ _('Stats') }</a></li>
    </ul>
    <div class="tab-content" style="max-height: 370px; height: 370px">
      <div class="tab-pane active" id="analysis-terms" data-bind="with: terms">
        <div class="widget-spinner" data-bind="visible: $parent.isLoading()">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <div class="alert" data-bind="visible: !$parent.isLoading() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
        <table style="width: 100%" data-bind="visible: !$parent.isLoading() && $data.data().length > 0" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td data-bind="text: val.value"></td>
            <td style="width: 22px" data-bind="click: $root.query.addSingleTermFacet">
              <a href="javascript: void(0)"><i class="fa fa-plus" title="${ _('Select this value') }"></i></a>
            </td>
            <td style="width: 22px" data-bind="click: $root.query.removeSingleTermFacet">
              <a href="javascript: void(0)"><i class="fa fa-minus" title="${ _('Exclude this value') }"></i></a>
            </td>
            <td style="width: 40px">
              <div class="progress">
                <div class="bar-label" data-bind="text:val.count"></div>
                <div class="bar bar-info" style="margin-top:-20px;" data-bind="style: {'width': ((val.count / $parent.data()[0].val.count) * 100) + '%'}"></div>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="tab-pane" id="analysis-stats" data-bind="with: stats">
        <div class="widget-spinner" data-bind="visible: $parent.isLoading()">
          <i class="fa fa-spinner fa-spin"></i>
        </div>
        <div class="alert" data-bind="visible: !$parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() == 'error'">${ _('This field does not support stats') }</div>
        <div class="alert" data-bind="visible: !$parent.isLoading() && $data.data().length == 0">${ _('There are no stats to be shown') }</div>
        <table style="width: 100%" data-bind="visible: !$parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() != 'error'" class="table table-condensed">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td style="vertical-align: top"><strong data-bind="text: key"></strong></td>
            <!-- ko if: key == 'facets' -->
            <td>
              <!-- ko if: val[Object.keys(val)[0]] != null -->
              <table style="width: 400px">
                <tbody data-bind="foreach: Object.keys(val[Object.keys(val)[0]])">
                  <tr>
                    <td style="vertical-align: top; padding-left: 4px; padding-right: 4px"><strong data-bind="text: $data"></strong></td>
                    <td data-bind="template: 'stats-facets'"></td>
                  </tr>
                </tbody>
              </table>
              <!-- /ko -->
              <!-- ko ifnot: val[Object.keys(val)[0]] != null -->
              ${ _('Not available') }
              <!-- /ko -->
            </td>
            <!-- /ko -->
            <!-- ko ifnot: key == 'facets' -->
            <td data-bind="text: val"></td>
            <!-- /ko -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="stats-facets">
  <table style="width: 100%">
    <tbody data-bind="foreach: Object.keys($parent.val[Object.keys($parent.val)[0]][$data])">
      <tr>
        <td style="vertical-align: top; padding-left: 4px; padding-right: 4px"><strong data-bind="text: $data"></strong></td>
        <!-- ko ifnot: $data == 'facets' -->
        <td style="vertical-align: top" data-bind="text: $parents[1].val[Object.keys($parents[1].val)[0]][$parent][$data]"></td>
        <!-- /ko -->
      </tr>
    </tbody>
  </table>
</script>

<div id="addFacetDemiModal" class="demi-modal fade" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" data-bind="click: addFacetDemiModalFieldCancel" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 10px;">
      <!-- ko component: {
        name: 'inline-autocomplete',
        params: {
          querySpec: $root.collection.template.fieldsModalFilter,
          facets: ['type'],
          knownFacetValues: $root.collection.engine() === 'solr' ? SOLR_ASSIST_KNOWN_FACET_VALUES : SQL_ASSIST_KNOWN_FACET_VALUES,
          autocompleteFromEntries: $root.collection.template.autocompleteFromFieldsModalFilter
        }
      } --><!-- /ko -->
##       <input id="addFacetInput" type="text" data-bind="clearable: $root.collection.template.fieldsModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.collection.template.filteredModalFields().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.collection.template.filteredModalFields().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li data-bind="visibleOnHover: { 'selector': '.entity-field-picker' }">
            <span class="badge badge-info" data-bind="text: name(), attr: {'title': type()}, click: addFacetDemiModalFieldPreview"></span>
            <a class="entity-field-picker inactive-action margin-right-10" href="javascript:void(0);" data-bind="sqlContextPopover: { sourceType: 'solr', namespace: $root.collection.activeNamespace(), compute: $root.collection.activeCompute(), path: 'default.' + $root.collection.name() + '.' + name()  }" style="margin-left: 2px;">
              <i class="fa fa-info" title="${_('Show Details')}"/>
            </a>
        </li>
      </ul>
      <div class="alert alert-info inline" data-bind="visible: $root.collection.template.filteredModalFields().length == 0" style="margin-left: 250px; margin-right: 50px; height: 42px;line-height: 42px">
        ${_('There are no fields matching your search term.')}
      </div>
    </div>
  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal" data-bind="click: addFacetDemiModalFieldCancel"><i class="fa fa-chevron-up"></i></a></div>
</div>

<div id="addDocumentFacetDemiModal" class="demi-modal fade" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" data-bind="click: addFacetDemiModalFieldCancel" class="pull-right"><i class="fa fa-times"></i></a>
    <div class="demi-modal-label">${ _('Query') }</div>
    <div class="selectize-wrapper selectize-400">
      <select placeholder="${ _('Search your queries...') }" data-bind="documentChooser: { value: $root.tempDocument.uuid, type: 'impala' }"></select>
    </div>
    <!-- ko if: $root.tempDocument.parsedStatements && $root.tempDocument.parsedStatements().length > 1 -->
      <div class="demi-modal-label">${ _('Statement') }</div>
      <div class="selectize-wrapper selectize-400">
        <select placeholder="${ _('Available statements') }" class="temp-document-statement" data-bind="selectize: $root.tempDocument.parsedStatements, optionsText: 'statement', optionsValue: 'statement', value: $root.tempDocument.selectedStatement"></select>
      </div>
    <!-- /ko -->
    <a class="btn btn-primary disable-feedback" data-bind="publish: 'dashboard.confirm.document'">${ _('Confirm') }</a>
  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal" data-bind="click: addFacetDemiModalFieldCancel"><i class="fa fa-chevron-up"></i></a></div>
</div>


<div id="settingsDemiModal" class="demi-modal fade" data-backdrop="false">
  <a href="javascript: void(0)" data-dismiss="modal" class="pull-right" style="margin: 10px"><i class="fa fa-times"></i></a>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="span12">
        <form class="form-horizontal">
          <fieldset>
            <legend><i class="fa fa-cogs"></i> ${ _('General settings') }</legend>
            <!-- ko if: $root.initial.inited() -->

            <!-- ko if: $root.collection.engine() == 'solr' -->
            <div class="control-group">
              <label class="control-label" for="settingssolrindex">${ _('Solr index') }</label>
              <div class="controls">
                <div data-bind="component: { name: 'hue-drop-down', params: { value: $root.collection.name, entries: $root.initial.collections.sort(), searchable: true, linkTitle: '${ _ko('Solr index') }' } }" style="display: inline-block; padding-top: 6px;"></div>
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: $root.collection.engine() != 'solr' -->
            <div class="control-group">
              <label class="control-label" for="settingssolrindex">${ _('Solr index') }</label>
              <div class="controls">
                <input type="text" class="no-margin" data-bind="hiveChooser: $root.collection.name, skipColumns: true, apiHelperUser: '${ user }', apiHelperType: $root.collection.engine()" placeholder="${ _('Table name or <database>.<table>') }">
              </div>
            </div>
            <!-- /ko -->

            <div class="control-group">
              <label class="control-label" for="settingsdescription">${ _('Description') }</label>
              <div class="controls">
                <input id="settingsdescription" type="text" class="input-xlarge" data-bind="textInput: $root.collection.description, tagsNotAllowed" style="margin-bottom: 0" />
              </div>
            </div>

            ## Potentially useful for regular search and not analytic search
            ##<!-- ko if: $root.collection.engine() == 'solr' -->
            ##<div class="control-group">
            ##  <label class="control-label">${ _('Autocomplete') }</label>
            ##  <div class="controls">
            ##    <label class="checkbox" style="padding-top:0">
            ##      <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.suggest.enabled">
            ##      <span data-bind="visible: $root.collection.suggest.enabled">
            ##        ${ _('Dictionary') } <input type="text" class="input-xlarge" style="margin-bottom: 0; margin-left: 6px;" data-bind="textInput: $root.collection.suggest.dictionary, tagsNotAllowed" placeholder="${ _('Dictionary name or blank for default') }">
            ##      </span>
            ##    </label>
            ##  </div>
            ##</div>
            <div class="control-group">
              <label class="control-label">
                ${ _('Auto-refresh') }
              </label>
              <div class="controls">
              <label class="checkbox inline-block">
                <input type="checkbox" data-bind="checked: $root.collection.autorefresh"/> ${ _('every') } <input type="number" class="input-mini" data-bind="textInput: $root.collection.autorefreshSeconds, enable: $root.collection.autorefresh"/> ${ _('seconds') }
              </label>
              </div>
            </div>
            <!-- ko if: $root.collection.supportAnalytics -->
            <div class="control-group">
              <label class="control-label">${ _('Nested documents') }</label>
              <div class="controls">
                <label class="checkbox" style="padding-top:0">
                  <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.nested.enabled"/>
                  <span data-bind="visible: $root.collection.nested.enabled">
                    ${ _('Schema') }
                    <span data-bind="template: {name: 'nested-document-schema-level', data: $root.collection.nested.schema()}"></span>
                  </span>
                </label>
              </div>
            </div>
            <!-- /ko -->
            <!-- /ko -->
          </fieldset>
        </form>
      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>

<div id="qdefinitionsDemiModal" class="demi-modal fade" data-backdrop="false">
  <a href="javascript: void(0)" data-dismiss="modal" class="pull-right" style="margin: 10px"><i class="fa fa-times"></i></a>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="span12">
        <form class="form-inline">
          <fieldset>
            <legend><i class="fa fa-bookmark-o"></i> ${ _('Query definitions') }
              <div class="input-append" style="margin-left: 30px; margin-top: 4px">
                <input id="newqname" type="text" class="input-xxlarge" data-bind="textInput: $root.collection.newQDefinitionName, valueUpdate:'afterkeydown', tagsNotAllowed" style="margin-bottom: 0" placeholder="${ _('Add current query as...') }" />
                <a title="${ _('Click on this button to add the current query as a new definition') }" class="btn plus-btn" data-bind="click: $root.collection.addQDefinition, css: {'disabled': $.trim($root.collection.newQDefinitionName()) == ''}" style="margin-top: 1px">
                  <i class="fa fa-plus"></i>
                </a>
              </div>
            </legend>
            <div class="control-group" data-bind="visible: $root.collection.qdefinitions().length > 0" style="margin-top: 0">
              <div class="controls">
                <ul class="unstyled airy qdefinitions" data-bind="foreach: $root.collection.qdefinitions">
                  <li>
                    <span class="badge badge-info badge-left pointer">
                      <span data-bind="text: name, attr:{'title': ko.mapping.toJSON(data, null, 2)}, click: $root.collection.loadQDefinition"></span>
                    </span><span class="badge badge-right trash-share" data-bind="click: $root.collection.removeQDefinition"> <i class="fa fa-times"></i></span>
                  </li>
                </ul>
              </div>
            </div>
            <div class="control-group" data-bind="visible: $root.collection.qdefinitions().length == 0">
              <div class="controls">
                <h4>${ _('There are currently no query definitions.') }</h4>
              </div>
            </div>
          </fieldset>

        </form>
      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>


<script type="text/html" id="nested-document-schema-level">
  <ul class="unstyled airy" data-bind="foreach: $data">
    <li>
      <input type="text" data-bind="value: filter" placeholder="e.g. type_s:books"/>
      <input type="checkbox" data-bind="checked: selected"/>
      <!-- ko if: values().length == 0 -->
        <a data-bind="click: function() { $root.collection.nestedAddLeaf(values); }" href="javascript:void(0)">
          <i class="fa fa-plus"></i>
        </a>
        <a data-bind="click: function() { $parent.pop($data); $root.collection.nested.schema.valueHasMutated(); }" href="javascript:void(0)">
          <i class="fa fa-minus"></i>
        </a>
      <!-- /ko -->
      <!-- ko if: values().length > 0 -->
        <span data-bind="template: {name: 'nested-document-schema-level', data: values()}"></span>
      <!-- /ko -->
    </li>
  </ul>
    <a data-bind="click: function() { $root.collection.nestedAddLeaf($data); $root.collection.nested.schema.valueHasMutated(); }" href="javascript:void(0)">
      <i class="fa fa-plus"></i> ${ _('Level') }
    </a>
    <br/>
</script>


<script type="text/html" id="time-filter">
  <span data-bind="visible: $root.availableDateFields().length > 0" >
    <span data-bind="template: {name: 'time-filter-select', data: {gap: collection.timeFilter.value} }"></span>
    <a class="btn pointer" title="${ _('Time Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#timeSettingsDemiModal">
      <i class="fa fa-calendar"></i>
    </a>
  </span>
</script>


<script type="text/html" id="time-fixed-filter">
  <span data-bind="visible: $root.availableDateFields().length > 0" class="muted" title="${ _('Time Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#timeSettingsDemiModal" style="cursor:pointer">
    &nbsp;
    <span data-bind="text: moment($root.collection.timeFilter.from()).utc().format('YYYY-MM-DD HH:mm:SS')"></span>
    <i class="fa fa-long-arrow-right"></i>
    <span data-bind="text: moment($root.collection.timeFilter.to()).utc().format('YYYY-MM-DD HH:mm:SS')"></span>
  </span>
</script>


<script type="text/html" id="time-filter-select">
  <select data-bind="value: $data.gap" class="input-small" style="margin-right: 4px">
    <option value="all">${ _('All') }</option>
    <option value="5MINUTES">${ _('Past 5 Minutes') }</option>
    <option value="30MINUTES">${ _('Past 30 Minutes') }</option>
    <option value="1HOURS">${ _('Past 1 Hour') }</option>
    <option value="12HOURS">${ _('Past 12 Hours') }</option>
    <option value="1DAYS">${ _('Past day') }</option>
    <option value="2DAYS">${ _('Past 2 days') }</option>
    <option value="7DAYS">${ _('Past 7 days') }</option>
    <option value="1MONTHS">${ _('Past 1 Month') }</option>
    <option value="3MONTHS">${ _('Past 3 Months') }</option>
    <option value="1YEARS">${ _('Past Year') }</option>
    <option value="2YEARS">${ _('Past 2 Years') }</option>
    <option value="10YEARS">${ _('Past 10 Years') }</option>
  </select>
</script>


<div id="timeSettingsDemiModal" class="demi-modal fade" data-backdrop="false">
  <a href="javascript: void(0)" data-dismiss="modal" class="pull-right" style="margin: 10px"><i class="fa fa-times"></i></a>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="span12">
        <form class="form-horizontal">
          <fieldset>
            <legend><i class="fa fa-calendar"></i> ${ _('Time settings') }</legend>

            <span data-bind="visible: $root.availableDateFields().length > 0">
              <div class="control-group">
                <label class="control-label">${ _('Date/time field') }</label>
                <div class="controls">
                  <select data-bind="options: $root.availableDateFields, value: collection.timeFilter.field, optionsValue: 'name'" class="input-medium"></select>
                </div>
              </div>
              <div class="control-group">
                <label class="control-label">${ _('Type') }</label>
                <div class="controls">
                  <label class="radio inline"><input type="radio" name="settingstimetype" value="rolling" data-bind="checked: collection.timeFilter.type" /> ${ _('Rolling') }</label>
                  <label class="radio inline"><input type="radio" name="settingstimetype" value="fixed" data-bind="checked: collection.timeFilter.type" /> ${ _('Fixed') }</label>
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'rolling'">
                <label class="control-label">${ _('Interval') }</label>
                <div class="controls">
                  <span data-bind="template: {name: 'time-filter-select', data: { gap: collection.timeFilter.value} }"></span>
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'fixed'">
                <label class="control-label">${ _('Start date/time') }</label>
                <div class="controls">
                  <input type="text" data-bind="value: collection.timeFilter.from, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:ss[Z]'}" />
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'fixed'">
                <label class="control-label">${ _('End date/time') }</label>
                <div class="controls">
                  <input type="text" data-bind="value: collection.timeFilter.to, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:ss[Z]'}" />
                </div>
              </div>
            </span>
          </fieldset>
        </form>

      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>

<div id="saveAsModalDashboard" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Save dashboard as...')}</h2>
  </div>

  <div class="modal-body">
    <form class="singleValued form-horizontal" onsubmit="return false">
      <div class="control-group">
        <label class="control-label">${_('Name')}</label>
        <div class="controls">
          <input type="text" class="input-xlarge" data-bind="value: collection.label, valueUpdate:'afterkeydown'"/>
        </div>
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <input type="button" class="btn btn-primary disable-feedback" value="${_('Save')}" data-dismiss="modal" data-bind="click: saveAs, enable: collection.label().length"/>
  </div>
</div>

<script type="text/html" id="nested-document-filter">
  <!-- ko if: $root.collection.supportAnalytics -->
  <span data-bind="visible: $root.collection.nested.enabled" >
    <a class="btn pointer" title="${ _('Nested schema') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal">
      <i class="fa fa-sitemap"></i>
    </a>
  </span>
  <!-- /ko -->
</script>


<div id="fieldAnalysis" class="popover mega-popover right">
  <div class="arrow"></div>
  <h3 class="popover-title" style="text-align: left">
    <a class="pull-right pointer" data-bind="click: function(){ $('#fieldAnalysis').hide(); $root.fieldAnalysesName(''); }"><i class="fa fa-times"></i></a>
    <strong data-bind="text: $root.fieldAnalysesName"></strong>
    <!-- ko if: $root.getFieldAnalysis() -->
      (<span data-bind="text: $root.getFieldAnalysis().type"></span>)
    <!-- /ko -->
  </h3>
  <div class="popover-content" data-bind="template: { name: 'analysis-window' }" style="text-align: left"></div>
</div>



## Extra code for style and custom JS
<span id="extra" data-bind="augmentHtml: $root.collection.template.extracode"></span>


<link rel="stylesheet" href="${ static('dashboard/css/search.css') }">
%if is_mobile:
<link rel="stylesheet" href="${ static('dashboard/css/search_mobile.css') }">
%endif
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.gridster.min.css') }">

${ dashboard.import_layout(True) }

% if not is_embeddable:
<script src="${ static('desktop/js/share2.vm.js') }"></script>
% endif
<script src="${ static('dashboard/js/search.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.textsqueezer.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/shortcut.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/mustache.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
<script src="${ static('dashboard/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.gridster.with-extras.min.js') }"></script>
<script src="${ static('desktop/js/gridster-knockout.js') }"></script>

${ dashboard.import_bindings() }

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get() or not is_embeddable:
  .search-bar {
    top: 58px!important;
  }
  .card-toolbar {
    top: 100px!important;
  }
  #emptyDashboardEditing {
    top: 190px!important;
  }
  .dashboard {
    margin-top: 20px;
  }
  .dashboard.with-top-margin {
    margin-top: 80px;
  }
% endif
</style>

<script type="text/javascript">

var searchViewModel;

moment.suppressDeprecationWarnings = true;

var NUMERIC_HIT_OPTIONS = [
    { value: "count", label: "${ _('Group by') }" },
    ## { value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "avg", label: "${ _('Average') }" },
    { value: "sum", label: "${ _('Sum') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" },
    { value: "median", label: "${ _('Median') }" },
    { value: "percentile", label: "${ _('Percentile') }" },
    { value: "stddev", label: "${ _('Stddev') }" },
    { value: "variance", label: "${ _('Variance') }" },
    { value: "formula", label: "${ _('Formula') }" },
];
var DATETIME_HIT_OPTIONS = [
    { value: "count", label: "${ _('Group by') }" },
    ## { value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" },
    { value: "median", label: "${ _('Median') }" },
    { value: "percentile", label: "${ _('Percentile') }" },
    { value: "formula", label: "${ _('Formula') }" },
];
var ALPHA_HIT_COUNTER_OPTIONS = [
    ##{ value: "count", label: "${ _('Group by') }" },
    ##{ value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" },
    { value: "formula", label: "${ _('Formula') }" },
];
var ALPHA_HIT_OPTIONS = [
    { value: "count", label: "${ _('Group by') }" },
    ## { value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" },
    { value: "formula", label: "${ _('Formula') }" },
];
var HIT_OPTIONS = NUMERIC_HIT_OPTIONS
;

function prepareShareModal() {
  shareViewModel.setDocUuid(this.collection.uuid());
  openShareModal();
}

function getHitOption(value) {
  for (var i=0; i < HIT_OPTIONS.length; i++){
    if (HIT_OPTIONS[i].value == value){
      return HIT_OPTIONS[i].label;
    }
  }
  return value;
}

function getPrettyMetric(facet) {
  if (facet.aggregate.function() == 'formula') {
    return facet.aggregate.plain_formula()
  } else if (facet.aggregate.function() == 'percentile') {
    return 'percentile(' + facet.aggregate.percentiles()[0]['value']() + ')';
  } else {
    return getHitOption(facet.aggregate.function());
  }
}

// if the date separator is a dot and there's no 4 digit year at either end we invalidate it because it's most likely a version
function getParsedDate(date) {
  var parsedDate = moment(date);

  if (parsedDate.isValid()) {
    var splits = date.split('.');
    if (splits.length === 3 && (splits[0].length !== 4 && splits[2].length !== 4)) {
      return moment.invalid(date);
    }
  }
  return parsedDate;
}

function prettifyDate(from, widget, to) {
  if (typeof from == "undefined" || $.isNumeric(from)) {
    return from;
  }
  if (typeof to != "undefined" && !$.isNumeric(to)) {
    return prettifyDateRange(from, to, widget);
  }
  var _mFrom = getParsedDate(from);
  if (_mFrom.isValid()) {
    var _format = "YYYY-MM-DD HH:mm:ss";
    var _minMaxDiff = 0;
    if (widget && widget.properties && widget.properties.min && widget.properties.min()) {
      _minMaxDiff = moment(widget.properties.max()).diff(moment(widget.properties.min()), 'seconds');
      if (moment(widget.properties.max()).seconds() == 0 && moment(widget.properties.min()).seconds() == 0) {
        _format = _format.substring(0, 16); // gets rid of :00 seconds
      }
    }
    _format = getFormat(_format, _minMaxDiff, widget);

    return _mFrom.utc().format(_format);
  }
  else {
    return from;
  }
}

function prettifyDateRange(from, to, widget, withCommon) {
  if (typeof from == "undefined" || $.isNumeric(from)) {
    return from + " - " + to;
  }
  var _mFrom = moment(from);
  var _mTo = moment(to);
  if (_mFrom.isValid() && _mTo.isValid()) {
    var _mFromFormatted = _mFrom.utc().format("YYYY-MM-DD HH:mm:ss");
    var _mToFormatted = _mTo.utc().format("YYYY-MM-DD HH:mm:ss");
    var _lastEqual = _mFromFormatted.length - 1;
    for (var i = _mFromFormatted.length - 1; i >= 0; i--) {
      if (_mFromFormatted[i] == _mToFormatted[i] && (_mFromFormatted[i] == "0" || _mFromFormatted[i] == ":")) {
        _lastEqual = i;
      }
      else break;
    }

    var _minMaxDiff = moment(to).diff(moment(from), 'seconds');
    var _format = "YYYY-MM-DD HH:mm:ss".substr(0, _lastEqual);
    if (_format.length == 13){
      _format += ":mm"; // hours without minutes are weird
    }
    var _formatWithCommon = _format.substring(10, _format.length);
    var _common = "YYYY-MM-DD";
    if (widget && widget.properties && widget.properties.min && widget.properties.min()) {
      _minMaxDiff = moment(widget.properties.max()).diff(moment(widget.properties.min()), 'seconds');
    }
    if (withCommon && _mTo.diff(_mFrom, 'days') >= 365){
      withCommon = false;
      _format = _common;
    }
    else {
      _format = getFormat(_format, _minMaxDiff, widget);
    }

    return ((_common != "" && withCommon) ? _mFrom.utc().format(_common) + "&nbsp;" : "") + _mFrom.utc().format(withCommon ? _formatWithCommon : _format) + " <i class='fa fa-long-arrow-right'></i> " + ((_common != "" && withCommon) ? _mTo.utc().format(_common) + "&nbsp;" : "") + _mTo.utc().format(withCommon ? _formatWithCommon : _format);
  }
  else {
    return from + " - " + to;
  }
}

function getFormat(format, minMaxDiff, widget) {
  var _hasWidget = widget && widget.properties && widget.properties.min && widget.properties.min();
  if (minMaxDiff > 0 && minMaxDiff <= 86400) { // max 1 day
    if (_hasWidget && moment(widget.properties.max()).date() != moment(widget.properties.min()).date()) {
      format = format.substring(5, format.length);
    }
    else {
      format = format.substring(10, format.length);
    }
  }
  if (minMaxDiff > 86400 && minMaxDiff <= 22464000) { // max 360 days
    format = format.substring(5, format.length);
  }
  if (minMaxDiff > 22464000){
    format = format.substr(0, 10);
  }

  if (format.indexOf("MM") == 0) {
    format = "MMM " + format.substr(3);
  }
  return format;
}


var lastWindowScrollPosition = 0;

var getDraggableOptions = function (options) {
  if (searchViewModel && searchViewModel.isGridster()) {
    var setup = {
      'start': function (event, ui) {
        $(ui.helper).css('z-index', '999999');
        huePubSub.publish('dashboard.widget.drag.start', {
          event: event,
          widget: options.data,
          gridsterWidget: options.parent
        });
        $(this).data('startingScrollTop', $('.page-content').scrollTop());
        if (options.plusButton) {
          searchViewModel.showPlusButtonHint(false);
        }
        if (options && options.start) {
          options.start();
        }
      },
      'drag': function (event, ui) {
        huePubSub.publish('dashboard.widget.drag', {
          event: event,
          widgetHeight: options.data.gridsterHeight ? options.data.gridsterHeight() : 6,
          gridsterWidget: options.parent
        });
        if (options.parent) {
          ui.position.top += $('.page-content').scrollTop() - parseInt($(this).data('startingScrollTop'));
        }
      },
      'stop': function (event, ui) {
        huePubSub.publish('dashboard.widget.drag.stop', {
          event: event,
          widget: options.data,
          gridsterWidget: options.parent
        });
        if (options && options.stop) {
          options.stop();
        }
      },
    };
    if (options.parent) { // extra options for an existing Gridster widget
      setup.appendTo = '.gridster';
      setup.helper = function () {
        return '<div class="gridster-helper">' + (options.data.name ? options.data.name() : '${ _ko('Empty widget')}') + '</div>'
      };
      setup.cursorAt = {
        top: 5,
        left: 5
      };
      setup.handle = 'h2';
    }
    if (options.plusButton) { // extra options for dragging from the plus button
      setup.appendTo = '.gridster';
      setup.helper = function () {
        return '<div class="gridster-helper">${ _ko('Add a widget')}</div>'
      };
      setup.cursorAt = {
        top: 5,
        left: 5
      };
    }
    setup.refreshPositions = true;
    return setup
  }
  else {
    return {
      'start': function (event, ui) {
        lastWindowScrollPosition = $('.page-content').scrollTop();
        $('.card-body').slideUp('fast');
        if (options && options.start) {
          options.start();
        }
      },
      'stop': function (event, ui) {
        $('.card-body').slideDown('fast', function () {
          $('.page-content').scrollTop(lastWindowScrollPosition)
        });
        if (options && options.stop) {
          options.stop();
        }
      }
    }
  }
};

function pieChartDataTransformer(data) {
  var _data = [];
  $(data.counts).each(function (cnt, item) {
    item.widget_id = data.widget_id;
    _data.push({
      label: item.value,
      value: item.count,
      obj: item
    });
  });
  return _data.filter(function (val) {
    return val.value >= 0;
  });
}

function _rangePieChartDataTransformer(data, isUp) {
  var _data = [];
  $(data.counts).each(function (cnt, item) {
    item.widget_id = data.widget_id;
    var _label = isUp ? (item.from + (item.is_up ? ' & ${ _('Up') }' : ' & ${ _('Less') }')) : (item.from + ' - ' + item.to);
    _data.push({
      label: _label,
      from: item.from,
      to: item.to,
      value: item.value,
      obj: item
    });
  });
  return _data.filter(function (val) {
    return val.value >= 0;
  });
}


function rangePieChartDataTransformer(data) {
  return _rangePieChartDataTransformer(data, false);
}

function rangeUpPieChartDataTransformer(data) {
  return _rangePieChartDataTransformer(data, true);
}

function pieChartDataTransformerGrid(data) {
  var _data = [];
  var chartX, chartY;
  if (data.chartX && typeof data.chartX === 'function') {
    chartX = data.chartX();
  } else if (!data.chartX) {
    chartX = searchViewModel.collection.template.chartSettings.chartX()
  } // else we just take value as is

  if (data.chartY && typeof data.chartY === 'function') {
    chartY = data.chartY();
  } else if (!data.chartY) {
    chartY = searchViewModel.collection.template.chartSettings.chartYSingle();
  } // else we just take value as is
  if (!chartX) {
    _data.message = window.I18n('Missing legend configuration.');
    return _data;
  } else if (!chartY) {
    _data.message = window.I18n('Missing value configuration.');
    return _data;
  }

  $(data.counts).each(function (cnt, item) {
    item.widget_id = data.widget_id;
    if (chartX != "" && item.item[chartX] && chartY != "" && item.item[chartY]) {
      item.from = item.item[chartX]();
      _data.push({
        label: item.item[chartX](),
        value: item.item[chartY](),
        obj: item
      });
    }
  });
  return _data.filter(function (val) {
    return val.value >= 0;
  });
}

function _barChartDataTransformer(rawDatum, isUp) {
  var _datum = [];
  var _data = [];

  $(rawDatum.counts).each(function (cnt, item) {
    item.widget_id = rawDatum.widget_id;
    if (typeof item.from != "undefined") {
      if (isUp){
        _data.push({
          series: 0,
          index: cnt,
          x: item.from + (item.is_up ? ' & ${ _('Up') }' : ' & ${ _('Less') }'),
          y: item.value,
          obj: item
        });
      }
      else {
        _data.push({
          series: 0,
          index: cnt,
          x: item.from,
          x_end: item.to,
          y: item.value,
          obj: item
        });
      }
    }
    else {
      _data.push({
        series: 0,
        index: cnt,
        x: item.value,
        y: item.count,
        obj: item
      });
    }
  });
  _datum.push({
    key: rawDatum.label,
    values: _data
  });
  _data.sort(function (a, b) {
    return a.x - b.x;
  });

  return _datum;
}

function barChartDataTransformer(rawDatum) {
  return _barChartDataTransformer(rawDatum, false);
}

function barChartDataTransformer2(rawDatum) {
  return _timelineChartDataTransformer(rawDatum, false);
}

function barChartRangeUpDataTransformer(rawDatum) {
  return _barChartDataTransformer(rawDatum, true);
}


function _partitionChartDataTransformer(counts) {
  var _categories = [];

  $(counts).each(function (cnt, item) {
    var _category = null;

    _categories.forEach(function (category) {
      if (category.name == item.value) {
        _category = category;
      }
    });

    if (_category == null) {
      _category = {
        name: item.value,
        size: item.count,
        obj: item,
        children: []
      }
      _categories.push(_category);
    }

    if (item.pivot != undefined) {
      var children = []
      $(item.pivot).each(function (cnt, child) {
        children = children.concat(_partitionChartDataTransformer(child));
      });
     _category.children = children;
    }
  });

  return _categories;
}

function partitionChartDataTransformer(rawDatum) {
  var _partitionData = {
    name: "${ _('Total') }",
    children: []
  }

  _partitionData.children = _partitionChartDataTransformer(rawDatum.counts);

  return _partitionData;
}



function pivotChartDataTransformer(rawDatum) {
  var _categories = [];

  $(rawDatum.counts).each(function (cnt, item) {
    item.widget_id = rawDatum.widget_id;

    var _key = Array.isArray(item.value) ? item.value[1] : item.value;
    var _category = null;

    _categories.forEach(function (category) {
      if (category.key == _key) {
        _category = category;
      }
    });

    if (_category == null) {
      _category = {
        key: _key,
        values: []
      };
      _categories.push(_category);
    }

    _category.values.push({
      series: 0,
      index: _category.values.length,
      x: item.cat,
      y: item.count,
      obj: item
    });
  });

  _categories.forEach(function (category) {
    category.values.sort(function (a, b) {
      return a.x - b.x;
    });
  });
  return _categories;
}

function lineChartDataTransformer(rawDatum) {
  var _datum = [];
  var _data = [];
  $(rawDatum.counts).each(function (cnt, item) {
    item.widget_id = rawDatum.widget_id;
    if (typeof item.from != "undefined") {
      _data.push({
        series: 0,
        x: item.from,
        x_end: item.to,
        y: item.value,
        obj: item
      });
    }
    else {
      _data.push({
        series: 0,
        x: item.value,
        y: item.count,
        obj: item
      });
    }
  });
  _datum.push({
    key: rawDatum.label,
    values: _data
  });
  return _datum;
}

function timelineChartDataTransformer (rawDatum) {
  return _timelineChartDataTransformer(rawDatum, true);
}

function _timelineChartDataTransformer(rawDatum, isDate) {
  var _datum = [];
  var _data = [];

  function getValue (value) {
    return isDate ? new Date(moment(value).valueOf()) : value
  }
  function getNumericValue(value) {
    return value && value.getTime ? value.getTime() : value;
  }

  $(rawDatum.counts).each(function (cnt, item) {
    item.widget_id = rawDatum.widget_id;
    _data.push({
      series: 0,
      index: cnt,
      x: getValue(item.from ? item.from : item.value), // When started from a non timeline widget
      x_end: item.to && getValue(item.to),
      y: item.from !== undefined ? item.value : item.count,
      obj: item
    });
  });

  if (_data.length) {
    _datum.push({
      key: rawDatum.label,
      values: _data
    });

    _data.sort(function (a, b) {
      return a.x - b.x;
    });
  }

  // In Solr, all series might not have values on all data point. If a value is 0 or if it's been filtered by the limit option, solr does not return a value.
  // Unfortunately, this causes the following issues in the chart:
  // 1) The x axis can be unsorted
  // 2) The stacked option does not render correctly.
  // To fix this we pad series that don't have values with zeros

  //Preprocess to obtain all the x values.
  var values = rawDatum.extraSeries.reduce(function (values, serie) {
    serie.counts.reduce(function (values, item) {
      var x = getNumericValue(getValue(item.from ? item.from : item.value));
      if (!values[x]) {
        values[x] = {};
      }
      values[x][serie.label] = item;
      return values;
    }, values);
    return values;
  }, {});


  // If multi query
  var keys = Object.keys(values);
  if (isDate) {
    keys.sort();
  }
  $(rawDatum.extraSeries).each(function (serieIndex, serie) {
    if (serieIndex == 0) {
      _datum = [];
    }
    var _data = [];

    $(keys).each(function (cnt, key) {
      if (values[key][serie.label]) {
        var item = values[key][serie.label];
        item.widget_id = rawDatum.widget_id;
        _data.push({
          series: serieIndex,
          index: _data.length,
          x: getValue(item.from ? item.from : item.value), // When started from a non timeline widget
          x_end: item.to && getValue(item.to),
          y: item.from !== undefined ? item.value : item.count,
          obj: item
        });
      } else {
        var keys = Object.keys(values[key]);
        var item = keys[0] && values[key][keys[0]];
        item.widget_id = rawDatum.widget_id;
        var copy = JSON.parse(JSON.stringify(item));
        copy.value = 0;
        _data.push({
          series: serieIndex,
          index: _data.length,
          x: getValue(item.from ? item.from : item.value),
          x_end: item.to && getValue(item.to),
          y: copy.value,
          obj: copy
        });
      }
    });

    _datum.push({
      key: serie.label,
      values: _data
    });
  });

  return _datum;
}

function mapChartDataTransformer(data) {
  var _data = [];
  $(data.counts).each(function (cnt, item) {
    item.fields = item.pivot ? item.pivot[0].fq_fields : item.fq_fields;
    item.values = item.pivot ? item.pivot[0].fq_values : item.fq_values;
    item.counts = item.pivot ? item.pivot[0].count : item.count; // unused yet
    item.is2d = item.pivot ? true : false; // unused yet

    if (item.value != null && item.value != "" && item.value.length < 4) {
      var _label = data.scope == "world" ? HueGeo.getISOAlpha3(item.value) : item.value.toUpperCase();
      var _found = false;
      for (var i = 0; i < _data.length; i++) { // we group lower and upper cases together
        if (_data[i].label == _label) {
          _data[i].value += item.pivot ? item.pivot[0].fq_values : item.count;
          _found = true;
          break;
        }
      }
      if (!_found) {
        _data.push({
          label: _label,
          value: item.pivot ? item.pivot[0].fq_values : item.count,
          obj: item
        });
      }
    }
  });
  return _data;
}


function gradientMapChartDataTransformer(data) {
  var _data = [];
  $(data.counts).each(function (cnt, item) {
    item.is2d = item.fq_fields ? true : false;
    item.fields = item.is2d ? item.fq_fields : [item.cat];
    item.values = item.is2d ? item.fq_values : [item.value];
    item.counts = item.count;
    item.value = item.is2d ? item.fq_values[0] : item.value;
    item.pivot = [];

    if (item.value != null && item.value != "" && item.value.length < 4) {
      var _label = data.scope == "world" ? HueGeo.getISOAlpha3(item.value) : item.value.toUpperCase();
      var _found = false;
      for (var i = 0; i < _data.length; i++) { // we group lower and upper cases together
        if (_data[i].label == _label) {
          _data[i].value += item.counts;
          _data[i].obj.pivot.push({count: item.counts, value: item.is2d ? (/\)/.test(item.cat) ? item.cat : item.fq_values[item.fq_values.length - 1]) : item.value});
          _found = true;

          break;
        }
      }
      if (! _found) {
        item.pivot = [{count: item.count, value: item.is2d ? (/\)/.test(item.cat) ? item.cat : item.fq_values[item.fq_values.length - 1]) : item.value}];
        _data.push({
          label: _label,
          value: item.counts,
          obj: item
        });
      }
    }
  });
  return _data;
}

function gradientMapChartDataTransformerGrid(data) {
  var chartX, chartY;
  if (data.chartX && typeof data.chartX === 'function') {
    chartX = data.chartX();
  } else if (!data.chartX) {
    chartX = searchViewModel.collection.template.chartSettings.chartX()
  } // else we just take value as is

  if (data.chartY && typeof data.chartY === 'function') {
    chartY = data.chartY();
  } else if (!data.chartY) {
    chartY = searchViewModel.collection.template.chartSettings.chartYSingle();
  } // else we just take value as is
  var _data = [];
  if (!chartX) {
    _data.message = window.I18n('Missing region configuration.');
    return _data;
  } else if (!chartY) {
    _data.message = window.I18n('Missing y axis configuration.');
    return _data;
  }
  $(data.counts).each(function (cnt, item) {
    if (typeof item.item[chartX] === 'function') {
      item.fields = [item.item[chartX]()];
    } else {
      item.fields = [item.item[chartX]];
    }
    if (typeof item.item[chartY] === 'function') {
      item.values = [item.item[chartY]()];
    } else {
      item.values = [item.item[chartY]];
    }
    item.field = item.fields[0];
    item.value = item.values[0];
    item.pivot = [];

    if (item.value != null && item.value != "" && item.field.length < 4) {
      var _label = data.scope == "world" ? HueGeo.getISOAlpha3(item.field) : item.field.toUpperCase();
      var _found = false;
      for (var i = 0; i < _data.length; i++) { // we group lower and upper cases together
        if (_data[i].label == _label) {
          _data[i].obj.pivot.push({count: item.value, value: item.field});
          _found = true;
          break;
        }
      }
      if (! _found) {
        item.pivot = [{field: item.value, value: item.field}];
        _data.push({
          label: _label,
          value: item.values,
          obj: item
        });
      }
    }
  });
  return _data;
}

function leafletMapChartDataTransformer(data) {
  var _data = [];
  if (!$.isEmptyObject(data.counts) && data.counts.response.docs && searchViewModel.collection.template.leafletmap.latitudeField() != "" && searchViewModel.collection.template.leafletmap.longitudeField() != "") {
    data.counts.response.docs.forEach(function (record) {
      var _obj = {
        lat: record[searchViewModel.collection.template.leafletmap.latitudeField()],
        lng: record[searchViewModel.collection.template.leafletmap.longitudeField()]
      }
      if (searchViewModel.collection.template.leafletmap.labelField() != "") {
        _obj.label = record[searchViewModel.collection.template.leafletmap.labelField()];
      }
      _data.push(_obj);
    });
  }
  return _data;
}

function leafletMapChartDataTransformerGrid(data) {
  var _data = [];
  var chartX, chartY, chartMapLabel;
  if (data.chartX && typeof data.chartX === 'function') {
    chartX = data.chartX();
  } else if (!data.chartX) {
    chartX = searchViewModel.collection.template.chartSettings.chartX()
  } // else we just take value as is

  if (data.chartY && typeof data.chartY === 'function') {
    chartY = data.chartY();
  } else if (!data.chartY) {
    chartY = searchViewModel.collection.template.chartSettings.chartYSingle();
  } // else we just take value as is

  if (data.chartZ && typeof data.chartZ === 'function') {
    chartMapLabel = data.chartZ();
  } else if (!data.chartZ) {
    chartMapLabel = searchViewModel.collection.template.chartSettings.chartMapLabel();
  }

  if (!chartX) {
    _data.message = window.I18n('Missing latitude configuration.');
    return _data;
  } else if (!chartY) {
    _data.message = window.I18n('Missing longitude configuration.');
    return _data;
  } else if (!chartMapLabel) {
    _data.message = window.I18n('Missing label configuration.');
    return _data;
  }

  $(data.counts).each(function (cnt, item) {
    if (chartX != "" && item.item[chartX] && chartY != "" && item.item[chartY]) {
      var _obj = {
        lat: item.item[chartX](),
        lng: item.item[chartY]()
      }
      if (chartMapLabel != "" && item.item[chartMapLabel]) {
        _obj.label = item.item[chartMapLabel]();
      }
      _data.push(_obj);
    }
  });
  return _data;
}


function multiSerieDataTransformer(rawDatum) {
  var _datum = [];

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYMulti().length > 0) {
    var _plottedSerie = 0;
    rawDatum.snippet.chartYMulti().forEach(function (col) {
      var _idxValue = -1;
      var _idxLabel = -1;
      rawDatum.snippet.result.meta().forEach(function (icol, idx) {
        if (icol.name == rawDatum.snippet.chartX()) {
          _idxLabel = idx;
        }
        if (icol.name == col) {
          _idxValue = idx;
        }
      });

      if (_idxValue > -1) {
        var _data = [];
        $(rawDatum.counts()).each(function (cnt, item) {
          _data.push({
            series: _plottedSerie,
            x: item[_idxLabel],
            y: item[_idxValue],
            obj: item
          });
        });
        if (rawDatum.sorting == "asc") {
          _data.sort(function (a, b) {
            return a.y - b.y
          });
        }
        if (rawDatum.sorting == "desc") {
          _data.sort(function (a, b) {
            return b.y - a.y
          });
        }
        _datum.push({
          key: col,
          values: _data
        });
        _plottedSerie++;
      }
    });
  }
  return _datum;
}


function multiSerieDataTransformerGrid(rawDatum, isTimeline) {
  var _datum = [];
  var chartX, chartY;
  if (rawDatum.chartX && typeof rawDatum.chartX === 'function') {
    chartX = rawDatum.chartX();
  } else if (!rawDatum.chartX) {
    chartX = searchViewModel.collection.template.chartSettings.chartX()
  } // else we just take value as is

  if (rawDatum.chartY && typeof rawDatum.chartY === 'function') {
    chartY = rawDatum.chartY();
  } else if (!rawDatum.chartY) {
    chartY = searchViewModel.collection.template.chartSettings.chartYMulti();
  } // else we just take value as is

  if (!chartX) {
    _datum.message = window.I18n('Missing x axis configuration.');
    return _datum;
  } else if (!chartY || !chartY.length) {
    _datum.message = window.I18n('Missing y axis configuration.');
    return _datum;
  }

  if (chartX != null && chartY.length > 0 && rawDatum.counts.length > 0) {
    var _plottedSerie = 0;
    chartY.forEach(function (col) {
      var _data = [];
      $(rawDatum.counts).each(function (cnt, item) {
        if (item.item[chartX] && item.item[col]) {
          _data.push({
            series: _plottedSerie,
            x: isTimeline && new Date(moment.utc(item.item[chartX]()).valueOf()) || item.item[chartX](),
            y: item.item[col](),
            obj: item.item
          });
        }
      });
      if (rawDatum.sorting == "asc") {
        _data.sort(function (a, b) {
          return a.y - b.y
        });
      }
      if (rawDatum.sorting == "desc") {
        _data.sort(function (a, b) {
          return b.y - a.y
        });
      }
      _datum.push({
        key: col,
        values: _data
      });
      _plottedSerie++;
    });
  }
  return _datum;
}


function resizeFieldsListCallback() {
  $('.fields-list').each(function(){
    $fieldsList = $(this);
    var $resultContainer = $fieldsList.parents('.card-widget').find('.result-container');
    $fieldsList.css("max-height", Math.max($resultContainer.height(), 230));
    window.setTimeout(function () {
      var _fillHeight = $resultContainer.height() - 40;
      if ($fieldsList.height() < _fillHeight) {
        $fieldsList.height(_fillHeight);
        $fieldsList.css("max-height", _fillHeight);
      }
    }, 100);

    var positionInfo = function () {
      var leftPos = 184;
      if ($fieldsList.get(0).scrollHeight > $fieldsList.height()) {
        leftPos -= hueUtils.scrollbarWidth();
      }
      $fieldsList.find('i').css('left', (leftPos + $fieldsList.scrollLeft()) + 'px');
    }

    var checkHeight = function () {
      if ($fieldsList.height() > 0) {
        positionInfo();
      } else {
        window.setTimeout(checkHeight, 100);
      }
    }

    checkHeight();

    $fieldsList.off('scroll');
    $fieldsList.on('scroll', positionInfo);
  });
}

var resizeTimeout = -1;
function resizeFieldsListThrottled() {
  window.clearTimeout(resizeTimeout);
  resizeTimeout = window.setTimeout(resizeFieldsListCallback, 200);
}

function resizeFieldsList() {
  if (!searchViewModel.isGridster()) {
    resizeFieldsListCallback();
  }
}

function toggleDocDetails(doc) {
  doc.showDetails(! doc.showDetails());

  if (doc.details().length == 0) {
    searchViewModel.getDocument(doc, resizeFieldsList);
  }
  else {
    resizeFieldsListThrottled();
  }
}


function queryTypeahead(query, process) {
  var _source = searchViewModel.collection.template.fieldsNames();
  _source = _source.concat("AND OR TO".split(" "))

  if (searchViewModel.collection.suggest.enabled()) {
    searchViewModel.suggest(query, function (data) {
      var _tmp = [];
      if (typeof data != "undefined" && data.response && data.response.suggest && data.response.suggest[searchViewModel.collection.suggest.dictionary()]) {
        var suggestions = data.response.suggest[searchViewModel.collection.suggest.dictionary()][query].suggestions;
        suggestions.forEach(function (sugg) {
          _tmp.push(sugg.term + "<i class='muted fa fa-search'></i>");
        });
      }
      process(_tmp.concat(_source));
    });
  }
  else {
    return _source;
  }
}

function newSearch() {
  huePubSub.publish('open.link', '/dashboard/new_search?engine=' + searchViewModel.collection.engine());
}

function loadSearch(collection, query, initial) {
  searchViewModel = new SearchViewModel(collection, query, initial, ${ USE_GRIDSTER.get() and 'true' or 'false' }, ${ USE_NEW_ADD_METHOD.get() and 'true' or 'false' });
  ko.applyBindings(searchViewModel, $('#searchComponents')[0]);

  searchViewModel.timelineChartTypes = ko.observableArray([{
      value: "line",
      label: "${ _('Lines')}"
    },
    {
      value: "bar",
      label: "${ _('Bars')}"
    }
  ]);

  searchViewModel.init(function(){
    $(".chosen-select").trigger("chosen:updated");
    if (searchViewModel.collection.engine() === 'report' || searchViewModel.collection.engine() === 'solr') {
      if (!searchViewModel.collectionJson.layout.length && (!searchViewModel.collectionJson.gridItems || !searchViewModel.collectionJson.gridItems.length)) {
        magicSearchLayout(searchViewModel);
      }
    }
    else {
      queryBuilderSearchLayout(searchViewModel);
    }
  });

  searchViewModel.isRetrievingResults.subscribe(function(value){
    if (!value){
      resizeFieldsList();
    }
  });

  searchViewModel.isEditing.subscribe(function(value){
    if (value){
      window.setTimeout(function(){
        if ($(".slider-cnt").length > 0 && $(".slider-cnt").data("slider")){
          $(".slider-cnt").slider("redraw");
        }
      }, 300);
    }
  });

  searchViewModel.isPlayerMode.subscribe(function(value) {
    if (value){
      $(".navigator").hide();
      $(HUE_CONTAINER).css("paddingTop", "40px");
    }
    else {
      $(".navigator").show();
      $(HUE_CONTAINER).css("paddingTop", "80px");
    }
  });

  var _refreshTimeout = null;
  var refresh = function () {
    _refreshTimeout = window.setTimeout(function () {
      if (searchViewModel.collection.autorefresh()) {
        searchViewModel.search(refresh);
      }
    }, ($.isNumeric(searchViewModel.collection.autorefreshSeconds()) ? searchViewModel.collection.autorefreshSeconds() * 1 : 60) * 1000)
  }

  var checkAutoRefresh = function () {
    if (searchViewModel.collection.autorefresh()) {
      window.clearTimeout(_refreshTimeout);
      refresh();
    }
  }

  if (searchViewModel.collection.autorefresh()) {
    refresh();
  }

  huePubSub.subscribe('check.autorefresh', function () {
    checkAutoRefresh();
  });

  searchViewModel.collection.autorefresh.subscribe(function (value) {
    if (value) {
      refresh();
    }
    else {
      window.clearTimeout(_refreshTimeout);
    }
  });

  searchViewModel.collection.autorefreshSeconds.subscribe(function (value) {
    checkAutoRefresh();
  });

  huePubSub.subscribe('dashboard.switch.collection', function(){
    queryBuilderSearchLayout(searchViewModel);
  }, 'dashboard');
}

$(document).ready(function () {

  var _resizeTimeout = -1;
  $(window).resize(function(){
    window.clearTimeout(_resizeTimeout);
    window.setTimeout(function(){
      resizeFieldsList();
    }, 200);
    huePubSub.publish('dashboard.window.resize');
    huePubSub.publish('gridster.remove.scrollbars');
  });

  %if is_report:
    huePubSub.publish('right.assist.hide', true);
  %endif

  var isDraggingOrResizingWidgets = false;
  var tempDraggableGridsterWidget = null;

  var WIDGET_BASE_HEIGHT = 50;
  var $gridster = $('.gridster>ul').gridster({
    widget_margins: [10, 10],
    widget_base_dimensions: ['auto', WIDGET_BASE_HEIGHT],
    scroll_container: '.page-content',
    avoid_overlapped_widgets: true,
    max_cols: 12,
    max_rows: 200,
    resize: {
      axes: ['x'],
      enabled: true,
      start: function (event, ui, $widget) {
        $widget.find('.card-widget').css('opacity', '.6');
        isDraggingOrResizingWidgets = true;
        huePubSub.publish('gridster.resize.start', $widget);
      },
      resize: function (event, ui, $widget, aa) {
        huePubSub.publish('gridster.resize', $widget);
      },
      stop: function (event, ui, $widget) {
        huePubSub.publish('resize.plotly.chart');
        huePubSub.publish('gridster.clean.whitespace');
        huePubSub.publish('gridster.resize.stop');
        $widget.find('.card-widget').height($widget.height()).css('opacity', '1');
        isDraggingOrResizingWidgets = false;
      },
    },
    draggable: {
      handle: '.does-not-exist', // trick to disable dragging
    }
  }).data('gridster');

  function addPreviewHolder() {
    if (!$('.hue-preview-holder').length && searchViewModel.columns().length > 0) {
      $('<li>').addClass('preview-holder hue-preview-holder').attr('data-sizex', '12').attr('data-sizey', '2').attr('data-row', '1').attr('data-col', '1').appendTo($('.gridster>ul'));
    }
  }

  function removePreviewHolder() {
    $('.hue-preview-holder').remove();
  }

  var overlapZone = null;

  function movePreviewHolder(options) {
    addPreviewHolder();
    var coords = {
      col: Math.ceil((options.event.clientX - $('.gridster').offset().left) / (widgetGridWidth + 10)),
      row: Math.ceil((options.event.pageY - $('.gridster').offset().top) / (WIDGET_BASE_HEIGHT + 10))
    }
    var $huePreviewHolder = $('.hue-preview-holder');
    if (coords.row > 0 && coords.col > 0 && coords.col <= 13) {
      var overlaps = false;
      var isEmptyWidget = false;
      var isOverSelf = tempDraggableGridsterWidget !== null && coords.col >= tempDraggableGridsterWidget.col() && coords.row >= tempDraggableGridsterWidget.row() && coords.col < tempDraggableGridsterWidget.col() + tempDraggableGridsterWidget.size_x() && coords.row < tempDraggableGridsterWidget.row() + tempDraggableGridsterWidget.size_y();
      $('li.gs-w').each(function () {
        var dimensions = {
          col: parseInt($(this).attr('data-original-col') || $(this).attr('data-previous-col')),
          row: parseInt($(this).attr('data-original-row') || $(this).attr('data-previous-row')),
          sizex: parseInt($(this).attr('data-original-sizex') || $(this).attr('data-previous-sizex')),
          sizey: parseInt($(this).attr('data-original-sizey') || $(this).attr('data-previous-sizey')),
          widgetId: parseInt($(this).attr('data-widgetid'))
        }
        var $widget = $(this);
        var isSelf = tempDraggableGridsterWidget !== null && tempDraggableGridsterWidget.widgetId() === dimensions.widgetId;
        if (coords.col >= dimensions.col && coords.row >= dimensions.row && coords.col < dimensions.col + dimensions.sizex && coords.row < dimensions.row + dimensions.sizey) {
          isEmptyWidget = $widget.children('.empty-gridster-widget').length > 0;
          overlaps = true;
          if (!isSelf) {
            var sidesWidth = Math.min(Math.floor(dimensions.sizex / 3), 1);
            var centerWidth = dimensions.sizex - sidesWidth * 2;
            var sidesHeight = Math.floor(dimensions.sizey / 3);
            var overlapZoneSideToSide = '';
            var overlapZoneTopDown = '';
            if (coords.col < dimensions.col + sidesWidth) {
              overlapZoneSideToSide = 'W';
            }
            else if (coords.col >= (dimensions.col + sidesWidth) && coords.col < (dimensions.col + sidesWidth + centerWidth)) {
              overlapZoneSideToSide = '';
            }
            else {
              overlapZoneSideToSide = 'E';
            }

            if (coords.row < dimensions.row + sidesHeight) {
              overlapZoneTopDown = 'N';
            }
            else {
              overlapZoneTopDown = 'S';
            }

            if (overlapZoneTopDown + overlapZoneSideToSide != overlapZone) {
              restoreWidgetSizes();
            }

            overlapZone = overlapZoneTopDown + overlapZoneSideToSide;

            if (isEmptyWidget) {
              if (coords.row < dimensions.row + 1) {
                overlapZone = 'N';
              }
              else {
                overlapZone = '';
              }
            }

            if (['NW', 'W', 'SW'].indexOf(overlapZone) > -1) {
              if (!$widget.attr('data-original-col')) {
                $widget.attr('data-original-col', $widget.attr('data-col'));
                $widget.attr('data-col', dimensions.col + 1);
                $widget.attr('data-original-sizex', $widget.attr('data-sizex'));
                $widget.attr('data-sizex', dimensions.sizex - 1);
                // shifts left the widget right next to it on the left
                $('li.gs-w[data-row='+ $widget.attr('data-row') +']').each(function (idx, sibling) {
                  var $sibling = $(sibling);
                  if (parseInt($sibling.data('widgetid')) !== parseInt($widget.data('widgetid')) && parseInt($sibling.attr('data-col')) + parseInt($sibling.attr('data-sizex')) === parseInt($widget.attr('data-original-col'))) {
                    $sibling.attr('data-original-sizex', $sibling.attr('data-sizex'));
                    $sibling.attr('data-sizex', parseInt($sibling.attr('data-sizex')) - 1);
                  }
                });
              }
              $huePreviewHolder.attr('data-col', dimensions.col > 1 ? dimensions.col - 1 : dimensions.col);
              $huePreviewHolder.attr('data-sizex', dimensions.col > 1 ? 2 : 1);
              $huePreviewHolder.attr('data-row', dimensions.row);
              $huePreviewHolder.attr('data-sizey', dimensions.sizey);
            }
            else if (overlapZone === 'N') {
              if (!$widget.attr('data-original-row')) {
                $widget.attr('data-original-row', $widget.attr('data-row'));
                $widget.attr('data-row', dimensions.row + 1);
                $widget.attr('data-original-sizey', $widget.attr('data-sizey'));
                $widget.attr('data-sizey', dimensions.sizey - 1);
                // shifts down the other widgets
                $('li.gs-w[data-row='+ $widget.attr('data-original-row') +']').each(function (idx, sibling) {
                  var $sibling = $(sibling);
                  if (parseInt($sibling.data('widgetid')) !== parseInt($widget.data('widgetid'))) {
                    $sibling.attr('data-original-row', $sibling.attr('data-row'));
                    $sibling.attr('data-row', parseInt($sibling.attr('data-row')) + 1);
                    $sibling.attr('data-original-sizey', $sibling.attr('data-sizey'));
                    $sibling.attr('data-sizey', parseInt($sibling.attr('data-sizey')) - 1);
                  }
                });
                // shifts up the other widgets that come before this one
                $('li.gs-w').each(function (idx, sibling) {
                  var $sibling = $(sibling);
                  if (parseInt($sibling.data('widgetid')) !== parseInt($widget.data('widgetid')) && parseInt($sibling.attr('data-row')) + parseInt($sibling.attr('data-sizey')) === parseInt($widget.attr('data-original-row'))) {
                    $sibling.attr('data-original-sizey', $sibling.attr('data-sizey'));
                    $sibling.attr('data-sizey', parseInt($sibling.attr('data-sizey')) - 1);
                  }
                });
              }
              $huePreviewHolder.attr('data-col', 1);
              $huePreviewHolder.attr('data-row', dimensions.row > 1 ? dimensions.row - 1 : dimensions.row);
              $huePreviewHolder.attr('data-sizex', 12);
              $huePreviewHolder.attr('data-sizey', dimensions.row > 1 ? 2: 1);
            }
            else if (overlapZone === 'S') {
              if (!$widget.attr('data-original-sizey')) {
                $widget.attr('data-original-sizey', $widget.attr('data-sizey'));
                $widget.attr('data-sizey', dimensions.sizey - 1);
                // shifts up the siblings
                $('li.gs-w[data-row='+ parseInt($widget.attr('data-row')) +']').each(function (idx, sibling) {
                  var $sibling = $(sibling);
                  if (parseInt($sibling.data('widgetid')) !== parseInt($widget.data('widgetid'))) {
                    $sibling.attr('data-original-sizey', $sibling.attr('data-sizey'));
                    $sibling.attr('data-sizey', parseInt($sibling.attr('data-sizey')) - 1);
                  }
                });
                // shifts down the other widgets that come after this one
                $('li.gs-w[data-row='+ (parseInt($widget.attr('data-row')) + parseInt($widget.attr('data-original-sizey'))) +']').each(function (idx, sibling) {
                  var $sibling = $(sibling);
                  $sibling.attr('data-original-row', $sibling.attr('data-row'));
                  $sibling.attr('data-row', parseInt($sibling.attr('data-row')) + 1);
                  $sibling.attr('data-original-sizey', $sibling.attr('data-sizey'));
                  $sibling.attr('data-sizey', parseInt($sibling.attr('data-sizey')) - 1);
                });
              }
              $huePreviewHolder.attr('data-col', 1);
              $huePreviewHolder.attr('data-row', dimensions.row + dimensions.sizey - 1);
              $huePreviewHolder.attr('data-sizex', 12);
              $huePreviewHolder.attr('data-sizey', 2);
            }
            else if (['NE', 'E', 'SE'].indexOf(overlapZone) > -1) {
              if (!$widget.attr('data-original-sizex')) {
                $widget.attr('data-original-sizex', $widget.attr('data-sizex'));
                $widget.attr('data-sizex', dimensions.sizex - 1);
                // shifts right the widget right next to it on the right
                var $sibling = $('li.gs-w[data-row='+ $widget.attr('data-row') +'][data-col='+ (parseInt($widget.attr('data-col')) + parseInt($widget.attr('data-original-sizex'))) +']');
                $sibling.attr('data-original-col', $sibling.attr('data-col'));
                $sibling.attr('data-col', parseInt($sibling.attr('data-col')) + 1);
                $sibling.attr('data-original-sizex', $sibling.attr('data-sizex'));
                $sibling.attr('data-sizex', parseInt($sibling.attr('data-sizex')) - 1);
              }
              $huePreviewHolder.attr('data-col', dimensions.col + dimensions.sizex - 1);
              $huePreviewHolder.attr('data-row', dimensions.row);
              $huePreviewHolder.attr('data-sizex', parseInt($huePreviewHolder.attr('data-col')) === 12 ? 1 : 2);
              $huePreviewHolder.attr('data-sizey', dimensions.sizey);
            }
            if (overlapZone !== '') {
              $huePreviewHolder.attr('data-overlapzone', overlapZone);
              $huePreviewHolder.attr('data-widgetid', $widget.attr('data-widgetid'));
              $huePreviewHolder.attr('data-widgetrow', $widget.attr('data-previous-row'));
              $huePreviewHolder.attr('data-widgetcol', $widget.attr('data-previous-col'));
              skipRestoreOnStop = false;
            }
            else {
              skipRestoreOnStop = true;
              restoreWidgetSizes();
            }
          }
          else {
            skipRestoreOnStop = true;
            restoreWidgetSizes();
          }
        }
      });
      $huePreviewHolder.show();

      if ((isEmptyWidget && overlapZone !== 'N') || isOverSelf) {
        $huePreviewHolder.hide();
      }
    }
    else {
      $huePreviewHolder.hide();
    }
  }

  var widgetGridWidth = null;

  var setWidgetGridWidth = function () {
    if (searchViewModel && searchViewModel.isGridster()) {
      // turns out Gridster generates CSS either with single or double quotes depending on the browser
      widgetGridWidth = typeof hueUtils.getStyleFromCSSClass('[data-sizex="1"]') !== 'undefined' ? parseInt(hueUtils.getStyleFromCSSClass('[data-sizex="1"]').width) : (hueUtils.getStyleFromCSSClass("[data-sizex='1']") ? parseInt(hueUtils.getStyleFromCSSClass("[data-sizex='1']").width) : null);
    }
  }

  setWidgetGridWidth();
  huePubSub.subscribe('dashboard.window.resize', setWidgetGridWidth, 'dashboard');

  function restoreWidgetSizes() {
    $('li.gs-w').each(function () {
      var $widget = $(this);
      $widget.attr('data-sizex', $widget.attr('data-previous-sizex'));
      $widget.attr('data-sizey', $widget.attr('data-previous-sizey'));
      $widget.attr('data-col', $widget.attr('data-previous-col'));
      $widget.attr('data-row', $widget.attr('data-previous-row'));
      $widget.removeAttr('data-original-sizex');
      $widget.removeAttr('data-original-sizey');
      $widget.removeAttr('data-original-col');
      $widget.removeAttr('data-original-row');
    });
  }

  function setPreviousWidgetSizes() {
    $('li.gs-w').each(function () {
      var $widget = $(this);
      $widget.attr('data-previous-sizex', $widget.attr('data-sizex'));
      $widget.attr('data-previous-sizey', $widget.attr('data-sizey'));
      $widget.attr('data-previous-col', $widget.attr('data-col'));
      $widget.attr('data-previous-row', $widget.attr('data-row'));
    });
  }

  function equalizeWidgetsHeights() {
    if (searchViewModel.isGridster() && !isDraggingOrResizingWidgets) {
      huePubSub.publish('gridster.remove.scrollbars');
      // widgets on the same row should have the same height
      var touched = [];
      searchViewModel.gridItems().forEach(function (existingWidget) {
        var siblings = [];
        if (existingWidget.widgetId && touched.indexOf(existingWidget.widgetId()) === -1) {
          touched.push(existingWidget.widgetId());
          var biggestSize = existingWidget.size_y();
          searchViewModel.gridItems().forEach(function (siblingWidget) {
            if (siblingWidget.row() === existingWidget.row() && existingWidget.widgetId() !== siblingWidget.widgetId()) {
              siblings.push(siblingWidget);
              if (siblingWidget.size_y() > biggestSize) {
                biggestSize = siblingWidget.size_y();
              }
              touched.push(siblingWidget.widgetId());
            }
          });
          if (siblings.length > 0) {
            siblings.push(existingWidget);
            if (!siblings.map(function (a) {
              return a.size_y()
            }).reduce(function (a, b) {
              return (a === b) ? a : NaN;
            })) {
              siblings.forEach(function (siblingWidget) {
                siblingWidget.size_y(biggestSize);
                $gridster.resize_widget($(siblingWidget.gridsterElement), siblingWidget.size_x(), siblingWidget.size_y());
              });
            }
          }
        }
        if (existingWidget.widget && existingWidget.widget.widgetType && existingWidget.widget.widgetType() === 'html-resultset-widget') {
          huePubSub.publish('gridster.clean.html.whitespace', existingWidget);
        }
      });
    }
  }

  window.setInterval(equalizeWidgetsHeights, 1000, 'dashboard');


  var tempDraggable = null;
  var skipRestoreOnStop = false;
  huePubSub.subscribe('dashboard.widget.drag.start', function (options) {
    isDraggingOrResizingWidgets = true;
    setPreviousWidgetSizes();
    skipRestoreOnStop = false;
    if (typeof options.gridsterWidget !== 'undefined') {
      tempDraggable = options.widget;
      tempDraggableGridsterWidget = options.gridsterWidget;
    }
    else {
      tempDraggableGridsterWidget = null;
      var widgetClone = ko.mapping.toJS(options.widget);
      widgetClone.id = hueUtils.UUID();
      tempDraggable = new Widget(widgetClone);
    }
    addPreviewHolder();
  }, 'dashboard');

  huePubSub.subscribe('dashboard.widget.drag.stop', function () {
    isDraggingOrResizingWidgets = false;
    if (!skipRestoreOnStop) {
      restoreWidgetSizes();
    }
  }, 'dashboard');

  huePubSub.subscribe('dashboard.widget.drag', function (options) {
    movePreviewHolder(options);
  }, 'dashboard');

  huePubSub.subscribe('draggable.text.drag', function (options) {
    if (searchViewModel.isGridster()) {
      movePreviewHolder(options);
    }
  }, 'dashboard');

  huePubSub.subscribe('draggable.text.stopped', function (options) {
    isDraggingOrResizingWidgets = false;
  }, 'dashboard');

  huePubSub.subscribe('dashboard.gridster.widget.drag', function (options) {
    movePreviewHolder(options);
  }, 'dashboard');

  huePubSub.subscribe('draggable.text.meta', function (options) {
    if (searchViewModel.isGridster()) {
      searchViewModel.showPlusButtonHint(false);
      isDraggingOrResizingWidgets = true;
      setPreviousWidgetSizes();
      skipRestoreOnStop = false;
      addPreviewHolder(options);
    }
  }, 'dashboard');

  huePubSub.subscribeOnce('gridster.added.widget', function () {
    $(window).trigger('resize');
  });

  huePubSub.subscribe('gridster.added.widget', removePreviewHolder, 'dashboard');

  huePubSub.subscribe('gridster.empty.drop', function (options) {
    showAddFacetDemiModal(options.widget, options.target);
    tempDraggable = null;
  }, 'dashboard');

  huePubSub.subscribe('gridster.empty.add', function (options) {
    var fakeRow = searchViewModel.columns()[0].addEmptyRow(true);
    var widgetClone = ko.mapping.toJS(options.widget);
    widgetClone.id = hueUtils.UUID();
    selectedWidget = new Widget(widgetClone);
    fakeRow.addWidget(selectedWidget);
    selectedGridster = options.target;
    huePubSub.subscribeOnce('search.facet.added', function (facet) {
      facet.template.chartSettings.chartType(selectedGridster.emptyProperties.fieldViz());
      var form = facet.properties.facets()[0];
      if (form) {
        form.aggregate.function(selectedGridster.emptyProperties.fieldOperation());
        form.sort(selectedGridster.emptyProperties.fieldSort());
      }
    }, 'dashboard');
    addFacetDemiModalFieldPreview({
      'name': function () {
        return selectedGridster.emptyProperties.fieldName
      }
    });

    tempDraggable = null;
  }, 'dashboard');

  function removeInternalScroll(widget) {
    if (widget && widget.gridsterElement) {
      var scrollDifference = widget.gridsterElement.scrollHeight - widget.gridsterElement.clientHeight;
      if (scrollDifference > 0) { // avoid scrollbars inside the widget
        widget.size_y(widget.size_y() + Math.ceil(scrollDifference / WIDGET_BASE_HEIGHT));
        $gridster.resize_widget($(widget.gridsterElement), widget.size_x(), widget.size_y(), function () {
          huePubSub.publish('gridster.clean.whitespace');
        });
      }
    }
  }

  function normalizeWidgetHeight(options) {
    var $gridsterWidget = options.target ? $(options.target).parents('li.gs-w') : options;

    searchViewModel.gridItems().forEach(function (widget) {
      if (widget.widgetId() === parseInt($gridsterWidget.data('widgetid'))) {
        removeInternalScroll(widget);
        var contentHeight = $(widget.gridsterElement).find('.card-widget').height();
        if (widget.gridsterElement.clientHeight - contentHeight > (WIDGET_BASE_HEIGHT + 10)) {
          widget.size_y(Math.ceil(contentHeight / (WIDGET_BASE_HEIGHT + 10)));
          $gridster.resize_widget($(widget.gridsterElement), widget.size_x(), widget.size_y(), function () {
            huePubSub.publish('gridster.clean.whitespace');
            equalizeWidgetsHeights();
          });
        }
      }
    });
  }

  huePubSub.subscribe('gridster.remove.scrollbars', function () {
    searchViewModel.gridItems().forEach(function (widget) {
      removeInternalScroll(widget);
    });
  }, 'dashboard');

  huePubSub.subscribe('gridster.clean.grid.whitespace', function (options) {
    var $gridsterWidget = $(options.event.target).parents('li.gs-w');
    var contentHeight = $gridsterWidget.find('.card-widget').height();

    var heightCheckInterval = -1;
    var elapsedTime = 0;

    hueUtils.waitForRendered(options.lookFor, function (el) {
      return el.is(':visible')
    }, function () {
      // monitor height for two seconds, as we don't have reliable animation/rendered events from the current chart library
      heightCheckInterval = window.setInterval(function () {
        if (contentHeight !== $gridsterWidget.find('.card-widget').height()) {
          searchViewModel.gridItems().forEach(function (widget) {
            if (widget.widgetId() === parseInt($gridsterWidget.data('widgetid'))) {
              removeInternalScroll(widget);
              contentHeight = $(widget.gridsterElement).find('.card-widget').height();
              if (widget.gridsterElement.clientHeight - contentHeight > (WIDGET_BASE_HEIGHT + 10)) {
                widget.size_y(Math.ceil(contentHeight / (WIDGET_BASE_HEIGHT + 10)));
                $gridster.resize_widget($(widget.gridsterElement), widget.size_x(), widget.size_y(), function () {
                  huePubSub.publish('gridster.clean.whitespace');
                  equalizeWidgetsHeights();
                });
              }
            }
          });
          window.clearInterval(heightCheckInterval);
        }
        if (elapsedTime > 2000) {
          window.clearInterval(heightCheckInterval);
        }
        elapsedTime += 50;
      }, 50);

    });
  });

  huePubSub.subscribe('gridster.clean.html.whitespace', removeInternalScroll);

  huePubSub.subscribe('gridster.clean.whitespace', function () {
    if (searchViewModel.isGridster()) {
      var maxRow = 0;
      var occupiedRows = [];
      searchViewModel.gridItems().forEach(function (existingWidget) {
        var tempRow = existingWidget.row() + existingWidget.size_y();
        for (var i = existingWidget.row(); i < existingWidget.size_y(); i++) {
          if (occupiedRows.indexOf(i) === -1) {
            occupiedRows.push(i);
          }
        }
        if (tempRow > maxRow) {
          maxRow = tempRow;
        }
      });
      for (var i = 0; i < maxRow; i++) {
        if (occupiedRows.indexOf(i) === -1) {
          $gridster.remove_empty_cells(1, i, 12, 1);
        }
      }
      huePubSub.publish('gridster.sync.model');
    }
  }, 'dashboard');

  huePubSub.subscribe('dashboard.drop.on.page', function (options) {
    skipRestoreOnStop = true;

    var $preview = $('.hue-preview-holder');
    var dimensions = {
      col: parseInt($preview.attr('data-col')),
      row: parseInt($preview.attr('data-row')),
      sizex: parseInt($preview.attr('data-sizex')),
      sizey: parseInt($preview.attr('data-sizey')),
      overlap: $preview.attr('data-overlapzone'),
      widgetId: parseInt($preview.attr('data-widgetid')),
      widgetRow: parseInt($preview.attr('data-widgetrow')),
      widgetCol: parseInt($preview.attr('data-widgetcol'))
    }

    removePreviewHolder();

    function resizeAndMove(widget, width, col, row) {
      $gridster.resize_widget($(widget.gridsterElement), width, widget.size_y());
      widget.size_x(width);
      var newRow = typeof row === 'undefined' ? widget.row() : row;
      widget.col(col);
      widget.row(newRow);
      $gridster.move_widget($(widget.gridsterElement), col, newRow, function () {
        normalizeWidgetHeight($(widget.gridsterElement));
      });
    }

    if (searchViewModel.columns().length > 0) {

      searchViewModel.showPlusButtonHint(false);

      if (typeof dimensions.overlap !== 'undefined') {
        if (dimensions.overlap === 'N') {
          dimensions.row = dimensions.widgetRow;
        }
        else if (dimensions.overlap === 'S') {
          dimensions.row = dimensions.row + 1;
        }
        else {
          var collidingWidgets = [];
          searchViewModel.gridItems().forEach(function (existingWidget) {
            var existingWidgetRow = parseInt($(existingWidget.gridsterElement).attr('data-row'));
            var isSelf = tempDraggable && tempDraggableGridsterWidget && tempDraggableGridsterWidget.widgetId() === parseInt($(existingWidget.gridsterElement).attr('data-widgetid'));
            if (existingWidgetRow === dimensions.widgetRow && !isSelf) {
              collidingWidgets.push(existingWidget);
            }
          });

          var newOptimalWidth = Math.floor(12 / (collidingWidgets.length + 1));
          collidingWidgets.sort(function (a, b) {
            return a.col() > b.col()
          });

          // yay for Gridster starting arrays at 1
          var droppedWidgetFauxColumn = Math.floor((dimensions.col - 1) / newOptimalWidth) + 1;
          var adjustedDropPosition = (Math.floor((dimensions.col - 1) / newOptimalWidth) * newOptimalWidth) + 1;
          dimensions.col = adjustedDropPosition;
          dimensions.sizex = newOptimalWidth;

          var resizeAndMoveSiblings = function() {
            var siblingCounter = 0;
            for (var i = 1; i <= 12 / newOptimalWidth; i++) {
              if (i !== droppedWidgetFauxColumn) {
                if (collidingWidgets[siblingCounter]) {
                  resizeAndMove(collidingWidgets[siblingCounter], newOptimalWidth, ((i - 1) * newOptimalWidth) + 1)
                }
                siblingCounter++;
              }
            }
          }

          if (tempDraggableGridsterWidget) {
            if (dimensions.row !== tempDraggableGridsterWidget.row()) {
              autoResizeSiblings(tempDraggableGridsterWidget, true);
            }
            $gridster.move_widget($(tempDraggableGridsterWidget.gridsterElement), -100, -100, resizeAndMoveSiblings); // temporarily move it off grid
          }
          else {
            resizeAndMoveSiblings();
          }

        }
      }

      if (tempDraggable) {
        if (tempDraggableGridsterWidget) {
          autoResizeSiblings(tempDraggableGridsterWidget, true);
          if (dimensions.overlap) {
            resizeAndMove(tempDraggableGridsterWidget, dimensions.sizex, dimensions.col, dimensions.row);
          }
          tempDraggableGridsterWidget = null;
        }
        else {
          searchViewModel.gridItems.push(
              ko.mapping.fromJS({
                col: dimensions.col,
                row: dimensions.row,
                size_x: dimensions.sizex,
                size_y: tempDraggable.gridsterHeight(),
                widget: null,
                emptyProperties: new EmptyGridsterWidget(searchViewModel),
                callback: function (el) {
                  if (!searchViewModel.hasNewAdd() || (searchViewModel.hasNewAdd() &&  ["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(tempDraggable.widgetType()) > -1)) {
                    showAddFacetDemiModal(tempDraggable, searchViewModel.gridItems()[searchViewModel.gridItems().length - 1]);
                  }
                  tempDraggable = null;
                }
              })
          );
        }
      }
      else if (searchViewModel.lastDraggedMeta()) {
        searchViewModel.gridItems.push(
            ko.mapping.fromJS({
              col: dimensions.col,
              row: dimensions.row,
              size_x: dimensions.sizex,
              size_y: 6,
              widget: null,
              emptyProperties: new EmptyGridsterWidget(searchViewModel),
              callback: function (el) {
                showAddFacetDemiModal(null, searchViewModel.gridItems()[searchViewModel.gridItems().length - 1]);
              }
            })
        );
      }
    }

  }, 'dashboard');

  var tempResize = {
    widget: null,
    sibling: null,
    previousWidgetSize: 0,
    previousSiblingSize: 0,
    previousSiblingCol: 0
  }

  function autoResizeSiblings(gridElement, skipRemoveFromGrid, countGridElement) {
    // resize the siblings to the max of the avail space
    var siblings = [];
    searchViewModel.gridItems().forEach(function (siblingWidget) {
      if (siblingWidget.row() === gridElement.row() && gridElement.widgetId() !== siblingWidget.widgetId()) {
        siblings.push(siblingWidget);
      }
    });
    siblings.sort(function (a, b) {
      return a.col() > b.col()
    });
    if (countGridElement) {
      // resize just the first sibling to the right
      siblings = siblings.filter(function (a) {
        return a.col() > gridElement.col();
      });

      if (siblings.length) {
        var widget = siblings[0];
        if (!tempResize.previousSiblingCol) {
          tempResize.previousSiblingCol = widget.col();
          tempResize.previousSiblingSize = widget.size_x();
        }
        var previewSize = $('.resize-preview-holder').attr('data-sizex');
        if (previewSize) {
          var newCol = tempResize.previousSiblingCol - (tempResize.previousWidgetSize - parseInt(previewSize));
          var newWidth = tempResize.previousSiblingSize + (tempResize.previousWidgetSize - parseInt(previewSize));
          if (newCol < 12 && newWidth >= 1) {
            $gridster.move_widget($(widget.gridsterElement), newCol, widget.row());
            widget.col(newCol);
            $gridster.resize_widget($(widget.gridsterElement), newWidth, widget.size_y());
            widget.size_x(newWidth);
          }
        }
      }
    }
    else {
      var optimalWidgetWidth = Math.floor(12 / siblings.length);
      for (var i = 1; i <= siblings.length; i++) {
        var widget = siblings[i - 1];
        $gridster.resize_widget($(widget.gridsterElement), optimalWidgetWidth, widget.size_y());
        widget.size_x(optimalWidgetWidth);
        var newCol = ((i - 1) * optimalWidgetWidth) + 1;
        $gridster.move_widget($(widget.gridsterElement), newCol, widget.row());
        widget.col(newCol);
      }
    }
    if (!skipRemoveFromGrid) {
      searchViewModel.gridItems.remove(gridElement);
    }
    huePubSub.publish('gridster.clean.whitespace');
  }

  huePubSub.subscribe('gridster.remove', autoResizeSiblings, 'dashboard');

  huePubSub.subscribe('gridster.resize.start', function ($widget) {
    searchViewModel.gridItems().forEach(function (item) {
      if (item.widgetId() === parseInt($widget.attr('data-widgetid'))) {
        tempResize.widget = item;
        tempResize.previousWidgetSize = item.size_x();
      }
    });
  }, 'dashboard');

  huePubSub.subscribe('gridster.resize', function () {
    autoResizeSiblings(tempResize.widget, true, true);
  }, 'dashboard');

  huePubSub.subscribe('gridster.resize.stop', function () {
    tempResize.previousSiblingCol = null;
    tempResize.previousSiblingSize = null;
  }, 'dashboard');

  huePubSub.subscribe('gridster.remove.widget', function (widgetId) {
    if (searchViewModel.isGridster()) {
      searchViewModel.gridItems().forEach(function (item) {
        if (item.widgetId() === parseInt($('#wdg_' + widgetId).parents('li.gs-w').attr('data-widgetid'))) {
          huePubSub.publish('gridster.remove', item);
        }
      });
    }
  }, 'dashboard');

  huePubSub.subscribe('gridster.add.widget', function (options) {
    var widget = searchViewModel.getWidgetById(options.id);
    if (widget) {
      var targetHeight = widget.gridsterHeight();
      if (options.target) {
        searchViewModel.gridItems().forEach(function (item) {
          if (item.widgetId() === options.target.widgetId()) {
            if (ko.isObservable(item.widget)) {
              item.widget(widget);
            }
            else {
              item.widget = ko.observable(widget);
            }
            item.size_y(targetHeight);
            $gridster.resize_widget($(item.gridsterElement), parseInt(item.size_x()), parseInt(item.size_y()), function () {
              var $widget = $(item.gridsterElement);
              $widget.attr('data-previous-sizex', $widget.attr('data-sizex'));
              $widget.attr('data-previous-sizey', $widget.attr('data-sizey'));
              $widget.attr('data-previous-col', $widget.attr('data-col'));
              $widget.attr('data-previous-row', $widget.attr('data-row'));
              huePubSub.publish('gridster.clean.whitespace');
            });
          }
        });
      }
      else {
        var newPosition = $gridster.next_position(12, targetHeight);
        searchViewModel.gridItems.push(
            ko.mapping.fromJS({
              col: newPosition.col,
              row: newPosition.row,
              size_x: 12,
              size_y: targetHeight,
              widget: widget,
              callback: function ($el) {
                $gridster.move_widget($el, 1, 1);
                $el.attr('data-previous-sizex', $widget.attr('data-sizex'));
                $el.attr('data-previous-sizey', $widget.attr('data-sizey'));
                $el.attr('data-previous-col', $widget.attr('data-col'));
                $el.attr('data-previous-row', $widget.attr('data-row'));
                huePubSub.publish('gridster.clean.whitespace');
              }
            })
        );
      }
    }
  }, 'dashboard');

  huePubSub.subscribe('dashboard.hide.dimensions', function (event) {
    if (searchViewModel.isGridster() && (!event || (event && !$(event.target).parents('.edit-dimensions').length))) {
      searchViewModel.collection.facets().forEach(function (facet) {
        facet.isAdding(false);
        facet.isEditing(false);
        if (facet.properties && facet.properties.facets && facet.properties.facets()) {
          facet.properties.facets().forEach(function (dimension) {
            dimension.isEditing(false);
          });
        }
      });
    }
  }, 'dashboard');

  huePubSub.subscribe('dashboard.confirm.document', function () {
    $('#addDocumentFacetDemiModal').modal('hide');
    if (selectedWidget != null) {
      if (searchViewModel.tempDocument.parsedStatements().length > 1) {
        // there's no programmatic way to get the selected index from the Selectize API...
        var $dropdown = $('.temp-document-statement')[0].selectize.$dropdown_content;
        if ($dropdown.find('.selected').length > 1) {
          searchViewModel.tempDocument.selectedStatementId($dropdown.find('.selected.active').index());
        }
        else {
          searchViewModel.tempDocument.selectedStatementId($dropdown.find('.selected').index());
        }
      }
      searchViewModel.collection.selectedDocument({
        uuid: searchViewModel.tempDocument.uuid(),
        statement_id: searchViewModel.tempDocument.selectedStatementId(),
        statement: searchViewModel.tempDocument.selectedStatement()
      });
      selectedWidget.hasBeenSelected = true;
      selectedWidget.isLoading(true);
      searchViewModel.collection.addFacet({
        'name': searchViewModel.tempDocument.name() ? searchViewModel.tempDocument.name() : 'Query',
        'widget_id': selectedWidget.id(),
        'widgetType': selectedWidget.widgetType()
      }, function () {
        if (searchViewModel.isGridster()) {
          huePubSub.publish('gridster.add.widget', {id: selectedWidget.id(), target: selectedGridster});
        }
      });
      if (!searchViewModel.isGridster() && selectedRow != null) {
        distributeRowWidgetsSize(selectedRow);
      }
    }

    searchViewModel.tempDocument.reset();
  }, 'dashboard');

  huePubSub.subscribe('app.dom.unload', function (app) {
    if (app === 'dashboard') {
      %if is_report:
      if (window.apiHelper.getFromTotalStorage('assist', 'right_assist_panel_visible', false)) {
        huePubSub.publish('right.assist.show');
      }
      %endif
      $gridster.destroy();
    }
  }, 'dashboard');

  huePubSub.subscribe('split.panel.resized', function () {
    $(window).trigger('resize');
  }, 'dashboard');

  $(document).on("click", ".widget-settings-pill", function () {
    $(this).parents(".card-body").find(".widget-section").hide();
    selectAllCollectionFields(); // Make sure all the collection fields appear
    $(this).parents(".card-body").find(".widget-settings-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-editor-pill", function () {
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-editor-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-html-pill", function () {
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-html-section").show();
    $(document).trigger("refreshCodemirror");
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-css-pill", function () {
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-css-section").show();
    $(document).trigger("refreshCodemirror");
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on('dblclick', 'li.gs-w', normalizeWidgetHeight);

  $('.dashboard-container').on('click', function (e) {
    huePubSub.publish('dashboard.hide.dimensions', e);
  });

  $(document).on("magicSearchLayout", function () {
    resizeFieldsList();
  });

  $(document).on("setLayout", function () {
    resizeFieldsList();
  });

  huePubSub.subscribe('gridChartForceUpdate', function () {
    window.setTimeout(function () {
      $('.grid-chart-container').children().trigger('forceUpdate')
    }, 200);
  });


  var _query = ${ query | n,unicode };

  loadSearch(${ collection.get_json(user) | n,unicode }, ${ query | n,unicode }, ${ initial | n,unicode });


  $("#addFacetDemiModal").on("hidden", function () {
    if (typeof selectedWidget.hasBeenSelected == "undefined"){
      addFacetDemiModalFieldCancel();
    }
  });
  $(document).off("shownAnalysis");
  $(document).on("shownAnalysis", function (e, originalEvent) {
    if (originalEvent.pageX == null && originalEvent.clientX != null) {
      var doc = document.documentElement, body = document.body;
      originalEvent.pageX = originalEvent.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);
      originalEvent.pageY = originalEvent.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc && doc.clientTop || body && body.clientTop || 0);
    }
    if ($('#searchComponents').offset().left > 0) {
      originalEvent.pageX = originalEvent.pageX - $('#searchComponents').offset().left;
      originalEvent.pageY = originalEvent.pageY - $('#searchComponents').offset().top;
    }
    $("#fieldAnalysis").show().css({
      top: Math.max(0, originalEvent.pageY - $("#fieldAnalysis").outerHeight() / 2),
      left: originalEvent.pageX
    })
  });

  $('#searchComponents .dashboard').droppable({
    accept: '.draggable-widget, .draggableText, .card-widget, .draggable-plus-button',
    drop: function( event, ui ) {
      if (searchViewModel.isGridster()) {
        huePubSub.publish('dashboard.drop.on.page', {event: event, ui: ui});
      }
    }
  });

  huePubSub.subscribe('open.link', function(link) {
    $(window).unbind("keydown.search");
  });

  % if is_owner:
  $(window).bind("keydown.search", "ctrl+s alt+s meta+s", function(e){
    e.preventDefault();
    if (searchViewModel.canSave()) {
      searchViewModel.save();
    } else {
      $('#saveAsModalDashboard').modal('show');
    }
    return false;
  });
  % endif

  $(window).bind("keydown.search", "esc", function () {
    if ($(".demi-modal.fade.in").length > 0) {
      $(".demi-modal.fade.in .demi-modal-chevron").click();
    }
    huePubSub.publish('dashboard.hide.dimensions');
  });

  $("#newqname").bind("keydown.search", "return", function (e) {
    e.preventDefault();
    searchViewModel.collection.addQDefinition();
  });

  $(document).on("loadedQDefinition", function() {
    if ($(".demi-modal.fade.in").length > 0) {
      $(".demi-modal.fade.in .demi-modal-chevron").click();
    }
  });

  function loadQueryDefinition(id) {
    var _qdef = searchViewModel.collection.getQDefinition(id);
    if (_qdef != null) {
      searchViewModel.collection.loadQDefinition(_qdef);
    }
  }

  if (window.location.hash != "" && window.location.hash.indexOf("qd=") > -1) {
    loadQueryDefinition(window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "").split("=")[1]);
  }
  else if (_query.qd) {
    loadQueryDefinition(_query.qd);
  }

});

  function throttledHeaderPadding(e) {
    $resultMain = $(e.target);
    $resultMain.find("thead>tr th").each(function () {
      var leftPosition = $(this).position().left - $resultMain.position().left;
      if (leftPosition + $(this).outerWidth() > 0 && leftPosition < 0) {
        if ($(this).find('span').width() + -leftPosition < $(this).outerWidth() - 20) { // 20 is the sorting css width
          $(this).find('span').css('paddingLeft', -leftPosition);
        }
      }
      else {
        $(this).find('span').css('paddingLeft', 0);
      }
    });
  }

  var throttledScrollTimeout = -1;
  function throttledHeaderScroll() {
    window.clearTimeout(throttledScrollTimeout);
    throttledScrollTimeout = window.setTimeout(function(){
      var scrollTimeout = -1;
      $('.result-main').off('scroll');
      $('.result-main').on('scroll', function (e) {
        window.clearTimeout(scrollTimeout);
        scrollTimeout = window.setTimeout(function(){
          throttledHeaderPadding(e);
        }, 200);
      });
    }, 200);
  }


  function toggleGridFieldsSelection(widget) {
    if (widget.widgetType() == 'resultset-widget') {
      searchViewModel.resultsHash = '';
    } else {
      widget.resultsHash = '';
    }

    if (widget.template.fields().length > 0) {
      widget.template.fieldsSelected.removeAll();
    }
    else {
      selectAllCollectionFields(widget);
    }
  }

  function selectAllCollectionFields(widget) {
    if (! widget) {
      widget = searchViewModel.collection;
    }
    var _fields = [];
    $.each(widget.fields(), function (index, field) {
      _fields.push(field.name());
    });
    widget.template.fieldsSelected(_fields);
  }

  function columnDropAdditionalHandler(widget) {
    if (searchViewModel.collection.getFacetById(widget.id()) == null) {
      showAddFacetDemiModal(widget);
    }
  }

  function widgetDraggedAdditionalHandler(widget, row) {
    showAddFacetDemiModal(widget, row);
  }

  function distributeRowWidgetsSize(row, waitForIt) {
    if (row) {
      if (waitForIt) {
        var _initial = row.widgets().length;
        var _widgetDropInterval = window.setInterval(function () {
          if (row.widgets().length != _initial) {
            window.clearInterval(_widgetDropInterval);
            row.autosizeWidgets();
          }
        }, 100, 'dashboard')
      }
      else {
        row.autosizeWidgets();
      }
    }
  }

  var selectedWidget = null;
  var selectedRow = null;
  var selectedGridster = null;

  function showAddFacetDemiModal(widget, target) {
    if (searchViewModel.isGridster()) {
      selectedGridster = target;
      if (widget && widget.id) {
        var fakeRow = searchViewModel.columns()[0].addEmptyRow(true);
        fakeRow.addWidget(widget);

        if (["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(widget.widgetType()) == -1) {
          searchViewModel.collection.template.fieldsModalFilter("");
          searchViewModel.collection.template.fieldsModalType(widget.widgetType());

          selectedWidget = widget;

          if (widget.widgetType() == 'document-widget') {
            $("#addDocumentFacetDemiModal").modal("show");
          }
          else {
            if (searchViewModel.collection.template.availableWidgetFields().length == 1) {
              addFacetDemiModalFieldPreview(searchViewModel.collection.template.availableWidgetFields()[0]);
            }
            else {
              $("#addFacetDemiModal").modal("show");
              $("#addFacetDemiModal input[type='text']").focus();
            }
          }
        }
        else {
          huePubSub.publish('gridster.add.widget', {id: widget.id(), target: target});
        }
      }
      else if (searchViewModel.lastDraggedMeta() && searchViewModel.lastDraggedMeta().type === 'sql' && searchViewModel.lastDraggedMeta().column && searchViewModel.collection.template.availableWidgetFieldsNames().indexOf(searchViewModel.lastDraggedMeta().column) > -1) {
        if (searchViewModel.collection.supportAnalytics()) {
          selectedWidget = searchViewModel.draggableBucket();
        }
        else {
          selectedWidget = searchViewModel.draggableBar();
        }
        var fakeRow = searchViewModel.columns()[0].addEmptyRow(true);
        var widgetClone = ko.mapping.toJS(selectedWidget);
        widgetClone.id = hueUtils.UUID();
        selectedWidget = new Widget(widgetClone);
        fakeRow.addWidget(selectedWidget);
        addFacetDemiModalFieldPreview({
          'name': function () {
            return searchViewModel.lastDraggedMeta().column
          }
        });
      }
    }
    else {
      if (["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(widget.widgetType()) == -1) {
        searchViewModel.collection.template.fieldsModalFilter("");
        searchViewModel.collection.template.fieldsModalType(widget.widgetType());

        selectedWidget = widget;
        selectedRow = target;

        if (searchViewModel.collection.template.availableWidgetFields().length == 1) {
          addFacetDemiModalFieldPreview(searchViewModel.collection.template.availableWidgetFields()[0]);
        }
        else {
          $("#addFacetDemiModal").modal("show");
          $("#addFacetDemiModal input[type='text']").focus();
        }
      }
      else {
        distributeRowWidgetsSize(target, true);
      }
    }
  }

  function addFacetDemiModalFieldPreview(field) {
    var _existingFacet = searchViewModel.collection.getFacetById(selectedWidget.id());
    if (selectedWidget != null) {
      selectedWidget.hasBeenSelected = true;
      selectedWidget.isLoading(true);
      searchViewModel.collection.addFacet({
        'name': field ? field.name() : 'Query',
        'widget_id': selectedWidget.id(),
        'widgetType': selectedWidget.widgetType()
      }, function () {
        if (searchViewModel.isGridster()) {
          huePubSub.publish('gridster.add.widget', {id: selectedWidget.id(), target: selectedGridster});
        }
      });
      if (_existingFacet != null) {
        _existingFacet.label(field.name());
        _existingFacet.field(field.name());
      }
      $("#addFacetDemiModal").modal("hide");
      if (!searchViewModel.isGridster() && selectedRow != null) {
        distributeRowWidgetsSize(selectedRow);
      }
    }
  }

  function addFacetDemiModalFieldCancel() {
    if (searchViewModel.isGridster()) {
      searchViewModel.gridItems.remove(selectedGridster);
    }
    searchViewModel.removeWidget(selectedWidget);
    selectedRow = null;
  }

  $(document).on("setResultsHeight", function () {
    $('.result-main').each(function(){
      $resultMain = $(this);
      $resultMain.height($resultMain.parents('.card-widget').find('.result-container').outerHeight() + 30);
    });
    resizeFieldsList();
  });

  function highlightColumn(column, e) {
    var $resultContainer = $(e.target).parents('.card-widget').find('.result-container');
    var _colName = $.trim(column.name());
    if (searchViewModel.collection.template.fieldsSelected.indexOf(_colName) > -1) {
      var _t = $resultContainer;
      var _col = _t.find("th").filter(function () {
        return $.trim($(this).text()) == _colName;
      });
      if (_t.find("tr td:nth-child(" + (_col.index() + 1) + ").columnSelected").length == 0) {
        _t.find(".columnSelected").removeClass("columnSelected");
        _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
        _t.parent().animate({
          scrollLeft: _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
        }, 300);
      }
      else {
        _t.find(".columnSelected").removeClass("columnSelected");
      }
    }
  }

  function checkResultHighlightingAvailability() {
    if (! searchViewModel.collection.idField()) {
      $(document).trigger("warn", "${ _('Result highlighting is unavailable: the collection does not have an index field') }");
    }
  }
</script>

</%def>
