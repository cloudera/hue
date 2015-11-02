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
from desktop.views import _ko
%>

<%namespace name="require" file="/require.mako" />

<%def name="includes()">
<link rel="stylesheet" href="${ static('desktop/css/common_dashboard.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
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
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('notebook/js/assist.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/js/hue.geo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.colors.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/leaflet/leaflet.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/leaflet/leaflet.markercluster.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/nv.d3.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topojson.v1.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/world.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/usa.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/chn.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/bra.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/can.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/ind.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/gbr.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/ita.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/fra.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/deu.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/jpn.topo.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/topo/aus.topo.js') }" type="text/javascript" charset="utf-8"></script>

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

<script src="${ static('desktop/ext/select2/select2.min.js') }" type="text/javascript" charset="utf-8"></script>

<!--[if IE 9]>
  <script src="${ static('desktop/ext/js/classList.min.js') }" type="text/javascript" charset="utf-8"></script>
<![endif]-->
<script src="${ static('desktop/ext/js/medium-editor.min.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/js/ace/ace.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    showProcessingMessages: false,
    tex2jax: { inlineMath: [['$','$'],['\\(','\\)']] },
    TeX: { equationNumbers: {autoNumber: "AMS"} }
  });
</script>

<script src="${ static('desktop/js/hue.utils.js') }"></script>

<script src="${ static('desktop/ext/js/download.min.js') }"></script>

${ require.config() }

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

<div class="print-logo">
  <img class="pull-right" src="${ static('desktop/art/icon_hue_48.png') }" />
</div>

<div class="search-bar" data-bind="visible: ! $root.isPlayerMode()">
  <div class="pull-right" style="padding-right:50px">
    <a class="btn pointer" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="click: toggleEditing, css: {'btn-inverse': isEditing}">
      <i class="fa fa-pencil"></i>
    </a>

    <a class="btn pointer" title="${ _('Sessions') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#sessionsDemiModal">
      <i class="fa fa-cogs"></i>
    </a>

    <div class="btn-group">
      <a class="btn dropdown-toggle" data-toggle="dropdown">
        <i class="fa fa-bars"></i>
      </a>
      <ul class="dropdown-menu pull-right">
        <li>
          <a class="pointer" data-bind="visible: $root.selectedNotebook() && $root.selectedNotebook().snippets().length > 0, click: function(){ hueUtils.goFullScreen(); $root.isEditing(false); $root.isPlayerMode(true); }" style="display:none">
            <i class="fa fa-fw fa-expand"></i> ${ _('Player mode') }
          </a>
        </li>
        <li>
          <a class="pointer" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
            <i class="fa fa-fw fa-play"></i> ${ _('Execute all snippets') }
          </a>
        </li>
        <li>
          <a class="pointer" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
            <i class="fa fa-fw fa-eraser"></i> ${ _('Clear all results') }
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: displayCombinedContent">
            <i class="fa fa-fw fa-file-text-o"></i> ${ _('Display all Notebook content') }
          </a>
        </li>
        <li>
          <a class="pointer" data-toggle="modal" data-target="#importGithubModal">
            <i class="fa fa-fw fa-github"></i> ${ _('Import from Github') }
          </a>
        </li>
        <li>
          <a class="pointer" data-bind="click: function() { $root.selectedNotebook().exportJupyterNotebook() }">
            <i class="fa fa-fw fa-file-code-o"></i> ${ _('Export to Jupyter') }
          </a>
        </li>
      </ul>
    </div>


    &nbsp;&nbsp;&nbsp;

    <a class="btn" title="${ _('Save') }" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: saveNotebook">
      <i class="fa fa-save"></i>
    </a>

    <a class="btn" href="${ url('notebook:new') }" title="${ _('New Notebook') }" rel="tooltip" data-placement="bottom">
      <i class="fa fa-file-o"></i>
    </a>

    <a class="btn" href="${ url('notebook:notebooks') }" title="${ _('Notebooks') }" rel="tooltip" data-placement="bottom">
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
        <span data-bind="editable: description, editableOptions: {enabled: $root.isEditing(), placement: 'right', emptytext: '${_ko('Add a description...')}'}" class="muted"></span>
      <!-- /ko  -->
      <!-- ko ifnot: $root.isEditing() -->
        <span data-bind="text: description" class="muted"></span>
      <!-- /ko  -->
    <!-- /ko -->
  </div>

</div>

<div class="player-toolbar" data-bind="visible: $root.isPlayerMode()" style="display: none;">
  <div class="pull-right pointer" data-bind="click: function(){ hueUtils.exitFullScreen(); $root.isPlayerMode(false); }"><i class="fa fa-times"></i></div>
  <img src="${ static('desktop/art/icon_hue_48.png') }" />
  <!-- ko if: $root.selectedNotebook() -->
  <h4 data-bind="text: $root.selectedNotebook().name"></h4>
  <!-- /ko -->
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


<div id="importGithubModal" class="modal hide" data-backdrop="true" style="width:780px;margin-left:-410px!important">
  <div class="modal-header">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <h3>${_('Import from Github')}</h3>
  </div>
  <div class="modal-body">
    <div class="input-prepend">
      <span class="add-on"><i class="fa fa-github"></i></span>
      <input id="importGithubUrl" type="text" placeholder="ie: https://github.com/romainr/hadoop-tutorials-examples/blob/master/notebook/shared_rdd/hue-sharedrdd-notebook.json" style="width: 726px" />
    </div>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
    <a id ="importGithubBtn" href="#" class="btn btn-primary disable-feedback" data-bind="click: authorizeGithub">${_('Import')}</a>
  </div>
</div>


<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { wasAssistVisible = true; $root.isLeftPanelVisible(true); }">
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
  <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
    <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { wasAssistVisible = false; $root.isLeftPanelVisible(false) }">
      <i class="fa fa-chevron-left"></i>
    </a>
    <div class="assist" data-bind="component: {
        name: 'assist-panel',
        params: { notebookViewModel: $root }
      }"></div>
  </div>
  <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
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
              var $element = $(event.target);
              $element.find('.snippet-body').slideDown('fast', function () { $(window).scrollTop(lastWindowScrollPosition); });
            },
            'helper': function(event) {
              lastWindowScrollPosition = $(window).scrollTop();
              var $element = $(event.target);
              $element.find('.snippet-body').slideUp('fast', function () {
                $('.sortable-snippets').sortable('refreshPositions')
              });
              var _par = $('<div>')
                .css('overflow', 'hidden')
                .addClass('card-widget snippet-move-helper')
                .width($element.parents('.snippet').width());
              $('<h2>')
                .addClass('card-heading')
                .html($element.parents('h2').html())
                .appendTo(_par)
                .find('.hover-actions')
                .removeClass('hover-actions');
              $('<pre>')
                .addClass('dragging-pre muted')
                .html(ko.dataFor($element.parents('.card-widget')[0]).statement())
                .appendTo(_par);
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

  <!-- ko if: viewSettings().snippetImage -->
  <img class="snippet-icon-image" data-bind="attr: { 'src': viewSettings().snippetImage }">
  <!-- /ko -->
  <!-- ko if: viewSettings().snippetIcon -->
  <i class="fa snippet-icon" data-bind="css: viewSettings().snippetIcon"></i>
  <!-- /ko -->

  <sup style="margin-left: -2px" data-bind="text: $root.getSnippetName(type())"></sup>
</script>


<script type="text/html" id="snippet">
  <div class="snippet-container row-fluid" data-bind="visibleOnHover: { override: inFocus, selector: '.hover-actions' }">
    <div data-bind="css: klass, attr: {'id': 'snippet_' + id()}">

      <h5 class="card-heading-print" data-bind="text: name, css: {'visible': name() != ''}"></h5>

      <h2 class="card-heading simple" data-bind="dblclick: function(){ $parent.newSnippetAbove(id()) }">

        <div class="inactive-action hover-actions dropdown inline widget-type">
          <a class="dropdown-toggle" data-toggle="dropdown" href="javascript:void(0)">
            <span data-bind="template: { name: 'snippetIcon', data: $data }"></span>
            <span>
              <b class="caret"></b>
            </span>
          </a>
          <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
            <li><a class="pointer" data-bind="click: function(){ $parent.type($data.type()); }, text: name"></a></li>
          </ul>
        </div>

        <div class="inactive-action hover-actions inline"><span data-bind="editable: name, editableOptions: { emptytext: '${_ko('Untitled')}', mode: 'inline', enabled: true, placement: 'right' }" style="border:none;"></span></div>

        <div class="hover-actions inline pull-right" style="font-size: 15px;">
          <a class="inactive-action move-widget" href="javascript:void(0)"><i class="fa fa-arrows"></i></a>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ codeVisible(! codeVisible()) }, visible: type() != 'text'"><i class="fa" data-bind="css: {'fa-compress' : codeVisible, 'fa-expand' : ! codeVisible() }"></i></a>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ settingsVisible(! settingsVisible()) }, visible: hasProperties, css: { 'blue' : settingsVisible }"><i class="fa fa-cog"></i></a>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ $root.removeSnippet($parent, $data); }"><i class="fa fa-times"></i></a>
        </div>

      </h2>

      <div style="position: relative;">
        <div class="snippet-row">
          <div class="snippet-left-bar" style="vertical-align: bottom;">
            <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-execution-controls' } --><!-- /ko -->
          </div>
          <div class="snippet-body">
            <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'code-editor-snippet-body' } --><!-- /ko -->
            <!-- ko template: { if: type() == 'text', name: 'text-snippet-body' } --><!-- /ko -->
            <!-- ko template: { if: type() == 'markdown', name: 'markdown-snippet-body' } --><!-- /ko -->
            <!-- ko template: { if: type() == 'jar' || type() == 'py', name: 'executable-snippet-body' } --><!-- /ko -->

          </div>
        </div>

        <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-execution-status' } --><!-- /ko -->
        <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-footer-actions' } --><!-- /ko -->

        <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'snippet-results' } --><!-- /ko -->

        <div style="position: absolute; top:0; z-index: 301; width: 100%;">
          <!-- ko template: 'snippet-settings' --><!-- /ko -->
        </div>

        <div class="clearfix"></div>
      </div>

      <div data-bind="delayedOverflow, visible: showLogs, css: resultsKlass" style="margin-top: 5px; position: relative; display: none;">
        <ul data-bind="visible: jobs().length > 0, foreach: jobs" class="unstyled jobs-overlay">
          <li><a data-bind="text: $.trim($data.name), attr: { href: $data.url }" target="_blank"></a></li>
        </ul>
        <pre data-bind="visible: result.logs().length == 0" class="logs logs-bigger">${ _('No logs available at this moment.') }</pre>
        <pre data-bind="visible: result.logs().length > 0, text: result.logs, logScroller: result.logs" class="logs logs-bigger"></pre>
      </div>

      <div data-bind="visible: ! result.hasResultset() && status() == 'available', css: resultsKlass" style="display:none;">
        <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-check muted"></i> ${ _('Success.') }</pre>
      </div>

      <div data-bind="visible: result.hasResultset() && status() == 'available' && result.data().length == 0 && result.fetchedOnce(), css: resultsKlass" style="display:none;">
        <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-check muted"></i> ${ _("Done. 0 results.") }</pre>
      </div>

      <div data-bind="visible: status() == 'available' && ! result.fetchedOnce(), css: resultsKlass" style="display:none;">
        <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-spin fa-spinner"></i> ${ _('Loading...') }</pre>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="property">
  <div data-bind="visibleOnHover: { selector: '.hover-actions' }, css: { 'spark-property' : typeof inline === 'undefined' || inline, 'control-group' : typeof inline !== 'undefined' && ! inline }">
    <label class="control-label" data-bind="text: label, style: { 'width' : typeof inline === 'undefined' || inline ? '120px' : '' }"></label>
    <div class="controls" style="margin-right:10px;" data-bind="style: { 'margin-left' : typeof inline === 'undefined' || inline ? '140px' : '' }">
      <!-- ko template: { name: 'property-' + type } --><!-- /ko -->
    </div>
    <!-- ko ifnot: typeof remove === "undefined" -->
    <div class="hover-actions spark-property-remove">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: remove" title="${ _('Remove') }">
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
        <!-- ko template: { if: typeof properties().archives != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _('Archives') }', value: properties().archives, title: '${ _('Archives to be extracted into the working directory of each executor (YARN only)') }', placeholder: '${ _('e.g. file.zip') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().files != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _('Files') }', value: properties().files, title: '${ _('Files to be placed in the working directory of each executor.') }', placeholder: '${ _('e.g. file.data') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().settings != 'undefined', name: 'property', data: { type: 'csv', label: '${ _('Settings') }', value: properties().settings, title: '${ _('Spark properties') }', placeholder: '${ _('e.g. foo=value') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().parameters != 'undefined', name: 'property', data: { type: 'csv', label: '${ _('Parameters') }', value: properties().parameters, title: '${ _('Names and values of Pig parameters and options') }', placeholder: '${ _('e.g. input /user/data, -param input=/user/data, -optimizer_off SplitFilter, -verbose') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv', label: '${ _('Hadoop properties') }', value: properties().hadoopProperties, title: '${ _('Name and values of Hadoop properties') }', placeholder: '${ _('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().resources != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _('Resources') }', value: properties().resources, title: '${ _('HDFS Files or compressed files') }', placeholder: '${ _('e.g. /tmp/file, /tmp.file.zip') }'}} --><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="code-editor-snippet-body">
  <div class="row-fluid" style="margin-bottom: 5px">
    <div class="editor span12" data-bind="verticalSlide: codeVisible, click: function(snippet, e){ setAceFocus(e, ace()); }">
      <div class="ace-editor" data-bind="css: {'active-editor': inFocus }, attr: { id: id() }, delayedOverflow, aceEditor: {
          snippet: $data,
          openIt: '${ _ko("Alt or Ctrl + Click to open it") }'
        }"></div>
      </div>
    <div class="clearfix"></div>
    <ul data-bind="foreach: variables" class="unstyled inline">
        <li>
          <div class="input-prepend margin-top-10">
            <span class="muted add-on" data-bind="text: name"></span>
            <input class="input-medium" type="text" placeholder="${ _("Variable value") }" data-bind="value: value">
          </div>
        </li>
      </ul>
  </div>
  <div class="clearfix"></div>

</script>

<script type="text/html" id="snippet-results">
  <div class="row-fluid" data-bind="slideVisible: result.hasSomeResults() && result.type() != 'table'" style="display:none; max-height: 400px; margin: 10px 0; overflow-y: auto">
    <!-- ko if: result.data().length != 0 && result.data()[0][1] != "" -->
    <pre data-bind="text: result.data()[0][1]" class="no-margin-bottom"></pre>
    <!-- /ko -->
    <!-- ko ifnot: result.data().length != 0 && result.data()[0][1] != "" -->
    <pre class="no-margin-bottom"><i class="fa fa-check muted"></i> ${ _("Done.") }</pre>
    <!-- /ko -->
    <!-- ko if: result.images().length != 0 -->
    <ul class="unstyled results-images" data-bind="foreach: result.images()">
      <li>
        <img data-bind="attr: {'src': 'data:image/png;base64,' + $data}" class="margin-bottom-10" />
      </li>
    </ul>
    <!-- /ko -->
  </div>

  <div class="row-fluid table-results" data-bind="visible: result.hasSomeResults() && result.type() == 'table'" style="display: none; max-height: 400px; margin-top: 4px;">
    <div data-bind="visible: showGrid" style="display: none;">
      <div data-bind="visible: isResultSettingsVisible, css:{'span2 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}">
        <ul class="nav nav-list" style="border: none; background-color: #FFF">
          <li class="nav-header pointer" data-bind="click: toggleResultSettings" title="${_('Hide columns')}">${_('columns')}</li>
          </a>
        </ul>
        <ul class="unstyled" data-bind="foreach: result.meta">
          <li data-bind="visible: name != ''">
            <input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" />
            <a class="pointer" title="${ _('Click to scroll to column') }" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }"></a>
          </li>
        </ul>
      </div>
      <div data-bind="css: {'span10': isResultSettingsVisible, 'span12 nomargin': !isResultSettingsVisible()}">
        <div data-bind="attr: { 'id': 'toggleResultSettingsGrid' + id() }, click: toggleResultSettings" class="hover-actions toggle-result-settings show-result-settings">
          <a class="inactive-action pointer" title="${_('Show columns')}" data-bind="visible: !isResultSettingsVisible()">
            <i class="fa fa-chevron-right"></i>
          </a>
          <a class="inactive-action pointer" title="${_('Hide')}" data-bind="visible: isResultSettingsVisible">
            <i class="fa fa-chevron-left"></i>
          </a>
        </div>
        <div data-bind="delayedOverflow, css: resultsKlass">
          <table class="table table-condensed resultTable">
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

    <div data-bind="visible: showChart" style="display:none;">
      <div data-bind="visible: isResultSettingsVisible, css:{'span2 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}">
        <div style="float: right; margin-right: -30px; margin-top:0" data-bind="attr: { 'class': 'hover-actions inline toggle-result-settings toggleResultSettingsChart' + id() }, click: toggleResultSettings">
          <a class="inactive-action pointer" title="${_('Hide')}" data-bind="visible: isResultSettingsVisible">
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
            <select data-bind="options: (chartType() == ko.HUE_CHARTS.TYPES.BARCHART || chartType() == ko.HUE_CHARTS.TYPES.PIECHART || chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP) ? result.cleanedMeta : result.cleanedNumericMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartX}" class="input-medium"></select>
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
            <select data-bind="options: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP ? result.cleanedMeta : result.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartYSingle}" class="input-medium"></select>
          </div>

          <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.MAP">
            <li class="nav-header">${_('label')}</li>
          </ul>
          <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP">
            <select data-bind="options: result.cleanedMeta, value: chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartMapLabel}" class="input-medium"></select>
          </div>

          <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
            <li class="nav-header">${_('scatter group')}</li>
          </ul>
          <div data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
            <select data-bind="options: result.cleanedMeta, value: chartScatterGroup, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterGroup}" class="input-medium"></select>
          </div>

          <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
            <li class="nav-header">${_('scatter size')}</li>
          </ul>
          <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
            <select data-bind="options: result.cleanedMeta, value: chartScatterSize, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterSize}" class="input-medium"></select>
          </div>

          <!-- ko if: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP -->
          <ul class="nav nav-list" style="border: none; background-color: #FFF">
            <li class="nav-header">${_('scope')}</li>
          </ul>
          <div data-bind="visible: chartType() != ''">
            <select data-bind="selectedOptions: chartScope, optionsCaption: '${_ko('Choose a scope...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a scope...") }', update: chartScope}">
              <option value="world">${ _("World") }</option>
              <option value="europe">${ _("Europe") }</option>
              <option value="aus">${ _("Australia") }</option>
              <option value="bra">${ _("Brazil") }</option>
              <option value="can">${ _("Canada") }</option>
              <option value="chn">${ _("China") }</option>
              <option value="fra">${ _("France") }</option>
              <option value="deu">${ _("Germany") }</option>
              <option value="ita">${ _("Italy") }</option>
              <option value="jpn">${ _("Japan") }</option>
              <option value="gbr">${ _("UK") }</option>
              <option value="usa">${ _("USA") }</option>
            </select>
          </div>
          <!-- /ko -->

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

      <div data-bind="css:{'span10 chart-container': isResultSettingsVisible, 'span12 nomargin chart-container': !isResultSettingsVisible() }">
        <div style="margin-right: -30px; margin-top:0" data-bind="visible: !isResultSettingsVisible(), click: toggleResultSettings, attr: { 'class': 'hover-actions inline toggle-result-settings toggleResultSettingsChart' + id()}">
          <a class="inactive-action pointer" title="${_('Show settings')}" data-bind="visible: !isResultSettingsVisible()">
            <i class="fa fa-chevron-right"></i>
          </a>
        </div>

        <h1 class="empty" data-bind="visible: !hasDataForChart()">${ _('Select the chart parameters on the left') }</h1>

        <div data-bind="visible: hasDataForChart()">
          <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                      transformer: pieChartDataTransformer, maxWidth: 350, parentSelector: '.chart-container' }, visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>

          <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true,
                      transformer: multiSerieDataTransformer, stacked: false, showLegend: true},  stacked: true, showLegend: true, visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>

          <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                      transformer: multiSerieDataTransformer, showControls: false }, visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>

          <div data-bind="attr:{'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                      transformer: leafletMapChartDataTransformer, showControls: false, height: 380, visible: chartType() == ko.HUE_CHARTS.TYPES.MAP, forceRedraw: true}" class="chart"></div>

          <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data, scope: chartScope()},
                      transformer: mapChartDataTransformer, isScale: true, showControls: false, height: 380, maxWidth: 750, parentSelector: '.chart-container', visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}" class="chart"></div>

          <div data-bind="attr:{'id': 'scatterChart_'+id()}, scatterChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                      transformer: scatterChartDataTransformer, maxWidth: 350 }, visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="text-snippet-body">
  <div data-bind="attr:{'id': 'editor_' + id()}, html: statement_raw, value: statement_raw, medium: {}" data-placeHolder="${ _('Type your text here, select some text to format it') }" class="text-snippet"></div>
</script>

<script type="text/html" id="markdown-snippet-body">
  <!-- ko if: $root.isEditing() -->
  <div class="row-fluid">
    <div class="span6">
      <div class="ace-editor" data-bind="attr: { id: id() }, aceEditor: {
        snippet: $data,
        updateOnInput: true
      }"></div>
    </div>
    <div class="span6">
      <div data-bind="html: renderMarkdown(statement_raw(), id()), attr: {'id': 'liveMD'+id()}"></div>
    </div>
  </div>
  <!-- /ko -->
  <!-- ko ifnot: $root.isEditing() -->
  <div data-bind="html: renderMarkdown(statement_raw(), id())"></div>
  <!-- /ko -->
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
</script>

<script type="text/html" id="snippet-execution-status">
  <div class="snippet-progress-container" data-bind="click: function(snippet, e){ setAceFocus(e, ace()); }">
    <div class="progress progress-striped active" data-bind="css: {
      'progress-warning': progress() > 0 && progress() < 100,
      'progress-success': progress() == 100,
      'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%">
      <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : progress()) + '%'}"></div>
    </div>
  </div>
  <div data-bind="visible: errors().length > 0, css: errorsKlass" style="margin-left: 3px">
    <ul class="unstyled" data-bind="foreach: errors">
      <li data-bind="text: message"></li>
    </ul>
  </div>
</script>

<script type="text/html" id="snippet-footer-actions">
  <div class="snippet-footer-actions-bar" data-bind="click: function(snippet, e){ setAceFocus(e, ace()); }">
    <!-- ko template: 'snippet-result-controls' --><!-- /ko -->
    <div class="pull-right hover-actions inline" style="padding-top: 8px; font-size: 15px;">
      <!-- ko template: 'snippet-execution-stats' --><!-- /ko -->
      <div data-bind="component: { name: 'downloadSnippetResults', params: { snippet: $data, notebook: $parent } }" style="display:inline-block;"></div>
    </div>
  </div>
</script>

<script type ="text/html" id="snippet-execution-controls">
  <div class="hover-actions" style="display:inline-block;">
    <a class="snippet-side-btn" style="cursor: default; color: #338bb8;" data-bind="visible: status() == 'loading'" title="${ _('Creating session') }">
      <i class="fa fa-spinner fa-spin"></i>
    </a>
    <a class="snippet-side-btn" style="color: #338bb8;"data-bind="click: cancel, visible: status() == 'running'" title="${ _('Cancel') }">
      <i class="fa fa-stop"></i>
    </a>
    <a class="snippet-side-btn" data-bind="click: execute, visible: status() != 'running' && status() != 'loading'" title="${ _('CTRL + ENTER') }">
      <i class="fa fa-play"></i>
    </a>
  </div>
</script>

<script type ="text/html" id="snippet-execution-stats">
  <span style="color: #CCC; padding-right: 10px;" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()"></span>

  <a class="inactive-action" href="javascript:void(0)" data-bind="visible: status() != 'ready' && status() != 'loading' && errors().length == 0, click: function() { $data.showLogs(! $data.showLogs()); window.setTimeout(redrawFixedHeaders, 100); }, css: {'blue': $data.showLogs}" title="${ _('Show Logs') }">
    <i class="fa fa-file-text-o"></i>
  </a>
</script>

<script type="text/html" id="snippet-result-controls">
  <div style="display: inline-block; margin-left: 15px;">
    <a class="btn" href="javascript: void(0)" data-bind="visible: result.type() == 'table' && result.hasSomeResults(), click: function() { $data.showGrid(true); }, css: {'active': $data.showGrid}" title="${ _('Grid') }" style="display:none;">
      <i class="fa fa-th"></i>
    </a>

    <div class="btn-group">
      <a class="btn" href="javascript: void(0)" data-bind="visible: result.type() == 'table' && result.hasSomeResults(), css: {'active': $data.showChart}, click: function(){ $data.showChart(true); }" style="display:none;">
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
              <!-- ko if: ['pyspark', 'spark'].indexOf(type()) != -1 && typeof properties != 'undefined' -->
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
                         optionsCaption: '${ _ko('Choose a property...') }'"></select>
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

<div class="hoverMsg hide">
  <p class="hoverText">${_('Drop iPython/Zeppelin notebooks here')}</p>
</div>


<div id="authModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Connect to the data source')}</h3>
  </div>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="span6">
        <div class="input-prepend">
          <span class="add-on muted"><i class="fa fa-user"></i></span>
          <input name="username" type="text" data-bind="value: $root.authSessionUsername" placeholder="${ _('Username') }"/>
        </div>
      </div>
      <div class="span6">
        <div class="input-prepend">
          <span class="add-on muted"><i class="fa fa-lock"></i></span>
          <input name="password" type="password" data-bind="value: $root.authSessionPassword" placeholder="${ _('Password') }"/>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <a class="btn btn-primary disable-feedback" data-dismiss="modal" data-bind="click: function() { $root.selectedNotebook().authSession(); }">${_('Connect')}</a>
  </div>
</div>
  
</%def>


<%def name="commonJS()">

<script type="text/javascript" charset="utf-8">

  function authorizeGithub() {
    if ($("#importGithubUrl").val().trim() != "") {
      $(".fa-github").addClass("fa-spinner fa-spin");
      $("#importGithubBtn").attr("disabled", "disabled");
      $.getJSON("/notebook/api/github/authorize?currentURL=" + location.pathname + (location.search != "" ? location.search : "?github=true") + "&fetchURL=" + $("#importGithubUrl").val(), function (data) {
        if (data.status == 0) {
          $(".fa-github").removeClass("fa-spinner fa-spin");
          $("#importGithubBtn").removeAttr("disabled");
          $("#importGithubModal").modal("hide");
          importGithub();
        }
        else {
          location.href = data.auth_url;
        }
      });
    }
  }

  function importGithub() {
    $(".hoverText").html("<i class='fa fa-spinner fa-spin'></i>");
    showHoverMsg();
    $.get("api/github/fetch?url=" + $("#importGithubUrl").val().trim(), function(data){
      if (data && data.content){
        if ($.isArray(data.content)) { // it's a Hue Notebook
          window.importExternalNotebook(JSON.parse(data.content[0].fields.data));
        }
        else { // iPython / Zeppelin
          window.parseExternalJSON(data.content);
        }
        $("#importGithubUrl").val("");
      }
      else {
        $.jHueNotify.error("${ _("Failed to load") } " + $("#importGithubUrl").val());
      }
    });
  }

  var showHoverMsg = function () {
    $(".hoverMsg").removeClass("hide");
  };

  var hideHoverMsg = function () {
    $(".hoverText").html("${_('Drop iPython/Zeppelin notebooks here')}");
    $(".hoverMsg").addClass("hide");
  };

  function escapeMathJax(code) {
    var escapeMap = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#x27;",
      "`": "&#x60;"
    };
    var escaper = function (match) {
      return escapeMap[match];
    };
    var source = "(?:" + Object.keys(escapeMap).join("|") + ")";
    var testRegexp = RegExp(source);
    var replaceRegexp = RegExp(source, "g");
    code = code == null ? "" : "" + code;
    return testRegexp.test(code) ? string.replace(replaceRegexp, escaper) : code;
  }

  var mathJaxTimeout = 0;

  if (typeof MathJax == "undefined") {
    escapeMathJax = function (code) {
      return code;
    }
  }

  function renderMarkdown(text, snippetId) {
    window.clearTimeout(mathJaxTimeout);

    text = text.replace(/([^$]*)([$]+[^$]*[$]+)?/g, function (a, text, code) {
      return markdown.toHTML(text).replace(/^<p>|<\/p>$/g, '') + (code ? escapeMathJax(code) : '');
    });
    if (typeof MathJax != "undefined") {
      mathJaxTimeout = window.setTimeout(function () {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub, $("#liveMD" + snippetId)[0]]);
      }, 500);
    }
    return text;
  }

  ace.config.set("basePath", "/static/desktop/js/ace");

  function setAceFocus(event, editor) {
    if (!$(event.target).hasClass("ace_content")) {
      editor.focus();
      editor.execCommand("gotolineend");
    }
  }

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
          maxHeight: 330,
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
      maxHeight: 330,
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
      if ($(el).closest(".results").css("overflow") == "hidden") {
        return;
      }
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
        return a.value - b.value
      });
    }
    if (rawDatum.sorting == "desc") {
      _data.sort(function (a, b) {
        return b.value - a.value
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
              return a.y - b.y
            });
          }
          if (rawDatum.sorting == "desc") {
            _data.sort(function (a, b) {
              return b.y - a.y
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

  require([
    "knockout",
    "ko.charts",
    "notebook/js/notebook.ko",
    "knockout-mapping",
    "knockout-sortable",
    "knockout-deferred-updates",
    "ko.editable",
    "ko.hue-bindings"
  ], function (ko, charts, EditorViewModel) {

    var VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode }, {
      user: '${ user.username }',
      assistAvailable: '${ autocomplete_base_url | n,unicode }' !== '',
      snippetViewSettings: {
        default: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/sql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        code: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          snippetIcon: 'fa-code'
        },
        hive: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/hive',
          snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
          sqlDialect: true
        },
        impala: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/impala',
          snippetImage: '${ static("impala/art/icon_impala_48.png") }',
          sqlDialect: true
        },
        jar : {
          snippetIcon: 'fa-file-archive-o '
        },
        mysql: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/mysql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        mysqljdbc: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/mysql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        pig: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/pig',
          snippetImage: '${ static("pig/art/icon_pig_48.png") }'
        },
        pgsql: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/pgsql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        py : {
          snippetIcon: 'fa-file-code-o'
        },
        pyspark: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/python',
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        r: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/r',
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        spark: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/scala',
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        text: {
          placeHolder: '${ _('Type your text here') }',
          aceMode: 'ace/mode/text',
          snippetIcon: 'fa-header'
        },
        markdown: {
          placeHolder: '${ _('Type your markdown here') }',
          aceMode: 'ace/mode/markdown',
          snippetIcon: 'fa-header'
        }
      }
    });

    var viewModel;

    var importExternalNotebook = function (notebook) {
      var currentNotebook = viewModel.notebooks()[0];
      currentNotebook.name(notebook.name);
      currentNotebook.description(notebook.description);
      currentNotebook.selectedDatabases = notebook.selectedDatabases;
      currentNotebook.selectedSnippet(notebook.selectedSnippet);
      notebook.snippets.forEach(function(snippet){
        var newSnippet = currentNotebook.addSnippet({
          type: snippet.type,
          result: {}
        });
        newSnippet.statement_raw(snippet.statement);
      });
      hideHoverMsg();
    };

    window.importExternalNotebook = importExternalNotebook;

    var redrawFixedHeaders = function () {
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
    };

    window.redrawFixedHeaders = redrawFixedHeaders;

    function addAce (content, snippetType) {
          var snip = viewModel.notebooks()[0].addSnippet({type: snippetType, result: {}}, true);
          snip.statement_raw(content);
          aceChecks++;
          snip.checkForAce = window.setInterval(function () {
            if (snip.ace()) {
              window.clearInterval(snip.checkForAce);
              aceChecks--;
              if (aceChecks == 0) {
                hideHoverMsg();
              }
            }
          }, 100);
        }

        function addMarkdown (content) {
          var snip = viewModel.notebooks()[0].addSnippet({type: "markdown", result: {}}, true);
          snip.statement_raw(content);
        }

        function addPySpark (content) {
          addAce(content, "pyspark");
        }

        function addSql (content) {
          addAce(content, "hive");
        }

        function addScala (content) {
          addAce(content, "spark");
        }

        function parseExternalJSON(raw) {
          try {
            var loaded = typeof raw == "string" ? JSON.parse(raw) : raw;
            if (loaded.nbformat) { //ipython
              var cells = [];
              if (loaded.nbformat == 3) {
                cells = loaded.worksheets[0].cells;
              }
              else if (loaded.nbformat == 4) {
                cells = loaded.cells;
              }
              cells.forEach(function (cell, cellCnt) {
                window.setTimeout(function () {
                  if (cell.cell_type == "code") {
                    if (loaded.nbformat == 3) {
                      addPySpark($.isArray(cell.input) ? cell.input.join("") : cell.input);
                    }
                    else {
                      addPySpark($.isArray(cell.source) ? cell.source.join("") : cell.source);
                    }
                  }
                  if (cell.cell_type == "heading") {
                    var heading = $.isArray(cell.source) ? cell.source.join("") : cell.source;
                    if (cell.level == 1) {
                      heading += "\n====================";
                    }
                    else if (cell.level == 2) {
                      heading += "\n--------------------";
                    }
                    else {
                      heading = "### " + heading;
                    }
                    addMarkdown(heading);
                  }
                  if (cell.cell_type == "markdown") {
                    addMarkdown($.isArray(cell.source) ? cell.source.join("") : cell.source);
                  }
                  if (cellCnt == cells.length - 1 && aceChecks == 0) {
                    hideHoverMsg();
                  }
                }, 10);
              });
            }

            if (loaded.paragraphs) { //zeppelin
              if (loaded.name) {
                viewModel.notebooks()[0].name(loaded.name);
              }
              loaded.paragraphs.forEach(function (paragraph) {
                if (paragraph.text) {
                  var content = paragraph.text.split("\n");
                  if (content[0].indexOf("%md") > -1) {
                    content.shift();
                    addMarkdown(content.join("\n"));
                  }
                  else if (content[0].indexOf("%sql") > -1 || content[0].indexOf("%hive") > -1) {
                    content.shift();
                    addSql(content.join("\n"));
                  }
                  else if (content[0].indexOf("%pyspark") > -1) {
                    content.shift();
                    addPySpark(content.join("\n"));
                  }
                  else {
                    if (content[0].indexOf("%spark") > -1) {
                      content.shift();
                    }
                    addScala(content.join("\n"));
                  }
                }
              });
            }
          }
          catch (e) {
            hideHoverMsg();
          }
        }

        window.parseExternalJSON = parseExternalJSON;

    // Drag and drop iPython / Zeppelin notebooks
    if (window.FileReader) {

      var aceChecks = 0;

      function handleFileSelect (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        var dt = evt.dataTransfer;
        var files = dt.files;
        if (files.length > 0){
          showHoverMsg();
        }
        else {
          hideHoverMsg();
        }

        for (var i = 0, f; f = files[i]; i++) {
          var reader = new FileReader();
          reader.onload = (function (file) {
            return function (e) {
              $(".hoverText").html("<i class='fa fa-spinner fa-spin'></i>");
              parseExternalJSON(e.target.result);
            };
          })(f);
          reader.readAsText(f);
        }
      }

      function handleDragOver (evt) {
        evt.stopPropagation();
        evt.preventDefault();
        evt.dataTransfer.dropEffect = "copy";
      }

      var dropZone = $("body")[0];
      dropZone.addEventListener("dragenter", showHoverMsg, false);
      dropZone.addEventListener("dragover", handleDragOver, false);
      dropZone.addEventListener("drop", handleFileSelect, false);

      var isDraggingOverText = false;

      $(".hoverText").on("dragenter", function (e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        isDraggingOverText = true;
      });

      $(".hoverText").on("dragleave", function (e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        isDraggingOverText = false;
      });

      $(".hoverMsg").on("dragleave", function (e) {
        if (!isDraggingOverText) {
          hideHoverMsg();
        }
      });
    }



    $(document).ready(function () {
      viewModel = new EditorViewModel(${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS);
      ko.applyBindings(viewModel);
      viewModel.init();

      if (location.getParameter("github_status") != "") {
        if (location.getParameter("github_status") == "0") {
          $.jHueNotify.info("${ _('User successfully authenticated to GitHub.') }");
          $("#importGithubUrl").val(location.getParameter("github_fetch"));
          importGithub();
        }
        else {
          $.jHueNotify.error("${ _('Could not decode Github file content to JSON.') }");
        }
      }

      window.hueDebug = {
        viewModel: viewModel,
        ko: ko
      };

      var isAssistAvailable = viewModel.assistAvailable();
      var wasAssistVisible = viewModel.isLeftPanelVisible();


      viewModel.isPlayerMode.subscribe(function (value) {
        if (value){
          $(".jHueNotify").hide();
          viewModel.assistAvailable(false);
          viewModel.isLeftPanelVisible(false);
          $(".navigator").hide();
          $(".add-snippet").hide();
          $(".main-content").css("top", "50px");
        }
        else {
          viewModel.isLeftPanelVisible(wasAssistVisible);
          viewModel.assistAvailable(isAssistAvailable);
          $(".navigator").show();
          $(".add-snippet").show();
          $(".main-content").css("top", "70px");
        }
      });

      $(document).on("showAuthModal", function (e, data) {
        viewModel.authSessionUsername('${ user.username }');
        viewModel.authSessionPassword('');
        viewModel.authSessionType(data['type']);
        viewModel.authSessionCallback(data['callback']);
        $("#authModal").modal("show");
      });

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

      $(window).bind("keydown", "ctrl+n alt+n meta+n", function (e) {
        e.preventDefault();
        viewModel.selectedNotebook().newSnippet();
        return false;
      });

      var initialResizePosition = 100;

      function getDraggableOptions (minY) {
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
      }

      $(".resize-panel a").each(function () {
        $(this).draggable(getDraggableOptions($(this).parents(".snippet").offset().top + 128));
      });

      function draggableHelper (el, e, ui, setSize) {
        var _snippet = ko.dataFor(el.parents(".snippet")[0]);
        var _cm = $("#snippet_" + _snippet.id()).data("editor");
        var _newSize = _snippet.codemirrorSize() + (ui.offset.top - initialResizePosition);
        _cm.setSize("99%", _newSize);
        if (setSize) {
          _snippet.codemirrorSize(_newSize);
        }
      }

      $(document).on("toggleResultSettings", function (e, snippet) {
        window.setTimeout(function () {
          $("#snippet_" + snippet.id()).find(".chart").trigger("forceUpdate");
          redrawFixedHeaders();
        }, 10)
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
      });

      function resizeToggleResultSettings (snippet) {
        var _dtElement;
        if (snippet.showGrid()) {
          _dtElement = $("#snippet_" + snippet.id()).find(".dataTables_wrapper");
        }
        else {
          _dtElement = $("#snippet_" + snippet.id()).find(".chart:visible");
        }
        if (_dtElement.length == 0) {
          _dtElement = $("#snippet_" + snippet.id()).find(".table-results");
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
          }, 300);
        }
        else {
          var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
          _dtElement.animate({opacity: '1'}, 50);
          _dtElement.off("scroll");
        }
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
  });

  var mathjax = document.createElement("script");
  mathjax.src = "//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML";
  mathjax.async = false;
  document.head.appendChild(mathjax);
</script>

</%def>
