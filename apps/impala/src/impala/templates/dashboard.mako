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

${ commonheader(None, "impala", user) | n,unicode }

<%dashboard:layout_toolbar>
  <%def name="widgets()">
    <div data-bind="css: { 'draggable-widget': true},
          draggable: {data: draggableResultset(), isEnabled: true,
              options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                        'stop': function(event, ui){$('.card-body').slideDown('fast'); }}}"
         title="${_('Grid Results')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
            <i class="fa fa-table"></i>
         </a>
    </div>
    <div data-bind="css: { 'draggable-widget': true},
          draggable: {data: draggablePie(), isEnabled: true,
              options: {'start': function(event, ui){lastWindowScrollPosition = $(window).scrollTop();$('.card-body').slideUp('fast');},
                        'stop': function(event, ui){$('.card-body').slideDown('fast'); }}}"
         title="${_('Pie Chart')}" rel="tooltip" data-placement="top">
         <a data-bind="style: { cursor: true ? 'move' : 'default' }">
            <i class="hcha hcha-pie-chart"></i>
         </a>
    </div>    
</%def>
</%dashboard:layout_toolbar>


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    % if user.is_superuser:
      <button type="button" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}"><i class="fa fa-pencil"></i></button>
    % endif
  </div>


  <form class="form-search" style="margin: 0" data-bind="submit: search">
    <strong>${_("Search")}</strong>
    <div class="input-append">

      <span data-bind="foreach: query.qs">
        <input data-bind="clearable: q" maxlength="4096" type="text" class="search-query input-xlarge">
  ##      <!-- ko if: $index() >= 1 -->
  ##      <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.removeQ"><i class="fa fa-minus"></i></a>
  ##      <!-- /ko -->
      </span>

  ##    <a class="btn" href="javascript:void(0)" data-bind="click: $root.query.addQ"><i class="fa fa-plus"></i></a>

      <button type="submit" id="search-btn" class="btn btn-inverse" style="margin-left:10px"><i class="fa fa-search"></i></button>
    </div>
  </form>
</div>


${ dashboard.layout_skeleton() }

<script type="text/html" id="resultset-widget">

<div id="result-main" style="overflow-x: auto">
  <table id="result-container" style="margin-top: 0; width: 100%">
    <thead>
    </thead>
    <tbody data-bind="foreach: { data: $root.results, as: 'row'}" class="result-tbody">
      <tr class="result-row">
        <td>
          <a href="javascript:void(0)">
            <i class="fa" data-bind="css: {'fa-caret-right' : true }"></i>
          </a>
        </td>
        <!-- ko foreach: row -->
          <td data-bind="html: $data"></td>
        <!-- /ko -->
      </tr>
    </tbody>
  </table>
</div>
</script>

<script type="text/html" id="pie-widget">
  <!-- ko if: $root.getFacetFromResult(id()) -->
  <div class="row-fluid" data-bind="with: $root.getFacetFromResult(id())">
    <div data-bind="visible: $root.isEditing, with: $root.dashboard.getFacetById ($parent.id())" style="margin-bottom: 20px">
      <input type="text" data-bind="value: properties.limit"></input>
    </div>
  
    <span data-bind="foreach: data()">
      <span data-bind="text: $data"></span>
    </span>
  </div>
  <!-- /ko -->
</script>



<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

${ dashboard.import_layout() }
${ dashboard.import_bindings() }
${ dashboard.import_charts() }

<script src="/impala/static/js/search.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  function columnDropAdditionalHandler(widget){
    console.log("column drop")
  }

  function widgetDraggedAdditionalHandler(widget){
    console.log("boom")
  }

  var viewModel = new TestViewModel(${ query_json | n,unicode }, ${ dashboard_json | n,unicode  });
  ko.applyBindings(viewModel);
</script>

${ commonfooter(messages) | n,unicode }
