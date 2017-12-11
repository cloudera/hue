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

from dashboard.conf import USE_GRIDSTER, HAS_REPORT_ENABLED
%>

<%namespace name="dashboard" file="common_dashboard.mako" />

<%def name="page_structure(is_mobile=False, is_embeddable=False)">

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
<div class="search-bar" data-bind="visible: ! $root.isPlayerMode()">
  <div class="search-bar-header">
    <div class="search-bar-logo">
      <div class="app-header">
        <a href="#" data-bind="hueLink: '${ url('dashboard:new_search') }'">
          <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Dashboard') }
          <!-- ko component: { name: 'hue-favorite-app', params: { hue4: IS_HUE_4, app: 'dashboard' }} --><!-- /ko -->
        </a>
      </div>
    </div>
    <div class="search-bar-middle">
      <form class="form-search" data-bind="visible: $root.isEditing() && columns().length == 0, submit: function() { return false }">
        <!-- ko if: $root.initial.engines().length > 1 -->
        <select class="input-medium" data-bind="options: $root.initial.engines, value: $root.collection.engine, optionsText: 'name',  optionsValue: 'type', disable: isSyncingCollections"></select>
        <!-- /ko -->
        <!-- ko ifnot: $root.initial.engines().length > 1 -->
        ${_('index')}
        <!-- /ko -->

        <!-- ko if: $root.collection.engine() == 'solr' -->
        <!-- ko if: columns().length == 0 -->
        <select data-bind="options: $root.initial.collections, value: $root.collection.name, disable: isSyncingCollections"></select>

        <label class="checkbox" style="display:inline-block; margin-left: 10px">
          <i class="fa fa-spinner fa-spin" data-bind="visible: isSyncingCollections"></i>
        </label>
        <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: $root.collection.engine() != 'solr' -->
        <!-- ko if: columns().length == 0 -->
        <input type="text" class="no-margin" data-bind="hivechooser: $root.collection.name, skipColumns: true, apiHelperUser: '${ user }', apiHelperType: $root.collection.engine()" placeholder="${ _('Table name or <database>.<table>') }" style="margin-top: 1px">
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
          <div class="search-bar-collection">
            <div class="selectMask">
              <span data-bind="editable: collection.label, editableOptions: { enabled: $root.isEditing(), placement: 'right' }"></span>
            </div>
          </div>
          <div class="search-bar-query" data-bind="foreach: query.qs">

            <div data-bind="component: { name: 'hue-simple-ace-editor', params: {
              value: q,
              onExec: $parent.searchBtn,
              placeHolder: $root.collection.engine() === 'solr' ? '${ _ko('Example: field:value, or press CTRL + space') }' : '${ _ko('Example: col = value, or press CTRL + space') }',
              autocomplete: { type: $root.collection.engine() + 'Query', support: { collection: $root.collection } },
              mode: $root.collection.engine(),
              singleLine: true }
            }"></div>
##             <input data-bind="clearable: q, valueUpdate:'afterkeydown', typeahead: { target: q, nonBindableSource: queryTypeahead, multipleValues: true, multipleValuesSeparator: ':', extraKeywords: 'AND OR TO', completeSolrRanges: true }, css: {'input-small': $root.query.qs().length > 1, 'flat-left': $index() === 0, 'input-xlarge': $root.collection.supportAnalytics()}" maxlength="4096" type="text" class="search-query">
            <!-- ko if: $index() >= 1 -->
              <a class="btn flat-left" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
            <!-- /ko -->
          </div>
          <div class="search-bar-query-operations">
            <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ, css: { 'flat-left': $root.query.qs().length === 1}, style: { 'margin-left': $root.query.qs().length > 1 ? '10px' : '0' }, visible: ! collection.supportAnalytics()">
              <i class="fa fa-plus"></i>
            </a>

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
      % if USE_GRIDSTER.get():
      <a class="btn pointer" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="visible: columns().length, click: function() { isToolbarVisible(!isToolbarVisible()) }, css: {'btn': true, 'btn-inverse': isToolbarVisible }">
        <i class="fa fa-plus"></i>
      </a>
      % endif
      <a class="btn pointer" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
        <i class="fa fa-pencil"></i>
      </a>
      % if is_owner:
        <a class="btn pointer" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: save, css: {'btn': true}, visible: columns().length != 0">
          <i class="fa fa-save"></i>
        </a>
      % endif

      <div class="dropdown pull-right margin-left-10">
        <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
          <i class="fa fa-fw fa-ellipsis-v"></i>
        </a>
        <ul class="dropdown-menu">
          <li>
            <a href="javascript:void(0)" data-bind="click: newSearch">
              <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
            </a>
          </li>
          <!-- ko if: IS_HUE_4 -->
          <li>
            <a href="/home/?type=search-dashboard">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> ${ _('Dashboards') }
            </a>
          </li>
          <!-- /ko -->
          <!-- ko ifnot: IS_HUE_4 -->
          <li>
            <a href="${ url('dashboard:admin_collections') }">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> ${ _('Dashboards') }
            </a>
          </li>
          <!-- /ko -->
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

<%dashboard:layout_toolbar>
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

    <div data-bind="visible: $root.collection.supportAnalytics,
                    css: { 'draggable-widget': true, 'disabled': !hasAvailableFields() },
                    draggable: {data: draggableCounter(), isEnabled: hasAvailableFields,
                    options: getDraggableOptions({ data: draggableCounter()}) }"
         title="${_('Counter')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.hasAvailableFields() ? 'move' : 'default' }">
                       <i class="fa fa-superscript" style="font-size: 110%"></i>
         </a>
    </div>
      </%def>

      <%def name="widgets()">
    <div data-bind="visible: ! $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
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
         title="${_('Text Facet')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sort-amount-asc"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
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
    <div data-bind="visible: ! $root.collection.supportAnalytics(),
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
         title="${_('Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-bar-chart"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': !availableDraggableNumbers() },
                    draggable: {data: draggableLine(), isEnabled: availableDraggableNumbers,
                    options: getDraggableOptions({ data: draggableLine() }) }"
         title="${_('Line Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableNumbers() ? 'move' : 'default' }">
                       <i class="hcha hcha-line-chart"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableTree(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableTree() }) }"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
    </div>
    <div data-bind="visible: $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableTree2(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableTree2() }) }"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableHeatmap(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableHeatmap() }) }"
         title="${_('Heatmap')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-th"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram,
                    options: getDraggableOptions({ data: draggableHistogram() }) }"
         title="${_('Timeline')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableHistogram() ? 'move' : 'default' }">
                       <i class="hcha hcha-timeline-chart"></i>
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
    <div data-bind="visible: ! $root.collection.supportAnalytics(), css: { 'draggable-widget': true, 'disabled': ! availableDraggableMap() },
                    draggable: {data: draggableMap(), isEnabled: availableDraggableMap,
                    options: getDraggableOptions({ data: draggableMap() }) }"
         title="${_('Gradient Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableMap() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
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
    % if HAS_REPORT_ENABLED.get():
    <div data-bind="visible: $root.collection.supportAnalytics(),
                    css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableDocument(), isEnabled: true,
                    options: getDraggableOptions({ data: draggableDocument() }) }"
         title="${_('Document')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
                       <i class="fa fa-file-o"></i>
         </a>
    </div>
    % endif
      </%def>
</%dashboard:layout_toolbar>

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
        <div data-bind="daterangepicker: {start: properties.start, end: properties.end, gap: properties.initial_gap, relatedgap: properties.gap, min: properties.min, max: properties.max}"></div>
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

  <ul data-bind="sortable: { data: properties.facets, allowDrop: false, options: { axis: 'x', containment: 'parent', handle: '.title' }}" class="unstyled pull-left white">
    <li class="filter-box">
      <div class="title move">
        <a data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }, visible: $parent.properties.facets().length > 1" class="pull-right" href="javascript:void(0)">
          <i class="fa fa-times"></i>
        </a>
        <div class="hit-title" data-bind="text: field, attr: {'title': field}"></div>
        <div class="clearfix"></div>
      </div>

      <div class="content">
        <div class="facet-field-cnt">
          <span class="spinedit-cnt">
            <span data-bind="template: { name: 'metric-form' }"></span>
          </span>
        </div>
      </div>
    </li>
  </ul>
  <!-- /ko -->

  <!-- ko ifnot: $root.isEditing -->
  <span data-bind="foreach: properties.facets, visible: ! $parents[1].isLoading()">
    <div class="filter-box" style="opacity: 0.7">
      <div class="content content-readonly">
        <strong class="hit-title" data-bind="text: field, attr: {'title': field}"></strong>
        <span class="spinedit-cnt">
          <span data-bind="template: { name: 'metric-form' }"></span>
        </span>
      </div>
    </div>
  </span>
  <!-- /ko -->

  <div class="filter-box" data-bind="visible: $root.isEditing() && properties.facets().length < 15 && widgetType() != 'hit-widget'" style="opacity: 0.7">
    <div class="title" style="border: 1px dashed #d8d8d8; border-bottom: none">
      <a data-bind="visible: properties.facets_form.field() && properties.facets_form.field() != 'formula' || properties.facets_form.aggregate.formula(), click: $root.collection.addPivotFacetValue2" class="pull-right" href="javascript:void(0)">
        <i class="fa fa-fw fa-plus"></i> ${ _('Add') }
      </a>
    </div>
    <div class="content" style="border: 1px dashed #d8d8d8; border-top: none">
      <div class="facet-field-cnt">
        <span class="spinedit-cnt">
          <span class="facet-field-label"></span>
          <span data-bind="template: { name: 'metric-form', data: properties.facets_form }"></span>
        </span>
      </div>
    </div>
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
                <!-- ko if: ! $data.selected -->
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
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle2', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>
    <div class="clearfix"></div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: properties.facets()[0].type() == 'field' -->
        <div data-bind="foreach: $parent.counts">
          <div class="trigger-exclude">
              <!-- ko if: $index() < $parent.properties.limit() -->
                <!-- ko if: ! $data.selected -->
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
      <!-- ko if: properties.facets()[0].type() == 'range' -->
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
      <!-- ko if: properties.facets()[0].type() == 'range-up' -->
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
<!-- ko if: $parent.widgetType() == 'resultset-widget' -->
  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
    <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP, ko.HUE_CHARTS.TYPES.PIECHART].indexOf(chartType()) == -1" class="nav-header">${_('x-axis')}</li>
    <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('region')}</li>
    <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
    <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('legend')}</li>
  </ul>
  <div data-bind="visible: chartType() != ''">
    <select data-bind="options: (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.PIECHART) ? $root.collection.template.cleanedMeta : $root.collection.template.cleanedNumericMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartX}" class="input-medium"></select>
  </div>

  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
    <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP, ko.HUE_CHARTS.TYPES.PIECHART].indexOf(chartType()) == -1" class="nav-header">${_('y-axis')}</li>
    <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
    <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('value')}</li>
  </ul>

  <div style="overflow-y: auto; max-height: 220px" data-bind="visible: chartType() != '' && (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.LINECHART)">
    <ul class="unstyled" data-bind="foreach: $root.collection.template.cleanedNumericMeta">
      <li><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></li>
    </ul>
  </div>
  <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART || chartType() == ko.HUE_CHARTS.TYPES.MAP">
    <select data-bind="options: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP ? $root.collection.template.cleanedMeta : $root.collection.template.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartYSingle}" class="input-medium"></select>
  </div>

  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.MAP">
    <li class="nav-header">${_('label')}</li>
  </ul>
  <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP">
    <select data-bind="options: $root.collection.template.cleanedMeta, value: chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartMapLabel}" class="input-medium"></select>
  </div>


  <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP">
    <li class="nav-header">${_('sorting')}</li>
  </ul>
  <div class="btn-group" data-toggle="buttons-radio" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP">
    <a rel="tooltip" data-placement="top" title="${_('No sorting')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'none'}, click: function(){ chartSorting('none'); }"><i class="fa fa-align-left fa-rotate-270"></i></a>
    <a rel="tooltip" data-placement="top" title="${_('Sort ascending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'asc'}, click: function(){ chartSorting('asc'); }"><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
    <a rel="tooltip" data-placement="top" title="${_('Sort descending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'desc'}, click: function(){ chartSorting('desc'); }"><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
  </div>
<!-- /ko -->

</script>

<script type="text/html" id="html-resultset-widget">
  <!-- ko ifnot: $root.collection.template.isGridLayout() -->
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <ul class="nav nav-pills">
        <li class="active"><a href="javascript: void(0)" class="widget-editor-pill">${_('Editor')}</a></li>
        <li><a href="javascript: void(0)" class="widget-html-pill">${_('HTML')}</a></li>
        <li><a href="javascript: void(0)" class="widget-css-pill">${_('CSS & JS')}</a></li>
        <li><a href="javascript: void(0)" class="widget-settings-pill">${_('Sorting')}</a></li>
      </ul>
    </div>

    <!-- ko if: $root.isEditing() -->
      <div class="widget-section widget-editor-section">
        <div class="row-fluid">
          <div class="span9">
            <div data-bind="freshereditor: {data: $root.collection.template.template}"></div>
          </div>
          <div class="span3">
            <h5 class="editor-title">${_('Available Fields')}</h5>
            <select data-bind="options: $root.collection.fields, optionsText: 'name', value: $root.collection.template.selectedVisualField" class="input-large chosen-select"></select>
            <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFieldToVisual">
              <i class="fa fa-plus"></i>
            </button>

            <h5 class="editor-title" style="margin-top: 30px">${_('Available Functions')}</h5>
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
            <button title="${ _('Click on this button to add the function') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFunctionToVisual">
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
            <h5 class="editor-title">${_('Available Fields')}</h5>
            <select data-bind="options: $root.collection.fields, optionsText: 'name', value: $root.collection.template.selectedSourceField" class="input-medium chosen-select"></select>
            <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFieldToSource">
              <i class="fa fa-plus"></i>
            </button>

            <h5 class="editor-title" style="margin-top: 30px">${_('Available Functions')}</h5>
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
    <!-- /ko -->

    <div class="result-main" style="overflow-x: auto">
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

      <div class="widget-spinner" data-bind="visible: ! $root.hasRetrievedResults()">
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
    <div class="document-details-actions pull-left" data-bind="visible: ${ 'true' if can_edit_index else 'false' } || externalLink()">
      <a href="javascript:void(0)" data-bind="visible: ! showEdit(), click: function() { showEdit(true); }" title="${ _('Edit this document') }">
        <i class="fa fa-edit fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: showEdit(), click: function(data, e) { $(e.currentTarget).parent().css('marginTop', '8px'); $root.getDocument($data); showEdit(false); }" title="${ _('Undo changes') }">
        <i class="fa fa-undo fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: showEdit() && originalDetails() != ko.toJSON(details), click: $root.updateDocument" title="${ _('Update this document') }">
        <i class="fa fa-save fa-fw"></i>
      </a>
      <a href="javascript:void(0)" data-bind="visible: externalLink(), attr: { href: externalLink}" target="_blank" title="${ _('Show original document') }">
        <i class="fa fa-external-link fa-fw"></i>
      </a>
    </div>
    <div class="document-details pull-left">
      <table class="table table-condensed">
        <tbody data-bind="foreach: details">
          <tr data-bind="css: {'readonly': ! $parent.showEdit()}">
             <th class="grid-th" data-bind="text: key"></th>
             <td width="100%">
               <span data-bind="text: value, visible: ! $parent.showEdit()"></span>
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
    <!-- ko if: $root.isEditing -->
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
  <span data-bind="text: Math.min(($data.response.start + ($parent.template ? $parent : $root.collection).template.rows()), $data.response.numFound)"></span>
  ${ _('of') }
  <span data-bind="text: $data.response.numFound"></span>
  ${ _(' results') }

  <span data-bind="visible: $root.isEditing()">
    ${ _('Show') }
    <span class="spinedit-cnt">
      <input type="text" data-bind="spinedit: ($parent.template ? $parent : $root.collection).template.rows, valueUpdate:'afterkeydown'" style="text-align: center; margin-bottom: 0" />
    </span>
    ${ _('results per page') }
  </span>

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
        <span class="facet-field-label">${ _('Chart Type') }</span>
        <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
        </select>&nbsp;
        <span class="facet-field-label">${ _('Interval') }</span>
        <select class="input-small" data-bind="options: $root.intervalOptions,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.gap">
        </select>&nbsp;
      </span>
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
      <span class="facet-field-label" data-bind="visible: $root.query.multiqs().length > 1">${ _('Group by') }</span>
      <select class="input-medium" data-bind="visible: $root.query.multiqs().length > 1, options: $root.query.multiqs, optionsValue: 'id', optionsText: 'label', value: $root.query.selectedMultiq"></select>
    </div>

    <!-- ko if: $root.collection.getFacetById($parent.id()) -->
      <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), enableSelection: $root.collection.getFacetById($parent.id()).properties.enableSelection(), field: field, label: label(), transformer: timelineChartDataTransformer,
        type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
        fqs: $root.query.fqs,
        onSelectRange: function(from, to){ $root.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
        onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); $root.collection.getFacetById($parent.id()).properties.enableSelection(state.selectionEnabled); },
        onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
        onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false) }}" />
      <div class="clearfix"></div>
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
      <span data-bind="with: $root.collection.getFacetById($parent.id())">
        <span class="facet-field-label">${ _('Chart Type') }</span>
        <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
        </select>&nbsp;
        <span class="facet-field-label">${ _('Interval') }</span>
        <select class="input-small" data-bind="options: $root.intervalOptions,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.facets()[0].gap">
        </select>&nbsp;
      </span>
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut2"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
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
    <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(),
      fqs: $root.query.fqs,
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
      onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
    />
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
             data-bind="click: function(){ template.showChart(false); template.showGrid(true); }, css: {'active': template.showGrid() }" title="${_('Grid')}">
            <i class="fa fa-th fa-fw"></i>
          </a>
        </div>

        <div class="dropdown">
          <a class="grid-side-btn" style="padding-right:0" href="javascript:void(0)"
             data-bind="css: {'active': template.showChart() }, click: function(){ template.showChart(true); template.showGrid(false); huePubSub.publish('gridChartForceUpdate'); }">
            <i class="hcha hcha-bar-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.BARCHART"></i>
            <i class="hcha hcha-line-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.LINECHART" style="display: none;"></i>
            <i class="hcha hcha-pie-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.PIECHART" style="display: none;"></i>
            <i class="fa fa-fw fa-line-chart" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART" style="display: none;"></i>
            <i class="hcha hcha-map-chart fa-fw" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" style="display: none;"></i>
            <i class="fa fa-fw fa-map-marker" data-bind="visible: template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.MAP" style="display: none;"></i>
          </a>
          <a class="dropdown-toggle grid-side-btn" style="padding:0" data-toggle="dropdown"
             href="javascript: void(0)" data-bind="css: {'active': template.showChart()}">
            <i class="fa fa-caret-down"></i>
          </a>

          <ul class="dropdown-menu">
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.BARCHART}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.BARCHART); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}"
                 class="active">
                <i class="hcha hcha-bar-chart fa-fw"></i> ${_('Bars')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.LINECHART}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.LINECHART); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}">
                <i class="hcha hcha-line-chart fa-fw"></i> ${_('Lines')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.PIECHART}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.PIECHART); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}">
                <i class="hcha hcha-pie-chart fa-fw"></i> ${_('Pie')}
              </a>
            </li>
            ##<!-- ko if: widgetType() != 'resultset-widget' -->
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.TIMELINECHART); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}">
                <i class="fa fa-fw fa-line-chart"></i> ${_('Timeline')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.GRADIENTMAP); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}">
                <i class="hcha fa-fw hcha-map-chart chart-icon"></i> ${_('Gradient Map')}
              </a>
            </li>
            <li>
              <a href="javascript:void(0)"
                 data-bind="css: {'active': template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.MAP}, click: function(){ template.showChart(true); template.chartSettings.chartType(ko.HUE_CHARTS.TYPES.MAP); template.showGrid(false); huePubSub.publish('gridChartForceUpdate');}">
                <i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}
              </a>
            </li>
          </ul>
        </div>

        <div data-bind="visible: template.showGrid() || (template.showChart() && widgetType() === 'resultset-widget')">
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
        <form method="POST" action="${ url('dashboard:download') }" style="display:inline">
          ${ csrf_token(request) | n,unicode }
          <input type="hidden" name="collection" data-bind="value: ko.mapping.toJSON($root.collection)"/>
          <input type="hidden" name="query" data-bind="value: ko.mapping.toJSON($root.query)"/>
          <input type="hidden" name="download">
          <input type="hidden" name="type" value="">
          ## Similar to isGridLayout
          <!-- ko if: widgetType() != 'resultset-widget' -->
            <input type="hidden" name="facet" data-bind="value: ko.mapping.toJSON($data)">
          <!-- /ko -->
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
        <div style="border-bottom: 1px solid #CCC; padding-bottom: 4px;">
          <a href="javascript: void(0)" class="btn btn-mini"
            data-bind="click: toggleGridFieldsSelection, css: { 'btn-inverse': template.fields().length > 0 }"
            style="margin-right: 2px;">
            <i class="fa fa-square-o"></i>
          </a>
          <strong>${_('Field Name')}</strong>
        </div>
        <div data-bind="visible: template.filteredAttributeFields().length == 0" style="padding-left:4px; padding-top:5px; color:#CCC">
          ${ _('No matches.') }
        </div>
        <div class="fields-list" data-bind="foreach: { data: template.filteredAttributeFields, afterRender: resizeFieldsListThrottled }">
          <div style="margin-bottom: 3px; white-space: nowrap; position:relative">
            <input type="checkbox" data-bind="checkedValue: name, checked: $parent.template.fieldsSelected" style="margin: 0" />
            <div data-bind="text: name, css:{'field-selector': true, 'hoverable': $parent.template.fieldsSelected.indexOf(name()) > -1}, click: highlightColumn, attr: {'title': name() + ' (' + type() + ')'}" style="margin-right:10px"></div>
            <i class="fa fa-question-circle muted pointer analysis" data-bind="click: function(data, e) { $root.fieldAnalysesName(name()); $root.showFieldAnalysis(data, e); }, attr: {'title': '${ _ko('Analyze') }'}, visible: type() != 'aggr'" style="position:absolute; left: 168px; background-color: #FFF"></i>
          </div>
        </div>
      </div>

      <div data-bind="visible: template.showFieldList() && template.showChart() &&  widgetType() === 'resultset-widget'" style="float:left; width:200px; margin-right:10px; background-color:#FFF; padding:5px;">
        <span data-bind="template: {name: 'grid-chart-settings', data: template.chartSettings}"></span>
      </div>
    </span>

      <div class="widget-spinner" data-bind="visible: ! $parent.hasRetrievedResults() || ! $parent.response().response">
        <i class="fa fa-spinner fa-spin"></i>
      </div>

      <div data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length == 0 && $parent.response().response">
        <br/>
        ${ _('Your search did not match any documents.') }
      </div>

      <div data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length > 0 && template.showGrid()">
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
                    &nbsp(<span data-bind="text: doc.childDocuments().length"></span>)
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

      <div data-bind="visible: $parent.hasRetrievedResults() && $parent.results().length > 0 && template.showChart()">
        <div data-bind="visible: ! template.hasDataForChart()" style="padding: 10px">${ _('Please select the chart parameters on the left.') }</div>
        <div class="grid-chart-container" data-bind="visible: template.hasDataForChart" style="overflow-x: auto">

        <!-- ko if: widgetType() == 'bucket-widget' -->
          <!-- ko with: $parent -->

          <!-- ko if: dimension() == 1 -->
            <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(),
              fqs: $root.query.fqs,
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
              onSelectRange: function(from, to){ searchViewModel.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
              onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
            />
            <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: dimension() == 2 -->
            <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(),
              isPivot: true,
              fqs: $root.query.fqs,
              transformer: pivotChartDataTransformer,
              onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
              onClick: function(d) {
                $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
              },
              onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
            />
            <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: dimension() == 3 -->
          <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
            type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
            fqs: $root.query.fqs,
            onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
            onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
            onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
            onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false) }}" />
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
              onComplete: function(){ var widget = searchViewModel.getWidgetById($parent.id()); if (widget != null) { widget.isLoading(false)}; } }" />
           <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'timeline-widget' -->
          <!-- ko with: $parent -->
          <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
            type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
            fqs: $root.query.fqs,
            onSelectRange: function(from, to){ $root.collection.selectTimelineFacet2({from: from, to: to, cat: field, widget_id: $parent.id()}) },
            onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
            onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
            onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false) }}" />
          <div class="clearfix"></div>
          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'pie2-widget' -->
          <!-- ko if: type() == 'range' -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: rangePieChartDataTransformer,
            maxWidth: 250,
            onClick: function(d){ searchViewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
          <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: type() == 'range-up' -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: rangeUpPieChartDataTransformer,
            rangeUp: true,
            maxWidth: 250,
            onClick: function(d){ searchViewModel.query.selectRangeUpFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field, 'exclude': false, is_up: d.data.obj.is_up}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
          <div class="clearfix"></div>
          <!-- /ko -->

          <!-- ko if: type().indexOf('range') == -1 -->
          <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
            transformer: pieChartDataTransformer,
            maxWidth: 250,
            onClick: function(d){ searchViewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id}) },
            onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
          <div class="clearfix"></div>
          <!-- /ko -->
        <!-- /ko -->

        <!-- ko if: widgetType() == 'resultset-widget' -->
          <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                transformer: pieChartDataTransformerGrid, maxWidth: 350, parentSelector: '.chart-container' }, visible: $root.collection.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>

          <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true,
                transformer: multiSerieDataTransformerGrid, stacked: false, showLegend: true},  stacked: true, showLegend: true, visible: $root.collection.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>

          <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data},
                transformer: multiSerieDataTransformerGrid, showControls: false }, visible: $root.collection.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>

          <div data-bind="attr: {'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: $root.results(), sorting: $root.collection.template.chartSettings.chartSorting(), snippet: $data},
                transformer: leafletMapChartDataTransformerGrid, showControls: false, height: 380, visible: $root.collection.template.chartSettings.chartType() == ko.HUE_CHARTS.TYPES.MAP, forceRedraw: true}" class="chart"></div>
          <div class="clearfix"></div>
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

      <input type="text" class="input-medium" data-bind="value: properties.engine"/>
      <textarea data-bind="value: properties.statement"><textarea/>

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

      <div class="pull-right" style="margin-top: 40px">

      <!-- ko if: properties.isDate -->
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px">
          <span class="facet-field-label">${ _('Chart Type') }</span>
          <select class="input-small" data-bind="options: $root.timelineChartTypes,
                       optionsText: 'label',
                       optionsValue: 'value',
                       value: properties.timelineChartType">
          </select>
        </div>
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px">
          <span class="facet-field-label">${ _('Interval') }</span>
          <select class="input-small" data-bind="options: $root.intervalOptions,
                         optionsText: 'label',
                         optionsValue: 'value',
                         value: properties.gap">
          </select>
        </div>
      <!-- /ko -->

      <!-- ko if: properties.canRange -->
        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px">
          <span class="facet-field-label">${ _('Zoom') }</span>
          <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
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

    <div data-bind="lineChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, field: field, label: label(),
      transformer: lineChartDataTransformer,
      onClick: function(d){ searchViewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onSelectRange: function(from, to){ searchViewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
    />
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
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
      <div class="clearfix"></div>
      <!-- /ko -->
      <!-- ko if: type() == 'range-up' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: rangeUpPieChartDataTransformer,
        rangeUp: true,
        maxWidth: 250,
        onClick: function(d){ searchViewModel.query.selectRangeUpFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field, 'exclude': false, is_up: d.data.obj.is_up}) },
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
      <div class="clearfix"></div>
      <!-- /ko -->
      <!-- ko if: type().indexOf('range') == -1 -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: pieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ searchViewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id}) },
        onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false)} }" />
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
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
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
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
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
        <div data-bind="barChart: {datum: {counts: $parent.counts(), widget_id: $parent.id(), label: $parent.label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(),
          isPivot: true,
          fqs: $root.query.fqs,
          transformer: pivotChartDataTransformer,
          onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
          onClick: function(d) {
            $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
          },
          onComplete: function(){ searchViewModel.getWidgetById($parent.id()).isLoading(false) } }"
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


<script type="text/html" id="hit-widget">
  <div class="widget-spinner" data-bind="visible: ! $root.hasRetrievedResults()">
    <i class="fa fa-spinner fa-spin"></i>
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle2' }"></span>
    </div>

    <span class="big-counter" data-bind="textSqueezer: counts"></span>
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="metric-form">

    <!-- ko if: $root.isEditing -->
    <div>
      <!-- ko with: aggregate -->
      <select data-bind="options: metrics, optionsText: 'label', optionsValue: 'value', value: $data.function, disable: ($parents[1].widgetType() == 'text-facet-widget' && $index() == 0 && !$parent.isFacetForm" class="input-small"></select>

      <!-- ko if: $data.function() == 'percentile' -->
      <input type="number" class="input-mini" data-bind="value: percentile"/>
      <!-- /ko -->

      <select data-bind="options: $root.collection.template.facetFieldsNames, value: $parent.field, optionsCaption: '${ _ko('Field...') }', selectize: $root.collection.template.facetFieldsNames" class="hit-options input-small" style="margin-bottom: 0"></select>

      <div class="clearfix"></div>
      <br/>

      <div data-bind="component: { name: 'hue-simple-ace-editor', params: { value: plain_formula, parsedValue: formula, autocomplete: { type: 'solrFormula', support: { fields: $root.collection.template.fieldsAttributes } }, singleLine: true, mode: $root.collection.engine() } }, visible: $parent.field() == 'formula'"></div>

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
            <span class="facet-field-label">
              ${ _('Limit') }
            </span>
            <input type="text" class="input-medium" data-bind="spinedit: $parent.limit"/>
          </span>
        </div>

        <div class="facet-field-cnt" data-bind="visible: $data.function() == 'count'">
          <span class="spinedit-cnt">
            <span class="facet-field-label">
              ${ _('Min Count') }
            </span>
            <input type="text" class="input-medium" data-bind="spinedit: $parent.mincount"/>
          </span>
        </div>
      <!-- /ko -->
      <!-- /ko -->

      <!-- ko if: $parent.widgetType() != 'hit-widget' && type() != 'field' -->
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
          <div data-bind="daterangepicker: {start: start, end: end, gap: initial_gap, relatedgap: gap, min: min, max: max}"></div>
        <!-- /ko -->

        <!-- /ko -->
        <!-- /ko -->
      </div>
    <!-- /ko -->

    <!-- ko if: !$root.isEditing() -->
    <div class="content" style="border: 1px solid #d8d8d8;">
      <div data-bind="text: getPrettyMetric($data)" class="muted"></div>
      <!-- ko if: aggregate.function() != 'field' && aggregate.metrics -->
      <i class="fa" data-bind="css: { 'fa-long-arrow-down': sort() == 'desc', 'fa-long-arrow-up': sort() == 'asc' }"></i>
      <!-- /ko -->
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
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function() { chartsUpdatingState(); $root.query.removeFilter($data); $root.search(); }">
          <i class="fa fa-times"></i>
        </a>
        <span data-bind="text: $data.field"></span>
        &nbsp;
      </div>
      <div class="content">
        <strong>${_('selected')}</strong>
        <span data-bind="foreach: $data.filter">
          <span class="label label-info" style="margin-left: 4px" data-bind="visible: ! $data.exclude(), html: prettifyDate($data.value()), attr: {'title': $data.value()}"></span>
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
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ chartsUpdatingState(); $root.query.removeFilter($data); $root.search() }">
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
              <strong data-bind="visible: ! $parent.is_up()">${ _('Until') }</strong>
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
        <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ chartsUpdatingState(); $root.query.removeFilter($data); $root.search() }">
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

    <div class="margin-bottom-10" data-bind="visible: ! $root.isEditing()">
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

      <div class="margin-bottom-10" data-bind="visible: ! $root.isEditing()">
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
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0" class="table table-condensed">
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
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() == 'error'">${ _('This field does not support stats') }</div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no stats to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() != 'error'" class="table table-condensed">
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
      <input id="addFacetInput" type="text" data-bind="clearable: $root.collection.template.fieldsModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" class="input" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.collection.template.filteredModalFields().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.collection.template.filteredModalFields().length > 0"
          class="unstyled inline fields-chooser" style="height: 100px; overflow-y: auto">
        <li data-bind="click: addFacetDemiModalFieldPreview">
          <span class="badge badge-info"><span data-bind="text: name(), attr: {'title': type()}"></span>
          </span>
        </li>
      </ul>
      <div class="alert alert-info inline" data-bind="visible: $root.collection.template.filteredModalFields().length == 0" style="margin-left: 250px; margin-right: 50px; height: 42px;line-height: 42px">
        ${_('There are no fields matching your search term.')}
      </div>
    </div>
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
                <select id="settingssolrindex" data-bind="options: $root.initial.collections, value: $root.collection.name"></select>
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: $root.collection.engine() != 'solr' -->
            <div class="control-group">
              <label class="control-label" for="settingssolrindex">${ _('Solr index') }</label>
              <div class="controls">
                <input type="text" class="no-margin" data-bind="hivechooser: $root.collection.name, skipColumns: true" placeholder="${ _('Table name or <database>.<table>') }">
              </div>
            </div>
            <!-- /ko -->

            <div class="control-group">
              <label class="control-label" for="settingsdescription">${ _('Description') }</label>
              <div class="controls">
                <input id="settingsdescription" type="text" class="input-xlarge" data-bind="textInput: $root.collection.description, tagsNotAllowed" style="margin-bottom: 0" />
              </div>
            </div>

            <!-- ko if: $root.collection.engine() == 'solr' -->
            <div class="control-group">
              <label class="control-label">${ _('Autocomplete') }</label>
              <div class="controls">
                <label class="checkbox" style="padding-top:0">
                  <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.suggest.enabled">
                  <span data-bind="visible: $root.collection.suggest.enabled">
                    ${ _('Dictionary') } <input type="text" class="input-xlarge" style="margin-bottom: 0; margin-left: 6px;" data-bind="textInput: $root.collection.suggest.dictionary, tagsNotAllowed" placeholder="${ _('Dictionary name or blank for default') }">
                  </span>
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
    <span data-bind="template: {name: 'time-filter-select'}"></span>
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
  <select id="settingstimeinterval" data-bind="value: collection.timeFilter.value" class="input-small" style="margin-right: 4px">
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
                <label class="control-label" for="settingstimefield">${ _('Date/time field') }</label>
                <div class="controls">
                  <select id="settingstimefield" data-bind="options: $root.availableDateFields, value: collection.timeFilter.field, optionsValue: 'name'" class="input-medium"></select>
                </div>
              </div>
              <div class="control-group">
                <label class="control-label" for="settingstimetype">${ _('Type') }</label>
                <div class="controls">
                  <label class="radio inline"><input type="radio" name="settingstimetype" value="rolling" data-bind="checked: collection.timeFilter.type" /> ${ _('Rolling') }</label>
                  <label class="radio inline"><input type="radio" name="settingstimetype" value="fixed" data-bind="checked: collection.timeFilter.type" /> ${ _('Fixed') }</label>
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'rolling'">
                <label class="control-label" for="settingstimeinterval">${ _('Interval') }</label>
                <div class="controls">
                  <span data-bind="template: {name: 'time-filter-select'}"></span>
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'fixed'">
                <label class="control-label" for="settingstimestart">${ _('Start date/time') }</label>
                <div class="controls">
                  <input id="settingstimestart" type="text" data-bind="value: collection.timeFilter.from, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:SS[Z]', disableUTC: true}" />
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'fixed'">
                <label class="control-label" for="settingstimeend">${ _('End date/time') }</label>
                <div class="controls">
                  <input id="settingstimeend" type="text" data-bind="value: collection.timeFilter.to, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:SS[Z]', disableUTC: true}" />
                </div>
              </div>
              <!-- ko if: collection.timeFilter.type() == 'rolling' -->
              <div class="control-group">
                <div class="controls">
                  <label class="checkbox inline-block">
                    <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.autorefresh"/> ${ _('Auto-refresh every') } <input type="number" class="input-mini" style="margin-bottom: 0; margin-left: 6px; margin-right: 6px; width: 46px; text-align:center" data-bind="textInput: $root.collection.autorefreshSeconds"/> ${ _('seconds') }
                  </label>
                </div>
              </div>
              <!-- /ko -->
            </span>

            <!-- ko if: $root.availableDateFields().length == 0 -->
              <label class="checkbox inline-block">
                <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.autorefresh"/> ${ _('Auto-refresh every') } <input type="number" class="input-mini" style="margin-bottom: 0; margin-left: 6px; margin-right: 6px; width: 46px; text-align:center" data-bind="textInput: $root.collection.autorefreshSeconds"/> ${ _('seconds') }
              </label>
            <!-- /ko -->
          </fieldset>
        </form>

      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
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
<span id="extra" data-bind="augmenthtml: $root.collection.template.extracode"></span>


<link rel="stylesheet" href="${ static('dashboard/css/search.css') }">
%if is_mobile:
<link rel="stylesheet" href="${ static('dashboard/css/search_mobile.css') }">
%endif
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/selectize.css') }">
%if USE_GRIDSTER.get():
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.gridster.min.css') }">
%endif

<script src="${ static('desktop/js/hue.json.js') }" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_layout(True) }

% if not is_embeddable:
<script src="${ static('desktop/js/share2.vm.js') }"></script>
% endif
<script src="${ static('dashboard/js/search.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.textsqueezer.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.editable.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/shortcut.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/mustache.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
<script src="${ static('desktop/ext/select2/select2.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/js/ko.selectize.js') }"></script>
<script src="${ static('dashboard/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>

%if USE_GRIDSTER.get():
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.gridster.with-extras.min.js') }"></script>
<script src="${ static('desktop/js/gridster-knockout.js') }"></script>
%endif

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
    { value: "variance", label: "${ _('Variance') }" }
];
var DATETIME_HIT_OPTIONS = [
    { value: "count", label: "${ _('Group by') }" },
    ## { value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" },
    { value: "median", label: "${ _('Median') }" },
    { value: "percentile", label: "${ _('Percentile') }" }
];
var ALPHA_HIT_COUNTER_OPTIONS = [
    ##{ value: "count", label: "${ _('Group by') }" },
    ##{ value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" }
];
var ALPHA_HIT_OPTIONS = [
    { value: "count", label: "${ _('Group by') }" },
    ## { value: "counts", label: "Count" },
    { value: "unique", label: "${ _('Unique') }" },
    { value: "min", label: "${ _('Min') }" },
    { value: "max", label: "${ _('Max') }" }
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
  if (facet.field() == 'formula') {
    return facet.aggregate.plain_formula()
  } else if (facet.aggregate.function() == 'percentile') {
    return 'percentile(' + facet.aggregate.percentiles()[0]['value']() + ')';
  } else {
    return getHitOption(facet.aggregate.function());
  }
}

function prettifyDate(from, widget, to) {
  if (typeof from == "undefined" || $.isNumeric(from)) {
    return from;
  }
  if (typeof to != "undefined" && !$.isNumeric(to)) {
    return prettifyDateRange(from, to, widget);
  }
  var _mFrom = moment(from);
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
%if USE_GRIDSTER.get():
var getDraggableOptions = function(options) {
  return {
    'start': function (event, ui) {
      $(ui.helper).css('z-index','999999');
      huePubSub.publish('dashboard.top.widget.drag.start', { event: event, widget: options.data });
    },
    'drag': function (event) {
      huePubSub.publish('dashboard.top.widget.drag', { event: event, widgetHeight: options.data.gridsterHeight() });
    }
  };
};
%else:
  var getDraggableOptions = function (options) {
    return {
      'start': function (event, ui) {
        lastWindowScrollPosition = $(window).scrollTop();
        $('.card-body').slideUp('fast');
        if (options && options.start) {
          options.start();
        }
      },
      'stop': function (event, ui) {
        $('.card-body').slideDown('fast', function () {
          $(window).scrollTop(lastWindowScrollPosition)
        });
        if (options && options.stop) {
          options.stop();
        }
      }
    }
  }
%endif

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
  return _data;
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
  return _data;
}


function rangePieChartDataTransformer(data) {
  return _rangePieChartDataTransformer(data, false);
}

function rangeUpPieChartDataTransformer(data) {
  return _rangePieChartDataTransformer(data, true);
}

function pieChartDataTransformerGrid(data) {
  var _data = [];
  var chartX = searchViewModel.collection.template.chartSettings.chartX();
  var chartY = searchViewModel.collection.template.chartSettings.chartYSingle();
  $(data.counts).each(function (cnt, item) {
    item.widget_id = data.widget_id;
    if (chartX != "" && item.item[chartX] && chartY != "" && item.item[chartY]) {
      _data.push({
        label: item.item[chartX](),
        value: item.item[chartY](),
        obj: item
      });
    }
  });
  return _data;
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
          x: item.from + (item.is_up ? ' & ${ _('Up') }' : ' & ${ _('Less') }'),
          y: item.value,
          obj: item
        });
      }
      else {
        _data.push({
          series: 0,
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

function barChartDataTransformer(rawDatum) {
  return _barChartDataTransformer(rawDatum, false);
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
      x: item.cat,
      y: item.count,
      obj: item
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

function timelineChartDataTransformer(rawDatum) {
  var _datum = [];
  var _data = [];

  $(rawDatum.counts).each(function (cnt, item) {
    _data.push({
      series: 0,
      x: new Date(moment(item.from).valueOf()),
      y: item.value,
      obj: item
    });
  });

  _datum.push({
    key: rawDatum.label,
    values: _data
  });

  // If multi query
  $(rawDatum.extraSeries).each(function (cnt, item) {
    if (cnt == 0) {
      _datum = [];
    }
    var _data = [];
    $(item.counts).each(function (cnt, item) {
      _data.push({
        series: cnt + 1,
        x: new Date(moment(item.from).valueOf()),
        y: item.value,
        obj: item
      });
    });

    _datum.push({
      key: item.label,
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
  $(data.counts).each(function (cnt, item) {
    var chartX = searchViewModel.collection.template.chartSettings.chartX();
    var chartY = searchViewModel.collection.template.chartSettings.chartYSingle();
    var chartMapLabel = searchViewModel.collection.template.chartSettings.chartMapLabel();
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


function multiSerieDataTransformerGrid(rawDatum) {
  var _datum = [];

  var chartX = searchViewModel.collection.template.chartSettings.chartX();
  var chartY = searchViewModel.collection.template.chartSettings.chartYMulti();

  if (chartX != null && chartY.length > 0 && rawDatum.counts.length > 0) {
    var _plottedSerie = 0;
    chartY.forEach(function (col) {
      var _data = [];
      $(rawDatum.counts).each(function (cnt, item) {
        if (item.item[chartX] && item.item[col]) {
          _data.push({
            series: _plottedSerie,
            x: item.item[chartX](),
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
  resizeFieldsListCallback();
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
  $.getJSON('/search/new_search?format=json', function(data){
    searchViewModel.collectionJson = data.collection;
    searchViewModel.queryJson = data.query;
    searchViewModel.initialJson = data.initial;
    searchViewModel.reset();
  });
}

function loadSearch(collection, query, initial) {

  searchViewModel = new SearchViewModel(collection, query, initial);

  ko.applyBindings(searchViewModel, $('#searchComponents')[0]);

  searchViewModel.timelineChartTypes = ko.observableArray([
    {
      value: "line",
      label: "${ _('Lines')}"
    },
    {
      value: "bar",
      label: "${ _('Bars')}"
    }
  ]);

  searchViewModel.init(function(data){
    $(".chosen-select").trigger("chosen:updated");
  });

  searchViewModel.isRetrievingResults.subscribe(function(value){
    if (! value){
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
}

$(document).ready(function () {

  var _resizeTimeout = -1;
  $(window).resize(function(){
    window.clearTimeout(_resizeTimeout);
    window.setTimeout(function(){
      resizeFieldsList();
    }, 200);
  });

%if USE_GRIDSTER.get():
  var WIDGET_BASE_HEIGHT = 50;
  $(".gridster>ul").gridster({
    widget_margins: [10, 10],
    widget_base_dimensions: ['auto', WIDGET_BASE_HEIGHT],
    shift_widgets_up: false,
    shift_larger_widgets_down: false,
    collision: {
      wait_for_mouseup: true
    },
    max_cols: 12,
    max_rows: 6000,
    resize: {
      enabled: true,
      start: function (event, ui, $widget) {
        $widget.find('.card-widget').css('opacity', '.6');
      },
      stop: function (event, ui, $widget) {
        huePubSub.publish('resize.plotly.chart');
        $widget.find('.card-widget').height($widget.height()).css('opacity', '1');
      },
    }
  });

  function addPreviewHolder() {
    if (!$('.hue-preview-holder').length && searchViewModel.columns().length > 0) {
      $('<li>').addClass('preview-holder hue-preview-holder').attr('data-sizex', '6').attr('data-sizey', '2').attr('data-row', '1').attr('data-col', '1').appendTo($('.gridster>ul'));
    }
  }

  function removePreviewHolder() {
    $('.hue-preview-holder').remove();
  }

  function movePreviewHolder (options) {
    var coords = {
      col: Math.ceil((options.event.clientX - $('.gridster').offset().left) / (widgetGridWidth + 10)),
      row: Math.ceil((options.event.pageY - $('.gridster').offset().top) / (widgetGridHeight + 10))
    }
    if (coords.row > 0 && coords.col > 0) {
      var overlaps = false;
      $('li.gs-w').each(function () {
        var dimensions = {
          col: parseInt($(this).attr('data-col')),
          row: parseInt($(this).attr('data-row')),
          sizex: parseInt($(this).attr('data-sizex')),
          sizey: parseInt($(this).attr('data-sizey'))
        }
        if (coords.col >= dimensions.col && coords.row >= dimensions.row && coords.col < dimensions.col + dimensions.sizex && coords.row < dimensions.row + dimensions.sizey) {
          overlaps = true;
        }
      });
      if (!$('.gridster').hasClass('dragging') && !overlaps) {
        $('.hue-preview-holder').show();
        $('.hue-preview-holder').attr('data-sizey', options.widgetHeight || 6);
        $('.hue-preview-holder').attr('data-col', coords.col);
        $('.hue-preview-holder').attr('data-row', coords.row);
      }
      else {
        $('.hue-preview-holder').hide();
      }
    }
    else {
      $('.hue-preview-holder').hide();
    }
  }

  var widgetGridHeight = parseInt(hueUtils.getStyleFromCSSClass('[data-sizey="1"]').height);
  var widgetGridWidth = parseInt(hueUtils.getStyleFromCSSClass('[data-sizex="1"]').width);

  var tempDraggable = null;
  huePubSub.subscribe('dashboard.top.widget.drag.start', function (options) {
    var widgetClone = ko.mapping.toJS(options.widget);
    widgetClone.id = UUID();
    tempDraggable = new Widget(widgetClone);
    addPreviewHolder();
  }, 'dashboard');

  huePubSub.subscribe('dashboard.top.widget.drag', movePreviewHolder, 'dashboard');
  huePubSub.subscribe('draggable.text.drag', movePreviewHolder, 'dashboard');

  huePubSub.subscribe('draggable.text.meta', addPreviewHolder, 'dashboard');

  huePubSub.subscribe('gridster.added.widget', removePreviewHolder, 'dashboard');

  huePubSub.subscribe('dashboard.drop.on.page', function (options) {
    removePreviewHolder();
    if (searchViewModel.columns().length > 0) {
      var dropPosition = {
        col: Math.ceil((options.event.clientX - $('.gridster').offset().left) / (widgetGridWidth + 10)),
        row: Math.ceil((options.event.pageY - $('.gridster').offset().top) / (widgetGridHeight + 10))
      }
      if (dropPosition.row > 0 && dropPosition.col > 0) {
        if (tempDraggable) {
          searchViewModel.gridItems.push(
              ko.mapping.fromJS({
                col: dropPosition.col,
                row: dropPosition.row,
                size_x: 6,
                size_y: tempDraggable.gridsterHeight(),
                widget: null,
                callback: function (el) {
                  showAddFacetDemiModal(tempDraggable, searchViewModel.gridItems()[searchViewModel.gridItems().length - 1]);
                  tempDraggable = null;
                }
              })
          );
        }
        else if (searchViewModel.lastDraggedMeta()) {
          searchViewModel.gridItems.push(
              ko.mapping.fromJS({
                col: dropPosition.col,
                row: dropPosition.row,
                size_x: 6,
                size_y: 6,
                widget: null,
                callback: function (el) {
                  showAddFacetDemiModal(null, searchViewModel.gridItems()[searchViewModel.gridItems().length - 1]);
                }
              })
          );
        }
      }
    }
  }, 'dashboard');

  function resizeGridsterWidget($el) {
    if ($el.find('.card-widget').length > 0) {
      $(".gridster>ul").data('gridster').resize_widget($el, $el.data('sizex'), Math.ceil($el.find('.card-widget').height() / WIDGET_BASE_HEIGHT));
    }
  }

  huePubSub.subscribe('plotly.afterplot', function (element) {
    resizeGridsterWidget($(element).parents('li.gs-w'));
  }, 'dashboard');

  huePubSub.subscribe('leaflet.afterplot', function (element) {
    resizeGridsterWidget($(element).parents('li.gs-w'));
  }, 'dashboard');

  huePubSub.subscribe('gridster.remove', function (gridElement) {
    searchViewModel.gridItems.remove(gridElement);
  }, 'dashboard')

  huePubSub.subscribe('gridster.remove.widget', function (widgetId) {
    searchViewModel.gridItems().forEach(function (item) {
      if (item.widgetId() === parseInt($('#wdg_' + widgetId).parents('li.gs-w').attr('data-widgetid'))) {
        huePubSub.publish('gridster.remove', item);
      }
    });
  }, 'dashboard');

  huePubSub.subscribe('gridster.add.widget', function (options) {
    var widget = searchViewModel.getWidgetById(options.id);
    if (widget) {
      var targetHeight = widget.gridsterHeight() || 6;
      if (options.target) {
        searchViewModel.gridItems().forEach(function (item) {
          if (item.col() === options.target.col() && item.row() === options.target.row()) {
            if (ko.isObservable(item.widget)) {
              item.widget(widget);
            }
            else {
              item.widget = ko.observable(widget);
            }
            item.size_y(targetHeight);
            $('.gridster ul').data('gridster').resize_widget($(item.gridsterElement), item.size_x(), item.size_y());
          }
        });
      }
      else {
        var newPosition = $('.gridster ul').data('gridster').next_position(12, targetHeight);
        searchViewModel.gridItems.push(
          ko.mapping.fromJS({
            col: newPosition.col,
            row: newPosition.row,
            size_x: 12,
            size_y: targetHeight,
            widget: widget,
            callback: function (el) {
              $('.gridster ul').data('gridster').move_widget(el, 1, 1);
            }
          })
        );
      }
    }
  }, 'dashboard');
%endif

  $(document).on("click", ".widget-settings-pill", function(){
    $(this).parents(".card-body").find(".widget-section").hide();
    selectAllCollectionFields(); // Make sure all the collection fields appear
    $(this).parents(".card-body").find(".widget-settings-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-editor-pill", function(){
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-editor-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-html-pill", function(){
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-html-section").show();
    $(document).trigger("refreshCodemirror");
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-css-pill", function(){
    $(this).parents(".card-body").find(".widget-section").hide();
    $(this).parents(".card-body").find(".widget-css-section").show();
    $(document).trigger("refreshCodemirror");
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("magicSearchLayout", function(){
    resizeFieldsList();
  });

  $(document).on("setLayout", function(){
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

  $('#searchComponents').parents('.embeddable').droppable({
    drop: function( event, ui ) {
      huePubSub.publish('dashboard.drop.on.page', {event: event, ui: ui});
    }
  });

  % if is_owner:
  $(window).bind("keydown", "ctrl+s alt+s meta+s", function(e){
    e.preventDefault();
    searchViewModel.save();
    return false;
  });
  % endif
  $(window).bind("keydown", "esc", function () {
    if ($(".demi-modal.fade.in").length > 0) {
      $(".demi-modal.fade.in .demi-modal-chevron").click();
    }
  });

  $("#newqname").bind("keydown", "return", function (e) {
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
    searchViewModel.search();
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
        }, 100, 'search')
      }
      else {
        row.autosizeWidgets();
      }
    }
  }

  var selectedWidget = null;
  var selectedRow = null;
  %if USE_GRIDSTER.get():
  var selectedGridster = null;
  function showAddFacetDemiModal(widget, gridsterTarget) {
    selectedGridster = gridsterTarget;
    if (widget && widget.id) {
      var fakeRow = searchViewModel.columns()[0].addEmptyRow(true);
      fakeRow.addWidget(widget);

      if (["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(widget.widgetType()) == -1) {
        searchViewModel.collection.template.fieldsModalFilter("");
        searchViewModel.collection.template.fieldsModalType(widget.widgetType());

        selectedWidget = widget;

        if (searchViewModel.collection.template.availableWidgetFields().length == 1) {
          addFacetDemiModalFieldPreview(searchViewModel.collection.template.availableWidgetFields()[0]);
        }
        else {
          $('#addFacetInput').typeahead({
            'source': searchViewModel.collection.template.availableWidgetFieldsNames(),
            'updater': function (item) {
              addFacetDemiModalFieldPreview({
                'name': function () {
                  return item
                }
              });
              return item;
            }
          });
          $("#addFacetDemiModal").modal("show");
          $("#addFacetDemiModal input[type='text']").focus();
        }
      }
      else {
        huePubSub.publish('gridster.add.widget', {id: widget.id(), target: gridsterTarget});
      }
    }
    else if (searchViewModel.lastDraggedMeta() && searchViewModel.lastDraggedMeta().type === 'sql' && searchViewModel.lastDraggedMeta().column && searchViewModel.collection.template.availableWidgetFieldsNames().indexOf(searchViewModel.lastDraggedMeta().column) > -1) {
      if (searchViewModel.collection.supportAnalytics()) {
        selectedWidget = searchViewModel.draggableTextFacet();
      }
      else {
        selectedWidget = searchViewModel.draggableFacet();
      }
      var fakeRow = searchViewModel.columns()[0].addEmptyRow(true);
      fakeRow.addWidget(selectedWidget);
      addFacetDemiModalFieldPreview({
        'name': function () {
          return searchViewModel.lastDraggedMeta().column
        }
      });
    }
  }

  function addFacetDemiModalFieldPreview(field) {
    var _existingFacet = searchViewModel.collection.getFacetById(selectedWidget.id());
    if (selectedWidget != null) {
      selectedWidget.hasBeenSelected = true;
      selectedWidget.isLoading(true);
      searchViewModel.collection.addFacet({
        'name': field.name(),
        'widget_id': selectedWidget.id(),
        'widgetType': selectedWidget.widgetType()
      }, function () {
        huePubSub.publish('gridster.add.widget', {id: selectedWidget.id(), target: selectedGridster});
      });
      if (_existingFacet != null) {
        _existingFacet.label(field.name());
        _existingFacet.field(field.name());
      }
      $("#addFacetDemiModal").modal("hide");
    }
  }

  function addFacetDemiModalFieldCancel() {
    searchViewModel.gridItems.remove(selectedGridster);
    searchViewModel.removeWidget(selectedWidget);
    selectedRow = null;
  }

  %else:
  function showAddFacetDemiModal(widget, row) {
    if (["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(widget.widgetType()) == -1) {
      searchViewModel.collection.template.fieldsModalFilter("");
      searchViewModel.collection.template.fieldsModalType(widget.widgetType());

      selectedWidget = widget;
      selectedRow = row;

      if (searchViewModel.collection.template.availableWidgetFields().length == 1 || widget.widgetType() == 'document-widget'){
        addFacetDemiModalFieldPreview(searchViewModel.collection.template.availableWidgetFields()[0]);
      }
      else {
        $('#addFacetInput').typeahead({
          'source': searchViewModel.collection.template.availableWidgetFieldsNames(),
          'updater': function (item) {
            addFacetDemiModalFieldPreview({'name': function () {
              return item
            }});
            return item;
          }
        });
        $("#addFacetDemiModal").modal("show");
        $("#addFacetDemiModal input[type='text']").focus();
      }
    }
    else {
      distributeRowWidgetsSize(row, true);
    }
  }


  function addFacetDemiModalFieldPreview(field) {
    var _existingFacet = searchViewModel.collection.getFacetById(selectedWidget.id());
    if (selectedWidget != null) {
      selectedWidget.hasBeenSelected = true;
      selectedWidget.isLoading(true);
      searchViewModel.collection.addFacet({'name': field.name(), 'widget_id': selectedWidget.id(), 'widgetType': selectedWidget.widgetType()});
      if (_existingFacet != null) {
        _existingFacet.label(field.name());
        _existingFacet.field(field.name());
      }
      $("#addFacetDemiModal").modal("hide");
      if (selectedRow != null) {
        distributeRowWidgetsSize(selectedRow);
      }
    }
  }

  function addFacetDemiModalFieldCancel() {
    searchViewModel.removeWidget(selectedWidget);
    selectedRow = null;
  }
  %endif

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
