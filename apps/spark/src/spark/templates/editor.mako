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

<%namespace name="koComponents" file="/ko_components.mako" />

${ commonheader(_('Query'), app_name, user, "68px") | n,unicode }

<script type="text/javascript">
  if (window.location.hash != "") {
    if (window.location.hash.indexOf("notebook") > -1) {
      location.href = "/spark/editor?" + window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
    }
  }
</script>


<link rel="stylesheet" href="${ static('desktop/css/common_dashboard.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/codemirror.css') }">
<link rel="stylesheet" href="${ static('spark/css/spark.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.markercluster.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/nv.d3.min.css') }">
<link rel="stylesheet" href="${ static('desktop/css/nv.d3.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/medium-editor.min.css') }">
<link rel="stylesheet" href="${ static('desktop/css/bootstrap-medium-editor.css') }">


<script src="${ static('desktop/ext/js/codemirror-3.11.js') }"></script>
<script src="${ static('desktop/js/codemirror-pig.js') }"></script>
<script src="${ static('desktop/js/codemirror-hql.js') }"></script>
<script src="${ static('desktop/js/codemirror-python.js') }"></script>
<script src="${ static('desktop/js/codemirror-clike.js') }"></script>

<script src="${ static('desktop/js/codemirror-show-hint.js') }"></script>

<script src="${ static('desktop/js/codemirror-isql-hint.js') }"></script>
<script src="${ static('desktop/js/codemirror-hql-hint.js') }"></script>
<script src="${ static('desktop/js/codemirror-pig-hint.js') }"></script>
<script src="${ static('desktop/js/codemirror-python-hint.js') }"></script>
<script src="${ static('desktop/js/codemirror-clike-hint.js') }"></script>

<script src="${ static('desktop/ext/js/markdown.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-deferred-updates.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.editable.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('spark/js/assist.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('spark/js/spark.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>


<script src="${ static('desktop/js/hue.geo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.colors.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/leaflet/leaflet.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/leaflet/leaflet.markercluster.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topojson.v1.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/world.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/usa.topo.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/js/nv.d3.datamaps.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.legend.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.multiBarWithBrushChart.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.lineWithBrushChart.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingDiscreteBar.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingDiscreteBarChart.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingMultiBar.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingMultiBarChart.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingPie.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.growingPieChart.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.scatter.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.scatterChart.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/js/ko.charts.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }"> type="text/javascript" charset="utf-8"</script>

<script src="${ static('desktop/ext/select2/select2.min.js') }" type="text/javascript" charset="utf-8"></script>

<!--[if IE 9]>
  <script src="${ static('desktop/ext/js/classList.min.js') }" type="text/javascript" charset="utf-8"></script>
<![endif]-->
<script src="${ static('desktop/ext/js/medium-editor.min.js') }" type="text/javascript" charset="utf-8"></script>

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .search-bar {
    top: 58px!important;
  }
  .show-assist {
    top: 110px!important;
  }
% endif
</style>


<div class="search-bar">
  <div class="pull-right" style="padding-right:50px">

    <div class="btn-group">
      <a class="btn dropdown-toggle" data-toggle="dropdown">
        <i class="fa fa-check-square-o"></i>
        <i class="fa fa-caret-down"></i>
      </a>
      <ul class="dropdown-menu">
        <li>
          <a href="javascript:void(0)" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
            <i class="fa fa-play fa-fw"></i> ${ _('Execute all snippets') }
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
            <i class="fa fa-eraser fa-fw"></i> ${ _('Clear all results') }
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: displayCombinedContent">
            <i class="fa fa-file-text-o fa-fw"></i> ${ _('Display all Notebook content') }
          </a>
        </li>
      </ul>
   </div>

   &nbsp;&nbsp;&nbsp;

   <a title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn': true, 'btn-inverse': isEditing}">
     <i class="fa fa-pencil"></i>
   </a>

   <a class="btn pointer" title="${ _('Sessions') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#sessionsDemiModal">
     <i class="fa fa-cloud"></i>
   </a>

   &nbsp;&nbsp;&nbsp;

   <a class="btn" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }"
      data-bind="click: saveNotebook, css: {'btn': true}">
     <i class="fa fa-save"></i>
   </a>

   &nbsp;&nbsp;&nbsp;

   <a class="btn" href="${ url('spark:new') }" title="${ _('New Notebook') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
     <i class="fa fa-file-o"></i>
   </a>

   <a class="btn" href="${ url('spark:notebooks') }" title="${ _('Notebooks') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true}">
     <i class="fa fa-tags"></i>
   </a>
  </div>


  <ul class="nav nav-tabs pull-left">
    <!-- ko foreach: notebooks -->
      <li data-bind="css: { active: $parent.selectedNotebook() === $data }">
        <a href="javascript:void(0)"><span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span></a>
      </li>
    <!-- /ko -->
    <li>
      ## <a href="javascript:void(0)" data-bind="click: newNotebook"><i class="fa fa-plus" title="${ _('Add a new notebook') }"></i></a>
    </li>
  </ul>

  <div class="pull-left" style="padding: 9px">
    <!-- ko foreach: notebooks -->
      <!-- ko if: $root.isEditing() -->
        <span data-bind="editable: description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_('Add a description...')}'}" class="muted"></span>
      <!-- /ko  -->
      <!-- ko ifnot: $root.isEditing() -->
        <span data-bind="text: description" class="muted"></span>
      <!-- /ko  -->
    <!-- /ko -->
  </div>

</div>

<div id="combinedContentModal" class="modal hide" data-backdrop="true" style="width:780px;margin-left:-410px!important">
  <div class="modal-header">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <h3>${_('All Notebook content')}</h3>
  </div>
  <div class="modal-body">
    <pre data-bind="oneClickSelect, text: combinedContent"></pre>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>


<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isAssistVisible() && $root.isAssistAvailable(), click: function() { $root.isAssistVisible(! $root.isAssistVisible()) }">
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

<script type="text/html" id="notebook">
  <div class="row-fluid">
    <assist-panel params="assist: assist, isAssistVisible: $root.isAssistVisible, isAssistAvailable: $root.isAssistAvailable, totalStorageId: 'sparkAssistVisible'"></assist-panel>
    <div data-bind="css:{'span10': $root.isAssistVisible, 'span12 nomargin': ! $root.isAssistVisible()}">
      <div data-bind="css: {'row-fluid row-container sortable-snippets':true, 'is-editing': $root.isEditing},
        sortable: { template: 'snippet', data: snippets, isEnabled: $root.isEditing,
        options: {'handle': '.move-widget', 'opacity': 0.7, 'placeholder': 'row-highlight', 'greedy': true,
            'stop': function(event, ui){$('.snippet-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition); });},
            'helper': function(event){lastWindowScrollPosition = $(window).scrollTop(); $('.snippet-body').slideUp('fast', function(){ $('.sortable-snippets').sortable('refreshPositions') }); var _par = $('<div>');_par.addClass('card card-widget');var _title = $('<h2>');_title.addClass('card-heading simple');_title.html($(event.toElement).parents('h2').find('img').outerHTML());_title.appendTo(_par);_par.height(40);_par.width(120);return _par;}},
            dragged: function(widget){$('.snippet-body').slideDown('fast', function(){$(window).scrollTop(lastWindowScrollPosition); });}}">
      </div>

      <h1 class="empty" data-bind="visible: snippets().length == 0">${ _('Add a snippet to start your new notebook') }</h1>

      <div class="add-snippet pointer" data-bind="click: function(notebook, e){ if (!($(e.target).is('select'))){ newSnippet(); } }">
        <div class="overlay pointer">
          <select data-bind="options: $root.availableSnippets, value: selectedSnippet, optionsText: 'name', optionsValue: 'type'" style="width: 115px">
          </select>
          <i class="fa fa-plus-circle fa-5x" title="${ _('Add a new snippet') }"></i>
        </div>
      </div>
      <div class="overlay" style="padding-bottom:70px"></div>
    </div>
  </div>

</script>

<script type="text/html" id="snippetIcon">

  <!-- ko if: type() == 'text' -->
  <i class="fa fa-header snippet-icon"></i><sup style="color: #338bb8; margin-left: -2px">${ _('Text') }</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'hive' -->
  <img src="${ static('beeswax/art/icon_beeswax_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">hive</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'jar' -->
  <i class="fa fa-file-archive-o snippet-icon"></i><sup style="color: #338bb8; margin-left: -2px">jar</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'py' -->
  <i class="fa fa-file-code-o snippet-icon"></i><sup style="color: #338bb8; margin-left: -2px">python</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'impala' -->
  <img src="${ static('impala/art/icon_impala_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">impala</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'scala' -->
  <img src="${ static('spark/art/icon_spark_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">scala</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'python' -->
  <img src="${ static('spark/art/icon_spark_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">python</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'sql' -->
  <img src="${ static('spark/art/icon_spark_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">sql</sup>
  <!-- /ko -->

  <!-- ko if: type() == 'pig' -->
  <img src="${ static('pig/art/icon_pig_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">pig</sup>
  <!-- /ko -->

</script>


<script type="text/html" id="snippet">
  <div class="snippet-container row-fluid">
    <div data-bind="css: klass, attr: {'id': 'snippet_' + id()}">

      <h2 class="card-heading simple" data-bind="visible: $root.isEditing() || (! $root.isEditing() && type() != 'text')">

        <span data-bind="visible: $root.isEditing">
          <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
          <a href="javascript:void(0)" data-bind="click: compress, visible: size() > 1"><i class="fa fa-step-backward"></i></a>
          <a href="javascript:void(0)" data-bind="click: expand, visible: size() < 12"><i class="fa fa-step-forward"></i></a>
          &nbsp;
        </span>
        <div class="dropdown inline widget-type">
          <!-- ko if: $root.isEditing() -->
          <a class="dropdown-toggle no-underline" data-toggle="dropdown" href="javascript:void(0)">
            <span data-bind="template: { name: 'snippetIcon', data: $data }"></span>
            <b class="caret" data-bind="visible: $root.isEditing()"></b>
          </a>
          <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
            <li><a class="pointer" data-bind="click: function(){ $parent.type($data.type()); }, text: name"></a></li>
          </ul>
          <!-- /ko -->
          <!-- ko ifnot: $root.isEditing() -->
          <span data-bind="template: { name: 'snippetIcon', data: $data }"></span>
          <!-- /ko -->
        </div>

        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>
        <div class="snippet-actions inline pull-right">
          <a href="javascript:void(0)" data-bind="click: function(){ codeVisible(! codeVisible()) }"><i class="fa" data-bind="css: {'fa-compress' : codeVisible, 'fa-expand' : ! codeVisible() }"></i></a>
          <a href="javascript:void(0)" data-bind="click: function(){ settingsVisible(! settingsVisible()) }, visible: Object.keys(ko.mapping.toJS(properties)).length > 0"><i class="fa fa-cog"></i></a>
          <a href="javascript:void(0)" data-bind="click: function(){ remove($parent, $data); window.setTimeout(redrawFixedHeaders, 100);}"><i class="fa fa-times"></i></a>
        </div>
      </h2>

      <div>
        <div style="float: left; width: 50%">
          <div class="snippet-body" style="position: relative; z-index: 90;">
            <!-- ko template: { if: ['text', 'jar', 'py'].indexOf(type()) == -1, name: 'code-editor-snippet-body' } --><!-- /ko -->
            <!-- ko template: { if: type() == 'text', name: 'text-snippet-body' } --><!-- /ko -->
            <!-- ko template: { if: type() == 'jar' || type() == 'py', name: 'executable-snippet-body' } --><!-- /ko -->
          </div>
        </div>

        <div style="float: left; width: 50%">
          <!-- ko template: 'snippet-settings' --><!-- /ko -->
        </div>

        <div class="clearfix"></div>
      </div>

      <div data-bind="visible: showLogs, css: resultsKlass" style="margin-top: 5px">
        <pre data-bind="visible: result.logs().length == 0" class="logs logs-bigger">${ _('No logs available at this moment.') }</pre>
        <pre data-bind="visible: result.logs().length > 0, text: result.logs" class="logs logs-bigger"></pre>
      </div>

      <div data-bind="visible: result.errors().length > 0, css: errorsKlass" style="margin-top: 5px">
        <span data-bind="text: result.errors"></span>
      </div>

      <div data-bind="visible: ! result.hasResultset() && status() == 'available', css: resultsKlass">
        ${ _('Success.') }
      </div>

      <div data-bind="visible: result.hasResultset() && status() == 'available' && result.data().length == 0 && result.fetchedOnce(), css: resultsKlass">
        ${ _('Success but empty results.') }
      </div>

      <div data-bind="visible: status() == 'available' && ! result.fetchedOnce(), css: resultsKlass">
        ${ _('Loading...') }
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-settings">
  <div class="snippet-settings" data-bind="slideVisible: settingsVisible" style="position: relative; z-index: 100;">
    <div class="snippet-settings-header">
      <h4><i class="fa fa-cog"></i> Settings</h4>
    </div>
    <div class="snippet-settings-body">
      <form class="form-horizontal">
        <!-- ko if: typeof properties.driver_cores != 'undefined' -->
        <div class="control-group" style="float: left;">
          <label class="control-label">${_('Driver Cores')}</label>
          <div class="controls">
            <input type="text" class="input-small" data-bind="numericTextInput: { value: properties.driver_cores, precision: 1, allowEmpty: true }, valueUpdate:'afterkeydown'" title="${ _('Number of cores used by the driver, only in cluster mode (Default: 1)') }"/>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko if: typeof properties.executor_cores != 'undefined' -->
        <div class="control-group" style="float: left;">
          <label class="control-label">${_('Executor Cores')}</label>
          <div class="controls">
            <input type="text" class="input-small" data-bind="numericTextInput: { value: properties.executor_cores, precision: 1, allowEmpty: true }, valueUpdate:'afterkeydown'" title="${ _('Number of cores per executor (Default: 1)') }"/>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko if: typeof properties.num_executors != 'undefined' -->
        <div class="control-group" style="float: left;">
          <label class="control-label">${_('Executors')}</label>
          <div class="controls">
            <input type="text" class="input-small" data-bind="numericTextInput: { value: properties.num_executors, precision: 1, allowEmpty: true}, valueUpdate:'afterkeydown'" title="${ _('Number of executors to launch (Default: 2)') }"/>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko if: typeof properties.queue != 'undefined' -->
        <div class="control-group" style="float: left;">
          <label class="control-label">${_('Queue')}</label>
          <div class="controls">
            <input type="text" class="input-small" data-bind="textInput: properties.queue, valueUpdate:'afterkeydown'" title="${ _('The YARN queue to submit to (Default: default)') }"/>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko template: { if: typeof properties.archives != 'undefined', name: 'settings-list-input', data: { values: properties.archives, placeholder: '${ _('e.g. archive.dat') }', label: '${_('Archives')}', addLabel: '${_('Archive')}' } }--><!-- /ko -->
        <!-- ko template: { if: typeof properties.files != 'undefined', name: 'settings-list-input', data: { values: properties.files, placeholder: '${ _('e.g. file.dat') }', label: '${_('Files')}', addLabel: '${_('File')}' } }--><!-- /ko -->
        <!-- ko template: { if: typeof properties.settings != 'undefined', name: 'settings-list-input', data: { values: properties.settings, placeholder: '${ _('e.g. foo') }', label: '${_('Settings')}', addLabel: '${_('Setting')}' } }--><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="settings-list-input">
  <div class="control-group" style="float: left;">
    <label class="control-label" data-bind="text: label"></label>
    <div class="controls">
      <ul data-bind="sortable: values, visible: values().length" class="unstyled">
        <li style="margin-bottom: 4px">
          <div class="input-append">
            <input type="text" data-bind="textInput: value, valueUpdate:'afterkeydown', attr: { placeholder: $parent.placeholder }"/>
            <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
          </div>
          <a href="#" data-bind="click: function(){ $parent.values.remove(this); }">
            <i class="fa fa-minus"></i>
          </a>
        </li>
      </ul>
      <div style="min-width: 280px; margin-top: 5px;">
        <a class="pointer" style="min-width: 280px;" data-bind="click: function(){ values.push({ value: ko.observable('') }) }">
          <i class="fa fa-plus"></i> <!-- ko text: addLabel --><!-- /ko -->
        </a>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="code-editor-snippet-body">
  <div class="row-fluid">
    <div data-bind="css: editorKlass, verticalSlide: codeVisible">
      <div data-bind="foreach: variables">
        <div>
          <span data-bind="text: name"></span>
          <input type="text" data-bind="value: value" />
        </div>
      </div>
      <textarea data-bind="value: statement_raw, codemirror: { 'id': id(), 'viewportMargin': Infinity, 'lineNumbers': true, 'indentUnit': 0, 'matchBrackets': true, 'mode': editorMode(), 'enter': execute }"></textarea>
    </div>
  </div>

  <!-- ko template: 'snippet-footer-actions' --><!-- /ko -->
  <!-- ko template: 'snippet-results' --><!-- /ko -->
</script>

<script type="text/html" id="snippet-results">
  <!-- ko if: result.hasSomeResults() && result.type() != 'table' -->
  <div class="row-fluid" style="max-height: 400px; margin: 10px 0;">
    <pre data-bind="text: result.data()[0][1]"></pre>
  </div>
  <!-- /ko -->

  <div class="row-fluid" data-bind="visible: result.hasSomeResults() && result.type() == 'table' && showGrid()" style="max-height: 400px; margin-top: 4px">
    <div data-bind="visible: isLeftPanelVisible, css:{'span2 left-panel': isLeftPanelVisible, 'hidden': ! isLeftPanelVisible()}">
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header pointer" data-bind="click: toggleLeftPanel" title="${_('Hide columns')}">${_('columns')}</li>
        </a>
      </ul>
      <ul class="unstyled" data-bind="foreach: result.meta">
        <li data-bind="visible: name != ''">
          <input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" />
          <a class="pointer" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }"></a>
        </li>
      </ul>
    </div>
    <div data-bind="css: {'span10': isLeftPanelVisible, 'span12 nomargin': !isLeftPanelVisible()}">
      <div data-bind="attr: { 'id': 'toggleLeftPanelGrid' + id()}, event: { mouseover: function(){ $('#toggleLeftPanelGrid' + id()).addClass('hoverable'); }, mouseout: function(){ $('#toggleLeftPanelGrid' + id()).removeClass('hoverable'); } }, click: toggleLeftPanel" class="toggle-left-panel">
        <a title="${_('Show columns')}" class="pointer" data-bind="visible: !isLeftPanelVisible()">
          <i class="fa fa-chevron-right"></i>
        </a>
        <a title="${_('Hide')}" class="pointer" data-bind="visible: isLeftPanelVisible()">
          <i class="fa fa-chevron-left"></i>
        </a>
      </div>
      <div data-bind="css: resultsKlass, event: { mouseover: function(){ $('#toggleLeftPanelGrid' + id()).addClass('hoverable'); }, mouseout: function(){ $('#toggleLeftPanelGrid' + id()).removeClass('hoverable'); } }">
        <table class="table table-condensed resultTable" data-tablescroller-fixed-height="360" data-tablescroller-enforce-height="true">
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

  <div class="row-fluid" data-bind="visible: status() != 'ready' && showChart()" style="max-height: 400px; margin-top: 4px">
    <div data-bind="visible: isLeftPanelVisible, css:{'span2 left-panel': isLeftPanelVisible, 'hidden': ! isLeftPanelVisible()}">
      <div style="float: right; margin-right: -30px; margin-top:0" data-bind="attr: { 'class': 'toggle-left-panel toggleLeftPanelChart' + id()}, event: { mouseover: function(){ $('.toggleLeftPanelChart' + id()).addClass('hoverable'); }, mouseout: function(){ $('.toggleLeftPanelChart' + id()).removeClass('hoverable'); } }, click: toggleLeftPanel">
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
    <div data-bind="css:{'span10 chart-container': isLeftPanelVisible, 'span12 nomargin chart-container': !isLeftPanelVisible()}, event: { mouseover: function(){ $('.toggleLeftPanelChart' + id()).addClass('hoverable'); }, mouseout: function(){ $('.toggleLeftPanelChart' + id()).removeClass('hoverable'); } }">

      <div style="margin-right: -30px; margin-top:0" data-bind="visible: !isLeftPanelVisible(), click: toggleLeftPanel, attr: { 'class': 'toggle-left-panel toggleLeftPanelChart' + id()}">
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
                  transformer: leafletMapChartDataTransformer, showControls: false, height: 380, visible: chartType() == ko.HUE_CHARTS.TYPES.MAP, forceRedraw: true}" class="chart"></div>

      <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: mapChartDataTransformer, isScale: true, showControls: false, height: 380, maxWidth: 750, parentSelector: '.chart-container', visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}" class="chart"></div>

      <div data-bind="attr:{'id': 'scatterChart_'+id()}, scatterChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                  transformer: scatterChartDataTransformer, maxWidth: 350 }, visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART" class="chart"></div>
    </div>
  </div>
</script>

<script type="text/html" id="text-snippet-body">
  <div data-bind="attr:{'id': 'editor_'+id()}, html: statement_raw, value: statement_raw, medium: {}" class="text-snippet"></div>
</script>

<script type="text/html" id="executable-snippet-body">
  <div data-bind="verticalSlide: codeVisible" style="padding:10px;">
    <form class="form-horizontal">
      <!-- ko if: type() == 'jar' -->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties.app_jar, valueUpdate:'afterkeydown', filechooser: properties.app_jar" placeholder="${ _('Path to application jar, e.g. hdfs://localhost:8020/user/hue/oozie-examples.jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Class')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties.class" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'py'-->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties.py_file, valueUpdate:'afterkeydown', filechooser: properties.py_file" placeholder="${ _('Path to python file, e.g. script.py') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko template: { if: typeof properties.arguments != 'undefined', name: 'settings-list-input', data: { values: properties.arguments, placeholder: '${ _('e.g. -foo=bar') }', label: '${_('Arguments')}', addLabel: '${_('Argument')}' } }--><!-- /ko -->
    </form>
  </div>

  <!-- ko template: 'snippet-footer-actions' --><!-- /ko -->
</script>

<script type="text/html" id="snippet-footer-actions">
  <div class="progress progress-striped active" data-bind="css: { 'progress-warning': progress() > 0 && progress() < 100, 'progress-success': progress() == 100, 'progress-danger': progress() == 0 && result.errors().length > 0}" style="height: 1px; background-color: #FFF; width: 100%">
    <div class="bar" data-bind="style: {'width': (result.errors().length > 0 ? 100 : progress()) + '%'}"></div>
  </div>

  <div class="snippet-footer-actions-bar">
    <a data-bind="visible: status() == 'loading'" class="btn btn-primary spark-btn" style="cursor: default;" title="${ _('Creating session') }">
      <i class="fa fa-spinner fa-spin"></i>
    </a>
    <a title="${ _('CTRL + ENTER') }" data-bind="click: execute, visible: status() != 'running' && status() != 'loading'" class="snippet-actions run-button btn btn-primary disable-feedback spark-btn pointer">
      <i class="fa fa-play"></i>
    </a>
    <a title="${ _('Cancel') }" data-bind="click: cancel, visible: status() == 'running'" class="btn btn-danger disable-feedback spark-btn pointer">
      <i class="fa fa-stop"></i>
    </a>
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
      <span data-bind="template: { name: 'snippet-log', data: $data }"></span>

      &nbsp;

      <form method="POST" action="${ url('spark:download') }" class="download-form" style="display: inline">
        ${ csrf_token(request) | n,unicode }
        <input type="hidden" name="notebook"/>
        <input type="hidden" name="snippet"/>
        <input type="hidden" name="format" class="download-format"/>

        <div class="btn-group" data-bind="visible: status() == 'available' && result.hasSomeResults() && result.type() == 'table'">
          <a class="btn dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-download"></i>
            <i class="fa fa-caret-down"></i>
          </a>
          <ul class="dropdown-menu pull-right">
            <li>
              <a class="download" href="javascript:void(0)" data-bind="click: function() { downloadResult($data, 'csv'); }" title="${ _('Download first rows as CSV') }">
                <i class="fa fa-file-o"></i> ${ _('CSV') }
              </a>
            </li>
            <li>
              <a class="download" href="javascript:void(0)" data-bind="click: function() { downloadResult($data, 'xls'); }" title="${ _('Download first rows as XLS') }">
                <i class="fa fa-file-excel-o"></i> ${ _('Excel') }
              </a>
            </li>
          </ul>
        </div>
      </form>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-log">
  <strong class="muted" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()"></strong>

  &nbsp;

  <a data-bind="visible: status() != 'ready' && status() != 'loading' && result.errors().length == 0, click: function() { $data.showLogs(! $data.showLogs()); window.setTimeout(redrawFixedHeaders, 100); }, css: {'active': $data.showLogs}" href="javascript:void(0)" class="btn" title="${ _('Show Logs') }">
    <i class="fa fa-file-text-o"></i>
  </a>
</script>


<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
      <div id="filechooser">
      </div>
  </div>
  <div class="modal-footer">
  </div>
</div>


<div id="sessionsDemiModal" class="demi-modal fade" data-backdrop="false">
  <a href="javascript: void(0)" data-dismiss="modal" class="pull-right" style="margin: 10px"><i class="fa fa-times"></i></a>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="span12">
        <!-- ko with: $root.selectedNotebook() -->
        <form class="form-horizontal">
          <fieldset>
            <legend><i class="fa fa-cloud"></i> ${ _('Sessions') }</legend>
            <!-- ko foreach: sessions -->
            <!-- ko with: $data.properties -->
            <h4 data-bind="text: $root.getSnippetName($parent.type())" style="clear:left;"></h4>
            <!-- ko if: typeof executor_cores !== 'undefined' -->
            <div class="control-group" style="float: left;">
              <label class="control-label">${_('Executor Cores')}</label>
              <div class="controls">
                <input class="input-small" type="text" data-bind="numericTextInput: { value: executor_cores, precision: 0 }" />
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: typeof executor_memory !== 'undefined' -->
            <div class="control-group" style="float: left;">
              <label class="control-label">${_('Executor Memory')}</label>
              <div class="controls">
                <jvm-memory-input params="value: executor_memory" />
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: typeof executor_count !== 'undefined' -->
            <div class="control-group" style="float: left;">
              <label class="control-label">${_('Executor Count')}</label>
              <div class="controls">
                <input class="input-small" type="text" data-bind="numericTextInput: { value: executor_count, precision: 0 }" />
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: typeof driver_cores !== 'undefined' -->
            <div class="control-group cl" style="float: left; clear: left;">
              <label class="control-label">${_('Driver Cores')}</label>
              <div class="controls">
                <input class="input-small" type="text" data-bind="numericTextInput: { value: driver_cores, precision: 0 }" />
              </div>
            </div>
            <!-- /ko -->
            <!-- ko if: typeof driver_memory !== 'undefined' -->
            <div class="control-group" style="float: left;">
              <label class="control-label">${_('Driver Memory')}</label>
              <div class="controls">
                <jvm-memory-input params="value: driver_memory" />
              </div>
            </div>
            <!-- /ko -->
            <a style="float: right;" class="btn pointer" title="${ _('Restart Session') }" data-dismiss="modal" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().restartSession($parent) }">
              <i class="fa fa-refresh"></i> ${ _('Session') }
            </a>
            <!-- /ko -->
            <!-- /ko -->
            </br>
          </fieldset>
        </form>
        <!-- /ko -->
      </div>
    </div>

  </div>
  <div><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>

${ koComponents.jvmMemoryInput() }
${ koComponents.assistPanel() }

<script type="text/javascript" charset="utf-8">

  var assist = new Assist({
    app: "beeswax",
    user: "${user}",
    failsSilentlyOn: [500], // error codes from beeswax/views.py - autocomplete
    baseURL: "${ autocomplete_base_url | n,unicode }"
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

  jQuery.fn.outerHTML = function(s) {
    return (s)
    ? this.before(s).remove()
    : jQuery("<p>").append(this.eq(0).clone()).html();
  }

  ko.bindingHandlers.medium = {
    init: function (element, valueAccessor, allBindings) {
        var editor = new MediumEditor($(element), {
          buttons: ['header1', 'header2', 'bold', 'italic', 'underline', 'quote', 'anchor', 'orderedlist', 'unorderedlist', 'pre', 'outdent', 'indent'],
          buttonLabels: 'fontawesome',
          anchorTarget: true,
          anchorInputPlaceholder: '${ _("Paste or type a link") }',
          anchorInputCheckboxLabel: '${ _("Open in new window") }',
          firstHeader: 'h2',
          secondHeader: 'h3'
      });
      $(element).on('blur', function() {
        allBindings().value($(element).html())
      });
    }
  }

  var activeCodemirrorEditor = null;

  huePubSub.subscribe('assist.dblClickItem', function addToActiveCodemirror(text) {
    if (activeCodemirrorEditor != null){
      activeCodemirrorEditor.replaceSelection(text);
      activeCodemirrorEditor.setSelection(activeCodemirrorEditor.getCursor());
      activeCodemirrorEditor.focus();
    }
  });

  ko.bindingHandlers.verticalSlide = {
    init: function(element, valueAccessor) {
      if (ko.utils.unwrapObservable(valueAccessor())) {
        $(element).show();
      } else {
        $(element).hide();
      }
    },
    update: function(element, valueAccessor) {
      if (ko.utils.unwrapObservable(valueAccessor())) {
        $(element).slideDown('fast');
      } else {
        $(element).slideUp('fast');
      }
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
                assist.getData(assist.selectedMainObject() + "/" + _foundTable);
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

            assist.getData(assist.selectedMainObject() + "/" + _table);

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
          assist.getData(assist.selectedMainObject());
        }
      }

      var options = $.extend(valueAccessor(), {
        lineNumbers: false,
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
      var wrapperElement = $(editor.getWrapperElement());

      var _changeTimeout = -1;
      editor.on("change", function () {
        window.clearTimeout(_changeTimeout);
        _changeTimeout = window.setTimeout(function(){
          allBindingsAccessor().value(editor.getValue());
        }, 300);
      });

      editor.on("focus", function () {
        activeCodemirrorEditor = editor;
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

  viewModel = new EditorViewModel(${ notebooks_json | n,unicode }, options);
  ko.applyBindings(viewModel);
  viewModel.init();

  $(document).ready(function () {
    // Close the notebook snippets when leaving the page
    window.onbeforeunload = function(e) {
      viewModel.selectedNotebook().close();
    };

    $(".preview-sample").css("right", (10 + $.scrollbarWidth()) + "px");

    $(window).bind("keydown", "ctrl+s alt+s meta+s", function(e){
      e.preventDefault();
      viewModel.saveNotebook();
      return false;
    });
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
          minHeight: Math.max($(window).height() - 400, 300),
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
      minHeight: Math.max($(window).height() - 400, 300),
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
          ui.helper.first().removeAttr("style");
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
      if (_handle.length > 0){
        _handle.draggable(getDraggableOptions(_handle.offset().top));
      }
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

    function resizeToggleLeftPanel(snippet) {
      var _dtElement;
      if (snippet.showGrid()){
        _dtElement = $("#snippet_" + snippet.id()).find(".dataTables_wrapper");
      }
      else {
        _dtElement = $("#snippet_" + snippet.id()).find(".chart:visible");
      }
      _dtElement.parents(".snippet-body").find(".toggle-left-panel").css({
        "height": (_dtElement.height() - 30) + "px",
        "line-height": (_dtElement.height() - 30) + "px"
      });
    }

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
          resizeToggleLeftPanel(options.snippet);
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

    $(document).on("gridShown", function (e, snippet) {
      window.setTimeout(function () {
        resizeToggleLeftPanel(snippet);
      }, 50);
    });

    $(document).on("chartShown", function (e, snippet) {
      window.setTimeout(function () {
        resizeToggleLeftPanel(snippet);
      }, 50);
    });

    $(document).on("forceChartDraw", function (e, snippet) {
      window.setTimeout(function () {
        snippet.chartX.notifySubscribers();
        snippet.chartX.valueHasMutated();
      }, 100);
    });

    $(document).on("refreshCodeMirror", function (e, snippet) {
      window.setTimeout(function () {
        $("#snippet_" + snippet.id()).find(".CodeMirror").each(function() {
          $(this)[0].CodeMirror.refresh();
        });
      }, 100);
    });

    $(document).on("puma", function (e, snippet) {
      forceChartDraws();
    });

    function forceChartDraws() {
      viewModel.notebooks().forEach(function (notebook) {
        notebook.snippets().forEach(function (snippet) {
          if (snippet.result.data().length > 0) {
            var _elCheckerInterval = -1;
            _elCheckerInterval = window.setInterval(function () {
              var _el = $("#snippet_" + snippet.id()).find(".resultTable");
              if ($("#snippet_" + snippet.id()).find(".resultTable").length > 0) {
                try {
                  var _dt = createDatatable(_el, snippet);
                  _dt.fnClearTable();
                  _dt.fnAddData(snippet.result.data());
                  resizeToggleLeftPanel(snippet);
                  $(document).trigger("forceChartDraw", snippet);
                  window.clearInterval(_elCheckerInterval);
                }
                catch (e) {
                }
              }
            }, 200)
          }
        });
      });
    }

    forceChartDraws();

    $(".CodeMirror").each(function () {
      $(this)[0].CodeMirror.refresh();
    });

    var _resizeTimeout = -1;
    $(window).on("resize", function(){
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(function(){
        forceChartDraws();
      }, 200);
    });
  });


  function downloadResult(snippet, format) {
    $('#snippet_' + snippet.id()).find('.download-format').val(format);
    $('#snippet_' + snippet.id()).find('input[name=\'notebook\']').val(ko.mapping.toJSON(viewModel.selectedNotebook().getContext()));
    $('#snippet_' + snippet.id()).find('input[name=\'snippet\']').val(ko.mapping.toJSON(snippet.getContext()));
    $('#snippet_' + snippet.id()).find('.download-form').submit();
  }

</script>

${ commonfooter(messages) | n,unicode }
