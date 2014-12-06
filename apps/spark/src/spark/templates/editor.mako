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


${ commonheader(_('Query'), app_name, user, "68px") | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("notebook") > -1) {
      location.href = "/spark/editor?" + window.location.hash.substr(1);
    }
  }
</script>


<link rel="stylesheet" href="/static/css/common_dashboard.css">
<link rel="stylesheet" href="/static/ext/css/codemirror.css">
<link rel="stylesheet" href="/spark/static/css/spark.css">
<link rel="stylesheet" href="/static/ext/css/bootstrap-editable.css">
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<link rel="stylesheet" href="/static/ext/css/hue-charts.css">
<link rel="stylesheet" href="/static/ext/css/leaflet.css">
<link rel="stylesheet" href="/static/ext/css/nv.d3.min.css">
<link rel="stylesheet" href="/static/css/nv.d3.css">


<script src="/static/ext/js/codemirror-3.11.js"></script>
<script src="/static/js/codemirror-pig.js"></script>
<script src="/static/js/codemirror-hql.js"></script>
<script src="/static/js/codemirror-python.js"></script>
<script src="/static/js/codemirror-clike.js"></script>

<script src="/static/js/codemirror-show-hint.js"></script>

<script src="/static/js/codemirror-isql-hint.js"></script>
<script src="/static/js/codemirror-hql-hint.js"></script>
<script src="/static/js/codemirror-pig-hint.js"></script>
<script src="/static/js/codemirror-python-hint.js"></script>
<script src="/static/js/codemirror-clike-hint.js"></script>

<script src="/static/ext/js/markdown.min.js"></script>
<script src="/static/ext/js/jquery/plugins/jquery.hotkeys.js"></script>
<script src="/static/js/bootstrap-wysiwyg.js"></script>

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.hue-bindings.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/assist.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/spark.vm.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>


<script src="/static/js/hue.geo.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.colors.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/js/d3.v3.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/topojson.v1.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/topo/world.topo.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/topo/usa.topo.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/js/nv.d3.datamaps.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.legend.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.multiBarWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.lineWithBrushChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingDiscreteBar.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingDiscreteBarChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingMultiBar.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingMultiBarChart.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingPie.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.growingPieChart.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/js/ko.charts.js" type="text/javascript" charset="utf-8"></script>



<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Submit') }" rel="tooltip" data-placement="bottom" data-bind="click: true, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    &nbsp;&nbsp;&nbsp;
    % if user.is_superuser:
      <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
          data-bind="click: saveNotebook, css: {'btn': true}">
        <i class="fa fa-save"></i>
      </button>
      &nbsp;&nbsp;&nbsp;
      <button type="button" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
          data-bind="click: newNotebook, css: {'btn': true}">
        <i class="fa fa-file-o"></i>
      </button>
      <button type="button" title="${ _('Open') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
          data-bind="click: newNotebook, css: {'btn': true}">
        <i class="fa fa-folder-open-o"></i>
      </button>      
      <a class="btn" href="${ url('spark:list_notebooks') }" title="${ _('Notebooks') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
        <i class="fa fa-terminal"></i>
      </a>
    % endif
  </div>


  <ul class="nav nav-tabs">
    <!-- ko foreach: notebooks -->
      <li data-bind="css: { active: $parent.selectedNotebook() === $data }">
        <a href="javascript:void(0)" data-bind="text: name, click: $parent.selectedNotebook.bind(null, $data)"></a>
      </li>
    <!-- /ko -->
    <li>
      <a href="javascript:void(0)" data-bind="click: newNotebook"><i class="fa fa-plus" title="${ _('Add a new notebook') }"></i></a>
    </li>
  </ul>
</div>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span12">
        <div class="tab-content" data-bind="foreach: notebooks">
          <div class="tab-pane" data-bind="css: { active: $parent.selectedNotebook() === $data }, template: { name: 'notebook'}">
          </div>
        </div>
    </div>
  </div>
</div>


<script type="text/html" id="notebook">
  <div class="row-fluid">
    <div class="span2">
      <div class="assist">
        <a href="#" title="${_('Double click on a table name or field to insert it in the editor')}" rel="tooltip" data-placement="top" class="pull-right" style="margin:3px; margin-top:7px">
          <i class="fa fa-question-circle"></i>
        </a>
        <a id="refreshNavigator" href="#" title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="top" class="pull-right" style="margin:3px; margin-top:7px">
          <i class="fa fa-refresh"></i>
        </a>
        <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF">
          <li class="nav-header">${_('database')}</li>
        </ul>
        <!-- ko if: $root.assistContent && $root.assistContent().mainObjects().length > 0 -->
          <select data-bind="options: $root.assistContent().mainObjects, chosen: {}" class="input-medium" data-placeholder="${_('Choose a database...')}"></select>
          <input type="text" placeholder="${ _('Table name...') }" style="width:90%; margin-top: 20px"/>
          <div data-bind="visible: Object.keys($root.assistContent().firstLevelObjects()).length == 0">${_('The selected database has no tables.')}</div>
          <ul data-bind="visible: Object.keys($root.assistContent().firstLevelObjects()).length > 0, foreach: Object.keys($root.assistContent().firstLevelObjects())" class="unstyled assist-main">
            <li>
              <a href="javascript:void(0)" class="pull-right" style="padding-right:5px"><i class="fa fa-list" title="${'Preview Sample data'}" style="margin-left:5px"></i></a>
              <a href="javascript:void(0)" data-bind="click: loadAssistSecondLevel"><i class="fa fa-table"></i> <span data-bind="text: $data"></span></a>

              <div data-bind="visible: $root.assistContent().firstLevelObjects()[$data].loaded() && $root.assistContent().firstLevelObjects()[$data].open()">
                <ul data-bind="visible: $root.assistContent().firstLevelObjects()[$data].items().length > 0, foreach: $root.assistContent().firstLevelObjects()[$data].items()" class="unstyled">
                  <li><a data-bind="attr: {'title': secondLevelTitle($data)}" style="padding-left:10px" href="javascript:void(0)"><i class="fa fa-columns"></i> <span data-bind="html: truncateSecondLevel($data)"></span></a></li>
                </ul>
              </div>
            </li>
          </ul>
        <!-- /ko -->

        <div id="navigatorLoader" class="center" data-bind="visible: $root.assistContent().isLoading">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
        </div>
      </div>
    </div>
    <div class="span10">
      <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
        sortable: { template: 'snippet', data: snippets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.card-body').slideUp('fast'); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
            dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}">
      </div>
      <div style="margin: 20px">
        <a href="javascript: void(0)" data-bind="click: newSnippet">
          <i class="fa fa-plus" title="${ _('Add') }"></i> ${ _('Add a new snippet') }
        </a>
        <select data-bind="options: availableSnippets, value: selectedSnippet">
        </select>
      </div>
    </div>
  </div>

</script>


<script type="text/html" id="snippet">
  <div class="row-fluid">
    <div data-bind="css: klass, attr: {'id': 'snippet_' + id()}">

      <h2 class="card-heading simple" data-bind="visible: $root.isEditing() || (! $root.isEditing() && type() != 'text')">

        <span data-bind="visible: $root.isEditing">
          <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
          <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
          <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
          &nbsp;
        </span>

        <!-- ko if: type() == 'text' -->
        <i class="fa fa-header snippet-icon"></i><sup style="color: #338bb8; margin-left: -2px">${ _('Text') }</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'hive' -->
        <img src="/beeswax/static/art/icon_beeswax_48.png" class="snippet-icon">
        <!-- /ko -->

        <!-- ko if: type() == 'impala' -->
        <img src="/impala/static/art/icon_impala_48.png" class="snippet-icon">
        <!-- /ko -->

        <!-- ko if: type() == 'scala' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">scala</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'python' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">python</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'sql' -->
        <img src="/spark/static/art/icon_spark_48.png" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">sql</sup>
        <!-- /ko -->

        <!-- ko if: type() == 'pig' -->
        <img src="/pig/static/art/icon_pig_48.png" class="snippet-icon">
        <!-- /ko -->


        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
        <div class="inline pull-right">
          <strong class="muted" data-bind="text: status, visible: type() != 'text'"></strong> &nbsp;
          <strong class="muted" data-bind="visible: type() != 'text'">Took 1s</strong> &nbsp;
          <a href="javascript:void(0)" data-bind="visible: $root.isEditing, click: function(){ remove($parent, $data);}"><i class="fa fa-times"></i></a>
        </div>
      </h2>

      <div data-bind="visible: type() != 'text'">
        <div class="row-fluid">
          <div data-bind="css: editorKlass">
            <div data-bind="foreach: variables">
              <div>
                <span data-bind="text: name"></span>
                <input type="text" data-bind="value: value" />
              </div>
            </div>
            <textarea data-bind="value: statement_raw, codemirror: { 'id': id(), 'viewportMargin': Infinity, 'lineNumbers': true, 'matchBrackets': true, 'mode': editorMode(), 'enter': execute }"></textarea>
            <a href="javascript:void(0)" data-bind="click: execute, visible: status() != 'running'" class="btn codeMirror-overlaybtn">${ _('Go!') }</a>
            <a href="javascript:void(0)" data-bind="click: cancel, visible: status() == 'running'" class="btn codeMirror-overlaybtn">${ _('Cancel') }</a>
            <div class="progress" data-bind="css:{'progress-neutral': progress() == 0, 'progress-warning': progress() > 0 && progress() < 100, 'progress-success': progress() == 100}" style="height: 1px">
              <div class="bar" data-bind="style: {'width': progress() + '%'}"></div>
            </div>
          </div>
        </div>

        <div style="padding-top: 10px;">
          <span>
          <a data-bind="visible: result.meta().length > 0, click: function() { $data.showGrid(true); }, css: {'active': $data.showGrid}" href="javascript:void(0)" class="btn" title="${ _('Grid') }"><i class="fa fa-th"></i></a>
          <a data-bind="visible: result.meta().length > 0, click: function() { $data.showChart(true); }, css: {'active': $data.showChart}" href="javascript:void(0)" class="btn" title="${ _('Chart') }"><i class="fa fa-line-chart"></i></a>
          </span>
          &nbsp;
          <a data-bind="visible: status() != 'ready', click: function() { $data.showLogs(! $data.showLogs()); }, css: {'active': $data.showLogs}" href="javascript:void(0)" class="btn" title="${ _('Logs') }"><i class="fa fa-file-text-o"></i></a>
          &nbsp;
          <a data-bind="visible: status() == 'available', click: function() { $data.showDownload(! $data.showDownload()); }" href="javascript:void(0)" class="btn" title="${ _('Logs') }">
            <i class="fa fa-arrow-circle-o-down"></i>
          </a>
          
          <span data-bind="visible: showDownload">
		    <form method="POST" action="${ url('spark:download') }">
		      ${ csrf_token(request) | n,unicode }
		      <input type="hidden" name="notebook" data-bind="value: ko.mapping.toJSON($root.selectedNotebook)"/>
		      <input type="hidden" name="snippet" data-bind="value: ko.mapping.toJSON($data)"/>
		
		      <button class="btn" type="submit" name="csv" title="${ _('Download first rows as CSV') }"><i class="fa fa-file-o"></i></button>
		      <button class="btn" type="submit" name="xls" title="${ _('Download first rows as XLS') }"><i class="fa fa-file-excel-o"></i></button>
		    </form>
          </span>          
        </div>

        <div data-bind="visible: showLogs, css: resultsKlass">
          <span data-bind="visible: result.logs().length == 0">${ _('Loading...') }</span>
          <span data-bind="text: result.logs"></span>
        </div>

        <div data-bind="visible: result.errors().length > 0, css: resultsKlass">
          <span data-bind="text: result.errors"></span>
        </div>

        <div class="row-fluid" data-bind="visible: result.meta().length > 0 && showGrid()" style="height: 400px">
          <div class="span2">
            <ul class="nav nav-list" style="border: none; background-color: #FFF">
              <li class="nav-header">${_('columns')}</li>
            </ul>
            <ul class="unstyled" data-bind="foreach: result.meta">
              <li data-bind="visible: name != ''"><input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" /> <a class="pointer" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }"></a></li>
            </ul>
          </div>
          <div class="span10">
            <div data-bind="css: resultsKlass">
              <table class="table table-condensed resultTable" data-tablescroller-fixed-height="360">
                <thead>
                  <tr data-bind="foreach: result.meta">
                    <th data-bind="html: ($index() == 0 ? '&nbsp;' : $data.name), css: { 'sort-numeric': isNumericColumn($data.type), 'sort-date': isDateTimeColumn($data.type), 'sort-string': isStringColumn($data.type)}, attr: {'width': $index() == 0 ? '1%' : ''}"></th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
              <a href="javascript:void(0)" data-bind="click: function() { $data.fetchResult(100, false); }" class="btn">${ _('Next') }</a>
            </div>
          </div>
        </div>

        <div class="row-fluid" data-bind="visible: showChart" style="height: 400px">
          <div class="span2">

            <ul class="nav nav-list" style="border: none; background-color: #FFF">
              <li class="nav-header">${_('type')}</li>
            </ul>

            <a rel="tooltip" data-placement="top" title="${_('Bars')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.BARCHART}, click: function(){ chartType(ko.HUE_CHARTS.TYPES.BARCHART); }"><i class="hcha hcha-bar-chart"></i></a>
            <a rel="tooltip" data-placement="top" title="${_('Lines')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.LINECHART}, click: function(){ chartType(ko.HUE_CHARTS.TYPES.LINECHART); }"><i class="hcha hcha-line-chart"></i></a>
            <a rel="tooltip" data-placement="top" title="${_('Pie')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.PIECHART}, click: function(){ chartType(ko.HUE_CHARTS.TYPES.PIECHART); }"><i class="hcha hcha-pie-chart"></i></a>
            <a rel="tooltip" data-placement="top" title="${_('Map')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.MAP}, click: function(){ chartType(ko.HUE_CHARTS.TYPES.MAP); }"><i class="hcha hcha-map-chart"></i></a>

            <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
              <li data-bind="visible: chartType() != ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('x-axis')}</li>
              <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
            </ul>
            <div data-bind="visible: chartType() != ''">
              <select data-bind="options: result.cleanedMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', chosen: {}" class="input-medium"></select>
            </div>

            <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
              <li data-bind="visible: chartType() != ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('y-axis')}</li>
              <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
            </ul>

            <div style="overflow-y: scroll; max-height: 220px" data-bind="visible: chartType() != '' && (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.LINECHART)">
              <ul class="unstyled" data-bind="foreach: result.cleanedMeta">
                <li><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></li>
              </ul>
            </div>
            <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART || chartType() == ko.HUE_CHARTS.TYPES.MAP">
              <select data-bind="options: result.cleanedMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', chosen: {}" class="input-medium"></select>
            </div>

            <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.MAP">
              <li class="nav-header">${_('label')}</li>
            </ul>
            <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP">
              <select data-bind="options: result.cleanedMeta, value: chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', chosen: {}" class="input-medium"></select>
            </div>

            <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP">
              <li class="nav-header">${_('sorting')}</li>
            </ul>
            <div class="btn-group" data-toggle="buttons-radio" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP">
              <a rel="tooltip" data-placement="top" title="${_('No sorting')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'none'}, click: function(){ chartSorting('none'); }"><i class="fa fa-align-left fa-rotate-270"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Sort ascending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'asc'}, click: function(){ chartSorting('asc'); }"><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
              <a rel="tooltip" data-placement="top" title="${_('Sort descending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'desc'}, click: function(){ chartSorting('desc'); }"><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
            </div>
          </div>
          <div class="span10">
            <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                  transformer: pieChartDataTransformer, maxWidth: 350 }, visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART"></div>

            <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true,
                  transformer: multiSerieDataTransformer, stacked: false, showLegend: true},  stacked: true, showLegend: true, visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART"></div>

            <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: multiSerieDataTransformer, showControls: false }, visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART"></div>

            <div data-bind="attr:{'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: leafletMapChartDataTransformer, showControls: false, height: 380, visible: chartType() == ko.HUE_CHARTS.TYPES.MAP}"></div>
          </div>
        </div>
      </div>

      <div data-bind="visible: type() == 'text'">
        <div data-bind="html: statement_raw, visible: ! $root.isEditing()"></div>

        <div class="btn-toolbar" data-role="editor-toolbar" data-bind="attr:{'data-target': '#editor_'+id()}, visible: $root.isEditing()">
          <div class="btn-group">
            <a class="btn dropdown-toggle" data-toggle="dropdown" title="Font Size"><i class="fa fa-text-height"></i>&nbsp;<b class="caret"></b></a>
              <ul class="dropdown-menu">
              <li><a data-edit="fontSize 5"><font size="5">Huge</font></a></li>
              <li><a data-edit="fontSize 3"><font size="3">Normal</font></a></li>
              <li><a data-edit="fontSize 1"><font size="1">Small</font></a></li>
              </ul>
          </div>
          <div class="btn-group">
            <a class="btn" data-edit="bold" title="Bold (Ctrl/Cmd+B)"><i class="fa fa-bold"></i></a>
            <a class="btn" data-edit="italic" title="Italic (Ctrl/Cmd+I)"><i class="fa fa-italic"></i></a>
            <a class="btn" data-edit="strikethrough" title="Strikethrough"><i class="fa fa-strikethrough"></i></a>
            <a class="btn" data-edit="underline" title="Underline (Ctrl/Cmd+U)"><i class="fa fa-underline"></i></a>
          </div>
          <div class="btn-group">
            <a class="btn" data-edit="insertunorderedlist" title="Bullet list"><i class="fa fa-list-ul"></i></a>
            <a class="btn" data-edit="insertorderedlist" title="Number list"><i class="fa fa-list-ol"></i></a>
            <a class="btn" data-edit="outdent" title="Reduce indent (Shift+Tab)"><i class="fa fa-indent"></i></a>
            <a class="btn" data-edit="indent" title="Indent (Tab)"><i class="fa fa-outdent"></i></a>
          </div>
          <div class="btn-group">
            <a class="btn" data-edit="justifyleft" title="Align Left (Ctrl/Cmd+L)"><i class="fa fa-align-left"></i></a>
            <a class="btn" data-edit="justifycenter" title="Center (Ctrl/Cmd+E)"><i class="fa fa-align-center"></i></a>
            <a class="btn" data-edit="justifyright" title="Align Right (Ctrl/Cmd+R)"><i class="fa fa-align-right"></i></a>
            <a class="btn" data-edit="justifyfull" title="Justify (Ctrl/Cmd+J)"><i class="fa fa-align-justify"></i></a>
          </div>
          <div class="btn-group">
            <a class="btn dropdown-toggle" data-toggle="dropdown" title="Hyperlink"><i class="fa fa-link"></i></a>
            <div class="dropdown-menu input-append">
              <input class="span2" placeholder="URL" type="text" data-edit="createLink"/>
              <button class="btn" type="button">Add</button>
            </div>
            <a class="btn" data-edit="unlink" title="Remove Hyperlink"><i class="fa fa-cut"></i></a>
          </div>
          <div class="btn-group">
            <a class="btn" data-edit="undo" title="Undo (Ctrl/Cmd+Z)"><i class="fa fa-undo"></i></a>
            <a class="btn" data-edit="redo" title="Redo (Ctrl/Cmd+Y)"><i class="fa fa-repeat"></i></a>
          </div>
        </div>

        <div data-bind="attr:{'id': 'editor_'+id()}, html: statement_raw, value: statement_raw, wysiwyg: {}, visible: $root.isEditing()"></div>

      </div>
    </div>
  </div>
</script>


<script type="text/javascript" charset="utf-8">

  var assist = new Assist({
    app: "beeswax",
    user: "${user}",
    failsSilentlyOn: [500], // error codes from beeswax/views.py - autocomplete
    baseURL: "${url('beeswax:api_autocomplete_databases')}"
  });

  ko.bindingHandlers.wysiwyg = {
    init: function (element, valueAccessor, allBindings) {
      $(element).wysiwyg();
      $(element).on("paste", function () {
        window.setTimeout(function(){
          if (markdown.toHTML($(element).text().trim()) != "<p>" + $(element).text().trim() + "</p>"){
            allBindings().html(markdown.toHTML($(element).text().trim()));
          }
        }, 200);

      });
      $(element).on("blur", function () {
        allBindings().html($(element).cleanHtml());
      });
    }
  };

  ko.bindingHandlers.chosen = {
    init: function (element) {
      $(element).chosen({
        disable_search_threshold: 5,
        width: "100%"
      }).change(function (e, obj) {
        viewModel.assistContent().selectedMainObject(obj.selected);
        loadAssistFirstLevel();
      });
    },
    update: function (element, valueAccessor, allBindings) {
      $(element).trigger('chosen:updated');
    }
  };


  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, snippet) {

      $(document).on("error.autocomplete", function () {
        $(".CodeMirror-spinner").remove();
      });

      function hiveImpalaAutocomplete(cm, autocompleteSet, comingFromKeyEvent) {
        CodeMirror.fromDot = false;

        CodeMirror.onAutocomplete = function (data, from, to) {
          if (data.indexOf("(") > -1) {
            cm.setCursor({line: from.line, ch: from.ch + data.length - 1});
            hiveImpalaAutocomplete(cm, autocompleteSet);
          }
          if (CodeMirror.tableFieldMagic) {
            cm.replaceRange(" ", from, from);
            cm.setCursor(from);
            hiveImpalaAutocomplete(cm, autocompleteSet);
          }
        };

        function splitStatements(hql) {
          var statements = [];
          var current = "";
          var betweenQuotes = null;
          for (var i = 0, len = hql.length; i < len; i++) {
            var c = hql[i];
            current += c;
            if ($.inArray(c, ['"', "'"]) > -1) {
              if (betweenQuotes == c) {
                betweenQuotes = null;
              }
              else if (betweenQuotes == null) {
                betweenQuotes = c;
              }
            }
            else if (c == ";") {
              if (betweenQuotes == null) {
                statements.push(current);
                current = "";
              }
            }
          }

          if (current != "" && current != ";") {
            statements.push(current);
          }
          return statements;
        }

        function getStatementAtCursor(cm) {
          var _pos = cm.indexFromPos(cm.getCursor());
          var _statements = splitStatements(cm.getValue());
          var _cumulativePos = 0;
          var _statementAtCursor = "";
          var _relativePos = 0;
          for (var i = 0; i < _statements.length; i++) {
            if (_cumulativePos + _statements[i].length >= _pos && _statementAtCursor == "") {
              _statementAtCursor = _statements[i].split("\n").join(" ");
              _relativePos = _pos - _cumulativePos;
            }
            _cumulativePos += _statements[i].length;
          }
          return {
            statement: _statementAtCursor,
            relativeIndex: _relativePos
          };
        }

        function getTableAliases(textScanned) {
          var _aliases = {};
          var _val = textScanned.split("\n").join(" ");
          var _from = _val.toUpperCase().indexOf("FROM ");
          if (_from > -1) {
            var _match = _val.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
            var _to = _val.length;
            if (_match) {
              _to = _match.index;
            }
            var _found = _val.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
            for (var i = 0; i < _found.length; i++) {
              var _tablealias = $.trim(_found[i]).split(" ");
              if (_tablealias.length > 1) {
                _aliases[_tablealias[1]] = _tablealias[0];
              }
            }
          }
          return _aliases;
        }

        function tableHasAlias(tableName, textScanned) {
          var _aliases = getTableAliases(textScanned);
          for (var alias in _aliases) {
            if (_aliases[alias] == tableName) {
              return true;
            }
          }
          return false;
        }


        function fieldsAutocomplete(cm) {
          CodeMirror.possibleSoloField = true;
          try {
            var _statement = getStatementAtCursor(cm).statement;
            var _from = _statement.toUpperCase().indexOf("FROM");
            if (_from > -1) {
              var _match = _statement.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
              var _to = _statement.length;
              if (_match) {
                _to = _match.index;
              }
              var _found = _statement.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
            }

            var _foundTable = "";
            for (var i = 0; i < _found.length; i++) {
              if ($.trim(_found[i]) != "" && _foundTable == "") {
                _foundTable = $.trim(_found[i]).split(" ")[0];
              }
            }
            if (_foundTable != "") {
              if (tableHasAlias(_foundTable, _statement)) {
                CodeMirror.possibleSoloField = false;
                CodeMirror.showHint(cm, autocompleteSet);
              }
              else {
                assist.options.onDataReceived = function (data) {
                  if (data.columns) {
                    CodeMirror.catalogFields = "* " + data.columns.join(" ");
                    CodeMirror.showHint(cm, autocompleteSet);
                  }
                }

                if (_foundTable.indexOf("(") > -1) {
                  _foundTable = _foundTable.substr(_foundTable.indexOf("(") + 1);
                }

                var _aliases = getTableAliases(_statement);
                if (_aliases[_foundTable]) {
                  _foundTable = _aliases[_foundTable];
                }

                assist.getData(viewModel.assistContent().selectedMainObject() + "/" + _foundTable);
              }
            }
          }
          catch (e) {
          }
        }

        var pos = cm.cursorCoords();
        if ($(".CodeMirror-spinner").length == 0) {
          $("<i class='fa fa-spinner fa-spin CodeMirror-spinner'></i>").appendTo($("body"));
        }
        $(".CodeMirror-spinner").css("top", pos.top + "px").css("left", (pos.left - 4) + "px").show();

        if (comingFromKeyEvent) {

          var _statement = getStatementAtCursor(cm).statement;
          var _line = cm.getLine(cm.getCursor().line);
          var _partial = _line.substring(0, cm.getCursor().ch);
          var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
          if (_statement.indexOf("FROM") > -1) {

            assist.options.onDataReceived = function (data) {
              if (data.columns) {
                var _cols = data.columns;
                for (var col in _cols) {
                  _cols[col] = "." + _cols[col];
                }
                CodeMirror.catalogFields = "* " + _cols.join(" ");
                CodeMirror.fromDot = true;
                CodeMirror.showHint(cm, autocompleteSet);
              }
            }

            if (_table.indexOf("(") > -1) {
              _table = _table.substr(_table.indexOf("(") + 1);
            }

            var _aliases = getTableAliases(_statement);
            if (_aliases[_table]) {
              _table = _aliases[_table];
            }

            assist.getData(viewModel.assistContent().selectedMainObject() + "/" + _table);

          }

        }
        else {
          assist.options.onDataReceived = function (data) {
            if (data.tables) {
              CodeMirror.catalogTables = data.tables.join(" ");
              var _statementAtCursor = getStatementAtCursor(cm);
              var _before = _statementAtCursor.statement.substr(0, _statementAtCursor.relativeIndex).replace(/;+$/, "");
              var _after = _statementAtCursor.statement.substr(_statementAtCursor.relativeIndex).replace(/;+$/, "");
              if ($.trim(_before).substr(-1) == ".") {
                var _statement = _statementAtCursor.statement;
                var _line = cm.getLine(cm.getCursor().line);
                var _partial = _line.substring(0, cm.getCursor().ch);
                var _table = _partial.substring(_partial.lastIndexOf(" ") + 1, _partial.length - 1);
                if (_statement.indexOf("FROM") > -1) {
                  assist.options.onDataReceived = function (data) {
                    if (data.columns) {
                      var _cols = data.columns;
                      for (var col in _cols) {
                        _cols[col] = "." + _cols[col];
                      }
                      CodeMirror.catalogFields = "* " + _cols.join(" ");
                      CodeMirror.showHint(cm, autocompleteSet);
                    }
                  }

                  if (_table.indexOf("(") > -1) {
                    _table = _table.substr(_table.indexOf("(") + 1);
                  }

                  var _aliases = getTableAliases(_statement);
                  if (_aliases[_table]) {
                    _table = _aliases[_table];
                  }

                  assist.getData(viewModel.assistContent().selectedMainObject() + "/" + _table);
                }
              }
              else {
                CodeMirror.possibleTable = false;
                CodeMirror.tableFieldMagic = false;
                if ((_before.toUpperCase().indexOf(" FROM ") > -1 || _before.toUpperCase().indexOf(" TABLE ") > -1 || _before.toUpperCase().indexOf(" STATS ") > -1) && _before.toUpperCase().indexOf(" ON ") == -1 && _before.toUpperCase().indexOf(" ORDER BY ") == -1 && _before.toUpperCase().indexOf(" WHERE ") == -1 ||
                    _before.toUpperCase().indexOf("REFRESH") > -1 || _before.toUpperCase().indexOf("METADATA") > -1 || _before.toUpperCase().indexOf("DESCRIBE") > -1) {
                  CodeMirror.possibleTable = true;
                }
                CodeMirror.possibleSoloField = false;
                if (_before.toUpperCase().indexOf("SELECT ") > -1 && _before.toUpperCase().indexOf(" FROM ") == -1 && !CodeMirror.fromDot) {
                  if (_after.toUpperCase().indexOf("FROM ") > -1 || $.trim(_before).substr(-1) == "(") {
                    fieldsAutocomplete(cm);
                  }
                  else {
                    CodeMirror.tableFieldMagic = true;
                    CodeMirror.showHint(cm, autocompleteSet);
                  }
                }
                else {
                  if ((_before.toUpperCase().indexOf("WHERE ") > -1 || _before.toUpperCase().indexOf("ORDER BY ") > -1) && !CodeMirror.fromDot && _before.toUpperCase().match(/ ON| LIMIT| GROUP| SORT/) == null) {
                    fieldsAutocomplete(cm);
                  }
                  else {
                    CodeMirror.showHint(cm, autocompleteSet);
                  }
                }
              }
            }
          }
          assist.getData(viewModel.assistContent().selectedMainObject());
        }
      }

      var options = $.extend(valueAccessor(), {
        extraKeys: {
          "Ctrl-Space": function (cm) {
            $(document.body).on("contextmenu", function (e) {
              e.preventDefault(); // prevents native menu on FF for Mac from being shown
            });
            switch (valueAccessor().mode) {
              case "text/x-pig":
                CodeMirror.availableVariables = [];
                CodeMirror.showHint(cm, CodeMirror.pigHint);
                break;
              case "text/x-python":
                CodeMirror.showHint(cm, CodeMirror.pythonHint);
                break;
              case "text/x-scala":
                CodeMirror.showHint(cm, CodeMirror.scalaHint);
                break;
              case "text/x-hiveql":
                hiveImpalaAutocomplete(cm, CodeMirror.hiveQLHint);
                break;
              case "text/x-impalaql":
                hiveImpalaAutocomplete(cm, CodeMirror.impalaSQLHint);
                break;
              default:
                break;
            }
          },
          "Ctrl-Enter": function () {
            valueAccessor().enter();
          }
        },
        onKeyEvent: function (cm, e) {
          switch (valueAccessor().mode) {
            case "text/x-hiveql":
              if (e.type == "keyup" && e.keyCode == 190) {
                hiveImpalaAutocomplete(cm, CodeMirror.hiveQLHint, true);
              }
              break;
            case "text/x-impalaql":
              if (e.type == "keyup" && e.keyCode == 190) {
                hiveImpalaAutocomplete(cm, CodeMirror.impalaSQLHint, true);
              }
              break;
            default:
              break;
          }
        }
      });
      var editor = CodeMirror.fromTextArea(element, options);

      element.editor = editor;
      $("#snippet_" + options.id).data("editor", editor);
      editor.setValue(allBindingsAccessor().value());
      editor.setSize("100%", "100px");
      var wrapperElement = $(editor.getWrapperElement());

      editor.on("change", function () {
        if (editor.lineCount() > 7 && editor.lineCount() < 21) {
          editor.setSize("100%", "auto");
        }
        if (editor.lineCount() >= 21) {
          editor.setSize("100%", "270px");
        }

        $("#snippet_" + snippet.id()).find(".resultTable").jHueTableExtender({
          fixedHeader: true,
          includeNavigator: false
        });

        allBindingsAccessor().value(editor.getValue());
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        wrapperElement.remove();
      });
    }
  };

  viewModel = new EditorViewModel(${ notebooks_json | n,unicode });
  viewModel.assistContent(assist);
  ko.applyBindings(viewModel);
  viewModel.init();

  function loadAssistSecondLevel(first) {
    if (!viewModel.assistContent().firstLevelObjects()[first].loaded()) {
      viewModel.assistContent().isLoading(true);
      assist.options.onDataReceived = function (data) {
        if (data.columns) {
          var _cols = data.extended_columns ? data.extended_columns : data.columns;
          viewModel.assistContent().firstLevelObjects()[first].items(_cols);
          viewModel.assistContent().firstLevelObjects()[first].loaded(true);
        }
        viewModel.assistContent().isLoading(false);
      }
      assist.getData(viewModel.assistContent().selectedMainObject() + "/" + first);
    }
    viewModel.assistContent().firstLevelObjects()[first].open(!viewModel.assistContent().firstLevelObjects()[first].open());
    window.setTimeout(resizeAssist, 100);
  }

  function loadAssistFirstLevel() {
    assist.options.onDataReceived = function (data) {
      if (data.tables) {
        var _obj = {};
        data.tables.forEach(function (item) {
          _obj[item] = {
            items: ko.observableArray([]),
            open: ko.observable(false),
            loaded: ko.observable(false)
          }
        });
        viewModel.assistContent().firstLevelObjects(_obj);
      }
      viewModel.assistContent().isLoading(false);
    }
    assist.getData(viewModel.assistContent().selectedMainObject());
  }

  function loadAssistMain() {
    assist.options.onDataReceived = function (data) {
      if (data.databases) {
        viewModel.assistContent().mainObjects(data.databases);
        if (viewModel.assistContent().mainObjects().length > 0 && !viewModel.assistContent().selectedMainObject()) {
          viewModel.assistContent().selectedMainObject(viewModel.assistContent().mainObjects()[0]);
          loadAssistFirstLevel();
        }
      }
    }
    assist.getData();
  }

  loadAssistMain();

  function needsTruncation(level) {
    return (level.name.length + level.type.length) > 20;
  }

  function secondLevelTitle(level) {
    var _title = "";

    if (level.comment && needsTruncation(level)) {
      _title = level.name + " (" + level.type + "): " + level.comment;
    } else if (needsTruncation(level)) {
      _title = level.name + " (" + level.type + ")";
    } else if (level.comment) {
      _title = level.comment;
    }
    return _title;
  }

  function truncateSecondLevel(level) {
    var escapeString = function (str) {
      return $("<span>").text(str).html().trim()
    }
    if (needsTruncation(level)) {
      return escapeString(level.name + " (" + level.type + ")").substr(0, 20) + "&hellip;";
    }
    return escapeString(level.name + " (" + level.type + ")");
  }

  function resizeAssist() {
    $(".assist").width($(".assist").parents(".span2").width());
    $(".assist").parents(".span2").height($(".assist").height() + 100);
    $(".assist-main").height($(window).height() - 230);
  }

  function createDatatable(el, snippet) {
    $(el).addClass("dt");
    var _dt = $(el).dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bDestroy": true,
      "bAutoWidth": false,
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}"
      },
      "fnDrawCallback": function (oSettings) {
        $(el).parents(".dataTables_wrapper").jHueTableScroller({
          minHeight: $(window).height() - 400,
          heightAfterCorrection: 0
        });

        $(el).jHueTableExtender({
          fixedHeader: true,
          includeNavigator: false
        });
      },
      "aoColumnDefs": [
        {
          "sType": "numeric",
          "aTargets": [ "sort-numeric" ]
        },
        {
          "sType": "string",
          "aTargets": [ "sort-string" ]
        },
        {
          "sType": "date",
          "aTargets": [ "sort-date" ]
        }
      ]
    });
    $(el).parents(".dataTables_wrapper").jHueTableScroller({
      minHeight: $(window).height() - 400,
      heightAfterCorrection: 0
    });

    $(el).jHueTableExtender({
      fixedHeader: true,
      includeNavigator: false
    });
    $(".dataTables_filter").hide();
    return _dt;
  }

  function toggleColumn(linkElement, index) {
    var _dt = $(linkElement).parents(".snippet").find("table:eq(1)").dataTable();
    _dt.fnSetColumnVis(index, !_dt.fnSettings().aoColumns[index].bVisible);
  }

  function scrollToColumn(linkElement) {
    var _t = $(linkElement).parents(".snippet").find("table:eq(1)");
    var _text = $.trim($(linkElement).text().split("(")[0]);
    var _col = _t.find("th").filter(function () {
      return $.trim($(this).text()) == _text;
    });
    _t.find(".columnSelected").removeClass("columnSelected");
    var _colSel = _t.find("tr td:nth-child(" + (_col.index() + 1) + ")");
    if (_colSel.length > 0) {
      _colSel.addClass("columnSelected");
      _t.parent().animate({
        scrollLeft: _colSel.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
      }, 300);
    }
  }

  function isNumericColumn(type) {
    return $.inArray(type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE', 'TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
  }

  function isDateTimeColumn(type) {
    return $.inArray(type, ['TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
  }

  function isStringColumn(type) {
    return !isNumericColumn(type) && !isDateTimeColumn(type);
  }

  $(document).ready(function () {
    resizeAssist();

    $(document).on("executeStarted", function (e, snippet) {
      var _el = $("#snippet_" + snippet.id()).find(".resultTable");
      $("#snippet_" + snippet.id()).find(".progress").animate({
        height: "4px"
      }, 100);
      if (_el.hasClass("dt")) {
        _el.removeClass("dt");
        $("#eT" + snippet.id() + "jHueTableExtenderClonedContainer").remove();
        _el.dataTable().fnClearTable();
        _el.dataTable().fnDestroy();
        _el.find("thead tr").empty();
      }
    });

    $(document).on("renderData", function (e, options) {
      var _el = $("#snippet_" + options.snippet.id()).find(".resultTable");
      if (options.data.length > 0) {
        window.setTimeout(function () {
          var _dt;
          if (options.initial){
            options.snippet.result.meta.notifySubscribers();
            $("#snippet_" + options.snippet.id()).find("select").trigger("chosen:updated");
            _dt = createDatatable(_el, options.snippet);
          }
          else {
            _dt = _el.dataTable();
          }
          _dt.fnAddData(options.data);
        }, 100);
      }
    });

    $(document).on("progress", function (e, options) {
      if (options.data == 100) {
        window.setTimeout(function () {
          $("#snippet_" + options.snippet.id()).find(".progress").animate({
            height: "1px"
          }, 100, function(){
            options.snippet.progress(0);
          });
        }, 2000);
      }
    });

    $(document).on("forceChartDraw", function(e, snippet) {
      window.setTimeout(function(){
        snippet.chartX.notifySubscribers();
      }, 100);
    });

    viewModel.notebooks().forEach(function(notebook){
      notebook.snippets().forEach(function(snippet){
        if (snippet.result.data().length > 0) {
          var _el = $("#snippet_" + snippet.id()).find(".resultTable");
          window.setTimeout(function () {
            var _dt = createDatatable(_el, snippet);
            _dt.fnAddData(snippet.result.data());
            $(document).trigger("forceChartDraw", snippet);
          }, 100);
        }
      });
    });

    $(".CodeMirror").each(function(){
      $(this)[0].CodeMirror.refresh();
    });
  });


function pieChartDataTransformer(rawDatum) {
  var _data = [];

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null){
    var _idxValue = -1;
    var _idxLabel = -1;
    rawDatum.snippet.result.meta().forEach(function(col, idx){
      if (col.name == rawDatum.snippet.chartX()){
        _idxLabel = idx;
      }
      if (col.name == rawDatum.snippet.chartYSingle()){
        _idxValue = idx;
      }
    });
    $(rawDatum.counts()).each(function (cnt, item) {
      _data.push({
        label: item[_idxLabel],
        value: item[_idxValue],
        obj: item
      });
    });
  }

  if (rawDatum.sorting == "asc"){
    _data.sort(function(a, b){
      return a.value > b.value
    });
  }
  if (rawDatum.sorting == "desc"){
    _data.sort(function(a, b){
      return b.value > a.value
    });
  }

  return _data;
}

function leafletMapChartDataTransformer(rawDatum) {
  var _data = [];
  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null){
    var _idxLat = -1;
    var _idxLng = -1;
    var _idxLabel = -1;
    rawDatum.snippet.result.meta().forEach(function(col, idx){
      if (col.name == rawDatum.snippet.chartX()){
        _idxLat = idx;
      }
      if (col.name == rawDatum.snippet.chartYSingle()){
        _idxLng = idx;
      }
      if (col.name == rawDatum.snippet.chartMapLabel()){
        _idxLabel = idx;
      }
    });
    if (rawDatum.snippet.chartMapLabel() != null){
      $(rawDatum.counts()).each(function (cnt, item) {
        _data.push({
          lat: item[_idxLat],
          lng: item[_idxLng],
          label: item[_idxLabel],
          obj: item
        });
      });
    }
    else {
      $(rawDatum.counts()).each(function (cnt, item) {
        _data.push({
          lat: item[_idxLat],
          lng: item[_idxLng],
          obj: item
        });
      });
    }
  }
  return _data;
}

function multiSerieDataTransformer(rawDatum) {
  var _datum = [];

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYMulti().length > 0){
    var _plottedSerie = 0;
    rawDatum.snippet.chartYMulti().forEach(function(col){
      var _idxValue = -1;
      var _idxLabel = -1;
      rawDatum.snippet.result.meta().forEach(function(icol, idx){
        if (icol.name == rawDatum.snippet.chartX()){
          _idxLabel = idx;
        }
        if (icol.name == col){
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
            return a.y > b.y
          });
        }
        if (rawDatum.sorting == "desc") {
          _data.sort(function (a, b) {
            return b.y > a.y
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


</script>

${ commonfooter(messages) | n,unicode }
