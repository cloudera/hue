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

${ commonheader(_('Search'), "search", user, "80px") | n,unicode }

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="padding-right:50px">
      <button type="button" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"  data-bind="click: save, css: {'btn': true}"><i class="fa fa-save"></i></button>
      <button type="button" title="${ _('Share') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-link"></i></button>
      &nbsp;&nbsp;&nbsp;            
      <a class="btn" href="${ url('search:new_search') }" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-file-o"></i></a>
      <a class="btn" href="${ url('search:admin_collections') }" title="${ _('Collections') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-tags"></i></a> 
    </div>
  % endif
  
  <form data-bind="visible: columns().length == 0">  
    ${ _('Search') }
    <!-- ko if: $root.initial.collections -->
    <select data-bind="options: $root.initial.collections, value: $root.collection.name">
    </select>
    <!-- /ko -->
  </form>
  
  <form class="form-search" style="margin: 0" data-bind="submit: searchBtn, visible: columns().length != 0"">
    <strong>${_("Search")}</strong>
    <div class="input-append">
      <div class="selectMask">
        <span class="current-collection" data-bind="text: collection.label"></span>
        ## click: show also collection list + edit label box        
      </div>

      <span data-bind="foreach: query.qs">
        <input data-bind="value: q" maxlength="256" type="text" class="search-query input-xlarge" style="cursor: auto;">
        <!-- ko if: $index() >= 1 -->
        <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
        <!-- /ko -->
      </span>

      <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ"><i class="fa fa-plus"></i></a>

      <button type="submit" id="search-btn" class="btn btn-inverse" style="margin-left:10px"><i class="fa fa-search"></i></button>
    </div>
  </form>
</div>

<div class="card card-toolbar" data-bind="slideVisible: isEditing">
  <div style="float: left">
    <div class="toolbar-label">${_('LAYOUT')}</div>
    <a href="javascript: oneThirdLeftLayout()" onmouseover="viewModel.previewColumns('oneThirdLeft')" onmouseout="viewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 24px"></div>
        <div class="layout-box" style="width: 72px; margin-left: 4px"></div>
      </div>
    </a>
    <!-- <a href="javascript: oneThirdRightLayout()" onmouseover="viewModel.previewColumns('oneThirdRight')" onmouseout="viewModel.previewColumns('')">
      <div class="layout-container">
        <div class="layout-box" style="width: 72px"></div>
        <div class="layout-box" style="width: 24px; margin-left: 4px"></div>
      </div>
    </a> -->
    <a href="javascript: fullLayout()" onmouseover="viewModel.previewColumns('full')" onmouseout="viewModel.previewColumns('')">
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

  <div style="float: left; margin-left: 20px" data-bind="visible: columns().length > 0">
    <div class="toolbar-label">${_('WIDGETS')}</div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableResultset(), isEnabled: availableDraggableResultset,
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast'); $root.collection.template.isGridLayout(true); }}}"
         title="${_('Grid Results')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableResultset()},
                       style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-table"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableHtmlResultset(), 
                    isEnabled: availableDraggableResultset, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast'); $root.collection.template.isGridLayout(false); }}}" 
         title="${_('HTML Results')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableResultset()}, 
                       style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-code"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableFacet(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Text Facet')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableChart()}, 
                       style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="fa fa-sort-amount-asc"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggablePie(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}"
         title="${_('Pie Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableChart()}, 
                       style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-pie-chart"></i>
         </a>
    </div>
    <!-- <div class="draggable-widget" data-bind="draggable: {data: draggableHit(), options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" title="${_('Hit Count')}" rel="tooltip" data-placement="top"><a data-bind="attr: {href: $root.availableDraggableResultset()}, css: {'btn-inverse': ! $root.availableDraggableResultset() }, style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }"><i class="fa fa-tachometer"></i></a></div> -->
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableBar(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableChart()}, 
                       style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableLine(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Line')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableChart()}, 
                       style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-line-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Histogram')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableHistogram()}, 
                       style: { cursor: $root.availableDraggableHistogram() ? 'move' : 'default' }">
                       <i class="fa fa-long-arrow-right"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableFilter() },
                    draggable: {data: draggableFilter(), isEnabled: availableDraggableFilter, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Filter Bar')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableFilter()}, 
                       style: { cursor: $root.availableDraggableFilter() ? 'move' : 'default' }">
                       <i class="fa fa-filter"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableMap(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 
                              'stop': function(event, ui){$('.card-body').slideDown('fast');}}}" 
         title="${_('Map')}" rel="tooltip" data-placement="top">
         <a data-bind="attr: {href: $root.availableDraggableChart()}, 
                       style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-map-chart"></i>
         </a>
   </div>
  </div>
  <div class="clearfix"></div>
</div>

<div id="emptyDashboard" data-bind="visible: !isEditing() && columns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${_('Click on the pencil to get started with your dashboard!')}</div>
  <img src="/search/static/art/hint_arrow.png" />
</div>


<div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0, css:{'with-top-margin': isEditing()}">
  <div class="container-fluid">
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneThirdLeft'">
      <div class="span3 preview-row"></div>
      <div class="span9 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'oneThirdRight'">
      <div class="span9 preview-row"></div>
      <div class="span3 preview-row"></div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'full'">
      <div class="span12 preview-row">
      </div>
    </div>
    <div class="row-fluid" data-bind="visible: previewColumns() == 'magic'">
      <div class="span12 preview-row">
        ${ _('Template predefined with some widgets.') }
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
    <div data-bind="template: { name: 'row-template', foreach: rows}">
    </div>
    <div style="height: 50px; padding-left: 6px" data-bind="visible: $root.isEditing">
      <a href="javascript:void(0)" class="btn" style="margin: 4px; margin-right: 10px" data-bind="click: addEmptyRow"><i class="fa fa-plus"></i> ${_('Row')}</a>
    </div>
  </div>
</script>

<script type="text/html" id="row-template">
  <div class="emptyRow" data-bind="visible: widgets().length == 0 && $index() == 0 && $root.isEditing() && $parent.size() > 4 && $parent.rows().length == 1">
    <img src="/search/static/art/hint_arrow_flipped.png" style="float:left; margin-right: 10px"/>
    <div style="float:left; text-align: center; width: 260px">${_('Drag any of the widgets inside your empty row')}</div>
    <div class="clearfix"></div>
  </div>
  <div class="container-fluid">
    <div class="row-header" data-bind="visible: $root.isEditing">
      <span class="muted">${_('Row')}</span>
      <div style="display: inline; margin-left: 60px">
        <a href="javascript:void(0)" data-bind="visible:$index()<$parent.rows().length-1, click: function(){moveDown($parent, this)}"><i class="fa fa-chevron-down"></i></a>
        <a href="javascript:void(0)" data-bind="visible:$index()>0, click: function(){moveUp($parent, this)}"><i class="fa fa-chevron-up"></i></a>
        <a href="javascript:void(0)" data-bind="visible:$parent.rows().length > 1, click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </div>
    <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing}, sortable: { template: 'widget-template', data: widgets, isEnabled: $root.isEditing, options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast');}, 'helper': function(event){$('.card-body').slideUp('fast');var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}}, dragged: function(widget){$('.card-body').slideDown('fast');showAddFacetDemiModal(widget);viewModel.search()}}">
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
      <span data-bind="with: $root.collection.getFacetById(id())">
        <span data-bind="editable: label"></span>
      </span>
      <!-- ko ifnot: $root.collection.getFacetById(id()) -->
        <span data-bind="text: name"></span>
      <!-- /ko -->
      <div class="inline pull-right" data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" data-bind="click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </h2>
    <div class="card-body" style="padding: 5px;">
    
      <div data-bind="template: { name: function() { return widgetType(); } }" class="widget-main-section"></div>
    <!--
      <ul class="nav nav-pills" data-bind="visible: $root.isEditing()">
        <li class="active">
          <a href="javascript: void(0)" class="widget-main-pill">${_('Preview')}</a>
        </li>
        <li><a href="javascript: void(0)" class="widget-settings-pill">${_('Settings')}</a></li>
      </ul>

      <div data-bind="template: { name: function() { return widgetType(); } }" class="widget-main-section"></div>
      <div data-bind="visible: $root.isEditing()" class="widget-settings-section">
        <ul class="unstyled" style="margin: 10px">
          <li>${ _('Name')}: <input type="text" data-bind="value: name" class="input-mini" /></li>
        </ul>
      </div>
    -->
    </div>
  </div>
</script>

<script type="text/html" id="empty-widget">
  ${ _('This is an empty widget.')}
</script>


<script type="text/html" id="hit-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

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
    <!-- ko if: type() == 'range' -->
      <br/>
      ${ _('Start') }: <input type="text" data-bind="value: properties.start" />
      ${ _('End') }: <input type="text" data-bind="value: properties.end" />
      ${ _('Gap') }: <input type="text" data-bind="value: properties.gap" />
    <!-- /ko -->
    <!-- ko if: type() == 'field' -->
      ${ _('Limit') }: <input type="text" data-bind="value: properties.limit" />      
    <!-- /ko -->

    <a href="javascript: void(0)" class="btn btn-loading" data-bind="visible: properties.canRange, click: $root.collection.toggleRangeFacet" data-loading-text="...">
      <i class="fa" data-bind="css: { 'fa-arrows-h': type() == 'range', 'fa-circle': type() == 'field' }, attr: { title: type() == 'range' ? 'Range' : 'Term' }"></i>
    </a>
    <a href="javascript: void(0)" class="btn btn-loading" data-bind="click: $root.collection.toggleSortFacet" data-loading-text="...">          
      <i class="fa" data-bind="css: { 'fa-caret-down': properties.sort() == 'desc', 'fa-caret-up': properties.sort() == 'asc' }"></i>
    </a>
</script>

<script type="text/html" id="facet-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

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
              <!-- ko if: $index() == $parent.properties.limit() -->
                </br>${ _('Show more...') }
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
    <div style="float:left; margin-right: 10px" >
      <span data-bind="visible: ! $root.collection.template.showFieldList()">
        <a href="javascript: void(0)" class="btn"
          data-bind="click: function(){ $root.collection.template.showFieldList(true) }">
          <i class="fa fa-chevron-right"></i>
        </a>
      </span>
    </div>
    <div data-bind="visible: $root.isEditing() || $root.collection.template.showFieldList()" style="float:left; margin-right: 10px" >
      <span data-bind="visible: $root.collection.template.showFieldList()">
        <a href="javascript: void(0)" class="btn"
          data-bind="click: function(){ $root.collection.template.showFieldList(false) }">
          <i class="fa fa-chevron-left"></i>
        </a>
        <strong>${ _('Fields') }</strong>      
        &nbsp;
        <a href="javascript: void(0)" class="btn"
          data-bind="click: toggleGridFieldsSelection, css: { 'btn-inverse': $root.collection.template.fields().length > 0 }">
          <i class="fa fa-square-o"></i>
        </a>
        <div data-bind="foreach: $root.collection.template.fieldsAttributes">
          <input type="checkbox" data-bind="checkedValue: name, checked: $root.collection.template.fieldsSelected" /> 
          <span data-bind="text: '&nbsp;' + name()"></span>
          <br/>
        </div>
      </span>
    </div>

    <div style="overflow-x: auto">
      <div data-bind="visible: $root.results().length == 0">
        ${ _('Your search did not match any documents.') }
      </div>
    
      <!-- ko if: $root.response().response -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->
    
      <table id="result-container" data-bind="visible: !$root.isRetrievingResults()" style="margin-top: 0">
        <thead>
          <tr data-bind="visible: $root.results().length > 0, foreach: $root.collection.template.fieldsSelected">        
            <th data-bind="with: $root.collection.getTemplateField($data)" style="white-space: nowrap">
              <a href="javascript: void(0)" data-bind="visible: $index() > 0, click: function(){ $root.collection.translateSelectedField($index(), 'left'); }"><i class="fa fa-chevron-left"></i></a>
              <a href="javascript: void(0)" title="${ _('Sort') }">
                <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
                <i class="fa" data-bind="visible: sort.direction() != null, css: { 'fa-chevron-down': sort.direction() == 'desc', 'fa-chevron-up': sort.direction() == 'asc' }"></i>
              </a>
              <a href="javascript: void(0)" data-bind="visible: $index() < $root.collection.template.fields().length - 1, click: function(){ $root.collection.translateSelectedField($index(), 'right'); }"><i class="fa fa-chevron-right"></i></a>
            </th>
          </tr>
          <tr data-bind="visible: $root.collection.template.fieldsSelected().length == 0">
            <th>${ ('Document') }</th>
          </tr>
        </thead>
        <tbody data-bind="foreach: { data: $root.results, as: 'documents' }">            
          <tr class="result-row" data-bind="foreach: row, click: $root.getDocument">
            <td data-bind="html: $data"></td>
          </tr>
        </tbody>
      </table>
    
      <div class="widget-spinner" data-bind="visible: $root.isRetrievingResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
      </div>	  
    </div>
  <!-- /ko -->
</script>

<script type="text/html" id="html-resultset-widget">
  <!-- ko ifnot: $root.collection.template.isGridLayout() -->
    <div data-bind="visible: $root.isEditing" style="margin-bottom: 20px">
      <ul class="nav nav-pills">
        <li class="active">
          <a href="javascript: void(0)" class="widget-main-pill">${_('Editor')}</a>
        </li>
        <li><a href="javascript: void(0)" class="widget-settings-pill">${_('HTML')}</a></li>
        <li><a href="javascript: void(0)" class="widget-settings-pill">${_('CSS & Js')}</a></li>
      </ul>
    </div>

    <!-- ko if: $root.isEditing() -->
      <textarea data-bind="value: $root.collection.template.template, codemirror: { 'lineNumbers': true, 'htmlMode': true, 'mode': 'text/html' }"></textarea>
      <br/>
      <textarea data-bind="value: $root.collection.template.extracode, codemirror: { 'lineNumbers': true, 'htmlMode': true, 'mode': 'text/html' }"></textarea>
      <br/>      
    <!-- /ko -->

    <div style="overflow-x: auto">
      <div data-bind="visible: $root.results().length == 0">
        ${ _('Your search did not match any documents.') }
      </div>
    
      <!-- ko if: $root.response().response -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->
    
      <div id="result-container" data-bind="foreach: $root.results">
        <div class="result-row" data-bind="html: $('<span>').html($('<span>').html($data).text()).text()"></div>
      </div>    
    
      <div class="widget-spinner" data-bind="visible: $root.isRetrievingResults()">
        <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
        <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
      </div>
    </div>
  <!-- /ko -->
</script>

<script type="text/html" id="resultset-pagination">
  <a href="javascript: void(0)" title="${ _('Previous') }">
    <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-left" data-bind="
        visible: $data.response.start >= $root.collection.template.rows(),
        click: function() { $root.query.paginate('prev') }">
    </i>
  </a>  

  <span data-bind="text: $data.response.start"></span>
  ${ _('of') }
  <span data-bind="text: $data.response.numFound"></span>
  
  <span data-bind="visible: $root.isEditing()">
    ${ _('by') }
    <input type="text" data-bind="value: $root.collection.template.rows, valueUpdate:'afterkeydown'"></input>
  </span>
  
  ${ _(' results') }  
  ## (<span data-bind="text: $data.responseHeader.QTime"></span> ${ _('ms') })
  
  <a href="javascript: void(0)" title="${ _('Next') }">
    <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-right" data-bind="
        visible: ($root.collection.template.rows() + $data.response.start) < $data.response.numFound,
        click: function() { $root.query.paginate('next') }">
    </i>
  </a>  
  
  <span class="pull-right" data-bind="visible: $data.response.numFound > 0 && $data.response.numFound <= 1000">
    <a class="btn" href="javascript:void(0)" id="download-csv"><i class="hfo hfo-file-csv"></i></a>
    <a class="btn" href="javascript:void(0)" id="download-xls"><i class="hfo hfo-file-xls"></i></a>
  </span>
</script>

<script type="text/html" id="histogram-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->text

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

    <a href="javascript:void(0)" data-bind="click: $root.collection.timeLineZoom"><i class="fa fa-search-minus"></i></a>
    <span>
      ${ _('Group By') }
      <select data-bind="options: $root.query.multiqs, optionsValue: 'id',optionsText: 'label', value: $root.query.selectedMultiq">
      </select>      
    </span>

    <div data-bind="timelineChart: {datum: {counts: counts, extraSeries: extraSeries, widget_id: $parent.id(), label: label}, stacked: $root.collection.getFacetById($parent.id()).properties.stacked(), field: field, label: label, transformer: timelineChartDataTransformer,
      onSelectRange: function(from, to){ viewModel.collection.selectTimelineFacet({from: from, to: to, cat: field, widget_id: $parent.id()}) },
      onStateChange: function(state){ $root.collection.getFacetById($parent.id()).properties.stacked(state.stacked); },
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) }}" />
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="bar-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

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

    <div data-bind="barChart: {datum: {counts: counts, widget_id: $parent.id(), label: label}, stacked: false, field: field, label: label,
      transformer: barChartDataTransformer,
      onStateChange: function(state){ console.log(state); },
      onClick: function(d){ viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) }, 
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) } }"
    />
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="line-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

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

    <div data-bind="lineChart: {datum: {counts: counts, widget_id: $parent.id(), label: label}, field: field, label: label,
      transformer: lineChartDataTransformer,
      onClick: function(d){ viewModel.query.selectRangeFacet({count: d.obj.value, widget_id: d.obj.widget_id, from: d.obj.from, to: d.obj.to, cat: d.obj.field}) },
      onComplete: function(){ viewModel.getWidgetById(id).isLoading(false) } }"
    />
  </div>
  <!-- /ko -->
</script>


<script type="text/html" id="pie-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

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
        onClick: function(d){ viewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) }, 
        onComplete: function(){ viewModel.getWidgetById($parent.id).isLoading(false)} }" />
      <!-- /ko -->
      <!-- ko if: type() != 'range' -->
      <div data-bind="pieChart: {data: {counts: $parent.counts, widget_id: $parent.id}, field: field, fqs: $root.query.fqs,
        transformer: pieChartDataTransformer,
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

<script type="text/html" id="area-widget">
  This is the area widget
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>

<script type="text/html" id="filter-widget">
  <div data-bind="visible: $root.query.fqs().length == 0">${_('There are no filters applied.')}</div>
  <div data-bind="foreach: { data: $root.query.fqs, afterRender: function(){ isLoading(false); } }">
    <!-- ko if: $data.type() == 'field' -->
    <span class="badge badge-left"><i class="fa fa-filter"></i> <span data-bind="text: $data.field"></span>: <span style="font-weight: normal" data-bind="text: $data.filter"></span></span><span class="badge badge-info badge-right trash-filter" data-bind="click: function(){ viewModel.query.removeFilter($data); viewModel.search() }"><i class="fa fa-times-circle"></i></span>
    <!-- /ko -->
    <!-- ko if: $data.type() == 'range' -->
    <span class="badge badge-left"><i class="fa fa-filter"></i> <span data-bind="text: $data.field"></span>:
      <span data-bind="foreach: $data.properties" style="font-weight: normal">
        <span style="font-style: italic">${_('from')}</span> <span data-bind="text: $data.from"></span> <span style="font-style: italic">${_('to')}</span> <span data-bind="text: $data.from"></span>
      </span>
    </span><span class="badge badge-info badge-right trash-filter" data-bind="click: function(){ viewModel.query.removeFilter($data); viewModel.search() }"><i class="fa fa-times-circle"></i></span>
    <!-- /ko -->
  </div>
  <div class="widget-spinner" data-bind="visible: isLoading() &&  $root.query.fqs().length > 0">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>

<script type="text/html" id="map-widget">
  <!-- ko ifnot: $root.getFacetFromQuery(id()) -->
    <a data-bind="click: showAddFacetDemiModal" class="btn" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
  <!-- /ko -->

  <!-- ko if: $root.getFacetFromQuery(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromQuery(id())">
    <div data-bind="visible: $root.isEditing, with: $root.collection.getFacetById($parent.id())" style="margin-bottom: 20px">
      ${ _('Label') }: <input type="text" data-bind="value: label" />
    </div>
    <div data-bind="with: $root.collection.getFacetById($parent.id())">
      <div data-bind="mapChart: {data: {counts: $parent.counts, widget_id: $parent.id}, field: field, fqs: $root.query.fqs,
        transformer: mapChartDataTransformer,
        onClick: function(d){ viewModel.query.selectRangeFacet({count: d.data.obj.value, widget_id: d.data.obj.widget_id, from: d.data.obj.from, to: d.data.obj.to, cat: d.data.obj.field}) },
        onComplete: function(){ viewModel.getWidgetById($parent.id).isLoading(false)} }" />
    </div>
  </div>
  <!-- /ko -->
  <div class="widget-spinner" data-bind="visible: isLoading()">
    <!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
    <!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
  </div>
</script>

<div id="addFacetDemiModal" class="demi-modal hide" data-backdrop="false">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Choose field')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <input id="addFacetInput" type="text" data-bind="value: $root.collection.template.fieldsModalFilter, valueUpdate:'afterkeydown'"
       placeholder="${_('Filter fields')}" class="input-xlarge" />
      <ul data-bind="foreach: $root.collection.template.filteredFieldsAttributes().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 })"
          class="unstyled inline fields-chooser">
        <li data-bind="click: addFacetDemiModalFieldClick">
          <span class="badge badge-info" style="font-size:20px"><span data-bind="text: name(), attr: {'title': type()}"></span>
          </span>
        </li>
      </ul>
      <div class="alert alert-info" data-bind="visible: $root.collection.template.filteredFieldsAttributes().length == 0">
        ${_('There are no fields matching your search term.')}
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <div>
      <input type="button" class="btn disabled" data-dismiss="modal" value="${_('Pick!')}" />
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
    </div>
  </div>  
</div>

<div id="showDocModal" class="modal hide">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Result inspector')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <table>
        <tbody data-bind="foreach: {data: Object.keys($root.collection.selectedDocument()), as: '_key'}">
          <tr>
            <th style="text-align: left" data-bind="text: _key"></th>
            <td data-bind="html: $root.collection.selectedDocument()[_key]"></td>
          </tr>
        </tbody>
      </table>
    </p>
  </div>
  <div class="modal-footer">
    <div>
      <input type="button" class="btn" data-dismiss="modal" value="${_('Close')}" />
    </div>
  </div>
</div>


## Extra code for style and custom JS
<span data-bind="html: $root.collection.template.extracode"></span>

<link rel="stylesheet" href="/search/static/css/search.css">
<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/leaflet.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/search/static/css/freshereditor.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">

<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/knockout.x-editable.js"></script>
<script src="/search/static/js/shortcut.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/freshereditor.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/codemirror-xml.js"></script>
<script src="/static/ext/js/mustache.js"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.categories.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>

<script src="/search/static/js/search.ko.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/js/hue.geo.js"></script>
<script src="/static/js/hue.colors.js"></script>

<script src="/static/ext/js/d3.v3.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/nv.d3.min.js" type="text/javascript" charset="utf-8"></script>
<link href="/static/ext/css/nv.d3.min.css" rel="stylesheet">
<script src="/static/ext/js/topojson.v1.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/datamaps.all.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/search/static/js/nv.d3.legend.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.multiBarWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.lineWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingDiscreteBar.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingDiscreteBarChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingMultiBar.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingMultiBarChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingPie.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/nv.d3.growingPieChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/charts.ko.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/js/less-1.7.0.min.js" type="text/javascript" charset="utf-8"></script>

<style type="text/css">
  .dashboard .container-fluid {
    padding: 6px;
  }

  .row-container {
    width: 100%;
    min-height: 70px;
  }

  .row-container.is-editing {
    border: 1px solid #e5e5e5;
  }

  .ui-sortable {
    background-color: #F3F3F3;
    min-height: 100px;
  }

  .ui-sortable h2 {
    padding-left: 10px!important;
  }

  .ui-sortable h2 ul {
    float: left;
    margin-right: 10px;
    font-size: 14px;
  }

  .ui-sortable-disabled {
    background-color: #FFF;
  }

  .card-column {
    border: none;
    min-height: 400px!important;
  }

  .card-widget {
    padding-top: 0;
    border: 0;
  }

  .card-widget .card-heading {
    font-size: 12px!important;
    font-weight: bold!important;
    line-height: 24px!important;
  }

  .card-widget .card-body {
    margin-top: 0;
  }

  .card-toolbar {
    margin: 0;
    padding: 4px;
    padding-top: 0;
    top: 70px;
    position: fixed;
    width: 100%;
    z-index: 1000;
  }

  .row-header {
    background-color: #F6F6F6;
    display: inline;
    padding: 3px;
    border: 1px solid #e5e5e5;
    border-bottom: none;
  }

  .row-highlight {
    background-color: #DDD;
    min-height: 100px;
  }

  #emptyDashboard {
    position: absolute;
    right: 164px;
    top: 80px;
    color: #666;
    font-size: 20px;
  }

  .emptyRow {
    margin-top: 10px;
    margin-left: 140px;
    color: #666;
    font-size: 18px;
  }

  .preview-row {
    background-color: #DDD;
    min-height: 400px!important;
    margin-top: 30px;
  }

  .toolbar-label {
    float: left;
    font-weight: bold;
    color: #999;
    padding-left: 8px;
    padding-top: 24px;
  }

  .draggable-widget {
    width: 60px;
    text-align: center;
    float: left;
    border: 1px solid #CCC;
    margin-top: 10px;
    margin-left: 10px;
    cursor: move;
  }

  .draggable-widget.disabled {
    cursor: default;
  }

  .draggable-widget a {
    font-size: 28px;
    line-height: 46px;
  }

  .draggable-widget.disabled a {
    cursor: default;
    color: #CCC;
  }

  .layout-container {
    width: 100px;
    float: left;
    margin-top: 10px;
    margin-left: 10px;
  }

  .layout-box {
    float: left;
    height: 48px;
    background-color: #DDD;
    text-align: center;
  }

  .layout-box i {
    color: #333;
    font-size: 28px;
    line-height: 48px;
  }

  .layout-container:hover .layout-box {
    background-color: #CCC;
  }

  .with-top-margin {
    margin-top: 60px;
  }

  .ui-sortable .card-heading {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }

  .search-bar {
    padding-top: 6px;
    padding-bottom: 6px;
  }

  .widget-settings-section {
    display: none;
  }

  em {
    font-weight: bold;
    background-color: yellow;
  }

  .nvd3 .nv-brush .extent {
    fill-opacity: .225!important;
  }

  .nvd3 .nv-legend .disabled rect {
    fill-opacity: 0;
  }


  .fields-chooser li {
    cursor: pointer;
    margin-bottom: 10px;
  }

  .fields-chooser li .badge {
    font-weight: normal;
    font-size: 12px;
  }

  .widget-spinner {
    padding: 10px;
    font-size: 80px;
    color: #CCC;
    text-align: center;
  }

  .card {
    margin: 0;
  }

  .badge-left {
    border-radius: 9px 0px 0px 9px;
    padding-right: 5px;
  }

  .badge-right {
    border-radius: 0px 9px 9px 0px;
    padding-left: 5px;
  }

  .trash-filter {
    cursor: pointer;
  }

  .move-widget {
    cursor: move;
  }

  .result-row {
    cursor: pointer;
  }

  body.modal-open {
      overflow: auto!important;
  }

  .editable-click {
    cursor: pointer;
  }


</style>

<script type="text/javascript" charset="utf-8">
var viewModel;

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
    if (typeof item.from != "undefined"){
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
    if (typeof item.from != "undefined"){
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
    item.widget_id = data.widget_id;
    _data.push({
      label: item.value,
      value: item.count,
      obj: item
    });
  });
  return _data;
}


$(document).ready(function () {

  $(document).on("showDoc", function(e, doc){
    viewModel.collection.selectedDocument(doc);
    $("#showDocModal").modal();
  });

  $(document).on("click", ".widget-settings-pill", function(){
    $(this).parents(".card-body").find(".widget-main-section").hide();
    $(this).parents(".card-body").find(".widget-settings-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

  $(document).on("click", ".widget-main-pill", function(){
    $(this).parents(".card-body").find(".widget-settings-section").hide();
    $(this).parents(".card-body").find(".widget-main-section").show();
    $(this).parent().siblings().removeClass("active");
    $(this).parent().addClass("active");
  });

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


  ko.extenders.numeric = function (target, precision) {
    var result = ko.computed({
      read: target,
      write: function (newValue) {
        var current = target(),
          roundingMultiplier = Math.pow(10, precision),
          newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue),
          valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

        if (valueToWrite !== current) {
          target(valueToWrite);
        } else {
          if (newValue !== current) {
            target.notifySubscribers(valueToWrite);
          }
        }
      }
    }).extend({ notify: 'always' });
    result(target());
    return result;
  };


  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend(valueAccessor(), {});
      var editor = CodeMirror.fromTextArea(element, options);
      element.editor = editor;
      editor.setValue(allBindingsAccessor().value());
      editor.refresh();
      var wrapperElement = $(editor.getWrapperElement());

      var sourceDelay = -1;
      editor.on("change", function (cm) {
        clearTimeout(sourceDelay);
        var _cm = cm;
        sourceDelay = setTimeout(function () {
          var _enc = $("<span>").html(_cm.getValue());
          if (_enc.find("style").length > 0){
            var parser = new less.Parser();
            $(_enc.find("style")).each(function(cnt, item){
              var _less = "#result-container {" + $(item).text() + "}";
              parser.parse(_less, function (err, tree) {
                $(item).text(tree.toCSS());
              });
            });
            allBindingsAccessor().value(_enc.html());
          }
          else {
            allBindingsAccessor().value(_cm.getValue());
          }
        }, 500);
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        wrapperElement.remove();
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var editor = element.editor;
      editor.refresh();
    }
  };


  viewModel = new SearchViewModel(${ collection.get_c(user) | n,unicode }, ${ query | n,unicode }, ${ initial | n,unicode });
  ko.applyBindings(viewModel);

  viewModel.init();
});

  function toggleGridFieldsSelection() {
    if (viewModel.collection.template.fields().length > 0) {
      viewModel.collection.template.fieldsSelected([])
    }
    else {
      var _fields = [];
      $.each(viewModel.collection.fields(), function (index, field) {
        _fields.push(field.name());
      });
      viewModel.collection.template.fieldsSelected(_fields);
    }
  }

  var selectedWidget = null;
  function showAddFacetDemiModal(widget) {
    if (["resultset-widget", "html-resultset-widget", "filter-widget"].indexOf(widget.widgetType()) == -1) {      
      viewModel.collection.template.fieldsModalFilter();
      viewModel.collection.template.fieldsModalType(widget.widgetType());
      viewModel.collection.template.fieldsModalFilter("");
      $('#addFacetInput').typeahead({
          'source': viewModel.collection.template.availableWidgetFieldsNames(), 
          'updater': function(item) {
              addFacetDemiModalFieldClick({'name': function(){return item}});
              return item;
           }
      });
      selectedWidget = widget;
      $("#addFacetDemiModal").modal("show");
      $("#addFacetDemiModal").on("shown", function(){
        window.setTimeout(function(){
          $(window).scrollTop($("#wdg_" + selectedWidget.id()).position().top);
        }, 500);
      });
      $("#addFacetDemiModal input[type='text']").focus();
    }
  }


  function addFacetDemiModalFieldClick(field) {
    var _existingFacet = viewModel.collection.getFacetById(selectedWidget.id());
    if (selectedWidget != null) {
      selectedWidget.isLoading(true);
      viewModel.collection.addFacet({'name': field.name(), 'widget_id': selectedWidget.id(), 'widgetType': selectedWidget.widgetType()});
      if (_existingFacet != null) {
        _existingFacet.label(field.name());
        _existingFacet.field(field.name());
      }      
      viewModel.search();
    }
  }
</script>

${ commonfooter(messages) | n,unicode }
