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

<script type="text/javascript">
  if (window.location.hash != ""){
    location.href = "/search/?" + window.location.hash.substr(1);
  }
</script>

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="padding-right:50px">
      <button type="button" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: save, css: {'btn': true}"><i class="fa fa-save"></i></button>
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}"><i class="fa fa-cog"></i></button>
      ## for enable, live search, max number of downloads, change solr
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
        <span
            data-bind="editable: collection.label, editableOptions: {enabled: $root.isEditing(), placement: 'right'}">
        </span>
        ##<i class="fa fa-edit" data-bind="visible: $root.isEditing() && ! $root.changeCollection(), click: function(){$root.changeCollection(true);}"></i>
        <!-- ko if: $root.isEditing() && $root.changeCollection() -->
        <select data-bind="options: $root.initial.collections, value: $root.collection.name">
        </select>        
        <!-- /ko -->
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
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast'); $root.collection.template.isGridLayout(true); }}}"
         title="${_('Grid Results')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }">
                       <i class="fa fa-table"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableResultset() },
                    draggable: {data: draggableHtmlResultset(), 
                    isEnabled: availableDraggableResultset, 
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)}); $root.collection.template.isGridLayout(false); }}}"
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
    <!-- <div class="draggable-widget" data-bind="draggable: {data: draggableHit(), options: {'start': function(event, ui){$('.card-body').slideUp('fast');}, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}" title="${_('Hit Count')}" rel="tooltip" data-placement="top"><a data-bind="attr: {href: $root.availableDraggableResultset()}, css: {'btn-inverse': ! $root.availableDraggableResultset() }, style: { cursor: $root.availableDraggableResultset() ? 'move' : 'default' }"><i class="fa fa-tachometer"></i></a></div> -->
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableBar(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Bar Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-bar-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableChart() },
                    draggable: {data: draggableLine(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Line')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
                       <i class="hcha hcha-line-chart"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true, 'disabled': !availableDraggableHistogram() },
                    draggable: {data: draggableHistogram(), isEnabled: availableDraggableHistogram, 
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Histogram')}" rel="tooltip" data-placement="top">
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
                    draggable: {data: draggableMap(), isEnabled: availableDraggableChart, 
                    options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                              'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}}"
         title="${_('Map')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: $root.availableDraggableChart() ? 'move' : 'default' }">
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
    <div class="container-fluid" data-bind="visible: $root.isEditing">
      <div data-bind="css: {'add-row': true, 'is-editing': $root.isEditing}, sortable: { data: drops, isEnabled: $root.isEditing, options: {'placeholder': 'row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}, dragged: function(widget){var _r = $data.addEmptyRow(); _r.addWidget(widget);$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});showAddFacetDemiModal(widget);viewModel.search()}}"></div>
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
        <a href="javascript:void(0)" data-bind="visible: $index()<$parent.rows().length-1, click: function(){moveDown($parent, this)}"><i class="fa fa-chevron-down"></i></a>
        <a href="javascript:void(0)" data-bind="visible: $index()>0, click: function(){moveUp($parent, this)}"><i class="fa fa-chevron-up"></i></a>
        <a href="javascript:void(0)" data-bind="visible: $parent.rows().length > 1, click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </div>
    <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing}, sortable: { template: 'widget-template', data: widgets, isEnabled: $root.isEditing, options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true, 'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}, 'helper': function(event){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}}, dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});showAddFacetDemiModal(widget);viewModel.search()}}">
    </div>
  </div>
</script>

<script type="text/html" id="widget-template">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass">
  <div data-bind="attr: {'id': 'wdg_'+ id(),}, css: klass">
    <h2 class="card-heading simple">
      <span data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
        <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
        <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
        &nbsp;
      </span>
      <span data-bind="with: $root.collection.getFacetById(id())">
        <span data-bind="editable: label, editableOptions: {enabled: $root.isEditing()}"></span>
      </span>
      <!-- ko ifnot: $root.collection.getFacetById(id()) -->
        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing()}"></span>
      <!-- /ko -->
      <div class="inline pull-right" data-bind="visible: $root.isEditing">
        <a href="javascript:void(0)" data-bind="click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </h2>
    <div class="card-body" style="padding: 5px;">    
      <div data-bind="template: { name: function() { return widgetType(); } }" class="widget-main-section"></div>
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
              <!-- ko if: $index() != $parent.properties.limit() -->
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
    <div style="float:left; margin-right: 10px" >
      <div data-bind="visible: ! $root.collection.template.showFieldList()" style="padding-top: 5px; display: inline-block">
        <a href="javascript: void(0)"  data-bind="click: function(){ $root.collection.template.showFieldList(true) }">
          <i class="fa fa-chevron-right"></i>
        </a>
      </div>
    </div>
    <div data-bind="visible: $root.collection.template.showFieldList()" style="float:left; margin-right: 10px; background-color: #F6F6F6; padding: 5px">
      <span data-bind="visible: $root.collection.template.showFieldList()">
        <div>
          <strong>${ _('Fields') }</strong>
          <a href="javascript: void(0)" class="pull-right" data-bind="click: function(){ $root.collection.template.showFieldList(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
        </div>
        <input type="text" data-bind="value: $root.collection.template.fieldsAttributesFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" style="width: 88%; margin-bottom: 3px" />
        <div class="fields-list" data-bind="foreach: $root.collection.template.filteredAttributeFields" style="max-height: 230px; overflow-y: auto">
          <input type="checkbox" data-bind="checkedValue: name, checked: $root.collection.template.fieldsSelected" /> 
          <span data-bind="text: '&nbsp;' + name()"></span>
          <br/>
        </div>
      </span>
    </div>

    <div style="overflow-x: auto">
      <div data-bind="visible: !$root.isRetrievingResults() && $root.results().length == 0">
        ${ _('Your search did not match any documents.') }
      </div>
    
      <!-- ko if: $root.response().response -->
        <div data-bind="template: {name: 'resultset-pagination', data: $root.response() }"></div>
      <!-- /ko -->
    
      <table id="result-container" data-bind="visible: !$root.isRetrievingResults()" style="margin-top: 0; width: 100%">
        <thead>
          <tr data-bind="visible: $root.results().length > 0">
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
              <a href="javascript: void(0)" title="${ _('Click to sort') }">
                <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
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
          </tr>
          <tr data-bind="visible: $root.collection.template.fieldsSelected().length == 0">
            <th style="width: 18px">&nbsp;</th>
            <th>${ ('Document') }</th>
          </tr>
        </thead>
        <tbody data-bind="foreach: { data: $root.results, as: 'documents' }" class="result-tbody">
          <tr class="result-row" data-bind="attr: {'id': 'doc_' + $data[$root.collection.idField()]}">
            <td><a href="javascript:void(0)" data-bind="click: toggleDocDetails"><i class="fa fa-caret-right"></i></a></td>
            <!-- ko foreach: row -->
            <td data-bind="html: $data"></td>
            <!-- /ko -->
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

            <h5 class="editor-title" style="margin-top: 30px">${_('Available Functions')}</h2>
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
            <h5 class="editor-title">${_('Available Fields')}</h2>
            <select data-bind="options: $root.collection.fields, optionsText: 'name', value: $root.collection.template.selectedSourceField" class="input-medium chosen-select"></select>
            <button title="${ _('Click on this button to add the field') }" class="btn plus-btn" data-bind="click: $root.collection.template.addFieldToSource">
              <i class="fa fa-plus"></i>
            </button>

            <h5 class="editor-title" style="margin-top: 30px">${_('Available Functions')}</h2>
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
         Sorting
      </div>
    <!-- /ko -->

    <div style="overflow-x: auto">
      <div data-bind="visible: $root.results().length == 0">
        ${ _('Your search did not match any documents.') }
      </div>
    
      <!-- ko if: $root.response().response -->
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

<script type="text/html" id="resultset-pagination">
  <a href="javascript: void(0)" title="${ _('Previous') }">
    <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-left" data-bind="
        visible: $data.response.start * 1.0 >= $root.collection.template.rows() * 1.0,
        click: function() { $root.query.paginate('prev') }">
    </i>
  </a>  

  <span data-bind="text: $data.response.start"></span>
  ${ _('of') }
  <span data-bind="text: $data.response.numFound"></span>
  
  <span data-bind="visible: $root.isEditing()">
    ${ _('by') }
    <input type="text" data-bind="spinedit: $root.collection.template.rows, valueUpdate:'afterkeydown'" />
  </span>
  
  ${ _(' results') }  
  ## (<span data-bind="text: $data.responseHeader.QTime"></span> ${ _('ms') })
  
  <a href="javascript: void(0)" title="${ _('Next') }">
    <span data-bind="text: name, click: $root.collection.toggleSortColumnGridLayout"></span>
    <i class="fa fa-arrow-right" data-bind="
        visible: ($root.collection.template.rows() * 1.0 + $data.response.start * 1.0) < $data.response.numFound,
        click: function() { $root.query.paginate('next') }">
    </i>
  </a>  
  
  <!-- ko if: $data.response.numFound > 0 && $data.response.numFound <= 1000 -->
  <span class="pull-right">
    <form method="POST" action="${ url('search:download') }">
      <input type="hidden" name="collection" data-bind="value: ko.mapping.toJSON($root.collection)"/>
      <input type="hidden" name="query" data-bind="value: ko.mapping.toJSON($root.query)"/>
      <button class="btn" type="submit" name="json" title="${ _('Download as JSON') }"><i class="hfo hfo-file-json"></i></button>
      <button class="btn" type="submit" name="csv" title="${ _('Download as CSV') }"><i class="hfo hfo-file-csv"></i></button>
      <button class="btn" type="submit" name="xls" title="${ _('Download as Excel') }"><i class="hfo hfo-file-xls"></i></button>
    </form>
  </span>
  <!-- /ko -->
</script>

<script type="text/html" id="histogram-widget">
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
      <div data-bind="mapChart: {data: {counts: $parent.counts, widget_id: $parent.id},
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
  <div class="modal-body">
    <div style="float: left; margin-right: 10px;text-align: center">
      <input id="addFacetInput" type="text" data-bind="value: $root.collection.template.fieldsModalFilter, valueUpdate:'afterkeydown'" placeholder="${_('Filter fields')}" class="input-small" style="float: left" /><br/>
    </div>
    <div>
      <ul data-bind="foreach: $root.collection.template.filteredModalFields().sort(function (l, r) { return l.name() > r.name() ? 1 : -1 }), visible: $root.collection.template.filteredModalFields().length > 0"
          class="unstyled inline fields-chooser" style="height: 70px; overflow-y: auto">
        <li data-bind="click: addFacetDemiModalFieldPreview">
          <span class="badge badge-info"><span data-bind="text: name(), attr: {'title': type()}"></span>
          </span>
        </li>
      </ul>
      <div class="alert alert-info inline" data-bind="visible: $root.collection.template.filteredModalFields().length == 0" style="margin-left: 124px;height: 42px;line-height: 42px">
        ${_('There are no fields matching your search term.')}
      </div>
      <div style="margin-left: 124px">
        <input type="button" class="btn btn-primary disabled" data-dismiss="modal" value="${_('Pick!')}" /> or
        <a href="javascript: void(0)" data-dismiss="modal" data-bind="click: addFacetDemiModalFieldCancel">${_('cancel')}</a>
      </div>
    </div>
  </div>
</div>

<div id="genericLoader" style="display: none">
<!--[if !IE]> --><i class="fa fa-spinner fa-spin"></i><!-- <![endif]-->
<!--[if IE]><img src="/static/art/spinner.gif" /><![endif]-->
</div>

<script id="document-details" type="x-tmpl-mustache">
<div class="document-details">
  <table>
    <tbody>
    {{#properties}}
      <tr>
        <th style="text-align: left; white-space: nobreak; vertical-align:top">{{key}}</th>
        <td width="100%">{{value}}</td>
      </tr>
      {{/properties}}
    </tbody>
  </table>
  </div>
</script>

## Extra code for style and custom JS
<span data-bind="html: $root.collection.template.extracode"></span>

<link rel="stylesheet" href="/search/static/css/search.css">
<link rel="stylesheet" href="/static/ext/css/hue-filetypes.css">
<link rel="stylesheet" href="/static/ext/css/leaflet.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/search/static/css/freshereditor.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">
<link rel="stylesheet" href="/static/ext/css/bootstrap-slider.min.css">
<link rel="stylesheet" href="/static/css/bootstrap-spinedit.css">
<link rel="stylesheet" href="/static/ext/css/nv.d3.min.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">

<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/bootstrap-slider.min.js"></script>
<script src="/static/js/bootstrap-spinedit.js"></script>
<script src="/static/js/ko.editable.js"></script>
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
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script src="/search/static/js/search.ko.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/js/hue.geo.js"></script>
<script src="/static/js/hue.colors.js"></script>

<script src="/static/ext/js/d3.v3.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/nv.d3.min.js" type="text/javascript" charset="utf-8"></script>
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

  body.modal-open {
      overflow: auto!important;
  }

  .editable-click {
    cursor: pointer;
  }

  .CodeMirror {
    border: 1px dotted #DDDDDD;
  }

  [contenteditable=true] {
    border: 1px dotted #DDDDDD;
    outline: 0;
    margin-top: 20px;
    margin-bottom: 20px;
    min-height: 150px;
  }

  [contenteditable=true] [class*="span"], .tmpl [class*="span"] {
    background-color: #eee;
    -webkit-border-radius: 3px;
    -moz-border-radius: 3px;
    border-radius: 3px;
    min-height: 40px;
    line-height: 40px;
    background-color: #F3F3F3;
    border: 2px dashed #DDD;
  }

  .tmpl {
    margin: 10px;
    height: 60px;
  }

  .tmpl [class*="span"] {
    color: #999;
    font-size: 12px;
    text-align: center;
    font-weight: bold;
  }

  .preview-row:nth-child(odd) {
    background-color: #f9f9f9;
  }

  .editor-title {
    font-weight: bold;
    color: #262626;
    border-bottom: 1px solid #338bb8;
  }

  .add-row {
    background-color: #F6F6F6;
    min-height: 40px;
    border: 2px dashed #CCC;
    text-align: center;
    padding: 4px;
  }

  .add-row:before {
    color:#EEE;
    display: inline-block;
    font-family: FontAwesome;
    font-style: normal;
    font-weight: normal;
    font-size: 48px;
    line-height: 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    content: "\f055";
  }

  .document-details {
    background-color: #F6F6F6;
    padding: 10px;
    border: 1px solid #e5e5e5;
  }

  .result-row:nth-child(even) {
    background-color: #F6F6F6;
  }

  .demi-modal {
    min-height: 80px;
  }

</style>

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

function toggleDocDetails(doc){
  var _docRow = $("#doc_" + doc[viewModel.collection.idField()]);
  if (_docRow.data("expanded") != null && _docRow.data("expanded")){
    $("#doc_" + doc[viewModel.collection.idField()] + "_details").parent().hide();
    _docRow.find(".fa-caret-down").removeClass("fa-caret-down").addClass("fa-caret-right");
    _docRow.data("expanded", false);
  }
  else {
    _docRow.data("expanded", true);
    var _detailsRow = $("#doc_" + doc[viewModel.collection.idField()] + "_details");
    if (_detailsRow.length > 0){
      _detailsRow.parent().show();
    }
    else {
      var _newRow = $("<tr>");
      var _newCell = $("<td>").attr("colspan", _docRow.find("td").length).attr("id", "doc_" + doc[viewModel.collection.idField()] + "_details").html($("#genericLoader").html());
      _newCell.appendTo(_newRow);
      _newRow.insertAfter(_docRow);
      viewModel.getDocument(doc);
    }
    _docRow.find(".fa-caret-right").removeClass("fa-caret-right").addClass("fa-caret-down");
  }
}

function resizeFieldsList() {
  $(".fields-list").css("max-height", Math.max($("#result-container").height(), 230));
}

$(document).ready(function () {

  var _resizeTimeout = -1;
  $(window).resize(function(){
    window.clearTimeout(_resizeTimeout);
    window.setTimeout(function(){
      resizeFieldsList();
    }, 200);
  });

  $(document).on("showDoc", function(e, doc){
    viewModel.collection.selectedDocument(doc);
    var _docDetailsRow = $("#doc_" + doc[viewModel.collection.idField()] + "_details");
    var _doc = {
      properties: []
    };
    for (var i=0; i< Object.keys(doc).length; i++){
      _doc.properties.push({
        key: Object.keys(doc)[i],
        value: doc[Object.keys(doc)[i]]
      });
    }
    var template = $("#document-details").html();
    Mustache.parse(template);
    var rendered = Mustache.render(template, _doc);
    _docDetailsRow.html(rendered);
  });

  $(document).on("click", ".widget-settings-pill", function(){
    $(this).parents(".card-body").find(".widget-section").hide();
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

  ko.bindingHandlers.freshereditor = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var _el = $(element);
      var options = $.extend(valueAccessor(), {});
      _el.html(options.data());
      _el.freshereditor({
        excludes: ['strikethrough', 'removeFormat', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
      });
      _el.freshereditor("edit", true);
      _el.on("mouseup", function () {
        storeSelection();
        updateValues();
      });

      var sourceDelay = -1;
      _el.on("keyup", function () {
        clearTimeout(sourceDelay);
        storeSelection();
        sourceDelay = setTimeout(function () {
          updateValues();
        }, 100);
      });

      $(".chosen-select").chosen({
        disable_search_threshold: 10,
        width: "75%"
      });

      $(document).on("addFieldToVisual", function(e, field){
        _el.focus();
        pasteHtmlAtCaret("{{" + field.name() + "}}");
      });

      $(document).on("addFunctionToVisual", function(e, fn){
        _el.focus();
        pasteHtmlAtCaret(fn);
      });

      function updateValues(){
        $("[data-template]")[0].editor.setValue(stripHtmlFromFunctions(_el.html()));
        valueAccessor().data(_el.html());
      }

      function storeSelection() {
        if (window.getSelection) {
          // IE9 and non-IE
          sel = window.getSelection();
          if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
            _el.data("range", range);
          }
        }
        else if (document.selection && document.selection.type != "Control") {
          // IE < 9
          _el.data("selection", document.selection);
        }
      }

    function pasteHtmlAtCaret(html) {
      var sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          if (_el.data("range")) {
            range = _el.data("range");
          }
          else {
            range = sel.getRangeAt(0);
          }
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // non-standard and not supported in all browsers (IE9, for one)
          var el = document.createElement("div");
          el.innerHTML = html;
          var frag = document.createDocumentFragment(), node, lastNode;
          while ((node = el.firstChild)) {
            lastNode = frag.appendChild(node);
          }
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        if (_el.data("selection")) {
          _el.data("selection").createRange().pasteHTML(html);
        }
        else {
          document.selection.createRange().pasteHTML(html);
        }
      }
    }
    }
  };

  ko.bindingHandlers.slider = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var _el = $(element);
      var _options = $.extend(valueAccessor(), {});
      _el.slider({
        min: _options.min ? _options.min : 1,
        max: _options.max ? _options.max : 10,
        step: _options.step ? _options.step : 1,
        handle: _options.handle ? _options.handle : 'circle',
        value: _options.data(),
        tooltip: 'always'
      });
      _el.on("slide", function (e) {
        _options.data(e.value);
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var _options = $.extend(valueAccessor(), {});
      $(element).slider("setValue", _options.data());
    }
  }

  ko.bindingHandlers.spinedit = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      $(element).spinedit({
        minimum: 0,
        maximum: 10000,
        step: 5,
        value: ko.unwrap(valueAccessor()),
        numberOfDecimals: 0
      });
      $(element).on("valueChanged", function (e) {
        valueAccessor()(e.value);
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      $(element).spinedit("setValue", ko.unwrap(valueAccessor()));
    }
  }

  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend(valueAccessor(), {});
      var editor = CodeMirror.fromTextArea(element, options);
      element.editor = editor;
      editor.setValue(options.data());
      editor.refresh();
      var wrapperElement = $(editor.getWrapperElement());

      $(document).on("refreshCodemirror", function(){
        editor.setSize("100%", 300);
        editor.refresh();
      });

      $(document).on("addFieldToSource", function(e, field){
        if ($(element).data("template")){
          editor.replaceSelection("{{" + field.name() + "}}");
        }
      });

      $(document).on("addFunctionToSource", function(e, fn){
        if ($(element).data("template")){
          editor.replaceSelection(fn);
        }
      });

      $(".chosen-select").chosen({
        disable_search_threshold: 10,
        width: "75%"
      });
      $('.chosen-select').trigger('chosen:updated');

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
              try {
                parser.parse(_less, function (err, tree) {
                  $(item).text(tree.toCSS());
                });
              }
              catch (e){}
            });
            valueAccessor().data(_enc.html());
          }
          else {
            valueAccessor().data(_cm.getValue());
          }
          if ($(".widget-html-pill").parent().hasClass("active")){
            $("[contenteditable=true]").html(stripHtmlFromFunctions(valueAccessor().data()));
          }
        }, 100);
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

  viewModel.init(function(data){
    $(".chosen-select").trigger("chosen:updated");
  });
  viewModel.isRetrievingResults.subscribe(function(value){
    if (!value){
      resizeFieldsList();
    }
  });
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
              addFacetDemiModalFieldPreview({'name': function(){return item}});
              $("#addFacetDemiModal").modal("hide");
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
      selectedWidget.isLoading(true);
      viewModel.collection.addFacet({'name': field.name(), 'widget_id': selectedWidget.id(), 'widgetType': selectedWidget.widgetType()});
      if (_existingFacet != null) {
        _existingFacet.label(field.name());
        _existingFacet.field(field.name());
      }      
    }
  }
  
  function addFacetDemiModalFieldCancel() {
    viewModel.removeWidget(selectedWidget);
  }

</script>

${ commonfooter(messages) | n,unicode }
