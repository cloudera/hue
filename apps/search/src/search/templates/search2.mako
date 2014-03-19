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

<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user, "90px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/search.css">
<link href="/static/ext/css/hue-filetypes.css" rel="stylesheet">
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/template.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/query.ko.js" type="text/javascript" charset="utf-8"></script>


<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 6px; margin-right: 40px">
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
          % if user.is_superuser:
            <li><a class="dropdown-collection" href="#" data-value="${ hue_collection.id }" data-settings-url="${ hue_collection.get_absolute_url() }">${ hue_collection.label }</a></li>
          % else:
            <li><a class="dropdown-hue_collection" href="#" data-value="${ hue_collection.id }">${ hue_collection.label }</a></li>
          % endif
        </ul>
      </div>

      ${ search_form | n,unicode }
      
      <button type="submit" id="search-btn" class="btn btn-inverse"><i class="fa fa-search"></i></button>
    </div>
  </form>
</div>

    <div>
      <ul class="nav nav-tabs">
        <li class="active"><a href="#tourStep1" class="tourStep">${ _('Search') }</a></li>
        <li><a href="#tourStep2" class="tourStep">${ _('Visualization') }</a></li>
        <li><a id="tourLastStep" href="#tourStep3" class="tourStep">${ _('Data') }</a></li>
      </ul>
    </div>
    
    <div class="tourSteps">
      <div id="tourStep1" class="tourStepDetails">

<div class="container results">

  <div id="mainContent" class="row">
    <div class="span2 results">
      <div class="row">
        <span class="pull-right">
          <a id="showAddFacetModal" href="javascript:void(0)"><i class="fa fa-plus"></i></a>
        </span>
      </div>
      <div class="row" data-bind="foreach: norm_facets">
        <span class="pull-right">
          <a href="javascript:void(0)" data-bind="click: editFacet"><i class="fa fa-pencil"></i></a>
          <a href="javascript:void(0)" data-bind="click: $root.removeFacet"><i class="fa fa-times"></i></a>
          <i class="fa fa-arrows" id="move-facet"></i>
        </span>
        <div data-bind="text: label"></div>
        <div data-bind="foreach: counts">
          <div>
            <a href="script:void(0)">
            <!-- ko if: selected -->
              <span data-bind="text: value, click: $root.unselectFacet"></span>
              <i data-bind="click: $root.unselectFacet" class="fa fa-times"></i>            
            <!-- /ko -->
            <!-- ko if: !selected -->           
              <span data-bind="text: value, click: $root.selectFacet"></span> (<span data-bind="text: count, click: $root.selectFacet"></span>)            
            <!-- /ko -->
            </a>
          </div>
        </div>
      </div>            
      
    </div> 
    
    <div class="span10 results">
      <div class="row">
        <span class="pull-right">
          <i class="fa fa-plus" id="edit-timeline"></i>
        </span>
      </div>
    
      <div class="row">
        <span class="pull-right">
          <a id="edit-template" href="javascript:void(0)"><i class="fa fa-pencil"></i></a>
        </span>
      </div>
      
      <!-- ko if: $root.template.isGridLayout() -->
      <table id="result-container">        
        <thead>
          <tr data-bind="foreach: $root.template.fields">
            <th data-bind="text: $data"></th>
          </tr>
        </thead>
        <tbody data-bind="foreach: results">
          <tr class="result-row" data-bind="foreach: $data">
            <td data-bind="text: $data"></td>
          </tr>
        </tbody>
      </table>
      <!-- /ko -->
      <!-- ko if: !$root.template.isGridLayout() -->
      <div id="result-container" data-bind="foreach: results">
        <div class="result-row" data-bind="html: $data"></div>
      </div>
      <!-- /ko -->
      
      </div>
    </div>

  </div>
</div>
        </div>
      </div>      


## unsused
<script type="text/html" id="error-template">
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
      <div class="alert alert-error">
        <h4 data-bind="text: title"></h4>
        <br/>
        <span class="decodeError" data-bind="text: message"></span>
      </div>
    </div>
  </div>
</div>
</script>


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
          ${ _('Grid result') }: <input type="checkbox" data-bind="checked: template.isGridLayout" />
        </p>
        
        <!-- ko if: template.isGridLayout() -->
        <p>
          ${ _('Fields') }
          <select data-bind="options: fields, selectedOptions: template.fields" size="5" multiple="true"></select>
        </p>  
        <!-- /ko -->
        
        <!-- ko if: !template.isGridLayout() -->
        <textarea data-bind="value: template.template, valueUpdate:'afterkeydown'"></textarea>
        <!-- /ko -->
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Ok')}</a>
  </div>
</div>

##<script src="/search/static/js/query.ko.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/mustache.js"></script>
<script src="/search/static/js/template.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
var viewModel;

$(document).ready(function () {
  viewModel = new SearchViewModel(${ hue_collection.result.data | n,unicode }, ${ hue_collection.facets.data | n,unicode });
  ko.applyBindings(viewModel);
  
  viewModel.search();

  $("#showAddFacetModal").click(function() {
    $("#addFacetModal").modal("show");
  });

  $("#submitAddFacetModal").click(function() {
    viewModel.addFacet({'name': $("#facetName").val()});
    $('#addFacetModal').modal("hide");
    viewModel.search();
  });

  $("#edit-template").click(function() {
    $("#editTemplateModal").modal("show");
  });
  

});

  function editFacet(facet) {
    viewModel.selectSingleFacet(facet);
    $("#editFacetModal").modal("show");
  };
</script>

${ commonfooter(messages) | n,unicode }
