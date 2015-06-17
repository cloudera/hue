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
from desktop import conf
from django.utils.translation import ugettext as _
%>

<%namespace name="dashboard" file="common_dashboard.mako" />

${ commonheader(_('Search'), "search", user, "80px") | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("collection") > -1) {
      location.href = "/search/?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
    }
  }

  SLIDER_LABELS = {
    STEP: "${_('Increment')}"
  }
</script>

<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a class="btn pointer" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    % if is_owner:
    <a class="btn pointer" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: save, css: {'btn': true}, visible: columns().length != 0">
      <i class="fa fa-save"></i>
    </a>
    % endif
    <a class="btn pointer" title="${ _('General Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal"
        data-bind="css: {'btn': true}, visible: columns().length != 0">
      <i class="fa fa-cog"></i>
    </a>
    <a class="btn pointer" title="${ _('Query Definitions') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#qdefinitionsDemiModal"
        data-bind="css: {'btn': true}, visible: columns().length != 0">
      <i class="fa fa-bookmark-o"></i>
    </a>

    <span data-bind="visible: columns().length != 0">&nbsp;&nbsp;&nbsp;</span>

    <a class="btn" href="${ url('search:new_search') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-file-o"></i>
    </a>
    <a class="btn" href="${ url('search:admin_collections') }" title="${ _('Dashboards') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-tags"></i>
    </a>
  </div>

  <form data-bind="visible: $root.isEditing() && columns().length == 0">
    ${ _('Select a search index') }
    <!-- ko if: columns().length == 0 -->
      <select data-bind="options: $root.initial.collections, value: $root.collection.name, disable: isSyncingCollections">
      </select>

      <label class="checkbox" style="display:inline-block; margin-left: 10px">
        <input type="checkbox" data-bind="checked: showCores" />${ _('Show cores') }
        <i class="fa fa-spinner fa-spin" data-bind="visible: isSyncingCollections"></i>
      </label>
    <!-- /ko -->

    <select data-bind="options: $root.availableDateFields, value: collection.timeFilter.field, optionsValue: 'name', visible: $root.isEditing() && $root.availableDateFields().length > 0" class="input-medium" style="margin-left: 4px"></select>
    <span data-bind="template: {name: 'time-filter'}, visible: collection.timeFilter.type() == 'rolling'"></span>
    <span data-bind="template: {name: 'time-fixed-filter'}, visible: collection.timeFilter.type() == 'fixed'"></span>
  </form>

  <form class="form-search" style="margin: 0" data-bind="submit: searchBtn, visible: columns().length != 0">
    <strong>${_("Search")}</strong>
    <div class="input-append">
      <div class="selectMask">
        <span
            data-bind="editable: collection.label, editableOptions: {enabled: $root.isEditing(), placement: 'right'}">
        </span>
      </div>

      <span data-bind="foreach: query.qs">
        <input data-bind="clearable: q, typeahead: { target: q, source: $root.collection.template.fieldsNames, multipleValues: true, multipleValuesSeparator: ':', extraKeywords: 'AND OR TO', completeSolrRanges: true }, css:{'input-xlarge': $root.query.qs().length == 1, 'input-medium': $root.query.qs().length < 4, 'input-small': $root.query.qs().length >= 4}" maxlength="4096" type="text" class="search-query">
        <!-- ko if: $index() >= 1 -->
        <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
        <!-- /ko -->
      </span>

      <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ"><i class="fa fa-plus"></i></a>

      <button type="submit" id="search-btn" class="btn btn-inverse" style="margin-left:10px; margin-right:10px">
        <i class="fa fa-search" data-bind="visible: ! isRetrievingResults()"></i>
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin" data-bind="visible: isRetrievingResults()"></i><!-- <![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner-inverted.gif') }" data-bind="visible: isRetrievingResults()"/><![endif]-->
      </button>

    </div>
    <span data-bind="template: {name: 'time-filter'}, visible: collection.timeFilter.type() == 'rolling'"></span>
    <span data-bind="template: {name: 'time-fixed-filter'}, visible: collection.timeFilter.type() == 'fixed'"></span>
  </form>
</div>


<%dashboard:layout_toolbar>
  <%def name="results()">
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableResultset(), isEnabled: availableDraggableResultset,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast'); $root.collection.template.isGridLayout(true); checkResultHighlightingAvailability(); }}}"
         title="${_('Grid')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-table"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableHtmlResultset(),
                    isEnabled: availableDraggableResultset,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){
                                  $('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});
                                  $root.collection.template.isGridLayout(false);
                                  checkResultHighlightingAvailability();
                               }
                             }
                    }"
         title="${_('HTML')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-code"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableFilter() },
                    draggable: {data: draggableFilter(), isEnabled: availableDraggableFilter,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Filter Bar')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableFilter() ? 'move' : 'default' }">
                       <i class="fa fa-filter"></i>
         </a>
    </div>

    <div data-bind="visible: $root.isLatest,
                    css: { 'draggable-widget': true, 'disabled': !availableDraggableNumbers() },
                    draggable: {data: draggableCounter(), isEnabled: availableDraggableNumbers,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Counter')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableNumbers() ? 'move' : 'default' }">
                       <i class="fa fa-superscript" style="font-size: 110%"></i>
         </a>
    </div>

    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableLeaflet()},
                    draggable: {data: draggableLeafletMap(), isEnabled: availableDraggableLeaflet,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Marker Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: 'move' }">
             <i class="fa fa-map-marker"></i>
         </a>
    </div>


      </%def>
      <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableFacet(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Text Facet')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sort-amount-asc"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggablePie(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Pie Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-pie-chart"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.isLatest(),
                    css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableBar(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.isLatest(),
                    css: { 'draggable-widget': true, 'disabled': !availableDraggableNumbers() },
                    draggable: {data: draggableLine(), isEnabled: availableDraggableNumbers,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Line Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableNumbers() ? 'move' : 'default' }">
                       <i class="hcha hcha-line-chart"></i>
         </a>
    </div>
    <div data-bind="visible: $root.isLatest(),
                    css: { 'draggable-widget': true, 'disabled': ! availableDraggableChart() },
                    draggable: {data: draggableBucket(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableTree(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
    </div>
    <div data-bind="visible: ! $root.isLatest(),
                    css: { 'draggable-widget': true, 'disabled': false },
                    draggable: {data: draggableHeatmap(), isEnabled: true,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Heatmap')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-th"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': ! availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Timeline')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableHistogram() ? 'move' : 'default' }">
                       <i class="hcha hcha-timeline-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': ! availableDraggableMap() },
                    draggable: {data: draggableMap(), isEnabled: availableDraggableMap,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Gradient Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableMap() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
         </a>
   </div>
      </%def>
</%dashboard:layout_toolbar>


${ dashboard.layout_skeleton() }


<script type="text/html" id="empty-widget">
  ${ _('This is an empty widget.')}
</script>


<script type="text/html" id="facet-toggle">
  <div class="facet-field-tile">
    <div class="facet-field-cnt">
      <span class="facet-field-label facet-field-label-fixed-width facet-field-label-fixed-width-double facet-field-label-title">${ _('Settings') }</span>
      <!--[if !IE]> --><i class="fa fa-spinner fa-spin" data-bind="visible: $root.isRetrievingResults()"></i><!-- <![endif]-->
      <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" data-bind="visible: $root.isRetrievingResults()"/><![endif]-->
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
        <br/>
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
            <select data-bind="options: $root.collection.template.fieldsNames, value: properties.facets_form.field, optionsCaption: '${ _('Choose...') }'"></select>
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
            <a class="pull-right" href="javascript: void(0)" data-bind="visible: ko.toJSON(properties.facets_form.field) != '', click: $root.collection.addPivotFacetValue">
              <i class="fa fa-plus"></i>
            </a>
          </span>
        </div>
      </div>
    <!-- /ko -->
    <div class="clearfix"></div>
</script>

<script type="text/html" id="facet-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'field' -->
        <div data-bind="foreach: $parent.counts">
          <div class="trigger-exclude">
              <!-- ko if: $index() < $parent.properties.limit() -->
                <!-- ko if: ! $data.selected -->
                  <a class="exclude pointer" data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id(), 'exclude': true}) }" title="${ _('Exclude this value') }"><i class="fa fa-minus"></i></a>
                  <div class="hellip">
                    <a class="pointer" data-bind="html: prettifyDate($data.value), click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }, attr: {'title': $data.value + ' (' + $data.count + ')'}"></a>
                    <span class="pointer counter" data-bind="text: ' (' + $data.count + ')', click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }"></span>
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

<script type="text/html" id="resultset-widget">
  <!-- ko if: $root.collection.template.isGridLayout() -->
    <div style="float:left; margin-right: 10px">
      <div data-bind="visible: ! $root.collection.template.showFieldList()" style="padding-top: 5px; display: inline-block">
        <a href="javascript: void(0)"  data-bind="click: function(){ $root.collection.template.showFieldList(true) }">
          <i class="fa fa-chevron-right"></i>
        </a>
      </div>
    </div>
    <div data-bind="visible: $root.collection.template.showFieldList()" style="float:left; margin-right: 10px; background-color: #F6F6F6; padding: 5px">
      <span data-bind="visible: $root.collection.template.showFieldList()">
        <div>
          <a href="javascript: void(0)" class="pull-right" data-bind="click: function(){ $root.collection.template.showFieldList(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <input type="text" data-bind="clearable: $root.collection.template.fieldsAttributesFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" style="width: 70%; margin-bottom: 10px" />
        </div>
        <div style="margin-bottom: 8px">
          <a href="javascript: void(0)" data-bind="click: function(){$root.collection.template.filteredAttributeFieldsAll(true)}, style: {'font-weight': $root.collection.template.filteredAttributeFieldsAll() ? 'bold': 'normal'}">${_('All')} (<span data-bind="text: $root.collection.template.fieldsAttributes().length"></span>)</a> / <a href="javascript: void(0)" data-bind="click: function(){$root.collection.template.filteredAttributeFieldsAll(false)}, style: {'font-weight': ! $root.collection.template.filteredAttributeFieldsAll() ? 'bold': 'normal'}">${_('Current')} (<span data-bind="text: $root.collection.template.fields().length"></span>)</a>
        </div>
        <div style="border-bottom: 1px solid #CCC; padding-bottom: 4px;">
          <a href="javascript: void(0)" class="btn btn-mini"
            data-bind="click: toggleGridFieldsSelection, css: { 'btn-inverse': $root.collection.template.fields().length > 0 }"
            style="margin-right: 2px;">
            <i class="fa fa-square-o"></i>
          </a>
          <strong>${_('Field Name')}</strong>
        </div>
        <div class="fields-list" data-bind="foreach: $root.collection.template.filteredAttributeFields">
          <div style="margin-bottom: 3px; white-space: nowrap">
            <i class="fa fa-question-circle pull-right muted pointer analysis" data-bind="click: function() { $root.fieldAnalysesName(name()); $root.showFieldAnalysis(); }, attr:{'title': '${ _('Click to analyze field') } ' + name()}"></i>
            <input type="checkbox" data-bind="checkedValue: name, checked: $root.collection.template.fieldsSelected" style="margin: 0" />
            <div data-bind="text: name, css:{'field-selector': true, 'hoverable': $root.collection.template.fieldsSelected.indexOf(name()) > -1}, click: highlightColumn" style="margin-right: 10px"></div>
          </div>
        </div>
        <div data-bind="visible: $root.collection.template.filteredAttributeFields().length == 0" style="padding-left: 4px; padding-top: 5px; font-size: 40px; color: #CCC">
          <i class="fa fa-frown-o"></i>
        </div>
      </span>
    </div>

    <div>
      <div class="widget-spinner" data-bind="visible: ! $root.hasRetrievedResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
      </div>

      <div data-bind="visible: $root.hasRetrievedResults() && $root.results().length == 0">
        <br/>
        ${ _('Your search did not match any documents.') }
      </div>

      <div data-bind="visible: $root.hasRetrievedResults() && $root.results().length > 0">
        <!-- ko if: $root.response().response -->
          <div data-bind="template: {name: 'resultset-pagination', data: $root.response()}" style="padding: 8px; color: #666"></div>
        <!-- /ko -->

        <div id="result-main" style="overflow-x: auto">
          <table id="result-container" data-bind="visible: $root.hasRetrievedResults()" style="margin-top: 0; width: 100%">
            <thead>
              <tr data-bind="visible: $root.collection.template.fieldsSelected().length > 0, template: {name: 'result-sorting'}">
              </tr>
              <tr data-bind="visible: $root.collection.template.fieldsSelected().length == 0">
                <th style="width: 18px">&nbsp;</th>
                <th>${ _('Document') }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: {data: $root.results, as: 'doc'}" class="result-tbody">
              <tr class="result-row">
                <td>
                  <a href="javascript:void(0)" data-bind="click: toggleDocDetails">
                    <i class="fa" data-bind="css: {'fa-caret-right' : ! doc.showDetails(), 'fa-caret-down': doc.showDetails()}"></i>
                  </a>
                </td>
                <!-- ko foreach: row -->
                  <td data-bind="html: $data"></td>
                <!-- /ko -->
              </tr>
              <tr data-bind="visible: doc.showDetails">
                <td data-bind="attr: {'colspan': $root.collection.template.fieldsSelected().length > 0 ? $root.collection.template.fieldsSelected().length + 1 : 2}">
                  <!-- ko if: $data.details().length == 0 -->
                    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
                    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
                  <!-- /ko -->
                  <!-- ko if: $data.details().length > 0 -->
                    <div class="document-details">
                      <table>
                        <tbody data-bind="foreach: details">
                          <tr>
                             <th style="text-align: left; white-space: nowrap; vertical-align:top; padding-right:20px" data-bind="text: key"></th>
                             <td width="100%" data-bind="text: value"></td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  <!-- /ko -->
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
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
            <tr data-bind="template: {name: 'result-sorting'}">
            </tr>
          </table>
        </div>
        <br/>
      </div>
    <!-- /ko -->

    <div id="result-main" style="overflow-x: auto">
      <div data-bind="visible: $root.hasRetrievedResults() && $root.results().length == 0">
        <br/>
        ${ _('Your search did not match any documents.') }
      </div>

      <!-- ko if: $root.response().response && $root.results().length > 0 -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->

      <div id="result-container" data-bind="foreach: $root.results">
        <div class="result-row" data-bind="html: $data"></div>
      </div>

      <div class="widget-spinner" data-bind="visible: ! $root.hasRetrievedResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
      </div>
    </div>
  <!-- /ko -->
</script>


<script type="text/html" id="result-sorting">
<th style="width: 18px">&nbsp;</th>
<!-- ko foreach: $root.collection.template.fieldsSelected -->
<th data-bind="with: $root.collection.getTemplateField($data), event: { mouseover: $root.enableGridlayoutResultChevron, mouseout: $root.disableGridlayoutResultChevron }" style="white-space: nowrap">
  <div style="display: inline-block; width:20px;">
    <a href="javascript: void(0)" data-bind="click: function(){ $root.collection.translateSelectedField($index(), 'left'); }">
      <i class="fa fa-chevron-left" data-bind="visible: $root.toggledGridlayoutResultChevron() && $index() > 0"></i>
      <i class="fa fa-chevron-left" style="color: #FFF" data-bind="visible: !$root.toggledGridlayoutResultChevron() || $index() == 0"></i>
    </a>
  </div>
  <div style="display: inline-block;">
    <a href="javascript: void(0)" data-bind="click: $root.collection.toggleSortColumnGridLayout" title="${ _('Click to sort') }">
      <span data-bind="text: name"></span>
      <i class="fa" data-bind="visible: sort.direction() != null, css: { 'fa-chevron-down': sort.direction() == 'desc', 'fa-chevron-up': sort.direction() == 'asc' }"></i>
    </a>
  </div>
  <div style="display: inline-block; width:20px;">
    <a href="javascript: void(0)" data-bind="click: function(){ $root.collection.translateSelectedField($index(), 'right'); }">
      <i class="fa fa-chevron-right" data-bind="visible: $root.toggledGridlayoutResultChevron() && $index() < $root.collection.template.fields().length - 1"></i>
      <i class="fa fa-chevron-up" style="color: #FFF" data-bind="visible: !$root.toggledGridlayoutResultChevron() || $index() == $root.collection.template.fields().length - 1,"></i>
    </a>
  </div>
</th>
<!-- /ko -->
</script>


<script type="text/html" id="resultset-pagination">
<!-- ko if: $data.response.numFound > 0 -->
<div class="pull-right" style="display:inline">
  <form method="POST" action="${ url('search:download') }" style="display:inline">
    ${ csrf_token(request) | n,unicode }
    <input type="hidden" name="collection" data-bind="value: ko.mapping.toJSON($root.collection)"/>
    <input type="hidden" name="query" data-bind="value: ko.mapping.toJSON($root.query)"/>
    <input type="hidden" name="download">
    <button class="btn" type="submit" name="json" title="${ _('Download first rows as JSON') }"><i class="hfo hfo-file-json"></i></button>
    <button class="btn" type="submit" name="csv" title="${ _('Download first rows as CSV') }"><i class="hfo hfo-file-csv"></i></button>
    <button class="btn" type="submit" name="xls" title="${ _('Download first rows as XLS') }"><i class="hfo hfo-file-xls"></i></button>
  </form>
</div>
<!-- /ko -->

<div style="text-align: center; margin-top: 4px">
  <a href="javascript: void(0)" title="${ _('Previous') }">
    <span data-bind="click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-left" data-bind="
        visible: $data.response.start * 1.0 >= $root.collection.template.rows() * 1.0,
        click: function() { $root.query.paginate('prev') }">
    </i>
  </a>

  ${ _('Showing') }
  <span data-bind="text: ($data.response.start + 1)"></span>
  ${ _('to') }
  <span data-bind="text: Math.min(($data.response.start + $root.collection.template.rows()), $data.response.numFound)"></span>
  ${ _('of') }
  <span data-bind="text: $data.response.numFound"></span>
  ${ _(' results') }

  <span data-bind="visible: $root.isEditing()">
    ${ _('Show') }
    <span class="spinedit-cnt">
      <input type="text" data-bind="spinedit: $root.collection.template.rows, valueUpdate:'afterkeydown'" style="text-align: center; margin-bottom: 0" />
    </span>
    ${ _('results per page') }
  </span>

  <a href="javascript: void(0)" title="${ _('Next') }">
    <span data-bind="click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-right" data-bind="
        visible: ($root.collection.template.rows() * 1.0 + $data.response.start * 1.0) < $data.response.numFound,
        click: function() { $root.query.paginate('next') }">
    </i>
  </a>
</div>
</script>


<script type="text/html" id="histogram-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

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
      <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
        type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
        fqs: $root.query.fqs,
        onSelectRange: function(from, to){ $root.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
        onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
        onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
        onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false) }}" />
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="bar-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

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
            viewModel.query.selectRangeUpFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field, 'exclude': false, is_up: d.obj.is_up});
          } else {
            viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field});
          }
        } else {
          viewModel.query.toggleFacet({facet: d.obj, widget_id: d.obj.widget_id});
        }
      },
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
    />
    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="bucket-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <span data-bind="foreach: properties.facets, visible: !$parents[1].isLoading()">
        <div class="filter-box">
          <div class="title">
            <a data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }" class="pull-right" href="javascript:void(0)">
              <i class="fa fa-times"></i>
            </a>
            <div class="hit-title" data-bind="text: field, attr: {'title': field}"></div>
            <div class="clearfix"></div>
          </div>

          <div class="content">
            <div class="facet-field-cnt">
              <span class="facet-field-label">${ _('Metric') }</span>
              <select data-bind="options: HIT_OPTIONS, optionsText: 'label', optionsValue: 'value', value: aggregate" class="hit-options"></select>
            </div>

            <div class="facet-field-cnt" data-bind="visible: $root.isEditing()">
              <span class="spinedit-cnt">
                <span class="facet-field-label">
                  ${ _('Limit') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: limit"/>
              </span>
            </div>

            <div class="facet-field-cnt" data-bind="visible: $root.isEditing()">
              <span class="spinedit-cnt">
                <span class="facet-field-label">
                  ${ _('Min Count') }
                </span>
                <input type="text" class="input-medium" data-bind="spinedit: mincount"/>
              </span>
            </div>
          </div>
        </div>
      </span>
      <div class="filter-box" data-bind="visible: $root.isEditing() && properties.facets().length < 2" style="opacity: 0.7">
        <div class="title" style="border: 1px dashed #d8d8d8; border-bottom: none">
          <a data-bind="visible: ko.toJSON(properties.facets_form.field) != '', click: $root.collection.addPivotFacetValue" class="pull-right" href="javascript:void(0)">
            <i class="fa fa-plus"></i> ${ _('Add') }
          </a>
          <select data-bind="options: $root.collection.template.fieldsNames, value: properties.facets_form.field, optionsCaption: '${ _('Field...') }'" class="hit-options" style="margin-bottom: 0; height: 20px"></select>
          <div class="clearfix"></div>
        </div>
        <div class="content" style="border: 1px dashed #d8d8d8; border-top: none">
          <div class="facet-field-cnt">
            <span class="spinedit-cnt">
              <span class="facet-field-label">
                ${ _('Metric') }
              </span>
              <select data-bind="options: HIT_OPTIONS, optionsText: 'label', optionsValue: 'value', value: properties.facets_form.aggregate" class="hit-options"></select>
            </span>
          </div>

          <div class="facet-field-cnt">
            <span class="spinedit-cnt">
              <span class="facet-field-label">
                ${ _('Limit') }
              </span>
              <input type="text" class="input-medium" data-bind="spinedit: properties.facets_form.limit"/>
            </span>
          </div>

          <div class="facet-field-cnt">
            <span class="spinedit-cnt">
              <span class="facet-field-label">
                ${ _('Min Count') }
              </span>
              <input type="text" class="input-medium" data-bind="spinedit: properties.facets_form.mincount"/>
            </span>
          </div>
        </div>
      </div>

      <div class="pull-right" style="margin-top: 40px">

        <div class="inline-block" style="padding-bottom: 10px; padding-right: 20px">
          <span class="facet-field-label">${ _('Sorting') }</span>
          <a href="javascript: void(0)" title="${ _('Toggle sort order') }" data-bind="click: $root.collection.toggleSortFacet">
            <i class="fa" data-bind="css: { 'fa-caret-down': properties.sort() == 'desc', 'fa-caret-up': properties.sort() == 'asc' }"></i>
            <span data-bind="visible: properties.sort() == 'desc'">${_('descending')}</span>
            <span data-bind="visible: properties.sort() == 'asc'">${_('ascending')}</span>
          </a>
        </div>


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

    <!-- ko if: $root.collection.getFacetById($parent.id()) -->
      <!-- ko if: dimension() == 1 -->
        <div data-bind="barChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(),
          fqs: $root.query.fqs,
          transformer: ($data.type == 'range-up' ? barChartRangeUpDataTransformer : barChartDataTransformer),
          onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
          onClick: function(d) {
            if (d.obj.field != undefined) {
              if ($data.type == 'range-up') {
                viewModel.query.selectRangeUpFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field, 'exclude': false, is_up: d.obj.is_up});
              } else {
                viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field});
              }
            } else {
              viewModel.query.toggleFacet({facet: d.obj, widget_id: d.obj.widget_id});
            }
          },
          onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
          onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
        />
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
          onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
        />
      <!-- /ko -->

      <!-- ko if: dimension() == 3 -->
      <div data-bind="timelineChart: {datum: {counts: counts(), extraSeries: extraSeries(), widget_id: $parent.id(), label: label()}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label(), transformer: timelineChartDataTransformer,
        type: $root.collection.getFacetById($parent.id()).properties.timelineChartType,
        fqs: $root.query.fqs,
        onSelectRange: function(from, to){ $root.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
        onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
        onClick: function(d){ $root.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
        onComplete: function(){ $root.getWidgetById($parent.id()).isLoading(false) }}" />
      <!-- /ko -->

    <!-- /ko -->
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="line-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px" data-bind="visible: counts.length > 0">
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.rangeZoomOut"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
    </div>

    <div data-bind="lineChart: {datum: {counts: counts(), widget_id: $parent.id(), label: label()}, field: field, label: label(),
      transformer: lineChartDataTransformer,
      onClick: function(d){ viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
    />
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

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'range' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: rangePieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ viewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
        onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false)} }" />
      <!-- /ko -->
      <!-- ko if: type() == 'range-up' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: rangeUpPieChartDataTransformer,
        rangeUp: true,
        maxWidth: 250,
        onClick: function(d){ viewModel.query.selectRangeUpFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field, 'exclude': false, is_up: d.data.obj.is_up}) },
        onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false)} }" />
      <!-- /ko -->
      <!-- ko if: type().indexOf('range') == -1 -->
      <div data-bind="pieChart: {data: {counts: $parent.counts(), widget_id: $parent.id()}, field: field, fqs: $root.query.fqs,
        transformer: pieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ viewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id}) },
        onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false)} }" />
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>
</script>


<script type="text/html" id="tree-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div class="responsive-facet-toggle-section" data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>

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
          tooltip: '${ _('Click to zoom, double click to select') }',
          transformer: partitionChartDataTransformer,
          onStateChange: function(state){ },
          onClick: function(d) {
            $root.query.togglePivotFacet({facet: d.obj, widget_id: id()});
          },
          onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
        />
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>
</script>


<script type="text/html" id="heatmap-widget">
  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div class="floating-facet-toggle-section" data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id()).isLoading(false); } }">
      </span>
    </div>

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
          onComplete: function(){ viewModel.getWidgetById($parent.id()).isLoading(false) } }"
        />
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>
</script>


<script type="text/html" id="hit-widget">
  <div class="widget-spinner" data-bind="visible: ! $root.hasRetrievedResults()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()).has_data() -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
        <span class="facet-field-label">${ _('Metric') }</span>
        <select data-bind="options: HIT_OPTIONS, optionsText: 'label', optionsValue: 'value', value: properties.aggregate"></select>
      </div>
      <div data-bind="visible: ! $root.isEditing(), text: getHitOption(properties.aggregate())" class="muted"></div>
    </div>
    <span class="big-counter" data-bind="textSqueezer: counts"></span>
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
  </div>
  <div class="clearfix"></div>
  <div class="widget-spinner" data-bind="visible: isLoading() &&  $root.query.fqs().length > 0">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
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
        onComplete: function(){ var widget = viewModel.getWidgetById($parent.id()); if (widget != null) { widget.isLoading(false)}; } }" />
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
  </div>
</script>


<script type="text/html" id="leafletmap-widget">
  <div class="row-fluid">
    <div data-bind="visible: $root.isEditing" style="margin-top: 10px; margin-bottom: 20px;" class="leaflet-align">
      <span class="facet-field-label">${_('Latitude')}</span><div class="break-on-small-column"></div>
      <select data-bind="options: $root.collection.template.sortedFieldsNames, value: $root.collection.template.leafletmap.latitudeField, optionsCaption: '${ _('Choose...') }'"></select>
      &nbsp;&nbsp;
      <div class="break-on-small-column"></div>
      <span class="facet-field-label">${_('Longitude')}</span><div class="break-on-small-column"></div>
      <select data-bind="options: $root.collection.template.sortedFieldsNames, value: $root.collection.template.leafletmap.longitudeField, optionsCaption: '${ _('Choose...') }'"></select>
      &nbsp;&nbsp;
      <div class="break-on-small-column"></div>
      <span class="facet-field-label">${_('Label')}</span><div class="break-on-small-column"></div>
      <select data-bind="options: $root.collection.template.sortedFieldsNames, value: $root.collection.template.leafletmap.labelField, optionsCaption: '${ _('Choose...') }'"></select>
    </div>

    <div data-bind="leafletMapChart: {visible: $root.hasRetrievedResults() && $root.collection.template.leafletmapOn(), isLoading: isLoading(), datum: {counts: $root.response()},
      transformer: leafletMapChartDataTransformer,
      onComplete: function(){ var widget = viewModel.getWidgetById(id()); if (widget != null) { widget.isLoading(false)}; } }">
    </div>
  </div>

  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
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
    <div class="tab-content">
      <div class="tab-pane active" id="analysis-terms" data-bind="with: terms">
        <div class="widget-spinner" data-bind="visible: $parent.isLoading()">
          <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
        </div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0" class="table-striped">
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
          <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }" /><![endif]-->
        </div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() == 'error'">${ _('This field does not support stats') }</div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no stats to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0 && $data.data()[0].key.toLowerCase() != 'error'" class="table-striped">
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
    <div style="float: left; margin-right: 10px;text-align: center">
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
      <div class="alert alert-info inline" data-bind="visible: $root.collection.template.filteredModalFields().length == 0" style="margin-left: 250px;margin-right: 50px; height: 42px;line-height: 42px">
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
            <div class="control-group">
              <label class="control-label" for="settingssolrindex">${ _('Solr index') }</label>
              <div class="controls">
                <select id="settingssolrindex" data-bind="options: $root.initial.collections, value: $root.collection.name"></select>
              </div>
            </div>
            <!-- /ko -->
            <div class="control-group">
              <label class="control-label" for="settingsdescription">${ _('Description') }</label>
              <div class="controls">
                <input id="settingsdescription" type="text" class="input-xlarge" data-bind="value: $root.collection.description" style="margin-bottom: 0" />
              </div>
            </div>
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
                <input id="newqname" type="text" class="input-xxlarge" data-bind="value: $root.collection.newQDefinitionName, valueUpdate:'afterkeydown'" style="margin-bottom: 0" placeholder="${ _('Add current query as...') }" />
                <a title="${ _('Click on this button to add the currenty query as a new definition') }" class="btn plus-btn" data-bind="click: $root.collection.addQDefinition, css:{'disabled': $.trim($root.collection.newQDefinitionName()) == ''}" style="margin-top: 1px">
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
                    </span><span class="badge badge-right trash-share" data-bind="click: $root.collection.removeQDefinition"> <i class="fa fa-times"></i></span></li>
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
  <select id="settingstimeinterval" data-bind="value: collection.timeFilter.value" class="input-medium" style="margin-right: 4px">
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
                  <input id="settingstimestart" type="text" data-bind="value: collection.timeFilter.from, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:SS[Z]'}" />
                </div>
              </div>
              <div class="control-group" data-bind="visible: collection.timeFilter.type() == 'fixed'">
                <label class="control-label" for="settingstimeend">${ _('End date/time') }</label>
                <div class="controls">
                  <input id="settingstimeend" type="text" data-bind="value: collection.timeFilter.to, datepicker: {momentFormat: 'YYYY-MM-DD[T]HH:mm:SS[Z]'}" />
                </div>
              </div>
              <div class="control-group">
                <div class="controls">
                  <label class="checkbox">
                    <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.autorefresh"/> ${ _('Auto-refresh every') } <input type="number" class="input-mini" style="margin-bottom: 0; margin-left: 6px; margin-right: 6px; width: 46px; text-align:center" data-bind="value: $root.collection.autorefreshSeconds"/> ${ _('seconds') }
                  </label>
                </div>
              </div>
            </span>

            <!-- ko if: $root.availableDateFields().length == 0 -->
              <label class="checkbox">
                <input type="checkbox" style="margin-right: 4px; margin-top: 9px" data-bind="checked: $root.collection.autorefresh"/> ${ _('Auto-refresh every') } <input type="number" class="input-mini" style="margin-bottom: 0; margin-left: 6px; margin-right: 6px; width: 46px; text-align:center" data-bind="value: $root.collection.autorefreshSeconds"/> ${ _('seconds') }
              </label>
            <!-- /ko -->
          </fieldset>
        </form>

      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>

<div id="fieldAnalysis" class="popover mega-popover right">
  <div class="arrow"></div>
  <h3 class="popover-title" style="text-align: left">
    <a class="pull-right pointer" data-bind="click: function(){ $('#fieldAnalysis').hide(); $root.fieldAnalysesName(''); }"><i class="fa fa-times"></i></a>
    <strong data-bind="text: $root.fieldAnalysesName"></strong> ${ _(' field analysis') }
  </h3>
  <div class="popover-content" data-bind="template: { name: 'analysis-window' }" style="text-align: left"></div>
</div>



## Extra code for style and custom JS
<span id="extra" data-bind="augmenthtml: $root.collection.template.extracode"></span>


<link rel="stylesheet" href="${ static('search/css/search.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-filetypes.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">

<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_layout(True) }

<script src="${ static('search/js/search.utils.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('search/js/lzstring.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.textsqueezer.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.editable.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/shortcut.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/mustache.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>

<script src="${ static('search/js/search.ko.js') }" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }
${ dashboard.import_charts() }

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .search-bar {
    top: 58px!important;
  }
  .card-toolbar {
    top: 100px!important;
  }
  #emptyDashboardEditing {
    top: 190px!important;
  }
% endif
</style>

<script type="text/javascript" charset="utf-8">
var viewModel;

nv.dev = false;

var HIT_OPTIONS = [
  { value: "count", label: "${ _('Count') }" },
  { value: "unique", label: "${ _('Unique Count') }" },
  { value: "avg", label: "${ _('Average') }" },
  { value: "sum", label: "${ _('Sum') }" },
  { value: "min", label: "${ _('Min') }" },
  { value: "max", label: "${ _('Max') }" },
  { value: "sumsq", label: "${ _('Sum of square') }" },
  { value: "median", label: "${ _('Median') }" }
];

function getHitOption(value){
  for (var i=0; i < HIT_OPTIONS.length; i++){
    if (HIT_OPTIONS[i].value == value){
      return HIT_OPTIONS[i].label;
    }
  }
  return '';
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

function leafletMapChartDataTransformer(data) {
  var _data = [];
  if (!$.isEmptyObject(data.counts) && data.counts.response.docs && viewModel.collection.template.leafletmap.latitudeField() != "" && viewModel.collection.template.leafletmap.longitudeField() != "") {
    data.counts.response.docs.forEach(function (record) {
      var _obj = {
        lat: record[viewModel.collection.template.leafletmap.latitudeField()],
        lng: record[viewModel.collection.template.leafletmap.longitudeField()]
      }
      if (viewModel.collection.template.leafletmap.labelField() != "") {
        _obj.label = record[viewModel.collection.template.leafletmap.labelField()];
      }
      _data.push(_obj);
    });
  }
  return _data;
}


function toggleDocDetails(doc) {
  doc.showDetails(! doc.showDetails());

  if (doc.details().length == 0) {
    viewModel.getDocument(doc);
  }
}

function resizeFieldsList() {
  $(".fields-list").css("max-height", Math.max($("#result-container").height(), 230));
  window.setTimeout(function () {
    var _fillHeight = $("#result-container").height() - 40;
    if ($(".fields-list").height() < _fillHeight) {
      $(".fields-list").height(_fillHeight);
      $(".fields-list").css("max-height", _fillHeight);
    }
  }, 100);
}

$(document).ready(function () {

  var _resizeTimeout = -1;
  $(window).resize(function(){
    window.clearTimeout(_resizeTimeout);
    window.setTimeout(function(){
      resizeFieldsList();
    }, 200);
  });

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

  $(document).on("magicLayout", function(){
    resizeFieldsList();
  });

  $(document).on("setLayout", function(){
    resizeFieldsList();
  });

  var _query = ${ query | n,unicode };
  if (window.location.hash != ""){
    if (window.location.hash.indexOf("collection") == -1){
      try {
        var _decompress = LZString.decompressFromBase64(window.location.hash.substr(1));
        if (_decompress != null && $.trim(_decompress) != ""){
          _query = ko.mapping.fromJSON(LZString.decompressFromBase64(window.location.hash.substr(1)));
        }
      }
      catch (e){}
    }
  }

  viewModel = new SearchViewModel(${ collection.get_json(user) | n,unicode }, _query, ${ initial | n,unicode });

  viewModel.timelineChartTypes = ko.observableArray([
    {
      value: "line",
      label: "${ _('Lines')}"
    },
    {
      value: "bar",
      label: "${ _('Bars')}"
    }
  ]);

  ko.applyBindings(viewModel);

  viewModel.init(function(data){
    $(".chosen-select").trigger("chosen:updated");
  });

  viewModel.isRetrievingResults.subscribe(function(value){
    if (! value){
      resizeFieldsList();
    }
  });

  viewModel.isEditing.subscribe(function(value){
    if (value){
      window.setTimeout(function(){
        if ($(".slider-cnt").length > 0 && $(".slider-cnt").data("slider")){
          $(".slider-cnt").slider("redraw");
        }
      }, 300);
    }
  });

  var _refreshTimeout = null;

  viewModel.collection.autorefresh.subscribe(function (value) {
    if (value) {
      refresh();
    }
    else {
      window.clearTimeout(_refreshTimeout);
    }
  });

  if (viewModel.collection.autorefresh()) {
    refresh();
  }

  function refresh() {
    _refreshTimeout = window.setTimeout(function () {
      if (viewModel.collection.autorefresh()) {
        viewModel.search(refresh);
      }
    }, ($.isNumeric(viewModel.collection.autorefreshSeconds()) ? viewModel.collection.autorefreshSeconds() * 1 : 60) * 1000)
  }


  $("#addFacetDemiModal").on("hidden", function () {
    if (typeof selectedWidget.hasBeenSelected == "undefined"){
      addFacetDemiModalFieldCancel();
    }
  });

  $(document).on("shownAnalysis", function(){
    var _fieldElement = $(".field-selector").filter(function(){ return $(this).text().toLowerCase() === viewModel.fieldAnalysesName().toLowerCase();}).parent();
    $("#fieldAnalysis").show().css("top", _fieldElement.position().top - $("#fieldAnalysis").outerHeight()/2 + _fieldElement.outerHeight()/2).css("left", _fieldElement.position().left + _fieldElement.outerWidth());
  });

  % if is_owner:
  $(window).bind("keydown", "ctrl+s alt+s meta+s", function(e){
    e.preventDefault();
    viewModel.save();
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
    viewModel.collection.addQDefinition();
  });

  $(document).on("loadedQDefinition", function() {
    if ($(".demi-modal.fade.in").length > 0) {
      $(".demi-modal.fade.in .demi-modal-chevron").click();
    }
  });

  if (window.location.hash != "") {
    if (window.location.hash.indexOf("q=") > -1) {
      var _qdef = viewModel.collection.getQDefinition(window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "").split("=")[1]);
      if (_qdef != null){
        viewModel.collection.loadQDefinition(_qdef);
      }
    }
  }
});


  function toggleGridFieldsSelection() {
    if (viewModel.collection.template.fields().length > 0) {
      viewModel.collection.template.fieldsSelected([])
    }
    else {
      selectAllCollectionFields();
    }
  }

  function selectAllCollectionFields() {
    var _fields = [];
    $.each(viewModel.collection.fields(), function (index, field) {
      _fields.push(field.name());
    });
    viewModel.collection.template.fieldsSelected(_fields);
  }

  function columnDropAdditionalHandler(widget) {
    if (viewModel.collection.getFacetById(widget.id()) == null) {
      showAddFacetDemiModal(widget);
    }
    viewModel.search();
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
        }, 100)
      }
      else {
        row.autosizeWidgets();
      }
    }
  }

  var selectedWidget = null;
  var selectedRow = null;
  function showAddFacetDemiModal(widget, row) {
    if (["resultset-widget", "html-resultset-widget", "filter-widget", "leafletmap-widget"].indexOf(widget.widgetType()) == -1) {
      viewModel.collection.template.fieldsModalFilter("");
      viewModel.collection.template.fieldsModalType(widget.widgetType());
      viewModel.collection.template.fieldsModalFilter.valueHasMutated();
      $('#addFacetInput').typeahead({
        'source': viewModel.collection.template.availableWidgetFieldsNames(),
        'updater': function (item) {
          addFacetDemiModalFieldPreview({'name': function () {
            return item
          }});
          return item;
        }
      });
      selectedWidget = widget;
      selectedRow = row;
      $("#addFacetDemiModal").modal("show");
      $("#addFacetDemiModal input[type='text']").focus();
    }
    else {
      distributeRowWidgetsSize(row, true);
    }
  }


  function addFacetDemiModalFieldPreview(field) {
    var _existingFacet = viewModel.collection.getFacetById(selectedWidget.id());
    if (selectedWidget != null) {
      selectedWidget.hasBeenSelected = true;
      selectedWidget.isLoading(true);
      viewModel.collection.addFacet({'name': field.name(), 'widget_id': selectedWidget.id(), 'widgetType': selectedWidget.widgetType()});
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
    viewModel.removeWidget(selectedWidget);
    selectedRow = null;
  }

  $(document).on("setResultsHeight", function () {
    $("#result-main").height($("#result-container").outerHeight() + 100);
    resizeFieldsList();
  });

  function highlightColumn(column) {
    var _colName = $.trim(column.name());
    if (viewModel.collection.template.fieldsSelected.indexOf(_colName) > -1) {
      var _t = $("#result-container");
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
    if (! viewModel.collection.idField()) {
      $(document).trigger("warn", "${ _('Result highlighting is unavailable: the collection does not have an index field') }");
    }
  }
</script>

${ commonfooter(messages) | n,unicode }
