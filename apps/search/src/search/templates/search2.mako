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

${ commonheader(_('Search'), "search", user, "90px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/search.css">
<link href="/static/ext/css/hue-filetypes.css" rel="stylesheet">
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>

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

  #emptyDashboard {
    position: absolute;
    right: 14px;
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

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 6px; margin-right: 40px">
      <button type="button" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>    
      <a class="change-settings" href="#"><i class="fa fa-save"></i> ${ _('Save') }</a> &nbsp;&nbsp;
      <a href="${ url('search:admin_collections') }"><i class="fa fa-sitemap"></i> ${ _('Collection manager') }</a>
    </div>
  % endif
  
  <form class="form-search" style="margin: 0" data-bind="submit: search">
    <strong>${_("Search")}</strong>
    <div class="input-append">
      <div class="selectMask">
        <span class="current-collection"></span>
        <ul class="unstyled">
          <li><a class="dropdown-collection" href="#" data-value="${ hue_collection.id }" data-settings-url="${ hue_collection.get_absolute_url() }">${ hue_collection.label }</a></li>
        </ul>
      </div>

      <input data-bind="value: query.q" name="query" maxlength="256" type="text" class="search-query input-xxlarge" id="id_query" style="cursor: auto;">
      
      <button type="submit" id="search-btn" class="btn btn-inverse"><i class="fa fa-search"></i></button>
      <span style="padding-left:15px">
        <button type="button" id="download-btn" class="btn btn-inverse dropdown-toggle" data-toggle="dropdown"><i class="fa fa-download"></i></button>
      </span>
    </div>
  </form>
</div>

<div class="card card-toolbar" data-bind="slideVisible: isEditing">
  <div style="float: left">
    <div style="font-weight: bold; color: #999; padding-left: 8px">${_('LAYOUT')}</div>
    <a href="javascript: oneThirdLeftLayout()" onmouseover="viewModel.previewColumns('oneThirdLeft')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_onethirdleft.png" /></a>
    <a href="javascript: oneThirdRightLayout()" onmouseover="viewModel.previewColumns('oneThirdRight')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_onethirdright.png" /></a>
    <a href="javascript: fullLayout()" onmouseover="viewModel.previewColumns('full')" onmouseout="viewModel.previewColumns('')"><img src="/search/static/art/layout_full.png" /></a>
  </div>

  <div style="float: left; margin-left: 20px" data-bind="visible: columns().length > 0">
    <div style="font-weight: bold; color: #999; padding-left: 8px">${_('WIDGETS')}</div>
    <div class="draggable-widget" data-bind="draggable: draggableResultset" title="${_('Results')}" rel="tooltip" data-placement="top"><a href="#"><i class="fa fa-table"></i></a></div>    
    <div class="draggable-widget" data-bind="draggable: draggableFacet" title="${_('Text Facet')}" rel="tooltip" data-placement="top"><a href="#"><i class="fa fa-sort-amount-desc"></i></a></div>    
    <div class="draggable-widget" data-bind="draggable: draggableBar" title="${_('Timeline')}" rel="tooltip" data-placement="top"><a href="#"><i class="hcha hcha-bar-chart"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggableArea" title="${_('Area Chart')}" rel="tooltip" data-placement="top"><a href="#"><i class="hcha hcha-area-chart"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggablePie" title="${_('Pie Chart')}" rel="tooltip" data-placement="top"><a href="#"><i class="hcha hcha-pie-chart"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggableLine" title="${_('Line Chart')}" rel="tooltip" data-placement="top"><a href="#"><i class="hcha hcha-line-chart"></i></a></div>
    <div class="draggable-widget" data-bind="draggable: draggableMap" title="${_('Map')}" rel="tooltip" data-placement="top"><a href="#"><i class="hcha hcha-map-chart"></i></a></div>
  </div>
  <div class="clearfix"></div>
</div>

<div id="emptyDashboard" data-bind="visible: !isEditing() && columns().length == 0">
  <div style="float:left; padding-top: 90px; margin-right: 20px; text-align: center; width: 260px">${_('Click on the pencil to get started with your dashboard!')}</div>
  <img src="/search/static/art/hint_arrow.png" />
</div>

<div data-bind="visible: isEditing() && previewColumns() != '' && columns().length == 0">
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
  </div>
</div>

<div data-bind="css: {'dashboard': true, 'unselectable': isEditing()}">
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
  <div class="emptyRow" data-bind="visible: widgets().length == 0 && $index()==0 && $root.isEditing() && $parent.size() > 4">
    <img src="/search/static/art/hint_arrow_flipped.png" style="float:left; margin-right: 10px"/>
    <div style="float:left; text-align: center; width: 260px">${_('Drag any of the widgets inside your empty row')}</div>
    <div class="clearfix"></div>
  </div>
  <div class="container-fluid">
    <div class="row-header" data-bind="visible: $root.isEditing">
      <span class="muted"><i class="fa fa-minus"></i> ${_('Row')}</span>
      <div style="display: inline; margin-left: 60px">
        <a href="javascript:void(0)" data-bind="visible:$index()<$parent.rows().length-1, click: function(){moveDown($parent, this)}"><i class="fa fa-chevron-down"></i></a>
        <a href="javascript:void(0)" data-bind="visible:$index()>0, click: function(){moveUp($parent, this)}"><i class="fa fa-chevron-up"></i></a>
        <a href="javascript:void(0)" data-bind="visible:$parent.rows().length > 1, click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a>
      </div>
    </div>
    <div class="row-fluid row-container" data-bind="sortable: { template: 'widget-template', data: widgets, isEnabled: $root.isEditing}">
    </div>
  </div>
</script>

<script type="text/html" id="widget-template">
  <div data-bind="css: klass">
    <h2 class="card-heading simple">
      <ul class="inline" data-bind="visible: $root.isEditing">
        <li><a href="javascript:void(0)" data-bind="click: function(){remove($parent, this)}"><i class="fa fa-times"></i></a></li>
        <li><a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a></li>
        <li><a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a></li>
      </ul>
      <span data-bind="text: name"></span>
    </h2>
    <div class="card-body">
      <p>
        <div data-bind="template: { name: function() { return widgetType(); }, data: properties }"></div>
      </p>
      <div data-bind="visible: $root.isEditing()">
        This is visible just when we edit.<br/>
        Common properties:
        <ul>
          <li> Name: <input type="text" data-bind="value: name" /></li>
          <li> Size: <input type="text" data-bind="value: size" /></li>
          <li> Offset: <input type="text" data-bind="value: offset" /></li>
        </ul>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="empty-widget">
  This is an empty widget.
</script>

<script type="text/html" id="facet-widget">
      <span class="pull-right">
        <a id="showAddFacetModal" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
      </span>

      ## Need to pick the facet ID from norm_facets instead of looping on all
      <div class="row" data-bind="foreach: $root.norm_facets">
        <span class="pull-right">
          <a href="javascript:void(0)" data-bind="click: editFacet"><i class="fa fa-pencil"></i></a>
          <a href="javascript:void(0)" data-bind="click: $root.removeFacet"><i class="fa fa-times"></i></a>
        </span>
        <div data-bind="text: label"></div>
        <div data-bind="foreach: counts">
          <div>
            <a href="script:void(0)">
            <!-- ko if: selected -->
              <span data-bind="text: value, click: $root.query.unselectFacet"></span>
              <i data-bind="click: $root.query.unselectFacet" class="fa fa-times"></i>            
            <!-- /ko -->
            <!-- ko if: !selected -->           
              <span data-bind="text: value, click: $root.query.selectFacet"></span> (<span data-bind="text: count, click: $root.query.selectFacet"></span>)            
            <!-- /ko -->
            </a>
          </div>
        </div>
      </div>    

</script>

<script type="text/html" id="resultset-widget">
      <div class="row">
        <span class="pull-right">
          <a data-bind="click: editTemplate" href="javascript:void(0)"><i class="fa fa-pencil"></i></a>
        </span>
      </div>
  
      <!-- ko if: $root.collection.template.isGridLayout() -->
      <table id="result-container">        
        <thead>
          <tr data-bind="foreach: $root.collection.template.fields">
            <th data-bind="text: $data"></th>
          </tr>
        </thead>
        <tbody data-bind="foreach: $root.results">
          <tr class="result-row" data-bind="foreach: $data">
            <td data-bind="html: $data"></td>
          </tr>
        </tbody>
      </table>
      <!-- /ko -->
      <!-- ko if: ! $root.collection.template.isGridLayout() -->
      <div id="result-container" data-bind="foreach: $root.results">
        <div class="result-row" data-bind="html: $data"></div>
      </div>
      <!-- /ko -->  
</script>

<script type="text/html" id="timeline-widget">
  This is the timeline widget
</script>

<script type="text/html" id="bar-widget">
  This is the bar widget
</script>

<script type="text/html" id="pie-widget">
  This is the pie widget
</script>

<script type="text/html" id="area-widget">
  This is the area widget
</script>

<script type="text/html" id="line-widget">
  This is the line widget
</script>

<script type="text/html" id="map-widget">
  This is the map widget
</script>


<style type="text/css">
  em {
    font-weight: bold; 
    background-color: yellow;
  }
</style>

<div id="addFacetModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Add facet')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="facetName" type="text">
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Back')}</a>
    <a id="submitAddFacetModal" class="btn btn-primary disable-feedback">${_('Ok')}</a>
  </div>
</div>


<div id="editFacetModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Edit Facet')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">        
        <!-- ko if: selectedFacet() -->
        <p>
          ${ _('Label') }: <input type="text" data-bind="value: selectedFacet().label" />
        </p>
        <!-- /ko -->
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn" data-bind="click: search">${_('Ok')}</a>
  </div>
</div>


<div id="editTemplateModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Edit Template')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">        
        <p>
          ${ _('Grid result') }: <input type="checkbox" data-bind="checked: collection.template.isGridLayout" />
        </p>
        
        <!-- ko if: $root.collection.template.isGridLayout() -->
        <p>
          ${ _('Fields') }
          <select data-bind="options: collection.fields, selectedOptions: collection.template.fields" size="5" multiple="true"></select>
        </p>  
        <!-- /ko -->
        
        <!-- ko if: ! $root.collection.template.isGridLayout() -->
        <textarea data-bind="value: collection.template.template, valueUpdate:'afterkeydown'"></textarea>
        <!-- /ko -->
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Ok')}</a>
  </div>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/mustache.js"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-draggable-droppable-sortable-1.8.23.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">
<link href="/static/ext/css/hue-charts.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.categories.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>

<script src="/search/static/js/search.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
var viewModel;

$(document).ready(function () {

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


  viewModel = new SearchViewModel(${ hue_collection.get_c(user) | n,unicode }, ${ hue_query | n,unicode });
  ko.applyBindings(viewModel);
  
  
  fullLayout();
  viewModel.isEditing(true);
  viewModel.columns()[0].rows()[0].addWidget(viewModel.draggableResultset());  
  viewModel.search();
  
  
  $("#showAddFacetModal").click(function() {
    $("#addFacetModal").modal("show");
  });

  $("#submitAddFacetModal").click(function() {
    viewModel.collection.addFacet({'name': $("#facetName").val()});
    $('#addFacetModal').modal("hide");
    viewModel.search();
  });
});

  function editTemplate(facet) {
    $("#editTemplateModal").modal("show");
  };

  function editFacet(facet) {
    viewModel.selectSingleFacet(facet);
    $("#editFacetModal").modal("show");
  };
</script>

${ commonfooter(messages) | n,unicode }
