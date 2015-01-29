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
<link rel="stylesheet" href="/static/ext/select2/select2.css">
<link rel="stylesheet" href="/static/ext/css/medium-editor.min.css">
<link rel="stylesheet" href="/static/css/bootstrap-medium-editor.css">


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

<script src="/static/ext/js/bootstrap-editable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ko.editable.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/hue.utils.js"></script>
<script src="/static/js/ko.hue-bindings.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/assist.js" type="text/javascript" charset="utf-8"></script>
<script src="/spark/static/js/spark.ko.js" type="text/javascript" charset="utf-8"></script>
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
<script src="/static/js/nv.d3.scatter.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/nv.d3.scatterChart.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/js/ko.charts.js" type="text/javascript" charset="utf-8"></script>

<script src="/static/ext/select2/select2.min.js" type="text/javascript" charset="utf-8"></script>

<!--[if IE 9]>
  <script src="/static/ext/js/classList.min.js" type="text/javascript" charset="utf-8"></script>  
<![endif]-->
<script src="/static/ext/js/medium-editor.min.js" type="text/javascript" charset="utf-8"></script>


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">
    <a title="${ _('Execute all') }" rel="tooltip" data-placement="bottom" data-bind="click: true, css: {'btn': true}">
      <i class="fa fa-play"></i>
    </a>
    
    <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>
    
    &nbsp;&nbsp;&nbsp;

    <button type="button" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
        data-bind="click: saveNotebook, css: {'btn': true}">
      <i class="fa fa-save"></i>
    </button>
      
    &nbsp;&nbsp;&nbsp;
      
    <button type="button" title="${ _('New') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
        data-bind="click: newNotebook, css: {'btn': true}">
      <i class="fa fa-file-o"></i>
    </button>
      
    <a class="btn" href="${ url('spark:new') }" title="${ _('Brand New') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-file-o"></i>
    </a>
            
    <button type="button" title="${ _('Open') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("New...") }"
        data-bind="click: newNotebook, css: {'btn': true}">
      <i class="fa fa-folder-open-o"></i>
    </button>      
    
    <a class="btn" href="${ url('spark:notebooks') }" title="${ _('Notebooks') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
      <i class="fa fa-terminal"></i>
    </a>
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


<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isAssistVisible(), click: $root.toggleAssist">
  <i class="fa fa-chevron-right"></i>
</a>


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

<div id="assistQuickLook" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Data sample for')} <span class="tableName"></span></h3>
    </div>
    <div class="modal-body" style="min-height: 100px">
      <div class="loader">
        <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
        <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
      </div>
      <div class="sample"></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Ok')}</button>
    </div>
  </div>


<script type="text/html" id="notebook">
  <div class="row-fluid">
    <div class="span2" data-bind="visible: $root.isAssistVisible, css:{'span2': $root.isAssistVisible, 'hidden': !$root.isAssistVisible()}, event: { mouseover: function(){ $('.assist-hover').show(); }, mouseout: function(){ $('.assist-hover').hide(); } }">
      <div class="assist">
        <a title="${_('Toggle Assist')}" class="pull-right pointer assist-hover" style="margin:3px; margin-top:9px; display:none" data-bind="click: $root.toggleAssist">
          <i class="fa fa-chevron-left"></i>
        </a>
        <a title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="top" class="pull-right pointer assist-hover" style="margin:3px; margin-top:9px; display:none" data-bind="click: reloadAssist">
          <i class="fa fa-refresh"></i>
        </a>
        <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF">
          <li class="nav-header">${_('database')}</li>
        </ul>
        <!-- ko if: $root.assistContent && $root.assistContent().mainObjects().length > 0 -->
          <select data-bind="options: $root.assistContent().mainObjects, select2: { width: '100%', placeholder: '${ _("Choose a database...") }', update: $root.assistSelectedMainObject}" class="input-medium" data-placeholder="${_('Choose a database...')}"></select>
          <input type="text" placeholder="${ _('Table name...') }" style="width:90%; margin-top: 20px" data-bind="value: $root.assistContent().filter, valueUpdate: 'afterkeydown'" />
          <div data-bind="visible: Object.keys($root.assistContent().firstLevelObjects()).length == 0">${_('The selected database has no tables.')}</div>
          <ul data-bind="visible: Object.keys($root.assistContent().firstLevelObjects()).length > 0, foreach: $root.assistContent().filteredFirstLevelObjects()" class="unstyled assist-main">
            <li data-bind="event: { mouseover: function(){ $('#assistHover_' + $data).show(); }, mouseout: function(){ $('#assistHover_' + $data).hide(); } }">
              <a href="javascript:void(0)" data-bind="attr: {'id': 'assistHover_' + $data}, click: showTablePreview" style="display: none; position: absolute; right: 10px; margin-left: auto; background-color: #FFF" class="preview-sample"><i class="fa fa-list" title="${'Preview Sample data'}" style="margin-left:5px"></i></a>
              <a href="javascript:void(0)" data-bind="click: loadAssistSecondLevel"><span data-bind="text: $data"></span></a>

              <div data-bind="visible: $root.assistContent().firstLevelObjects()[$data].loaded() && $root.assistContent().firstLevelObjects()[$data].open()">
                <ul data-bind="visible: $root.assistContent().firstLevelObjects()[$data].items().length > 0, foreach: $root.assistContent().firstLevelObjects()[$data].items()" class="unstyled">
                  <li><a data-bind="attr: {'title': secondLevelTitle($data)}" style="padding-left:10px" href="javascript:void(0)"><span data-bind="html: truncateSecondLevel($data)"></span></a></li>
                </ul>
              </div>
            </li>
          </ul>
        <!-- /ko -->

        <div id="navigatorLoader" class="center" data-bind="visible: $root.assistContent().isLoading">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
        </div>

        <div class="center" data-bind="visible: $root.assistContent().hasErrors">
          ${ _('The database list cannot be loaded.') }
        </div>
      </div>
    </div>
    <div data-bind="css:{'span10': $root.isAssistVisible, 'span12 nomargin': ! $root.isAssistVisible()}">
      <div data-bind="css: {'row-fluid': true, 'row-container':true, 'is-editing': $root.isEditing},
        sortable: { template: 'snippet', data: snippets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.card-body').slideUp('fast'); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.text($(event.toElement).text());_title.appendTo(_par);_par.height(80);_par.width(180);return _par;}},
            dragged: function(widget){$('.card-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition)});}}">
      </div>

      <h1 class="empty" data-bind="visible: snippets().length == 0">${ _('Add a snippet to start your new notebook') }</h1>

      <div class="add-snippet pointer">
        <div class="overlay pointer" data-bind="click: function(notebook, e){ if (!($(e.target).is('select'))){ newSnippet(); } }">
          <select data-bind="options: $root.availableSnippets, value: selectedSnippet, optionsText: 'name', optionsValue: 'type'" style="width: 115px">
          </select>
          <i class="fa fa-plus-circle fa-5x" title="${ _('Add a new snippet') }"></i>          
        </div>       
      </div>
      <div class="overlay" style="padding-bottom:70px"></div>
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
          <a href="javascript:void(0)" data-bind="visible: $root.isEditing, click: function(){ remove($parent, $data); window.setTimeout(redrawFixedHeaders, 100);}"><i class="fa fa-times"></i></a>
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
            <textarea data-bind="value: statement_raw, codemirror: { 'id': id(), 'viewportMargin': Infinity, 'lineNumbers': true, 'matchBrackets': true, 'mode': editorMode(), 'enter': execute }">
            </textarea>
            <span data-bind="visible: status() == 'loading'" class="codeMirror-overlaybtn pointer">
              <i class='fa fa-spinner fa-spin fa-2x'></i>
            </span>
            <a title="${ _('CTRL + ENTER') }" data-bind="click: execute, visible: status() != 'running' && status() != 'loading'" class="btn codeMirror-overlaybtn pointer">
              ${ _('Go!') }
            </a>
            <a data-bind="click: cancel, visible: status() == 'running'" class="btn codeMirror-overlaybtn pointer">${ _('Cancel') }</a>
            <div class="progress progress-striped active" data-bind="css: {'progress-neutral': progress() == 0 && result.errors().length == 0, 'progress-warning': progress() > 0 && progress() < 100, 'progress-success': progress() == 100, 'progress-danger': progress() == 0 && result.errors().length > 0}" style="height: 1px">
              <div class="bar" data-bind="style: {'width': (result.errors().length > 0 ? 100 : progress()) + '%'}"></div>
            </div>
            <div class="resize-panel center"><a href="javascript:void(0)"><i class="fa fa-ellipsis-h"></i></a></div>
          </div>
        </div>

        <div style="padding-top: 10px;">
          <button data-bind="visible: result.type() == 'table' && result.hasSomeResults(), click: function() { $data.showGrid(true); }, css: {'active': $data.showGrid}" href="javascript:void(0)" class="btn" title="${ _('Grid') }">
            <i class="fa fa-th"></i>
          </button>
          <div class="btn-group" data-bind="visible: result.type() == 'table' && result.hasSomeResults()">
            <button class="btn" data-bind="css: {'active': $data.showChart}, click: function(){ $data.showChart(true); }">
              <i class="hcha hcha-bar-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART"></i>
              <i class="hcha hcha-line-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART"></i>
              <i class="hcha hcha-pie-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART"></i>
              <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART"></i>
              <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP"></i>
              <i class="hcha hcha-map-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP"></i>
            </button>
            <button class="btn dropdown-toggle" data-bind="visible: result.type() == 'table', css: {'active': $data.showChart}" data-toggle="dropdown">
              <i class="fa fa-caret-down"></i>
            </button>
            <ul class="dropdown-menu">
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.BARCHART}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.BARCHART); }">
                  <i class="hcha hcha-bar-chart"></i> ${_('Bars')}
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.LINECHART}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.LINECHART); }">
                  <i class="hcha hcha-line-chart"></i> ${_('Lines')}
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.PIECHART}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.PIECHART); }">
                  <i class="hcha hcha-pie-chart"></i> ${_('Pie')}
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.SCATTERCHART); }">
                  <i class="fa fa-fw fa-dot-circle-o chart-icon"></i> ${_('Scatter')}
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.MAP}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.MAP); }">
                  <i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.GRADIENTMAP); }">
                  <i class="hcha hcha-map-chart"></i> ${_('Gradient Map')}
                </a>
              </li>
            </ul>
          </div>

          <div class="pull-right">
            <strong class="muted" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()"></strong>
            
            &nbsp;
            
            <a data-bind="visible: status() != 'ready' && status() != 'loading' && result.errors().length == 0, click: function() { $data.showLogs(! $data.showLogs()); window.setTimeout(redrawFixedHeaders, 100); }, css: {'active': $data.showLogs}" href="javascript:void(0)" class="btn" title="${ _('Show Logs') }">
              <i class="fa fa-file-text-o"></i>
            </a>

            &nbsp;
            
            <form method="POST" action="${ url('spark:download') }" class="download-form" style="display: inline">
              ${ csrf_token(request) | n,unicode }
              <input type="hidden" name="notebook" data-bind="value: ko.mapping.toJSON($root.selectedNotebook)"/>
              <input type="hidden" name="snippet" data-bind="value: ko.mapping.toJSON($data)"/>
              <input type="hidden" name="format" class="download-format"/>

              <div class="btn-group" data-bind="visible: status() == 'available' && result.hasSomeResults()">
                <button class="btn dropdown-toggle" data-toggle="dropdown">
                  <i class="fa fa-download"></i>
                  <i class="fa fa-caret-down"></i>
                </button>
                <ul class="dropdown-menu pull-right">
                  <li>
                    <a class="download" href="javascript:void(0)" data-bind="click: function() { $('#snippet_' + $data.id()).find('.download-format').val('csv'); $('#snippet_' + $data.id()).find('.download-form').submit(); }" title="${ _('Download first rows as CSV') }">
                      <i class="fa fa-file-o"></i> ${ _('CSV') } 
                    </a>
                  </li>
                  <li>
                    <a class="download" href="javascript:void(0)" data-bind="click: function() { $('#snippet_' + $data.id()).find('.download-format').val('xls'); $('#snippet_' + $data.id()).find('.download-form').submit(); }" title="${ _('Download first rows as XLS') }">
                      <i class="fa fa-file-excel-o"></i> ${ _('Excel') } 
                    </a>                  
                  </li>
                </ul>            
              </div>
            </form>
            
          </div>
        </div>

        <div data-bind="visible: showLogs, css: resultsKlass" style="margin-top: 5px">
          <pre data-bind="visible: result.logs().length == 0" class="logs">${ _('Loading...') }</pre>
          <pre data-bind="visible: result.logs().length > 0, text: result.logs" class="logs"></pre>
        </div>

        <div data-bind="visible: result.errors().length > 0, css: errorsKlass" style="margin-top: 5px">
          <span data-bind="text: result.errors"></span>
        </div>
        
        <div data-bind="visible: ! result.hasResultset() && status() == 'available', css: resultsKlass">
          ${ _('Success.') }
        </div>
        
        <div data-bind="visible: result.hasResultset() && status() == 'available' && result.data().length == 0 && result.meta().length > 0, css: resultsKlass">
          ${ _('Success but empty results.') }
        </div>

        <div class="row-fluid" data-bind="visible: result.hasSomeResults() && showGrid()" style="max-height: 400px; margin-top: 4px">
          <div data-bind="visible: isLeftPanelVisible, css:{'span2': isLeftPanelVisible, 'hidden': !isLeftPanelVisible()}">
            <ul class="nav nav-list" style="border: none; background-color: #FFF">              
              <li class="nav-header pointer" data-bind="click: toggleLeftPanel" title="${_('Hide columns')}">${_('columns')}</li>
              </a>
            </ul>
            <ul class="unstyled" data-bind="foreach: result.meta">
              <li data-bind="visible: name != ''"><input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" /> <a class="pointer" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }"></a></li>
            </ul>
          </div>
          <div data-bind="css: {'span10': isLeftPanelVisible, 'span12 nomargin': !isLeftPanelVisible()}">
            <div class="toggle-left-panel" data-bind="click: toggleLeftPanel">
              <a title="${_('Show columns')}" class="pointer" data-bind="visible: !isLeftPanelVisible()">
                <i class="fa fa-chevron-right"></i>
              </a>
              <a title="${_('Hide')}" class="pointer" data-bind="visible: isLeftPanelVisible()">
                <i class="fa fa-chevron-left"></i>
              </a>
            </div>
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
            </div>
          </div>
        </div>

        <div class="row-fluid" data-bind="visible: result.meta().length > 0 && showChart()" style="max-height: 400px; margin-top: 4px">
          <div data-bind="visible: isLeftPanelVisible, css:{'span2': isLeftPanelVisible, 'hidden': ! isLeftPanelVisible()}">
            <div class="toggle-left-panel" style="float: right; margin-right: -30px; height: 400px; line-height: 400px; margin-top:0" data-bind="click: toggleLeftPanel">
              <a title="${_('Hide settings')}" class="pointer">
                <i class="fa fa-chevron-left"></i>
              </a>
            </div>
            <div>
              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
                <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP, ko.HUE_CHARTS.TYPES.PIECHART].indexOf(chartType()) == -1" class="nav-header">${_('x-axis')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('region')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('legend')}</li>
              </ul>
              <div data-bind="visible: chartType() != ''">
                <select data-bind="options: (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.PIECHART || chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP) ? result.cleanedMeta : result.cleanedNumericMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', select2: { width: '100%', placeholder: '${ _("Choose a column...") }', update: chartX}" class="input-medium"></select>
              </div>

              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
                <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP, ko.HUE_CHARTS.TYPES.PIECHART].indexOf(chartType()) == -1" class="nav-header">${_('y-axis')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('value')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
                <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="nav-header">${_('value')}</li>
              </ul>

              <div style="overflow-y: scroll; max-height: 220px" data-bind="visible: chartType() != '' && (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.LINECHART)">
                <ul class="unstyled" data-bind="foreach: result.cleanedNumericMeta">
                  <li><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></li>
                </ul>
              </div>
              <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART || chartType() == ko.HUE_CHARTS.TYPES.MAP || chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP || chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <select data-bind="options: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP ? result.cleanedMeta : result.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', select2: { width: '100%', placeholder: '${ _("Choose a column...") }', update: chartYSingle}" class="input-medium"></select>
              </div>

              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.MAP">
                <li class="nav-header">${_('label')}</li>
              </ul>
              <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP">
                <select data-bind="options: result.cleanedMeta, value: chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', select2: { width: '100%', placeholder: '${ _("Choose a column...") }', update: chartMapLabel}" class="input-medium"></select>
              </div>

              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <li class="nav-header">${_('scatter group')}</li>
              </ul>
              <div data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <select data-bind="options: result.cleanedMeta, value: chartScatterGroup, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', select2: { width: '100%', placeholder: '${ _("Choose a column...") }', update: chartScatterGroup}" class="input-medium"></select>
              </div>

              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <li class="nav-header">${_('scatter size')}</li>
              </ul>
              <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <select data-bind="options: result.cleanedMeta, value: chartScatterSize, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_('Choose a column...')}', select2: { width: '100%', placeholder: '${ _("Choose a column...") }', update: chartScatterSize}" class="input-medium"></select>
              </div>

              <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP && chartType() != ko.HUE_CHARTS.TYPES.GRADIENTMAP && chartType() != ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <li class="nav-header">${_('sorting')}</li>
              </ul>
              <div class="btn-group" data-toggle="buttons-radio" data-bind="visible: chartType() != '' && chartType() != ko.HUE_CHARTS.TYPES.MAP && chartType() != ko.HUE_CHARTS.TYPES.GRADIENTMAP && chartType() != ko.HUE_CHARTS.TYPES.SCATTERCHART">
                <a rel="tooltip" data-placement="top" title="${_('No sorting')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'none'}, click: function(){ chartSorting('none'); }"><i class="fa fa-align-left fa-rotate-270"></i></a>
                <a rel="tooltip" data-placement="top" title="${_('Sort ascending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'asc'}, click: function(){ chartSorting('asc'); }"><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
                <a rel="tooltip" data-placement="top" title="${_('Sort descending')}" href="javascript:void(0)" class="btn" data-bind="css: {'active': chartSorting() == 'desc'}, click: function(){ chartSorting('desc'); }"><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
              </div>
            </div>
          </div>
          <div data-bind="css:{'span10 chart-container': isLeftPanelVisible, 'span12 nomargin chart-container': !isLeftPanelVisible()}">

            <div class="toggle-left-panel" style="margin-right: -30px; height: 400px; line-height: 400px; margin-top:0" data-bind="visible: !isLeftPanelVisible(), click: toggleLeftPanel">
              <a title="${_('Show settings')}" class="pointer">
                <i class="fa fa-chevron-right"></i>
              </a>
            </div>

            <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                  transformer: pieChartDataTransformer, maxWidth: 350, parentSelector: '.chart-container' }, visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>

            <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true,
                  transformer: multiSerieDataTransformer, stacked: false, showLegend: true},  stacked: true, showLegend: true, visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>

            <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: multiSerieDataTransformer, showControls: false }, visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>

            <div data-bind="attr:{'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: leafletMapChartDataTransformer, showControls: false, height: 380, visible: chartType() == ko.HUE_CHARTS.TYPES.MAP}" class="chart"></div>

            <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: mapChartDataTransformer, isScale: true, showControls: false, height: 380, maxWidth: 750, parentSelector: '.chart-container', visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}" class="chart"></div>

            <div data-bind="attr:{'id': 'scatterChart_'+id()}, scatterChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: scatterChartDataTransformer, maxWidth: 350 }, visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART" class="chart"></div>
          </div>
        </div>
      </div>

      <div data-bind="visible: type() == 'text'">
        <div data-bind="html: statement_raw, visible: ! $root.isEditing()"></div>
        <div data-bind="attr:{'id': 'editor_'+id()}, html: statement_raw, value: statement_raw, medium: {}, visible: $root.isEditing()"></div>
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

  Number.prototype.toHHMMSS = function () {
    var _s = this;
    var _ms = _s % 1000;
    _s = (_s - _ms) / 1000;
    var _secs = _s % 60;
    _s = (_s - _secs) / 60;
    var _mins = _s % 60;
    var _hrs = (_s - _mins) / 60;

    return (_hrs > 0 ? _hrs + "h, " : "") + (_mins > 0 ? _mins + "m, " : "") + _secs + "." + _ms + "s";
  }

  $.scrollbarWidth = function() {
    var _parent, _child, _width;
    _parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
    _child = _parent.children();
    _width = _child.innerWidth() - _child.height(99).innerWidth();
    _parent.remove();
    return _width;
  };

  ko.bindingHandlers.medium = {
    init: function (element, valueAccessor, allBindings) {
        var editor = new MediumEditor($(element), {
          buttons: ['bold', 'italic', 'underline', 'quote', 'anchor', 'orderedlist', 'unorderedlist', 'pre', 'outdent', 'indent'],
          buttonLabels: 'fontawesome',
          anchorTarget: true
      });
      $(element).on('input', function() {
        allBindings().value($(element).html())
      });
    }
  }

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
            var _found = [];
            if (_from > -1) {
              var _match = _statement.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
              var _to = _statement.length;
              if (_match) {
                _to = _match.index;
              }
              _found = _statement.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
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
                    CodeMirror.catalogTables = "";
                    CodeMirror.possibleTable = false;
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
                  if ((_before.toUpperCase().indexOf("WHERE ") > -1 || _before.toUpperCase().indexOf("ORDER BY ") > -1 || _before.toUpperCase().indexOf("GROUP BY ") > -1) && !CodeMirror.fromDot && _before.toUpperCase().match(/ ON| LIMIT| SORT/) == null) {
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
            allBindingsAccessor().value(editor.getValue());
            if (snippet.status() != 'running' && snippet.status() != 'loading'){
              valueAccessor().enter();
            }
          }
        },
        onKeyEvent: function (cm, e) {
          switch (valueAccessor().mode) {
            case "text/x-hiveql":
              if (e.type == "keyup" && e.keyCode == 190 && !e.shiftKey) {
                hiveImpalaAutocomplete(cm, CodeMirror.hiveQLHint, true);
              }
              break;
            case "text/x-impalaql":
              if (e.type == "keyup" && e.keyCode == 190 && !e.shiftKey) {
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
      editor.setSize("100%", snippet.codemirrorSize());
      var wrapperElement = $(editor.getWrapperElement());

      var _changeTimeout = -1;
      editor.on("change", function () {
        window.clearTimeout(_changeTimeout);
        _changeTimeout = window.setTimeout(function(){
          allBindingsAccessor().value(editor.getValue());
        }, 300);
      });

      editor.on("focus", function () {
        if (editor.getValue() == viewModel.snippetPlaceholders[snippet.type()]) {
          editor.setValue("");
        }
      });

      editor.on("blur", function () {
        if (editor.getValue() == ""){
          editor.setValue(viewModel.snippetPlaceholders[snippet.type()]); 
        }
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        wrapperElement.remove();
      });
    }
  };

  var options = ${ options_json | n,unicode };
  $.extend(options, {
    assistVisible: $.totalStorage("sparkAssistVisible") != null ? $.totalStorage("sparkAssistVisible") : false
  });

  viewModel = new EditorViewModel(${ notebooks_json | n,unicode }, options);
  viewModel.assistContent(assist);
  ko.applyBindings(viewModel);
  viewModel.init();

  $(document).ready(function () {
    // Close the notebook snippets when leaving the page
    window.onbeforeunload = function(e) {
      viewModel.selectedNotebook().close();
    };

    $(".preview-sample").css("right", (10 + $.scrollbarWidth()) + "px");
  });

  viewModel.assistSelectedMainObject.subscribe(function(newVal) {
    viewModel.assistContent().selectedMainObject(newVal);
    loadAssistFirstLevel();
  });

  function loadAssistSecondLevel(first, force) {
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

  function loadAssistFirstLevel(force) {
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
    assist.getData(viewModel.assistContent().selectedMainObject(), force);
  }

  function loadAssistMain(force) {
    assist.options.onDataReceived = function (data) {
      if (data.databases) {
        viewModel.assistContent().mainObjects(data.databases);
        if (force) {
          loadAssistFirstLevel(force);
        }
        else if (viewModel.assistContent().mainObjects().length > 0 && !viewModel.assistContent().selectedMainObject()) {
          viewModel.assistContent().selectedMainObject(viewModel.assistContent().mainObjects()[0]);
          viewModel.assistSelectedMainObject(viewModel.assistContent().selectedMainObject());
          loadAssistFirstLevel();
        }
      }
    }
    assist.options.onError = function (error) {
      viewModel.assistContent().isLoading(false);
    }
    assist.getData(null, force);
  }

  loadAssistMain();

  function reloadAssist() {
    loadAssistMain(true);
  }

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
          includeNavigator: false,
          parentId: snippet.id()
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
      includeNavigator: false,
      parentId: snippet.id()
    });
    $(".dataTables_filter").hide();
    var dataTableEl = $(el).parents(".dataTables_wrapper");

    dataTableEl.bind('mousewheel DOMMouseScroll wheel', function (e) {
      var _e = e.originalEvent,
          _deltaX = _e.wheelDeltaX || -_e.deltaX,
          _deltaY = _e.wheelDeltaY || -_e.deltaY;
      this.scrollTop += -_deltaY / 2;
      this.scrollLeft += -_deltaX / 2;

      if (this.scrollTop == 0){
        $("body")[0].scrollTop += -_deltaY / 3;
        $("html")[0].scrollTop += -_deltaY / 3; // for firefox
      }
      e.preventDefault();
    });

    var _scrollTimeout = -1;
    dataTableEl.on("scroll", function () {
      var _lastScrollPosition = dataTableEl.data("scrollPosition") != null ? dataTableEl.data("scrollPosition") : 0;
      window.clearTimeout(_scrollTimeout);
      _scrollTimeout = window.setTimeout(function () {
        dataTableEl.data("scrollPosition", dataTableEl.scrollTop());
        if (_lastScrollPosition != dataTableEl.scrollTop() && dataTableEl.scrollTop() + dataTableEl.outerHeight() + 20 > dataTableEl[0].scrollHeight && _dt) {
          dataTableEl.animate({opacity: '0.55'}, 200);
          snippet.fetchResult(100, false);
        }
      }, 100);
    });

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


  function pieChartDataTransformer(rawDatum) {
    var _data = [];

    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      var _idxValue = -1;
      var _idxLabel = -1;
      rawDatum.snippet.result.meta().forEach(function (col, idx) {
        if (col.name == rawDatum.snippet.chartX()) {
          _idxLabel = idx;
        }
        if (col.name == rawDatum.snippet.chartYSingle()) {
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

    if (rawDatum.sorting == "asc") {
      _data.sort(function (a, b) {
        return a.value > b.value
      });
    }
    if (rawDatum.sorting == "desc") {
      _data.sort(function (a, b) {
        return b.value > a.value
      });
    }

    return _data;
  }

  function mapChartDataTransformer(rawDatum) {
    var _data = [];
    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      var _idxRegion = -1;
      var _idxValue = -1;
      rawDatum.snippet.result.meta().forEach(function (col, idx) {
        if (col.name == rawDatum.snippet.chartX()) {
          _idxRegion = idx;
        }
        if (col.name == rawDatum.snippet.chartYSingle()) {
          _idxValue = idx;
        }
      });

      $(rawDatum.counts()).each(function (cnt, item) {
        _data.push({
          label: item[_idxRegion],
          value: item[_idxValue],
          obj: item
        });
      });
    }
    
    return _data;
  }

  function leafletMapChartDataTransformer(rawDatum) {
    var _data = [];
    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      var _idxLat = -1;
      var _idxLng = -1;
      var _idxLabel = -1;
      rawDatum.snippet.result.meta().forEach(function (col, idx) {
        if (col.name == rawDatum.snippet.chartX()) {
          _idxLat = idx;
        }
        if (col.name == rawDatum.snippet.chartYSingle()) {
          _idxLng = idx;
        }
        if (col.name == rawDatum.snippet.chartMapLabel()) {
          _idxLabel = idx;
        }
      });
      if (rawDatum.snippet.chartMapLabel() != null) {
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

  function scatterChartDataTransformer(rawDatum) {
    var _datum = [];
    
    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      function addToDatum(col) {
        var _idxX = -1;
        var _idxY = -1;
        var _idxSize = -1;
        var _idxGroup = -1;
        rawDatum.snippet.result.meta().forEach(function (icol, idx) {
          if (icol.name == rawDatum.snippet.chartX()) {
            _idxX = idx;
          }
          if (icol.name == rawDatum.snippet.chartYSingle()) {
            _idxY = idx;
          }
          if (icol.name == rawDatum.snippet.chartScatterSize()) {
            _idxSize = idx;
          }
          if (icol.name == rawDatum.snippet.chartScatterGroup()) {
            _idxGroup = idx;
          }
        });

        if (_idxX > -1 && _idxY > -1) {
          var _data = [];
          $(rawDatum.counts()).each(function (cnt, item) {
            if (_idxGroup == -1 || item[_idxGroup] == col){
              _data.push({
                x: item[_idxX],
                y: item[_idxY],
                shape: 'circle',
                size: _idxSize > -1 ? item[_idxSize] : 100,
                obj: item
              });
            }
          });
          _datum.push({
            key: col,
            values: _data
          });
        }
      }

      if (rawDatum.snippet.chartScatterGroup() != null){
        var _idxGroup = -1;
        rawDatum.snippet.result.meta().forEach(function (icol, idx) {
          if (icol.name == rawDatum.snippet.chartScatterGroup()) {
            _idxGroup = idx;
          }
        });
        if (_idxGroup > -1) {
        $(rawDatum.counts()).each(function (cnt, item) {
          addToDatum(item[_idxGroup]);
        });
        }
      }
      else {
        addToDatum('${ _('Distribution') }');
      }
      
    }
    return _datum;
  }


  function showTablePreview(table) {
    var tableUrl = "/beeswax/api/table/" + viewModel.assistContent().selectedMainObject() + "/" + table;
    $("#assistQuickLook").find(".tableName").text(table);
    $("#assistQuickLook").find(".tableLink").attr("href", "/metastore/table/" + viewModel.assistContent().selectedMainObject() + "/" + table);
    $("#assistQuickLook").find(".sample").empty("");
    $("#assistQuickLook").attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");
    $.ajax({
      url: tableUrl,
      data: {"sample": true},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "html",
      success: function (data) {
        $("#assistQuickLook").find(".loader").hide();
        $("#assistQuickLook").find(".sample").html(data);
      },
      error: function (e) {
        if (e.status == 500) {
          $(document).trigger("error", "${ _('There was a problem loading the table preview.') }");
          $("#assistQuickLook").modal("hide");
        }
      }
    });
    $("#assistQuickLook").modal("show");
  }

  function redrawFixedHeaders() {
      viewModel.notebooks().forEach(function (notebook) {
        notebook.snippets().forEach(function (snippet) {
          var _el = $("#snippet_" + snippet.id()).find(".resultTable");
          _el.jHueTableExtender({
            fixedHeader: true,
            includeNavigator: false,
            parentId: snippet.id()
          });
        });
      });
    }

  $(document).ready(function () {
    resizeAssist();

    var initialResizePosition = 100;

    function getDraggableOptions(minY) {
      return {
        axis: "y",
        start: function(e, ui) {
          initialResizePosition = ui.offset.top;
        },
        drag: function(e, ui) {
          draggableHelper($(this), e, ui);
          $(".jHueTableExtenderClonedContainer").hide();
        },
        stop: function(e, ui) {
          $(".jHueTableExtenderClonedContainer").show();
          draggableHelper($(this), e, ui, true);
          redrawFixedHeaders();
        },
        containment: [0, minY, 4000, minY + 400]
      }
    };

    $(".resize-panel a").each(function(){
      $(this).draggable(getDraggableOptions($(this).parents(".snippet").offset().top + 128));
    });

    function draggableHelper(el, e, ui, setSize) {
      var _snippet = ko.dataFor(el.parents(".snippet")[0]);
      var _cm = $("#snippet_" + _snippet.id()).data("editor");
      var _newSize = _snippet.codemirrorSize() + (ui.offset.top - initialResizePosition);
      _cm.setSize("99%", _newSize);
      if (setSize) {
        _snippet.codemirrorSize(_newSize);
      }
    }

    $(document).on("snippetAdded", function(e, snippet) {
      var _handle = $("#snippet_" + snippet.id()).find(".resize-panel a");
      _handle.draggable(getDraggableOptions(_handle.offset().top));
    });

    $(document).on("toggleAssist", function(){
      $.totalStorage("sparkAssistVisible", viewModel.isAssistVisible());
      resizeAssist();
    });

    $(document).on("toggleLeftPanel", function(e, snippet){
      $("#snippet_" + snippet.id()).find(".chart").trigger("forceUpdate");
      redrawFixedHeaders();
    });

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
      snippet.tempChartOptions = {
        x: snippet.chartX(),
        yS: snippet.chartYSingle(),
        yM: snippet.chartYMulti(),
        label: snippet.chartMapLabel()
      }
    });

    $(document).on("renderData", function (e, options) {
      var _el = $("#snippet_" + options.snippet.id()).find(".resultTable");
      if (options.data.length > 0) {
        window.setTimeout(function () {
          var _dt;
          if (options.initial) {
            options.snippet.result.meta.notifySubscribers();
            $("#snippet_" + options.snippet.id()).find("select").trigger("chosen:updated");
            _dt = createDatatable(_el, options.snippet);
          }
          else {
            _dt = _el.dataTable();
          }
          _dt.fnAddData(options.data);
          var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
          _dtElement.animate({opacity: '1'}, 50);
          _dtElement.scrollTop(_dtElement.data("scrollPosition"));
          redrawFixedHeaders();
          _dtElement.parent().siblings(".toggle-left-panel").height(_dtElement.height());
        }, 100);
      }
      else {
        var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
        _dtElement.animate({opacity: '1'}, 50);
        _dtElement.off("scroll");
      }
      options.snippet.chartX(options.snippet.tempChartOptions.x);
      options.snippet.chartX(options.snippet.tempChartOptions.x);
      options.snippet.chartYSingle(options.snippet.tempChartOptions.yS);
      options.snippet.chartMapLabel(options.snippet.tempChartOptions.label);
      $("#snippet_" + options.snippet.id()).find("select").trigger('chosen:updated');
    });

    $(document).on("renderDataError", function (e, options){
      var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
      _dtElement.animate({opacity: '1'}, 50);
      _dtElement.off("scroll");
    });

    $(document).on("progress", function (e, options) {
      if (options.data == 100) {
        window.setTimeout(function () {
          $("#snippet_" + options.snippet.id()).find(".progress").animate({
            height: "1px"
          }, 100, function () {
            options.snippet.progress(0);
            redrawFixedHeaders();
          });
        }, 2000);
      }
    });

    $(document).on("forceChartDraw", function (e, snippet) {
      window.setTimeout(function () {
        snippet.chartX.notifySubscribers();
      }, 100);
    });

    viewModel.notebooks().forEach(function (notebook) {
      notebook.snippets().forEach(function (snippet) {
        if (snippet.result.data().length > 0) {
          var _el = $("#snippet_" + snippet.id()).find(".resultTable");
          window.setTimeout(function () {
            var _dt = createDatatable(_el, snippet);
            _dt.fnAddData(snippet.result.data());
            var _dtElement = $("#snippet_" + snippet.id()).find(".dataTables_wrapper");
            _dtElement.parent().siblings(".toggle-left-panel").css({
              "height": (_dtElement.height() - 30) + "px",
              "line-height": (_dtElement.height() - 30) + "px"
            });
            $(document).trigger("forceChartDraw", snippet);
          }, 100);
        }
      });
    });

    $(".CodeMirror").each(function () {
      $(this)[0].CodeMirror.refresh();
    });

    var _resizeTimeout = -1;
    $(window).on("resize", function(){
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(resizeAssist, 200);
    });
  });

</script>

${ commonfooter(messages) | n,unicode }
