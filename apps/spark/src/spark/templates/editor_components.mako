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
from desktop import conf
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

<%def name="includes()">
<link rel="stylesheet" href="${ static('desktop/css/common_dashboard.css') }">
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

<script src="${ static('desktop/js/ace/ace.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>
<script src="${ static('spark/js/ace.autocomplete.js') }" type="text/javascript" charset="utf-8"></script>
</%def>


<%def name="commonHTML()">

<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .search-bar {
    top: 58px!important;
  }
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 100px!important;
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


<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible(), click: function() { $root.isLeftPanelVisible(true) }">
  <i class="fa fa-chevron-right"></i>
</a>


<div class="main-content">
  <div class="vertical-full container-fluid">
    <div class="vertical-full tab-content" data-bind="foreach: notebooks">
      <div class="vertical-full tab-pane row-fluid panel-container" data-bind="css: { active: $parent.selectedNotebook() === $data }, template: { name: 'notebook'}">
      </div>
    </div>
  </div>
</div>

<script type="text/html" id="notebook">
  <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible()">
    <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
      <i class="fa fa-chevron-left"></i>
    </a>
    <div class="assist" data-bind="component: { name: 'assist-panel', params: { assist: assist, appName: 'spark' }}"></div>
  </div>
  <div class="resizer" data-bind="visible: $root.isLeftPanelVisible(), splitDraggable : { appName: 'spark', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
  <div class="right-panel" data-bind="event: { scroll: function(){ $(document).trigger('hideAutocomplete'); } }">
    <div>
      <div class="row-fluid row-container sortable-snippets" data-bind="css: {'is-editing': $root.isEditing},
        sortable: {
          template: 'snippet',
          data: snippets,
          isEnabled: true,
          options: {
            'handle': '.move-widget',
            'axis' : 'y',
            'opacity': 0.8,
            'placeholder': 'snippet-move-placeholder',
            'greedy': true,
            'stop': function(event, ui) {
              $('.snippet-body').slideDown('fast', function () { $(window).scrollTop(lastWindowScrollPosition); });
            },
            'helper': function(event) {
              lastWindowScrollPosition = $(window).scrollTop();
              $('.snippet-body').slideUp('fast', function () {
                $('.sortable-snippets').sortable('refreshPositions')
              });
              var $element = $(event.target);
              var _par = $('<div>')
                .addClass('card-widget snippet-move-helper')
                .width($element.parents('.snippet').width());
              $('<h2>')
                .addClass('card-heading')
                .html($element.parents('h2').html())
                .appendTo(_par)
                .find('.hover-actions')
                .removeClass('hover-actions');
              _par.css('height', '100px');
              return _par;
            }
          },
          dragged: function (widget) {
            $('.snippet-body').slideDown('fast', function () { $(window).scrollTop(lastWindowScrollPosition); });
          }
        }">
      </div>
      %if hasattr(caller, "addSnippetHTML"):
        ${caller.addSnippetHTML()}
      %endif
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

  <!-- ko if: type() == 'r' -->
  <img src="${ static('spark/art/icon_spark_48.png') }" class="snippet-icon"><sup style="color: #338bb8; margin-left: -2px">R</sup>
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
  <div class="snippet-container reveals-actions row-fluid">
    <div data-bind="css: klass, attr: {'id': 'snippet_' + id()}">

      <h2 class="card-heading simple">

        <div class="dropdown inline widget-type" data-bind="visible: type() != 'text' || $root.isEditing()">
          <a class="dropdown-toggle no-underline" data-toggle="dropdown" href="javascript:void(0)">
            <span data-bind="template: { name: 'snippetIcon', data: $data }"></span>
            <span class="hover-actions-no-transition">
              <b class="caret"></b>
            </span>
          </a>
          <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
            <li><a class="pointer" data-bind="click: function(){ $parent.type($data.type()); }, text: name"></a></li>
          </ul>
        </div>

        <span data-bind="visible: type() == 'text'">&nbsp;</span>

        <span data-bind="editable: name, editableOptions: {enabled: $root.isEditing(), placement: 'right'}"></span>

        <div class="hover-actions inline pull-right" style="font-size: 15px;">
          <a href="javascript:void(0)" class="move-widget"><i class="fa fa-arrows"></i></a>
          <a href="javascript:void(0)" data-bind="click: function(){ codeVisible(! codeVisible()) }, visible: type() != 'text'"><i class="fa" data-bind="css: {'fa-compress' : codeVisible, 'fa-expand' : ! codeVisible() }"></i></a>
          <a href="javascript:void(0)" data-bind="click: function(){ settingsVisible(! settingsVisible()) }, visible: hasProperties, css: { 'blue' : settingsVisible }"><i class="fa fa-cog"></i></a>
          <a href="javascript:void(0)" data-bind="click: function(){ $root.removeSnippet($parent, $data); }"><i class="fa fa-times"></i></a>
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
        <pre data-bind="visible: result.logs().length > 0, text: result.logs, logScroller: result.logs" class="logs logs-bigger"></pre>
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

<script type="text/html" id="property">
  <div class="reveals-actions" data-bind="css: { 'spark-property' : typeof inline === 'undefined' || inline, 'control-group' : typeof inline !== 'undefined' && ! inline }">
    <label class="control-label" data-bind="text: label, style: { 'width' : typeof inline === 'undefined' || inline ? '120px' : '' }"></label>
    <div class="controls" style="margin-right:10px;" data-bind="style: { 'margin-left' : typeof inline === 'undefined' || inline ? '140px' : '' }">
      <!-- ko template: { name: 'property-' + type } --><!-- /ko -->
    </div>
    <!-- ko ifnot: typeof remove === "undefined" -->
    <div class="hover-actions spark-property-remove">
      <a href="javascript:void(0)" data-bind="click: remove" title="${ _('Remove') }">
        <i class="fa fa-times"></i>
      </a>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="property-jvm">
  <div data-bind="component: { name: 'jvm-memory-input', params: { value: value } }"></div>
</script>

<script type="text/html" id="property-number">
  <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 1, allowEmpty: true }, valueUpdate:'afterkeydown', attr: { 'title': typeof title === 'undefined' ? '' : title }"/>
</script>

<script type="text/html" id="property-string">
  <input class="input-small" type="text" data-bind="textInput: value, valueUpdate:'afterkeydown'" />
</script>

<script type="text/html" id="property-csv">
  <div data-bind="component: { name: 'csv-list-input', params: { value: value, placeholder: typeof placeholder === 'undefined' ? '' : placeholder } }"></div>
</script>

<script type="text/html" id="property-csv-hdfs-files">
  <div data-bind="component: { name: 'csv-list-input', params: { value: value, inputTemplate: 'property-csv-hdfs-file-input', placeholder: typeof placeholder === 'undefined' ? '' : placeholder } }"></div>
</script>

<script type="text/html" id="property-csv-hdfs-file-input">
  <input type="text" class="filechooser-input" data-bind="value: value, valueUpdate:'afterkeydown', filechooser: { value: value, isAddon: true }" placeholder="${ _('Path to the file, e.g. hdfs://localhost:8020/user/hue/file.hue') }"/>
</script>

<script type="text/html" id="snippet-settings">
  <div class="snippet-settings" data-bind="slideVisible: settingsVisible" style="position: relative; z-index: 100;">
    <div class="snippet-settings-header">
      <h4><i class="fa fa-cog"></i> '${ _('Settings') }'</h4>
    </div>
    <div class="snippet-settings-body">
      <form class="form-horizontal">
        <!-- ko template: { if: typeof properties().driverCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _('Driver Cores') }', value: properties().driverCores, title: '${ _('Number of cores used by the driver, only in cluster mode (Default: 1)') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().executorCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _('Executor Cores') }', value: properties().executorCores, title: '${ _('Number of cores per executor (Default: 1)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().numExecutors != 'undefined', name: 'property', data: { type: 'number', label: '${ _('Executors') }', value: properties().numExecutors, title: '${ _('Number of executors to launch (Default: 2)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().queue != 'undefined', name: 'property', data: { type: 'string', label: '${ _('Queue') }', value: properties().queue, title: '${ _('The YARN queue to submit to (Default: default)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().archives != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _('Archives') }', value: properties().archives, title: '${ _('The YARN queue to submit to (Default: default)') }', placeholder: '${ _('e.g. archive.dat') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().files != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _('Files') }', value: properties().files, title: '${ _('The YARN queue to submit to (Default: default)') }', placeholder: '${ _('e.g. file.dat') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().settings != 'undefined', name: 'property', data: { type: 'csv', label: '${ _('Settings') }', value: properties().settings, title: '${ _('The YARN queue to submit to (Default: default)') }', placeholder: '${ _('e.g. foo') }'}} --><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="code-editor-snippet-body">
  <div class="row-fluid">
    <div class="editor span12" data-bind="verticalSlide: codeVisible">
      <div data-bind="foreach: variables">
        <div>
          <span data-bind="text: name"></span>
          <input type="text" data-bind="value: value" />
        </div>
      </div>
      <div class="ace-editor" data-bind="attr: { id: id() }, aceEditor: {
          value: statement_raw,
          onExecute: execute,
          aceInstance: ace,
          mode: aceEditorMode,
          extraCompleters: completers,
          errors: errors,
          autocompleter: aceAutocomplete,
          placeholder: $root.snippetPlaceholders[type()] }"></div>
      </div>
  </div>

  <!-- ko template: 'snippet-footer-actions' --><!-- /ko -->
  <!-- ko template: 'snippet-results' --><!-- /ko -->
</script>

<script type="text/html" id="snippet-results">
  <div class="row-fluid" data-bind="slideVisible: result.hasSomeResults() && result.type() != 'table'" style="display:none; max-height: 400px; margin: 10px 0;">
    <!-- ko if: result.data().length != 0 -->
    <pre data-bind="text: result.data()[0][1]"></pre>
    <!-- /ko -->
  </div>

  <div class="row-fluid" data-bind="slideVisible: result.hasSomeResults() && result.type() == 'table' && showGrid()" style="display:none; max-height: 400px; margin-top: 4px">
    <div data-bind="visible: isResultSettingsVisible, css:{'span2 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}">
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header pointer" data-bind="click: toggleResultSettings" title="${_('Hide columns')}">${_('columns')}</li>
        </a>
      </ul>
      <ul class="unstyled" data-bind="foreach: result.meta">
        <li data-bind="visible: name != ''">
          <input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" />
          <a class="pointer" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }"></a>
        </li>
      </ul>
    </div>
    <div data-bind="css: {'span10': isResultSettingsVisible, 'span12 nomargin': !isResultSettingsVisible()}">
      <div data-bind="attr: { 'id': 'toggleResultSettingsGrid' + id()}, event: { mouseover: function(){ $('#toggleResultSettingsGrid' + id()).addClass('hoverable'); }, mouseout: function(){ $('#toggleResultSettingsGrid' + id()).removeClass('hoverable'); } }, click: toggleResultSettings" class="toggle-result-settings">
        <a title="${_('Show columns')}" class="pointer" data-bind="visible: !isResultSettingsVisible()">
          <i class="fa fa-chevron-right"></i>
        </a>
        <a title="${_('Hide')}" class="pointer" data-bind="visible: isResultSettingsVisible">
          <i class="fa fa-chevron-left"></i>
        </a>
      </div>
      <div data-bind="css: resultsKlass, event: { mouseover: function(){ $('#toggleResultSettingsGrid' + id()).addClass('hoverable'); }, mouseout: function(){ $('#toggleResultSettingsGrid' + id()).removeClass('hoverable'); } }">
        <table class="table table-condensed resultTable" data-tablescroller-fixed-height="360" data-tablescroller-enforce-height="false">
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

  <div class="row-fluid" data-bind="slideVisible: status() != 'ready' && showChart()" style="display:none; max-height: 400px; margin-top: 4px">
    <div data-bind="visible: isResultSettingsVisible, css:{'span2 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}">
      <div style="float: right; margin-right: -30px; margin-top:0" data-bind="attr: { 'class': 'toggle-result-settings toggleResultSettingsChart' + id()}, event: { mouseover: function(){ $('.toggleResultSettingsChart' + id()).addClass('hoverable'); }, mouseout: function(){ $('.toggleResultSettingsChart' + id()).removeClass('hoverable'); } }, click: toggleResultSettings">
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
    <div data-bind="css:{'span10 chart-container': isResultSettingsVisible, 'span12 nomargin chart-container': !isResultSettingsVisible()}, event: { mouseover: function(){ $('.toggleResultSettingsChart' + id()).addClass('hoverable'); }, mouseout: function(){ $('.toggleResultSettingsChart' + id()).removeClass('hoverable'); } }">

      <div style="margin-right: -30px; margin-top:0" data-bind="visible: !isResultSettingsVisible(), click: toggleResultSettings, attr: { 'class': 'toggle-result-settings toggleResultSettingsChart' + id()}">
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
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().app_jar, valueUpdate:'afterkeydown', filechooser: properties().app_jar" placeholder="${ _('Path to application jar, e.g. hdfs://localhost:8020/user/hue/oozie-examples.jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Class')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().class" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'py'-->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().py_file, valueUpdate:'afterkeydown', filechooser: properties().py_file" placeholder="${ _('Path to python file, e.g. script.py') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv', label: '${ _('Arguments') }', value: properties().arguments, title: '${ _('The YARN queue to submit to (Default: default)') }', placeholder: '${ _('e.g. -foo=bar') }', inline: false }} --><!-- /ko -->
    </form>
  </div>

  <!-- ko template: 'snippet-footer-actions' --><!-- /ko -->
</script>

<script type="text/html" id="snippet-footer-actions">
  <div class="snippet-progress-container">
    <div class="progress progress-striped active" style="height: 0" data-bind="css: {
      'progress-warning': progress() > 0 && progress() < 100,
      'progress-success': progress() == 100,
      'progress-danger': progress() == 0 && result.errors().length > 0}" style="background-color: #FFF; width: 100%">
      <div class="bar" data-bind="style: {'width': (result.errors().length > 0 ? 100 : progress()) + '%'}"></div>
    </div>
  </div>

  <div class="snippet-footer-actions-bar">
    <a data-bind="visible: status() == 'loading'" class="btn btn-primary spark-btn" style="cursor: default;" title="${ _('Creating session') }">
      <i class="fa fa-spinner fa-spin"></i>
    </a>
    <a title="${ _('Cancel') }" data-bind="click: cancel, visible: status() == 'running'" class="btn btn-danger disable-feedback spark-btn pointer">
      <i class="fa fa-stop"></i>
    </a>
    <div class="hover-actions">
      <a title="${ _('CTRL + ENTER') }" data-bind="click: execute, visible: status() != 'running' && status() != 'loading'" class="run-button btn btn-primary disable-feedback spark-btn pointer" style="color: #FFF;"><i class="fa fa-play"></i></a>

      <div style="display: inline-block; margin-left: 15px;">
        <a class="btn" href="javascript: void(0)" data-bind="visible: result.type() == 'table' && result.hasSomeResults(), click: function() { $data.showGrid(true); }, css: {'active': $data.showGrid}" title="${ _('Grid') }">
          <i class="fa fa-th"></i>
        </a>

        <div class="btn-group">
        <a class="btn" href="javascript: void(0)" data-bind="visible: result.type() == 'table' && result.hasSomeResults(), css: {'active': $data.showChart}, click: function(){ $data.showChart(true); }">
          <i class="hcha hcha-bar-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART"></i>
          <i class="hcha hcha-line-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART"></i>
          <i class="hcha hcha-pie-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART"></i>
          <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART"></i>
          <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP"></i>
          <i class="hcha hcha-map-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP"></i>
        </a>
        <a style="min-width: 12px; width: 12px;" class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)" data-bind="visible: result.type() == 'table' && result.hasSomeResults(), css: {'active': $data.showChart}">
          <i class="fa fa-caret-down"></i>
        </a>

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
      </div>
    </div>

    <div class="pull-right hover-actions" style="padding-top: 8px; font-size: 15px;">
      <span style="color: #CCC; padding-right: 10px;" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()"></span>

      <a href="javascript:void(0)" data-bind="visible: status() != 'ready' && status() != 'loading' && result.errors().length == 0, click: function() { $data.showLogs(! $data.showLogs()); window.setTimeout(redrawFixedHeaders, 100); }, css: {'blue': $data.showLogs}" title="${ _('Show Logs') }">
        <i class="fa fa-file-text-o"></i>
      </a>

      <form method="POST" action="${ url('spark:download') }" class="download-form" style="display: inline">
        ${ csrf_token(request) | n,unicode }
        <input type="hidden" name="notebook"/>
        <input type="hidden" name="snippet"/>
        <input type="hidden" name="format" class="download-format"/>

        <div class="hover-actions hover-dropdown" data-bind="visible: status() == 'available' && result.hasSomeResults() && result.type() == 'table'">
          <a class="dropdown-toggle" data-toggle="dropdown">
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

<div id="chooseFile" class="modal hide fade" style="z-index: 10000;">
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

<div class="ace-filechooser">
  <a class="pointer pull-right" data-bind="click: function(){ $('.filechooser').hide(); }"><i class="fa fa-times"></i></a>
  <div class="ace-filechooser-content">
    <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
    <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
  </div>
</div>

<div id="removeSnippetModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Confirm Remove')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to remove this snippet?')}</p>
  </div>
  <div class="modal-footer" data-bind="with: $root.removeSnippetConfirmation">
    <a class="btn" data-dismiss="modal" data-bind="click: function() { $root.removeSnippetConfirmation(null); }">${_('No')}</a>
    <input type="submit" data-dismiss="modal" value="${_('Yes')}" class="btn btn-danger" data-bind="click: function() { notebook.snippets.remove(snippet); window.setTimeout(redrawFixedHeaders, 100); $root.removeSnippetConfirmation(null); }" />
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
            <!-- ko ifnot: sessions().length -->
            <p>${ _('There are currently no active sessions.') }</p>
            <!-- /ko -->
            <!-- ko foreach: sessions -->
              <!-- ko if: ['pyspark', 'scala'].indexOf(type()) != -1 && typeof properties != 'undefined' -->
              <h4 data-bind="text: $root.getSnippetName(type())" style="clear:left;"></h4>
              <div style="display:block; width:100%;">
                <!-- ko foreach: properties -->
                  <!-- ko template: {
                    name: 'property',
                    data: {
                      type: $root.getSessionProperties(name()).type,
                      label: $root.getSessionProperties(name()).nice_name,
                      value: value,
                      remove: function () { $parent.properties.remove($data) }
                    }
                  } --><!-- /ko -->
                <!-- /ko -->
              </div>
              <div style="clear:both; padding-left: 120px;">
                <!-- ko if: availableNewProperties().length -->
                <select data-bind="options: availableNewProperties,
                         optionsText: 'nice_name',
                         optionsValue: 'name',
                         value: selectedSessionProperty,
                         optionsCaption: '${ _('Choose a property...') }'"></select>
                <a class="pointer" style="padding:5px;" data-bind="click: selectedSessionProperty() && function() {
                    properties.push(ko.mapping.fromJS({'name': selectedSessionProperty(), 'value': ''}));
                    selectedSessionProperty('');
                  }" style="margin-left:10px;vertical-align: text-top;">
                  <i class="fa fa-plus"></i>
                </a>
                <!-- /ko -->
                <a style="float: right;" class="btn pointer" title="${ _('Recreate session') }" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().restartSession($data) }">
                  <i class="fa fa-refresh" data-bind="css: { 'fa-spin': restarting }"></i> ${ _('Recreate') }
                </a>
                <a style="margin-right: 5px; float: right;" class="btn pointer" title="${ _('Close session') }" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().closeAndRemoveSession($data) }">
                  <i class="fa fa-times"></i> ${ _('Close') }
                </a>
              </div>
              <!-- /ko -->
            <!-- /ko -->
            </br>
          </fieldset>
        </form>
        <!-- /ko -->
      </div>
    </div>

  </div>
  <div style="position:absolute; width:100%; bottom: 0;"><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>
</%def>


<%def name="commonJS()">
<script type="text/javascript" charset="utf-8">

  $.scrollbarWidth = function() {
    var _parent, _child, _width;
    _parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
    _child = _parent.children();
    _width = _child.innerWidth() - _child.height(99).innerWidth();
    _parent.remove();
    return _width;
  };

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
          parentId: 'snippet_' + snippet.id(),
          clonedContainerPosition: "absolute"
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
      parentId: 'snippet_' + snippet.id(),
      clonedContainerPosition: "absolute"
    });
    $(".dataTables_filter").hide();
    var dataTableEl = $(el).parents(".dataTables_wrapper");

    dataTableEl.bind('mousewheel DOMMouseScroll wheel', function (e) {
      var _e = e.originalEvent,
          _deltaX = _e.wheelDeltaX || -_e.deltaX,
          _deltaY = _e.wheelDeltaY || -_e.deltaY;
      this.scrollTop += -_deltaY / 2;
      this.scrollLeft += -_deltaX / 2;

      if (this.scrollTop == 0) {
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
            if (_idxGroup == -1 || item[_idxGroup] == col) {
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

      if (rawDatum.snippet.chartScatterGroup() != null) {
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
          parentId: 'snippet_' + snippet.id(),
          clonedContainerPosition: "absolute"
        });
      });
    });
  }

  $(document).ready(function () {
    // Close the notebook snippets when leaving the page
    window.onbeforeunload = function (e) {
      viewModel.selectedNotebook().close();
    };

    $(".preview-sample").css("right", (10 + $.scrollbarWidth()) + "px");

    $(window).bind("keydown", "ctrl+s alt+s meta+s", function (e) {
      e.preventDefault();
      viewModel.saveNotebook();
      return false;
    });

    var initialResizePosition = 100;

    function getDraggableOptions(minY) {
      return {
        axis: "y",
        start: function (e, ui) {
          initialResizePosition = ui.offset.top;
        },
        drag: function (e, ui) {
          draggableHelper($(this), e, ui);
          $(".jHueTableExtenderClonedContainer").hide();
        },
        stop: function (e, ui) {
          $(".jHueTableExtenderClonedContainer").show();
          draggableHelper($(this), e, ui, true);
          redrawFixedHeaders();
          ui.helper.first().removeAttr("style");
        },
        containment: [0, minY, 4000, minY + 400]
      }
    };

    $(".resize-panel a").each(function () {
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

    $(document).on("snippetAdded", function (e, snippet) {
      var _handle = $("#snippet_" + snippet.id()).find(".resize-panel a");
      if (_handle.length > 0) {
        _handle.draggable(getDraggableOptions(_handle.offset().top));
      }
    });

    $(document).on("toggleResultSettings", function (e, snippet) {
      $("#snippet_" + snippet.id()).find(".chart").trigger("forceUpdate");
      redrawFixedHeaders();
    });

    $(document).on("editorSizeChanged", function () {
      window.setTimeout(redrawFixedHeaders, 50);
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

    function resizeToggleResultSettings(snippet) {
      var _dtElement;
      if (snippet.showGrid()) {
        _dtElement = $("#snippet_" + snippet.id()).find(".dataTables_wrapper");
      }
      else {
        _dtElement = $("#snippet_" + snippet.id()).find(".chart:visible");
      }
      _dtElement.parents(".snippet-body").find(".toggle-result-settings").css({
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
          resizeToggleResultSettings(options.snippet);
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

    $(document).on("renderDataError", function (e, options) {
      var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
      _dtElement.animate({opacity: '1'}, 50);
      _dtElement.off("scroll");
    });

    $(document).on("progress", function (e, options) {
      if (options.data == 100) {
        window.setTimeout(function () {
          $("#snippet_" + options.snippet.id()).find(".progress").animate({
            height: "0"
          }, 100, function () {
            options.snippet.progress(0);
            redrawFixedHeaders();
          });
        }, 2000);
      }
    });

    $(document).on("gridShown", function (e, snippet) {
      window.setTimeout(function () {
        resizeToggleResultSettings(snippet);
      }, 50);
    });

    $(document).on("chartShown", function (e, snippet) {
      window.setTimeout(function () {
        resizeToggleResultSettings(snippet);
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
        $("#snippet_" + snippet.id()).find(".CodeMirror").each(function () {
          $(this)[0].CodeMirror.refresh();
        });
      }, 100);
    });

    var hideTimeout = -1;
    $(document).on("hideAutocomplete", function () {
      window.clearTimeout(hideTimeout);
      hideTimeout = window.setTimeout(function () {
        $aceAutocomplete = $(".ace_editor.ace_autocomplete");
        if ($aceAutocomplete.is(":visible")) {
          $aceAutocomplete.hide();
        }
      }, 100);
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
                  resizeToggleResultSettings(snippet);
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
    $(window).on("resize", function () {
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(function () {
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
</%def>
