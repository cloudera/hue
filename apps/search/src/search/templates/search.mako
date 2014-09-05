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

<%namespace name="dashboard" file="common_dashboard.mako" />

${ commonheader(_('Search'), "search", user, "80px") | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("collection") > -1) {
      location.href = "/search/?" + window.location.hash.substr(1);
    }
  }
</script>

<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    % if user.is_superuser:
      <button type="button" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: save, css: {'btn': true}"><i class="fa fa-save"></i></button>
      <button type="button" title="${ _('Settings') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#settingsDemiModal"
          data-bind="css: {'btn': true}">
        <i class="fa fa-cog"></i>
      </button>
    % endif
      <button type="button" title="${ _('Share') }" rel="tooltip" data-placement="bottom" data-bind="click: showShareModal, css: {'btn': true}"><i class="fa fa-link"></i></button>
    % if user.is_superuser:
      &nbsp;&nbsp;&nbsp;
      <a class="btn" href="${ url('search:new_search') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-file-o"></i></a>
      <a class="btn" href="${ url('search:admin_collections') }" title="${ _('Dashboards') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-tags"></i></a>
    % endif
  </div>

  <form data-bind="visible: $root.isEditing() && columns().length == 0">
    ${ _('Select a search index') }
    <!-- ko if: columns().length == 0 -->
    <select data-bind="options: $root.initial.collections, value: $root.collection.name">
    </select>
    <!-- /ko -->
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
        <input data-bind="clearable: q" maxlength="4096" type="text" class="search-query input-xlarge">
        <!-- ko if: $index() >= 1 -->
        <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
        <!-- /ko -->
      </span>

      <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ"><i class="fa fa-plus"></i></a>

      <button type="submit" id="search-btn" class="btn btn-inverse" style="margin-left:10px"><i class="fa fa-search"></i></button>
    </div>
  </form>
</div>

<%dashboard:layout_toolbar>
      <%def name="widgets()">
        <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableResultset(), isEnabled: availableDraggableResultset,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast'); $root.collection.template.isGridLayout(true); checkResultHighlightingAvailability(); }}}"
         title="${_('Grid Results')}" rel="tooltip" data-placement="top">
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
         title="${_('HTML Results')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-code"></i>
         </a>
    </div>
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
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableBar(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableNumbers() },
                    draggable: {data: draggableLine(), isEnabled: availableDraggableNumbers,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Line Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableNumbers() ? 'move' : 'default' }">
                       <i class="hcha hcha-line-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Timeline')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableHistogram() ? 'move' : 'default' }">
                       <i class="hcha hcha-timeline-chart"></i>
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
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableTree(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Tree')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sitemap fa-rotate-270"></i>
         </a>
   </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableMap(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
         </a>
   </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableLeafletMap(), isEnabled: availableDraggableChart,
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Marker Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-map-marker"></i>
         </a>
   </div>
      </%def>
</%dashboard:layout_toolbar>

${ dashboard.layout_skeleton() }


<script type="text/html" id="empty-widget">
  ${ _('This is an empty widget.')}
</script>


<script type="text/html" id="hit-widget">
  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      ${ _('Label') }: <input type="text" data-bind="value: label" />
    </div>

    <span data-bind="text: query" />: <span data-bind="text: count" />
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="facet-toggle">
    <div class="facet-field-cnt" data-bind="visible: properties.canRange">
      <span class="facet-field-label facet-field-label-fixed-width">${ _('Type') }</span>
      <a href="javascript: void(0)" title="${ _('Toggle range or field facet') }" data-bind="click: $root.collection.toggleRangeFacet" data-loading-text="...">
        <i class="fa" data-bind="css: { 'fa-arrows-h': type() == 'range', 'fa-circle': type() == 'field' }, attr: { title: type() == 'range' ? 'Range' : 'Term' }"></i>
        <span data-bind="visible: type() == 'range'">${_('range')}</span>
        <span data-bind="visible: type() == 'field'">${_('field')}</span>
      </a>
    </div>

    <div class="facet-field-cnt">
      <span class="facet-field-label facet-field-label-fixed-width">${ _('Sorting') }</span>
      <a href="javascript: void(0)" title="${ _('Toggle sort order') }" data-bind="click: $root.collection.toggleSortFacet" data-loading-text="...">
        <i class="fa" data-bind="css: { 'fa-caret-down': properties.sort() == 'desc', 'fa-caret-up': properties.sort() == 'asc' }"></i>
        <span data-bind="visible: properties.sort() == 'desc'">${_('descending')}</span>
        <span data-bind="visible: properties.sort() == 'asc'">${_('ascending')}</span>
      </a>
    </div>

    <!-- ko if: type() == 'pivot' -->
      <select data-bind="options: $root.collection.template.availableWidgetFieldsNames, value: properties.facets_form.field, optionsCaption: ' '"></select>
      <input type="text" class="input-medium" data-bind="value: properties.facets_form.limit"/>
      <input type="text" class="input-medium" data-bind="value: properties.facets_form.mincount"/>

      <a href="javascript: void(0)" data-bind="click: $root.collection.addPivotFacetValue">
        <i class="fa fa-plus"></i>
      </a>

      ${ _('Limit') } <input type="text" class="input-medium" data-bind="value: properties.limit"/>
      ${ _('Mincount') } <input type="text" class="input-medium" data-bind="value: properties.mincount"/>
      ${ _('Plot') } <input type="checkbox" data-bind="checked: properties.graph"></span>
    <!-- /ko -->

    <!-- ko if: type() == 'range' -->
      <!-- ko ifnot: properties.isDate() -->
        <div class="slider-cnt" data-bind="slider: {start: properties.min, end: properties.max, gap: properties.gap, min: properties.start, max: properties.end}"></div>
      <!-- /ko -->
      <!-- ko if: properties.isDate() -->
        <div data-bind="daterangepicker: {start: properties.start, end: properties.end, gap: properties.gap, min: properties.min, max: properties.max}"></div>
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

</script>

<script type="text/html" id="facet-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id).isLoading(false); } }">
      </span>
    </div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() != 'range' -->
        <div data-bind="foreach: $parent.counts">
          <div>
            <a href="javascript: void(0)">
              <!-- ko if: $index() < $parent.properties.limit() -->
                <!-- ko if: ! $data.selected -->
                  <span data-bind="text: $data.value, click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }"></span>
                  <span class="counter" data-bind="text: ' (' + $data.count + ')', click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }"></span>
                <!-- /ko -->
                <!-- ko if: $data.selected -->
                  <span data-bind="click: function(){ $root.query.toggleFacet({facet: $data, widget_id: $parent.id()}) }">
                    <span data-bind="text: $data.value"></span>
                    <i class="fa fa-times"></i>
                  </span>
                <!-- /ko -->
              <!-- /ko -->
              <!-- ko if: $index() == $parent.properties.limit() -->
                <!-- ko if: $parent.properties.prevLimit == undefined || $parent.properties.prevLimit == $parent.properties.limit() -->
                  <span data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                    ${ _('Show more...') }
                  </span>
                <!-- /ko -->
                <!-- ko if: $parent.properties.prevLimit != undefined && $parent.properties.prevLimit != $parent.properties.limit() -->
                  <span data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'up') }">
                    ${ _('Show more') }
                  </span>
                  /
                  <span data-bind="click: function(){ $root.collection.upDownFacetLimit($parent.id(), 'down') }">
                    ${ _('less...') }
                  </span>
                </span>
                <!-- /ko -->
              <!-- /ko -->
            </a>
          </div>
        </div>
      <!-- /ko -->
      <!-- ko if: type() == 'range' -->
        <div data-bind="foreach: $parent.counts">
          <div>
            <a href="javascript: void(0)">
              <!-- ko if: ! selected -->
                <span data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }">
                  <span data-bind="text: $data.from + ' - ' + $data.to"></span>
                  <span class="counter" data-bind="text: ' (' + $data.value + ')'"></span>
                </span>
              <!-- /ko -->
              <!-- ko if: selected -->
                <span data-bind="click: function(){ $root.query.selectRangeFacet({count: $data.value, widget_id: $parent.id(), from: $data.from, to: $data.to, cat: $data.field}) }">
                  <span data-bind="text: $data.from + ' - ' + $data.to"></span>
                  <i class="fa fa-times"></i>
                </span>
              <!-- /ko -->
            </a>
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
        <div class="fields-list" data-bind="foreach: $root.collection.template.filteredAttributeFields" style="max-height: 230px; overflow-y: auto; padding-left: 4px">
          <div style="margin-bottom: 3px">
            <input type="checkbox" data-bind="checkedValue: name, checked: $root.collection.template.fieldsSelected" style="margin: 0" />
            <div data-bind="text: name, css:{'field-selector': true, 'hoverable': $root.collection.template.fieldsSelected.indexOf(name()) > -1}, click: highlightColumn"></div>
            <i class="fa fa-question-circle pull-right muted pointer analysis" title="${ _('Click to analyse field') }" data-bind="click: function() { $root.fieldAnalysesName(name()); $root.showFieldAnalysis(); }"></i>
          </div>
        </div>
        <div data-bind="visible: $root.collection.template.filteredAttributeFields().length == 0" style="padding-left: 4px; padding-top: 5px; font-size: 40px; color: #CCC">
          <i class="fa fa-frown-o"></i>
        </div>
      </span>
    </div>

    <div>
      <div class="widget-spinner" data-bind="visible: $root.isRetrievingResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
      </div>

      <div data-bind="visible: !$root.isRetrievingResults() && $root.results().length == 0">
        </br>
        ${ _('Your search did not match any documents.') }
      </div>

      <div data-bind="visible: !$root.isRetrievingResults() && $root.results().length > 0">
        <!-- ko if: $root.response().response -->
          <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }" style="padding: 8px; color: #666"></div>
        <!-- /ko -->

        <div id="result-main" style="overflow-x: auto">
          <table id="result-container" data-bind="visible: ! $root.isRetrievingResults()" style="margin-top: 0; width: 100%">
            <thead>
              <tr data-bind="visible: $root.collection.template.fieldsSelected().length > 0, template: {name: 'result-sorting'}">
              </tr>
              <tr data-bind="visible: $root.collection.template.fieldsSelected().length == 0">
                <th style="width: 18px">&nbsp;</th>
                <th>${ ('Document') }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: { data: $root.results, as: 'doc'}" class="result-tbody">
              <tr class="result-row">
                <td>
                  <a href="javascript:void(0)" data-bind="click: toggleDocDetails">
                    <i class="fa" data-bind="css: {'fa-caret-right' : ! doc.showDetails(), 'fa-caret-down': doc.showDetails() }"></i>
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
                    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
                  <!-- /ko -->
                  <!-- ko if: $data.details().length > 0 -->
                    <div class="document-details">
                      <table>
                        <tbody data-bind="foreach: details">
                          <tr>
                             <th style="text-align: left; white-space: nobreak; vertical-align:top; padding-right:20px", data-bind="text: key"></th>
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
            <textarea data-bind="codemirror: {data: $root.collection.template.template, lineNumbers: true, htmlMode: true, mode: 'text/html' }" data-template="true"></textarea>
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
      <div data-bind="visible: ! $root.isRetrievingResults() && $root.results().length == 0">
        </br>
        ${ _('Your search did not match any documents.') }
      </div>

      <!-- ko if: $root.response().response && $root.results().length > 0 -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->

      <div id="result-container" data-bind="foreach: $root.results">
        <div class="result-row" data-bind="html: $data"></div>
      </div>

      <div class="widget-spinner" data-bind="visible: $root.isRetrievingResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
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
  <span data-bind="text: ($data.response.start + $root.collection.template.rows())"></span>
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

  <!-- ko if: $data.response.numFound > 0 -->
  <span class="pull-right">
    <form method="POST" action="${ url('search:download') }">
      <input type="hidden" name="collection" data-bind="value: ko.mapping.toJSON($root.collection)"/>
      <input type="hidden" name="query" data-bind="value: ko.mapping.toJSON($root.query)"/>
      <input type="hidden" name="download">
      <button class="btn" type="submit" name="json" title="${ _('Download first rows as JSON') }"><i class="hfo hfo-file-json"></i></button>
      <button class="btn" type="submit" name="csv" title="${ _('Download first rows as CSV') }"><i class="hfo hfo-file-csv"></i></button>
      <button class="btn" type="submit" name="xls" title="${ _('Download first rows as XLS') }"><i class="hfo hfo-file-xls"></i></button>
    </form>
  </span>
  <!-- /ko -->
</div>
</script>

<script type="text/html" id="histogram-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px" data-bind="visible: counts.length > 0">
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.timeLineZoom"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
      <span class="facet-field-label">${ _('Group by') }</span>
      <select class="input-medium" data-bind="options: $root.query.multiqs, optionsValue: 'id', optionsText: 'label', value: $root.query.selectedMultiq"></select>
    </div>

    <div data-bind="timelineChart: {datum: {counts: counts, extraSeries: extraSeries, widget_id: $parent.id(), label: label}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label, transformer: timelineChartDataTransformer,
      fqs: $root.query.fqs,
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
      onClick: function(d){ viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: $parent.id(), from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) }}" />
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="bar-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'range' -->
        <div style="padding-bottom: 10px; text-align: right; padding-right: 20px">
          <span class="facet-field-label">${ _('Zoom') }</span>
          <a href="javascript:void(0)" data-bind="click: $root.collection.timeLineZoom"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
        </div>
      <!-- /ko -->
    </div>

    <div data-bind="barChart: {datum: {counts: counts, widget_id: $parent.id(), label: label}, stacked: false, field: field, label: label,
      fqs: $root.query.fqs,
      transformer: barChartDataTransformer,
      onStateChange: function(state){ },
      onClick: function(d) {
        if (d.obj.field != undefined) {
          viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field});
        } else {
          viewModel.query.toggleFacet({facet: d.obj, widget_id: d.obj.widget_id});
        }
      },
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: id}) },
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) } }"
    />
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="line-widget">
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>

  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

    <div style="padding-bottom: 10px; text-align: right; padding-right: 20px" data-bind="visible: counts.length > 0">
      <span class="facet-field-label">${ _('Zoom') }</span>
      <a href="javascript:void(0)" data-bind="click: $root.collection.timeLineZoom"><i class="fa fa-search-minus"></i> ${ _('reset') }</a>
    </div>

    <div data-bind="lineChart: {datum: {counts: counts, widget_id: $parent.id(), label: label}, field: field, label: label,
      transformer: lineChartDataTransformer,
      onClick: function(d){ viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) } }"
    />
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="pie-widget">
  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <!-- ko if: type() == 'range' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts, widget_id: $parent.id}, field: field, fqs: $root.query.fqs,
        transformer: rangePieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){ viewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
        onComplete: function(){ viewModel.getWidgetById($parent.id).isLoading(false)} }" />
      <!-- /ko -->
      <!-- ko if: type() != 'range' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts, widget_id: $parent.id}, field: field, fqs: $root.query.fqs,
        transformer: pieChartDataTransformer,
        maxWidth: 250,
        onClick: function(d){viewModel.query.toggleFacet({facet: d.data.obj, widget_id: d.data.obj.widget_id})},
        onComplete: function(){viewModel.getWidgetById($parent.id).isLoading(false)}}" />
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>


<script type="text/html" id="tree-widget">
  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle', afterRender: function(){ $root.getWidgetById($parent.id).isLoading(false); } }">
      </span>
    </div>

    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      ${ _('Cross with') }
      <div data-bind="foreach: $data.properties.facets">
        <span data-bind="text: field"></span>
        ${ _('Limit') } <input type="text" class="input-medium" data-bind="value: limit"/>
        ${ _('Mincount') } <input type="text" class="input-medium" data-bind="value: mincount"/>
        <a href="javascript: void(0)" data-bind="click: function() { $root.collection.removePivotFacetValue({'pivot_facet': $parent, 'value': $data}); }">
          <i class="fa fa-minus"></i>
        </a>
      </div>
    </div>

    <span data-bind="text: ko.mapping.toJSON(count)"></span>

  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>


<script type="text/html" id="filter-widget">
  <div data-bind="visible: $root.query.fqs().length == 0" style="margin-top: 10px">${_('There are currently no filters applied.')}</div>
  <div data-bind="foreach: { data: $root.query.fqs, afterRender: function(){ isLoading(false); } }">
    <!-- ko if: $data.type() == 'field' -->
    <div class="filter-box">
      <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ chartsUpdatingState(); viewModel.query.removeFilter($data); viewModel.search() }"><i class="fa fa-times"></i></a>
      <strong>${_('field')}</strong>:
      <span data-bind="text: $data.field"></span>
      <br/>
      <strong>${_('value')}</strong>:
      <span data-bind="text: $data.filter"></span>
    </div>
    <!-- /ko -->
    <!-- ko if: $data.type() == 'range' -->
    <div class="filter-box">
      <a href="javascript:void(0)" class="pull-right" data-bind="click: function(){ chartsUpdatingState(); viewModel.query.removeFilter($data); viewModel.search() }"><i class="fa fa-times"></i></a>
      <strong>${_('field')}</strong>:
      <span data-bind="text: $data.field"></span>
      <br/>
      <span data-bind="foreach: $data.properties" style="font-weight: normal">
        <strong>${_('from')}</strong>: <span data-bind="text: $data.from"></span>
        <br/>
        <strong>${_('to')}</strong>: <span data-bind="text: $data.to"></span>
      </span>
    </div>
    <!-- /ko -->
  </div>
  <div class="clearfix"></div>
  <div class="widget-spinner" data-bind="visible: isLoading() &&  $root.query.fqs().length > 0">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>


<script type="text/html" id="map-widget">
  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      ${ _('Scope') }:
      <select data-bind="selectedOptions: properties.scope" class="input-small">
        <option value="world">${ _("World") }</option>
        <option value="usa">${ _("USA") }</option>
      </select>
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div data-bind="mapChart: {data: {counts: $parent.counts, scope: $root.collection.getFacetById($parent.id).properties.scope()},
        transformer: mapChartDataTransformer,
        maxWidth: 750,
        isScale: true,
        onClick: function(d){ viewModel.query.toggleFacet({facet: d, widget_id: $parent.id}) },
        onComplete: function(){ var widget = viewModel.getWidgetById($parent.id); if (widget != null) {widget.isLoading(false)};} }" />
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
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
          <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
        </div>
        <div class="alert" data-bind="visible: ! $parent.isLoading() && $data.data().length == 0">${ _('There are no terms to be shown') }</div>
        <table style="width: 100%" data-bind="visible: ! $parent.isLoading() && $data.data().length > 0" class="table-striped">
          <tbody data-bind="foreach: $data.data">
          <tr>
            <td data-bind="text: val.value"></td>
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
          <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
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

<script type="text/html" id="leafletmap-widget">
  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById(id)" style="margin-bottom: 20px">
      <span data-bind="template: { name: 'facet-toggle' }">
      </span>
    </div>
    <div data-bind="leafletMapChart: {datum: {counts: counts},
      transformer: leafletMapChartDataTransformer,
      onComplete: function(){ var widget = viewModel.getWidgetById(id); if (widget != null) {widget.isLoading(false)};} }" />
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>

<div id="shareModal" class="modal hide" data-backdrop="true">
  <div class="modal-header">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <h3>${_('Share this dashboard')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('The following URL will show the current dashboard and the applied filters.')}</p>
    <input type="text" style="width: 540px" />
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>


<div id="addFacetDemiModal" class="demi-modal hide" data-backdrop="false">
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
</div>

<div id="settingsDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-body">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <div style="float: left; margin-right: 30px; text-align: center; line-height: 28px">
      <!-- ko if: $root.initial.inited() -->
      ${ _('Solr index') }
      <select data-bind="options: $root.initial.collections, value: $root.collection.name" style="margin-bottom: 0">
      </select>
      <!-- /ko -->
    </div>
    <label class="checkbox" style="margin-top: 4px">
      ${ _('Visible to everybody') } <input type="checkbox" data-bind="checked: $root.collection.enabled"/>
    </label>
  </div>
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


<link rel="stylesheet" href="/search/static/css/search.css">
<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">

<script src="/static/ext/js/moment-with-langs.min.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_layout() }

<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/lzstring.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/shortcut.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/mustache.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/search/static/js/search.ko.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_bindings() }
${ dashboard.import_charts() }

<script type="text/javascript" charset="utf-8">
var viewModel;

nv.dev = false;

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

function rangePieChartDataTransformer(data) {
  var _data = [];
  $(data.counts).each(function (cnt, item) {
    item.widget_id = data.widget_id;
    _data.push({
      label: item.from + ' - ' + item.to,
      from: item.from,
      to: item.to,
      value: item.value,
      obj: item
    });
  });
  return _data;
}

function barChartDataTransformer(rawDatum) {
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
    _data.push({
      label: item.value,
      value: item.count,
      obj: item
    });
  });
  return _data;
}

function leafletMapChartDataTransformer(data) {
  var _data = [];
  _data.push({lat: 33.305606842041016, lng: -111.978759765625});
  _data.push({lat: 33.4143447876, lng: -111.913032532});
  _data.push({lat: 33.5229454041, lng: -111.90788269});
  _data.push({lat: 33.3910255432, lng: -111.68447876});
  _data.push({lat: 33.3907928467, lng: -112.012504578});
  _data.push({lat: 33.4691314697, lng: -112.04750824});
  _data.push({lat: 33.4347496033, lng: -112.006439209});
  _data.push({lat: 33.5096054077, lng: -112.025741577});
  _data.push({lat: 33.4495391846, lng: -112.065666199});
  _data.push({lat: 33.4248809814, lng: -111.940200806});
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

  viewModel = new SearchViewModel(${ collection.get_c(user) | n,unicode }, _query, ${ initial | n,unicode });
  ko.applyBindings(viewModel);


  viewModel.init(function(data){
    $(".chosen-select").trigger("chosen:updated");
  });
  viewModel.isRetrievingResults.subscribe(function(value){
    if (!value){
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

  $("#addFacetDemiModal").on("hidden", function () {
    if (typeof selectedWidget.hasBeenSelected == "undefined"){
      addFacetDemiModalFieldCancel();
    }
  });

  $(document).on("shown.fieldAnalysis", function(){

    var _fieldElement = $(".field-selector").filter(function(){ return $(this).text().toLowerCase() === viewModel.fieldAnalysesName();}).parent();
    $("#fieldAnalysis").show().css("top", _fieldElement.position().top - $("#fieldAnalysis").outerHeight()/2 + _fieldElement.outerHeight()/2).css("left", _fieldElement.position().left + _fieldElement.outerWidth());
  });
});

  function showShareModal() {
    if (window.location.search.indexOf("collection") == -1 && window.location.hash.indexOf("collection") == -1) {
      $(document).trigger("error", "${_('The current collection must be saved to be shared.')}");
    }
    else {
      $("#shareModal input[type='text']").on("focus", function () {
        this.select();
      });
      var _search = window.location.search;
      var _pathname = window.location.pathname;
      if (_pathname.indexOf("${ url('search:new_search') }") > -1) {
        _pathname = "${ url('search:index') }";
      }
      if (_search == "" && window.location.hash.indexOf("collection") > -1) {
        _search = "?" + window.location.hash.substr(1);
      }

      if (_search != "") {
        $("#shareModal input[type='text']").val(window.location.origin + _pathname + _search + "#" + LZString.compressToBase64(ko.mapping.toJSON(viewModel.query))).focus();
        $("#shareModal").modal("show");
      }
      else {
        $(document).trigger("error", "${_('The current collection cannot be shared.')}");
      }
    }
  }

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

  function widgetDraggedAdditionalHandler(widget) {
    showAddFacetDemiModal(widget);
  }

  var selectedWidget = null;
  function showAddFacetDemiModal(widget) {
    if (["resultset-widget", "html-resultset-widget", "filter-widget"].indexOf(widget.widgetType()) == -1) {
      viewModel.collection.template.fieldsModalFilter("");
      viewModel.collection.template.fieldsModalType(widget.widgetType());
      viewModel.collection.template.fieldsModalFilter.valueHasMutated();
      $('#addFacetInput').typeahead({
          'source': viewModel.collection.template.availableWidgetFieldsNames(),
          'updater': function(item) {
              addFacetDemiModalFieldPreview({'name': function(){return item}});
              return item;
           }
      });
      selectedWidget = widget;
      $("#addFacetDemiModal").modal("show");
      $("#addFacetDemiModal input[type='text']").focus();
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
    }
  }

  function addFacetDemiModalFieldCancel() {
    viewModel.removeWidget(selectedWidget);
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
