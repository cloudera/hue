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
from notebook.conf import ENABLE_QUERY_BUILDER
%>

<%namespace name="require" file="/require.mako" />
<%namespace name="hueIcons" file="/hue_icons.mako" />

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

<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('desktop/ext/js/markdown.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>

%if ENABLE_QUERY_BUILDER.get():
<!-- For query builder -->
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.contextMenu.min.css') }">
<link rel="stylesheet" href="${ static('desktop/css/queryBuilder.css') }">
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.contextMenu.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.ui.position.min.js') }"></script>
<script src="${ static('desktop/js/queryBuilder.js') }"></script>
<script>


  // query-builder-menu is the class to use
  // Callback will run after each rule add, just focus to the queryBuilder tab
  QueryBuilder.bindMenu('.query-builder-menu', function () {
    $("a[href='#queryBuilderTab']").click();
  });
  function generateQuery() {
    var result = QueryBuilder.buildHiveQuery();
    if (result.status == "fail") {
      $("#invalidQueryBuilder").modal("show");
    } else {
      replaceAce(result.query);
    }
  }

  window.setInterval(function(){
    if ($('#queryBuilder tbody').length > 0 && $('#queryBuilder tbody').find('tr').length > 0){
      $('.button-panel').show();
      $('#queryBuilder').show();
      $('#queryBuilderAlert').hide();
    }
    else {
      $('.button-panel').hide();
      $('#queryBuilder').hide();
      $('#queryBuilderAlert').show();
    }
  }, 500);

</script>
<!-- End query builder imports -->
%endif

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/vkbeautify.js') }" type="text/javascript" charset="utf-8"></script>

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
<script src="${ static('desktop/js/ace/mode-impala.js') }"></script>
<script src="${ static('desktop/js/ace/mode-hive.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>

<script src="${ static('desktop/js/jquery.hiveautocomplete.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/jquery.hdfsautocomplete.js') }" type="text/javascript" charset="utf-8"></script>

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

<%def name="topBar(mode='notebook', editor_type='notebook')">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .search-bar {
    top: 58px!important;
  }
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>

${ hueIcons.symbols() }

<div class="print-logo">
  <img class="pull-right" src="${ static('desktop/art/icon_hue_48.png') }" />
</div>

<div class="navbar navbar-inverse navbar-fixed-top" data-bind="visible: ! $root.isPlayerMode()">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="pull-right">

        <div class="btn-group">
          <a class="btn" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: function() { if ($root.canSave() ) { saveNotebook() } else { $('#saveAsModal').modal('show');} }, attr: { title: $root.canSave() ? '${ _ko('Save') }' : '${ _ko('Save As') }' }"><i class="fa fa-save"></i></a>

          <!-- ko if: $root.canSave -->
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
          <ul class="dropdown-menu">
            <li>
              <a class="pointer" data-bind="click: function() { $('#saveAsModal').modal('show'); }">
                <i class="fa fa-save"></i> ${ _('Save as...') }
              </a>
            </li>
          </ul>
          <!-- /ko -->
        </div>


        &nbsp;&nbsp;&nbsp;

        <a class="btn pointer" title="${ _('Sessions') }" rel="tooltip" data-placement="bottom" data-toggle="modal" data-target="#sessionsDemiModal">
          <i class="fa fa-cogs"></i>
        </a>

        % if mode == 'editor':
        <div class="btn-group">
          <a class="btn" title="${ _('Schedule') }" rel="tooltip" data-placement="bottom" data-bind="click: function() { $root.selectedNotebook().schedule() }, css: {'disabled': ! $root.selectedNotebook() || ! $root.selectedNotebook().id() }">
            <i class="fa fa-fw fa-calendar"></i>
          </a>

           <!-- ko if: $root.selectedNotebook() && $root.selectedNotebook().dependentsWorkflows().length > 0 -->
            <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
            <ul class="dropdown-menu pull-right" data-bind="foreach: $root.selectedNotebook().dependentsWorkflows">
              <li>
                <a class="pointer" data-bind="attr: { 'href': absoluteUrl }">
                  <img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> <span data-bind="text: name"></span>
                </a>
              </li>
            </ul>
            <!-- /ko -->
          </div>
        % endif

        % if mode != 'editor':
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-bars"></i>
          </a>
          <ul class="dropdown-menu pull-right">
            <li>
              <a class="pointer" data-bind="click: function(){ hueUtils.goFullScreen(); $root.isEditing(false); $root.isFullscreenMode(true); $root.isPlayerMode(true);}">
                <i class="fa fa-fw fa-expand"></i> ${ _('Player mode') }
              </a>
            </li>
            <li>
              <a class="pointer" data-bind="click: function() { $root.selectedNotebook().executeAll() }">
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
        % endif

        &nbsp;&nbsp;&nbsp;

        % if mode == 'editor':
        <a class="btn" href="${ url('notebook:editor') }?type=${ editor_type }&new=true" title="${ _('New %s Query') % editor_type.title() }" rel="tooltip" data-placement="bottom">
          <i class="fa fa-file-o"></i>
        </a>
        % else:
        <a class="btn" href="${ url('notebook:new') }" title="${ _('New Notebook') }" rel="tooltip" data-placement="bottom">
          <i class="fa fa-file-o"></i>
        </a>
        % endif

        <a class="btn" href="${ url('notebook:notebooks') }?type=${ editor_type }" title="${ _('Queries' if mode == 'editor' else 'Notebooks') }" rel="tooltip" data-placement="bottom">
          <i class="fa fa-tags"></i>
        </a>
      </div>

      <div class="nav-collapse">
        <ul class="nav editor-nav">
          <li class="currentApp">

            % if mode == 'editor':
              <a href="${ url('notebook:editor') }?type=${ editor_type }" title="${ _('%s Editor') % editor_type.title() }" style="cursor: pointer">
              % if editor_type == 'impala':
                <img src="${ static('impala/art/icon_impala_48.png') }" class="app-icon" />
                Impala
              % elif editor_type == 'rdbms':
                <img src="${ static('rdbms/art/icon_rdbms_48.png') }" class="app-icon" />
                DB Query
              % elif editor_type == 'pig':
                <img src="${ static('pig/art/icon_pig_48.png') }" class="app-icon" />
                Pig
              % elif editor_type in ('beeswax', 'hive'):
                <img src="${ static('beeswax/art/icon_beeswax_48.png') }" class="app-icon" />
                Hive
              % else:
                <img src="${ static('rdbms/art/icon_rdbms_48.png') }" class="app-icon" />
                SQL
              % endif
              </a>
            % else:
              <i class="fa fa-file-text-o app-icon" style="vertical-align: middle"></i>
                Notebook
            % endif
          </li>
          <!-- ko with: selectedNotebook -->
          <li data-bind="visible: isHistory" style="display: none">
            <!-- ko if: parentSavedQueryUuid -->
              <a title="${ _('Open saved query') }" data-bind="click: function() { $root.openNotebook(parentSavedQueryUuid()) }" style="cursor: pointer"><i class="fa fa-fw fa-history"></i></a>
            <!-- /ko -->
            <!-- ko ifnot: parentSavedQueryUuid -->
              <a title="${ _('Query history') }"><i class="fa fa-fw fa-history"></i></a>
            <!-- /ko -->
          </li>
          <li data-bind="visible: directoryUuid" style="display: none">
            <a title="${ _('Open in home directory') }" data-bind="attr: { 'href': '/home?uuid=' + directoryUuid() }" style="cursor: pointer"><i class="fa fa-fw fa-folder-o"></i></a>
          </li>
          <li class="query-name">
            <a href="javascript:void(0)">
              <div class="notebook-name-desc" data-bind="editable: name, editableOptions: { inputclass: 'notebook-name-input', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a name...')}', tpl: '<input type=\'text\' maxlength=\'255\'>' }"></div>
            </a>
          </li>
          <li data-bind="tooltip: { placement: 'bottom', title: description }">
            <a href="javascript:void(0)">
              <div class="notebook-name-desc" data-bind="editable: description, editableOptions: { type: 'textarea', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a description...')}' }"></div>
            </a>
          </li>
          <!-- /ko -->
        </ul>
      </div>
    </div>
  </div>
</div>

 <div class="player-toolbar" data-bind="visible: $root.isPlayerMode() && $root.isFullscreenMode()" style="display: none;">
    <div class="pull-right pointer" data-bind="click: function(){ hueUtils.exitFullScreen(); $root.isPlayerMode(false); $root.isFullscreenMode(false);  }"><i class="fa fa-times"></i></div>
    <img src="${ static('desktop/art/icon_hue_48.png') }" />
    <!-- ko if: $root.selectedNotebook() -->
    <h4 data-bind="text: $root.selectedNotebook().name"></h4>
    <!-- /ko -->
  </div>
</%def>


<%def name="commonHTML()">

<div id="helpModal" class="modal transparent-modal hide" data-backdrop="true" style="width:980px;margin-left:-510px!important">
  <div class="modal-header">
    <a href="javascript: void(0)" data-dismiss="modal" class="pull-right"><i class="fa fa-times"></i></a>
    <h3>${_('Editor keyboard shortcuts')}</h3>
  </div>
  <div class="modal-body">

      <ul class="nav nav-tabs">
        <li class="active"><a href="#helpLineOperations" data-toggle="tab">${ _('Line Operations')}</a></li>
        <li><a href="#helpSelection" data-toggle="tab">${ _('Selection')}</a></li>
        <li><a href="#helpMulticursor" data-toggle="tab">${ _('Multicursor')}</a></li>
        <li><a href="#helpGoTo" data-toggle="tab">${ _('Go to')}</a></li>
        <li><a href="#helpFindReplace" data-toggle="tab">${ _('Find/Replace')}</a></li>
        <li><a href="#helpFolding" data-toggle="tab">${ _('Folding')}</a></li>
        <li><a href="#helpOther" data-toggle="tab">${ _('Other')}</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane active" id="helpLineOperations">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Ctrl-D</td>
          <td>Command-D</td>
          <td>${ _('Remove line')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-Down</td>
          <td>Command-Option-Down</td>
          <td>${ _('Copy lines down')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-Up</td>
          <td>Command-Option-Up</td>
          <td>${ _('Copy lines up')}</td>
        </tr>
        <tr>
          <td>Alt-Down</td>
          <td>Option-Down</td>
          <td>${ _('Move lines down')}</td>
        </tr>
        <tr>
          <td>Alt-Up</td>
          <td>Option-Up</td>
          <td>${ _('Move lines up')}</td>
        </tr>
        <tr>
          <td>Alt-Delete</td>
          <td>Ctrl-K</td>
          <td>${ _('Remove to line end')}</td>
        </tr>
        <tr>
          <td>Alt-Backspace</td>
          <td>Command-Backspace</td>
          <td>${ _('Remove to line start')}</td>
        </tr>
        <tr>
          <td>Ctrl-Backspace</td>
          <td>Option-Backspace, Ctrl-Option-Backspace</td>
          <td>${ _('Remove word left')}</td>
        </tr>
        <tr>
          <td>Ctrl-Delete</td>
          <td>Option-Delete</td>
          <td>${ _('Remove word right')}</td>
        </tr>
        <tr>
          <td>---</td>
          <td>Ctrl-O</td>
          <td>${ _('Split line')}</td>
        </tr>
        </tbody>
      </table>
        </div>
        <div class="tab-pane" id="helpSelection">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Ctrl-A</td>
          <td>Command-A</td>
          <td>${ _('Select all')}</td>
        </tr>
        <tr>
          <td>Shift-Left</td>
          <td>Shift-Left</td>
          <td>${ _('Select left')}</td>
        </tr>
        <tr>
          <td>Shift-Right</td>
          <td>Shift-Right</td>
          <td>${ _('Select right')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-Left</td>
          <td>Option-Shift-Left</td>
          <td>${ _('Select word left')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-Right</td>
          <td>Option-Shift-Right</td>
          <td>${ _('Select word right')}</td>
        </tr>
        <tr>
          <td>Shift-Home</td>
          <td>Shift-Home</td>
          <td>${ _('Select line start')}</td>
        </tr>
        <tr>
          <td>Shift-End</td>
          <td>Shift-End</td>
          <td>${ _('Select line end')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-Right</td>
          <td>Command-Shift-Right</td>
          <td>${ _('Select to line end')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-Left</td>
          <td>Command-Shift-Left</td>
          <td>${ _('Select to line start')}</td>
        </tr>
        <tr>
          <td>Shift-Up</td>
          <td>Shift-Up</td>
          <td>${ _('Select up')}</td>
        </tr>
        <tr>
          <td>Shift-Down</td>
          <td>Shift-Down</td>
          <td>${ _('Select down')}</td>
        </tr>
        <tr>
          <td>Shift-PageUp</td>
          <td>Shift-PageUp</td>
          <td>${ _('Select page up')}</td>
        </tr>
        <tr>
          <td>Shift-PageDown</td>
          <td>Shift-PageDown</td>
          <td>${ _('Select page down')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-Home</td>
          <td>Command-Shift-Up</td>
          <td>${ _('Select to start')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-End</td>
          <td>Command-Shift-Down</td>
          <td>${ _('Select to end')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-D</td>
          <td>Command-Shift-D</td>
          <td>${ _('Duplicate selection')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-P</td>
          <td>---</td>
          <td>${ _('Select to matching bracket')}</td>
        </tr>
        </tbody>
      </table>
        </div>
        <div class="tab-pane" id="helpMulticursor">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Ctrl-Alt-Up</td>
          <td>Ctrl-Option-Up</td>
          <td>${ _('Add multi-cursor above')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Down</td>
          <td>Ctrl-Option-Down</td>
          <td>${ _('Add multi-cursor below')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Right</td>
          <td>Ctrl-Option-Right</td>
          <td>${ _('Add next occurrence to multi-selection')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Left</td>
          <td>Ctrl-Option-Left</td>
          <td>${ _('Add previous occurrence to multi-selection')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Shift-Up</td>
          <td>Ctrl-Option-Shift-Up</td>
          <td>${ _('Move multicursor from current line to the line above')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Shift-Down</td>
          <td>Ctrl-Option-Shift-Down</td>
          <td>${ _('Move multicursor from current line to the line below')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Shift-Right</td>
          <td>Ctrl-Option-Shift-Right</td>
          <td>${ _('Remove current occurrence from multi-selection and move to next')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-Shift-Left</td>
          <td>Ctrl-Option-Shift-Left</td>
          <td>${ _('Remove current occurrence from multi-selection and move to previous')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-L</td>
          <td>Ctrl-Shift-L</td>
          <td>${ _('Select all from multi-selection')}</td>
        </tr>
        </tbody>
      </table>
        </div>
        <div class="tab-pane" id="helpGoTo">
          <table class="table">
      <thead>
      <tr>
        <th>Windows/Linux</th>
        <th>Mac</th>
        <th>${ _('Action')}</th>
      </tr>
      </thead>
      <tbody>
      <tr>
        <td>Left</td>
        <td>Left, Ctrl-B</td>
        <td>${ _('Go to left')}</td>
      </tr>
      <tr>
        <td>Right</td>
        <td>Right, Ctrl-F</td>
        <td>${ _('Go to right')}</td>
      </tr>
      <tr>
        <td>Ctrl-Left</td>
        <td>Option-Left</td>
        <td>${ _('Go to word left')}</td>
      </tr>
      <tr>
        <td>Ctrl-Right</td>
        <td>Option-Right</td>
        <td>${ _('Go to word right')}</td>
      </tr>
      <tr>
        <td>Up</td>
        <td>Up, Ctrl-P</td>
        <td>${ _('Go line up')}</td>
      </tr>
      <tr>
        <td>Down</td>
        <td>Down, Ctrl-N</td>
        <td>${ _('Go line down')}</td>
      </tr>
      <tr>
        <td>Alt-Left, Home</td>
        <td>Command-Left, Home, Ctrl-A</td>
        <td>${ _('Go to line start')}</td>
      </tr>
      <tr>
        <td>Alt-Right, End</td>
        <td>Command-Right, End, Ctrl-E</td>
        <td>${ _('Go to line end')}</td>
      </tr>
      <tr>
        <td>PageUp</td>
        <td>Option-PageUp</td>
        <td>${ _('Go to page up')}</td>
      </tr>
      <tr>
        <td>PageDown</td>
        <td>Option-PageDown, Ctrl-V</td>
        <td>${ _('Go to page down')}</td>
      </tr>
      <tr>
        <td>Ctrl-Home</td>
        <td>Command-Home, Command-Up</td>
        <td>${ _('Go to start')}</td>
      </tr>
      <tr>
        <td>Ctrl-End</td>
        <td>Command-End, Command-Down</td>
        <td>${ _('Go to end')}</td>
      </tr>
      <tr>
        <td>Ctrl-L</td>
        <td>Command-L</td>
        <td>${ _('Go to line')}</td>
      </tr>
      <tr>
        <td>Ctrl-Down</td>
        <td>Command-Down</td>
        <td>${ _('Scroll line down')}</td>
      </tr>
      <tr>
        <td>Ctrl-Up</td>
        <td>---</td>
        <td>${ _('Scroll line up')}</td>
      </tr>
      <tr>
        <td>Ctrl-P</td>
        <td>---</td>
        <td>${ _('Go to matching bracket')}</td>
      </tr>
      <tr>
        <td>---</td>
        <td>Option-PageDown</td>
        <td>${ _('Scroll page down')}</td>
      </tr>
      <tr>
        <td>---</td>
        <td>Option-PageUp</td>
        <td>${ _('Scroll page up')}</td>
      </tr>
      </tbody>
    </table>
        </div>
        <div class="tab-pane" id="helpFindReplace">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Ctrl-F</td>
          <td>Command-F</td>
          <td>${ _('Find')}</td>
        </tr>
        <tr>
          <td>Ctrl-H</td>
          <td>Command-Option-F</td>
          <td>${ _('Replace')}</td>
        </tr>
        <tr>
          <td>Ctrl-K</td>
          <td>Command-G</td>
          <td>${ _('Find next')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-K</td>
          <td>Command-Shift-G</td>
          <td>${ _('Find previous')}</td>
        </tr>
        </tbody>
      </table>
        </div>
        <div class="tab-pane" id="helpFolding">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Alt-L, Ctrl-F1</td>
          <td>Command-Option-L, Command-F1</td>
          <td>${ _('Fold selection')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-L, Ctrl-Shift-F1</td>
          <td>Command-Option-Shift-L, Command-Shift-F1</td>
          <td>${ _('Unfold')}</td>
        </tr>
        <tr>
          <td>Alt-0</td>
          <td>Command-Option-0</td>
          <td>${ _('Fold all')}</td>
        </tr>
        <tr>
          <td>Alt-Shift-0</td>
          <td>Command-Option-Shift-0</td>
          <td>${ _('Unfold all')}</td>
        </tr>
        </tbody>
      </table>
        </div>
        <div class="tab-pane" id="helpOther">
          <table class="table">
        <thead>
        <tr>
          <th>Windows/Linux</th>
          <th>Mac</th>
          <th>${ _('Action')}</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <td>Tab</td>
          <td>Tab</td>
          <td>${ _('Indent')}</td>
        </tr>
        <tr>
          <td>Shift-Tab</td>
          <td>Shift-Tab</td>
          <td>${ _('Outdent')}</td>
        </tr>
        <tr>
          <td>Ctrl-Z</td>
          <td>Command-Z</td>
          <td>${ _('Undo')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-Z, Ctrl-Y</td>
          <td>Command-Shift-Z, Command-Y</td>
          <td>${ _('Redo')}</td>
        </tr>
        <tr>
          <td>Ctrl-,</td>
          <td>Command-,</td>
          <td>${ _('Show the settings menu')}</td>
        </tr>
        <tr>
          <td>Ctrl-/</td>
          <td>Command-/</td>
          <td>${ _('Toggle comment')}</td>
        </tr>
        <tr>
          <td>Ctrl-T</td>
          <td>Ctrl-T</td>
          <td>${ _('Transpose letters')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-U</td>
          <td>Ctrl-Shift-U</td>
          <td>${ _('Change to lower case')}</td>
        </tr>
        <tr>
          <td>Ctrl-U</td>
          <td>Ctrl-U</td>
          <td>${ _('Change to upper case')}</td>
        </tr>
        <tr>
          <td>Insert</td>
          <td>Insert</td>
          <td>${ _('Overwrite')}</td>
        </tr>
        <tr>
          <td>Ctrl-Shift-E</td>
          <td>Command-Shift-E</td>
          <td>${ _('Macros replay')}</td>
        </tr>
        <tr>
          <td>Ctrl-Alt-E</td>
          <td>---</td>
          <td>${ _('Macros recording')}</td>
        </tr>
        <tr>
          <td>Delete</td>
          <td>---</td>
          <td>${ _('Delete')}</td>
        </tr>
        <tr>
          <td>---</td>
          <td>Ctrl-L</td>
          <td>${ _('Center selection')}</td>
        </tr>
        </tbody>
      </table>
        </div>
      </div>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
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

%if ENABLE_QUERY_BUILDER.get():
<div id="invalidQueryBuilder" class="modal hide">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Invalid Query')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('Query requires a select or an aggregate.')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>
%endif

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); huePubSub.publish('assist.set.manual.visibility'); }">
  <i class="fa fa-chevron-right"></i>
</a>


<div data-bind="css: {'main-content': true, 'editor-mode': $root.editorMode}">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() || $root.isPlayerMode() ? '0' : '20px' }" >
    <div class="vertical-full">
      <div class="vertical-full tab-pane row-fluid panel-container" data-bind="css: { active: selectedNotebook() === $data }, template: { name: 'notebook'}">
      </div>
    </div>
  </div>
</div>

<script type="text/html" id="notebook">
  <div class="assist-container left-panel" data-bind="visible: isLeftPanelVisible() && assistAvailable()">
    <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { isLeftPanelVisible(false); huePubSub.publish('assist.set.manual.visibility'); }">
      <i class="fa fa-chevron-left"></i>
    </a>
    <div class="assist" data-bind="component: {
        name: 'assist-panel',
        params: {
          user: user,
          sql: {
            sourceTypes: sqlSourceTypes,
            activeSourceType: activeSqlSourceType,
            navigationSettings: {
              openDatabase: false,
              openItem: false,
              showStats: true
            },
          },
          visibleAssistPanels: editorMode ? ['sql'] : []
        }
      }"></div>
  </div>
  <div class="resizer" data-bind="visible: isLeftPanelVisible() && assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: isLeftPanelVisible, onPosition: function(){ huePubSub.publish('split.draggable.position') } }"><div class="resize-bar">&nbsp;</div></div>
  <div class="right-panel" data-bind="event: { scroll: function(){ $(document).trigger('hideAutocomplete'); } }, niceScroll, with: selectedNotebook">
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
              $element.find('.snippet-body').slideDown('fast', function () { $('.right-panel').scrollTop(lastWindowScrollPosition); });
            },
            'helper': function(event) {
              lastWindowScrollPosition = $('.right-panel').scrollTop();
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
                .find('.hover-actions, .snippet-actions')
                .removeClass('hover-actions')
                .removeClass('snippet-actions');
              $('<pre>')
                .addClass('dragging-pre muted')
                .html(ko.dataFor($element.parents('.card-widget')[0]).statement())
                .appendTo(_par);
              _par.css('height', '100px');
              return _par;
            }
          },
          dragged: function (widget) {
            $('.snippet-body').slideDown('fast', function () { $('.right-panel').scrollTop(lastWindowScrollPosition); });
          }
        }">
      </div>
      %if hasattr(caller, "addSnippetHTML"):
        ${ caller.addSnippetHTML() }
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
</script>

<script type="text/html" id="snippet-log">
  <div class="snippet-log-container margin-bottom-10" data-bind="slideVisible: showLogs() && status() != 'ready' && status() != 'loading', onComplete: function(){ redrawFixedHeaders(200); }" style="display: none;">
    <div data-bind="delayedOverflow, css: resultsKlass" style="margin-top: 5px; position: relative;">
      <ul data-bind="visible: jobs().length > 0, foreach: jobs" class="unstyled jobs-overlay">
        <li><a data-bind="text: $.trim($data.name), attr: { href: $data.url }" target="_blank"></a></li>
      </ul>
      <pre data-bind="visible: result.logs().length == 0" class="logs logs-bigger">${ _('No logs available at this moment.') }</pre>
      <pre data-bind="visible: result.logs().length > 0, text: result.logs, logScroller: result.logs" class="logs logs-bigger logs-populated"></pre>
    </div>
    <div class="snippet-log-resizer" data-bind="visible: result.logs().length > 0, logResizer: {parent: '.snippet-log-container', target: '.logs-populated', onStart: hideFixedHeaders, onResize: function(){ hideFixedHeaders(); redrawFixedHeaders(500); }}">
      <i class="fa fa-ellipsis-h"></i>
    </div>
  </div>
  <div class="snippet-log-container margin-bottom-10">
    <div data-bind="visible: ! result.hasResultset() && status() == 'available' && result.fetchedOnce(), css: resultsKlass, click: function(){  }" style="display:none;">
      <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-check muted"></i> ${ _('Success.') }</pre>
    </div>

    <div data-bind="visible: result.hasResultset() && status() == 'available' && result.data().length == 0 && result.fetchedOnce() && result.explanation().length <= 0, css: resultsKlass" style="display:none;">
      <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-check muted"></i> ${ _("Done. 0 results.") }</pre>
    </div>

    <div data-bind="visible: status() == 'expired', css: resultsKlass" style="display:none;">
      <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-check muted"></i> ${ _("Results have expired, rerun the query if needed.") }</pre>
    </div>

    <div data-bind="visible: status() == 'available' && ! result.fetchedOnce(), css: resultsKlass" style="display:none;">
      <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-spin fa-spinner"></i> ${ _('Loading...') }</pre>
    </div>
  </div>
</script>

<script type="text/html" id="query-tabs">
  <div class="query-history-container" data-bind="onComplete: function(){ redrawFixedHeaders(200); }">
    <div data-bind="delayedOverflow, css: resultsKlass" style="margin-top: 5px; position: relative;">
      <ul class="nav nav-tabs">
        <li data-bind="click: function(){ currentQueryTab('queryHistory'); }, css: {'active': currentQueryTab() == 'queryHistory'}">
          <a class="inactive-action" href="#queryHistory" data-toggle="tab">${_('Query History')}
            <div class="inline-block inactive-action margin-left-10 pointer" title="${_('Clear the query history')}" data-target="#clearHistoryModal" data-toggle="modal" rel="tooltip" data-bind="visible: $parent.history().length > 0"><i class="snippet-icon fa fa-calendar-times-o"></i></div>
          </a>
        </li>
        <li data-bind="click: function(){ currentQueryTab('savedQueries'); }, css: {'active': currentQueryTab() == 'savedQueries'}"><a class="inactive-action" href="#savedQueries" data-toggle="tab">${_('Saved Queries')}</a></li>
        %if ENABLE_QUERY_BUILDER.get():
        <li data-bind="click: function(){ currentQueryTab('queryBuilderTab'); }, css: {'active': currentQueryTab() == 'queryBuilderTab'}"><a class="inactive-action" href="#queryBuilderTab" data-toggle="tab">${_('Query Builder')}</a></li>
        %endif
        <!-- ko if: result.hasSomeResults -->
        <li data-bind="click: function(){ currentQueryTab('queryResults'); }, css: {'active': currentQueryTab() == 'queryResults'}">
          <a class="inactive-action" href="#queryResults" data-toggle="tab">${_('Results')}
            <div class="inline-block inactive-action margin-left-10 pointer" title="${_('Expand results')}" rel="tooltip" data-bind="visible: !$root.isFullscreenMode() && !$root.isPlayerMode(), click: function(){ $root.isPlayerMode(true); }"><i class="snippet-icon fa fa-expand"></i></div>
            <div class="inline-block inactive-action margin-left-10 pointer" title="${_('Collapse results')}" rel="tooltip" data-bind="visible: !$root.isFullscreenMode() && $root.isPlayerMode(), click: function(){ $root.isPlayerMode(false); }"><i class="snippet-icon fa fa-compress"></i></div>
          </a>
        </li>
        <!-- /ko -->
        <!-- ko if: result.explanation().length > 0 -->
        <li data-bind="click: function(){ currentQueryTab('queryExplain'); }, css: {'active': currentQueryTab() == 'queryExplain'}"><a class="inactive-action" href="#queryExplain" data-toggle="tab">${_('Explain')}</a></li>
        <!-- /ko -->
      </ul>
      <div class="tab-content" style="border: none">
        <div class="tab-pane" id="queryHistory" data-bind="css: {'active': currentQueryTab() == 'queryHistory'}">
          <!-- ko if: $parent.loadingHistory -->
          <div style="padding: 20px">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->

          <!-- ko ifnot: $parent.loadingHistory -->
            <!-- ko if: $parent.history().length === 0 -->
            <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("No queries to be shown.") }</div>
            <!-- /ko -->
            <!-- ko if: $parent.history().length > 0 -->
            <table class="table table-condensed margin-top-10 history-table">
              <tbody data-bind="foreach: $parent.history">
                <tr class="pointer" data-bind="click: function() { if (getSelection().toString().length == 0) { $root.openNotebook(uuid()) } }">
                  <td style="width: 100px" class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
                    <span data-bind="momentFromNow: {data: lastExecuted, interval: 10000, titleFormat: 'LLL'}"></span>
                  </td>
                  <td style="width: 25px" class="muted" data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}">
                    <!-- ko switch: status -->
                    <!-- ko case: 'running' -->
                    <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query running") }', placement: 'bottom' }"><i class="fa fa-fighter-jet fa-fw"></i></div>
                    <!-- /ko -->
                    <!-- ko case: 'failed' -->
                    <div class="history-status" data-bind="tooltip: { title: '${ _ko("Query failed") }', placement: 'bottom' }"><i class="fa fa-exclamation fa-fw"></i></div>
                    <!-- /ko -->
                    <!-- ko case: 'available' -->
                    <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result available") }', placement: 'bottom' }"><i class="fa fa-check fa-fw"></i></div>
                    <!-- /ko -->
                    <!-- ko case: 'expired' -->
                    <div class="history-status" data-bind="tooltip: { title: '${ _ko("Result expired") }', placement: 'bottom' }"><i class="fa fa-unlink fa-fw"></i></div>
                    <!-- /ko -->
                    <!-- /ko -->
                  </td>
                  <td style="width: 25px" class="muted" data-bind="ellipsis: {data: name(), length: 30}, style: {'border-top-width': $index() == 0 ? '0' : ''}"></td>
                  <td data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}"><div data-bind="highlight: query(), flavor: $parent.type" class="history-item"></div></td>
                </tr>
              </tbody>
            </table>
            <!-- /ko -->
          <!-- /ko -->
        </div>

        <div class="tab-pane" id="savedQueries" data-bind="css: {'active': currentQueryTab() == 'savedQueries'}">
          <!-- ko if: loadingQueries -->
          <div style="padding: 20px">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->
          <!-- ko if: queriesHasErrors() -->
          <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("Error loading my queries") }</div>
          <!-- /ko -->
          <!-- ko if: ! queriesHasErrors() && ! loadingQueries() && queries().length === 0 -->
          <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("You don't have any saved query.") }</div>
          <!-- /ko -->
          <!-- ko if: ! queriesHasErrors() && ! loadingQueries() && queries().length > 0 -->
          <table class="table table-condensed margin-top-10">
            <thead>
              <tr>
                <th style="width: 16%">${ _("Name") }</th>
                <th style="width: 50%">${ _("Description") }</th>
                <th style="width: 18%">${ _("Owner") }</th>
                <th style="width: 16%">${ _("Last Modified") }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: queries">
            <tr class="pointer" data-bind="click: function() { $root.openNotebook(uuid) }">
              <td style="width: 16%"><span data-bind="ellipsis: {data: name, length: 30}"></span></td>
              <td style="width: 50%; white-space: normal"><span data-bind="text: description"></span></td>
              <td style="width: 18%"><span data-bind="text: owner"></span></td>
              <td style="width: 16%"><span data-bind="text: localeFormat(last_modified)"></span></td>
            </tr>
            </tbody>
          </table>
          <div class="pagination" data-bind="visible: queriesTotalPages() > 1">
            <ul>
              <li data-bind="css: { 'disabled' : queriesCurrentPage() === 1 }"><a href="javascript: void(0);" data-bind="click: prevQueriesPage">${ _("Prev") }</a></li>
              <li class="active"><span data-bind="text: queriesCurrentPage() + '/' + queriesTotalPages()"></span></li>
              <li data-bind="css: { 'disabled' : queriesCurrentPage() === queriesTotalPages() }"><a href="javascript: void(0);" data-bind="click: nextQueriesPage">${ _("Next") }</a></li>
            </ul>
          </div>
          <!-- /ko -->
        </div>
        %if ENABLE_QUERY_BUILDER.get():
        <div class="tab-pane margin-top-10" id="queryBuilderTab" data-bind="css: {'active': currentQueryTab() == 'queryBuilderTab'}">
          <div id="queryBuilderAlert" style="display: none" class="alert">${ _('There are currently no rules defined. To get started, right click on any table column in the SQL Assist panel.') }</div>
          <table id="queryBuilder" class="table table-condensed">
            <thead>
              <tr>
                <th width="10%">${ _('Table') }</th>
                <th>${ _('Column') }</th>
                <th width="10%">${ _('Operation') }</th>
                <th width="1%">&nbsp;</th>
              </tr>
            </thead>
          </table>
          <div class="button-panel">
            <button class="btn btn-primary disable-feedback" data-bind="click: generateQuery">${_('Build query')}</button>
          </div>
        </div>
        %endif
        <div class="tab-pane" id="queryResults" data-bind="css: {'active': currentQueryTab() == 'queryResults'}">
          <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'snippet-results' } --><!-- /ko -->
        </div>
        <!-- ko if: result.explanation().length > 0 -->
        <div class="tab-pane" id="queryExplain" data-bind="css: {'active': currentQueryTab() == 'queryExplain'}">
          <!-- ko template: { name: 'snippet-explain' } --><!-- /ko -->
        </div>
        <!-- /ko -->
      </div>

    </div>
  </div>
</script>

<script type="text/html" id="notebook-snippet-header">
  <div class="inactive-action hover-actions inline"><span class="inactive-action" data-bind="css: { 'empty-title': name() === '' }, editable: name, editableOptions: { emptytext: '${_ko('My Snippet')}', mode: 'inline', enabled: true, placement: 'right' }" style="border:none;color: #DDD"></span></div>
  <div class="hover-actions inline pull-right" style="font-size: 15px;">
    <a class="inactive-action" href="javascript:void(0)" data-bind="visible: status() != 'ready' && status() != 'loading' && errors().length == 0, click: function() { hideFixedHeaders(); $data.showLogs(!$data.showLogs());}, css: {'blue': $data.showLogs}" title="${ _('Show Logs') }"><i class="fa fa-file-text-o"></i></a>
    <span class="execution-timer" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>
    <a class="inactive-action move-widget" href="javascript:void(0)"><i class="fa fa-arrows"></i></a>
    <a class="inactive-action" href="javascript:void(0)" data-bind="toggle: settingsVisible, visible: hasProperties, css: { 'blue' : settingsVisible }" title="${ _('Settings and properties') }"><i class="fa fa-cog"></i></a>
    <a class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ $root.removeSnippet($parent, $data); }"><i class="fa fa-times"></i></a>
  </div>
</script>

<script type="text/html" id="editor-snippet-header">
  <div class="hover-actions inline pull-right" style="font-size: 15px; position: relative;">
    <span class="execution-timer" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>
    <!-- ko if: availableDatabases().length > 0 -->
    <a class="inactive-action active-database margin-left-10" href="javascript:void(0)" data-toggle="dropdown" data-bind="toggle: dbSelectionVisible, css: { 'blue': dbSelectionVisible }"><span data-bind="visible: isSqlDialect, text: database"  title="${ _('Selected database') }"></span> <i class="fa fa-caret-down"></i></a>
    <div class="dropdown-menu" style="overflow-y: scroll; min-width: 170px; min-height: 34px; max-height: 200px;">
      <ul class="hue-inner-drop-down" data-bind="foreachVisible: { data: availableDatabases, minHeight: 34, container: '.dropdown-menu' }">
        <li><a href="javascript:void(0)" data-bind="text: $data, click: function () { $parent.database($data); }"></a></li>
      </ul>
    </div>
    <!-- /ko -->
    <a class="inactive-action margin-left-10" href="javascript:void(0)" data-bind="visible: status() != 'ready' && status() != 'loading', click: function() { hideFixedHeaders(); $data.showLogs(!$data.showLogs());}, css: {'blue': $data.showLogs}" title="${ _('Show Logs') }"><i class="fa fa-file-text-o"></i></a>
    <a class="inactive-action margin-left-10" href="javascript:void(0)" data-bind="toggle: settingsVisible, visible: hasProperties, css: { 'blue' : settingsVisible }" title="${ _('Settings and properties') }"><i class="fa fa-cog"></i></a>
    <a class="inactive-action margin-left-10" href="javascript:void(0)" title="${ _('Show editor shortcuts') }" data-toggle="modal" data-target="#helpModal"><i class="fa fa-question"></i></a>
  </div>
</script>

<script type="text/html" id="snippet">
  <div data-bind="visibleOnHover: { override: inFocus() || settingsVisible() || dbSelectionVisible() || $root.editorMode, selector: '.hover-actions' }">
    <div class="snippet-container row-fluid" data-bind="visibleOnHover: { override: $root.editorMode || inFocus, selector: '.snippet-actions' }">
      <div class="snippet card card-widget" data-bind="css: {'notebook-snippet' : ! $root.editorMode, 'editor-mode': $root.editorMode, 'active-editor': inFocus, 'snippet-text' : type() == 'text'}, attr: {'id': 'snippet_' + id()}, clickForAceFocus: ace">
        <div style="position: relative;">
          <div class="snippet-row" style="position: relative;">
            <div class="snippet-left-bar">
              <!-- ko template: { if: ! $root.editorMode, name: 'notebook-snippet-type-controls' } --><!-- /ko -->
              <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-execution-controls' } --><!-- /ko -->
            </div>
            <div class="snippet-body" data-bind="clickForAceFocus: ace">
              <h5 class="card-heading-print" data-bind="text: name, css: {'visible': name() != ''}"></h5>

              <h2 style="margin-left:5px;padding: 3px 0" class="card-heading simple" data-bind="dblclick: function(){ if (!$root.editorMode) { $parent.newSnippetAbove(id()) } }, clickForAceFocus: ace">
                <!-- ko template: { if: $root.editorMode, name: 'editor-snippet-header' } --><!-- /ko -->
                <!-- ko template: { if: ! $root.editorMode, name: 'notebook-snippet-header' } --><!-- /ko -->
              </h2>
              <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'code-editor-snippet-body' } --><!-- /ko -->
              <!-- ko template: { if: type() == 'text', name: 'text-snippet-body' } --><!-- /ko -->
              <!-- ko template: { if: type() == 'markdown', name: 'markdown-snippet-body' } --><!-- /ko -->
              <!-- ko template: { if: type() == 'jar' || type() == 'py', name: 'executable-snippet-body' } --><!-- /ko -->
            </div>
            <div style="position: absolute; top:25px; margin-left:35px; width: calc(100% - 35px)" data-bind="style: { 'z-index': 400 - $index() }">
              <!-- ko template: 'snippet-settings' --><!-- /ko -->
            </div>
          </div>
          <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-execution-status' } --><!-- /ko -->
          <!-- ko template: { if: $root.editorMode, name: 'snippet-code-resizer' } --><!-- /ko -->
          <!-- ko if: $root.editorMode -->
          <!-- ko template: 'snippet-log' --><!-- /ko -->
          <!-- ko template: 'query-tabs' --><!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: $root.editorMode -->
          <!-- ko template: 'snippet-log' --><!-- /ko -->
          <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'snippet-results' } --><!-- /ko -->
          <!-- /ko -->

          <div class="clearfix"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-settings">
  <div class="snippet-settings" data-bind="slideVisible: settingsVisible" style="position: relative; z-index: 100;">
    <div class="snippet-settings-header">
      <h4><i class="fa fa-cog"></i> ${ _('Settings') }</h4>
    </div>
    <div class="snippet-settings-body">
      <form class="form-horizontal">
        <!-- ko template: { if: typeof properties().driverCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Driver Cores') }', value: properties().driverCores, title: '${ _ko('Number of cores used by the driver, only in cluster mode (Default: 1)') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().executorCores != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Executor Cores') }', value: properties().executorCores, title: '${ _ko('Number of cores per executor (Default: 1)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().numExecutors != 'undefined', name: 'property', data: { type: 'number', label: '${ _ko('Executors') }', value: properties().numExecutors, title: '${ _ko('Number of executors to launch (Default: 2)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().queue != 'undefined', name: 'property', data: { type: 'string', label: '${ _ko('Queue') }', value: properties().queue, title: '${ _ko('The YARN queue to submit to (Default: default)') }' }} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().archives != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Archives') }', value: properties().archives, title: '${ _ko('Archives to be extracted into the working directory of each executor (YARN only)') }', placeholder: '${ _ko('e.g. file.zip') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().files != 'undefined', name: 'property', data: { type: 'hdfs-files', label: '${ _ko('Files') }', value: properties().files, visibleObservable: settingsVisible, title: '${ _ko('Files to be placed in the working directory of each executor.') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().functions != 'undefined', name: 'property', data: { type: 'functions', label: '${ _ko('Functions') }', value: properties().functions, visibleObservable: settingsVisible, title: '${ _ko('UDFs name and class') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().settings != 'undefined', name: 'property', data: { type: 'settings', label: '${ _ko('Settings') }', value: properties().settings, visibleObservable: settingsVisible, title: '${ _ko('Properties') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().parameters != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Parameters') }', value: properties().parameters, title: '${ _ko('Names and values of Pig parameters and options') }', placeholder: '${ _ko('e.g. input /user/data, -param input=/user/data, -optimizer_off SplitFilter, -verbose') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Hadoop properties') }', value: properties().hadoopProperties, title: '${ _ko('Name and values of Hadoop properties') }', placeholder: '${ _ko('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().resources != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Resources') }', value: properties().resources, title: '${ _ko('HDFS Files or compressed files') }', placeholder: '${ _ko('e.g. /tmp/file, /tmp.file.zip') }'}} --><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="code-editor-snippet-body">
  <div class="alert alert-gradient" data-bind="visible: is_redacted">
    <div style="float:left;">
      <svg class="hi" style="height: 20px; width: 20px;">
        <use xlink:href="#hi-warning"></use>
      </svg>
    </div>
    <div style="margin-left: 30px; line-height:20px;vertical-align: middle;">${ _('The current query has been redacted to hide sensitive information.') }</div>
  </div>
  <div class="alert alert-error alert-error-gradient" data-bind="visible: hasComplexity">
    <div style="float:left;">
      <svg class="hi" style="height: 20px; width: 20px;">
        <use xlink:href="#hi-warning"></use>
      </svg>
    </div>
    <div style="margin-left: 30px; line-height:20px;vertical-align: middle;">
      <span style="margin-right:10px; font-weight: bold;" data-bind="text: complexityLevel"></span><span data-bind="text: complexity"></span>
    </div>
  </div>
  <div class="alert" data-bind="visible: hasSuggestion">
    <div style="float:left;">
      <svg class="hi" style="height: 20px; width: 20px;">
        <use xlink:href="#hi-warning"></use>
      </svg>
    </div>
    <div style="margin-left: 30px; line-height:20px;vertical-align: middle;">
      <!-- ko if: hasSuggestion -->
      <!-- ko with: suggestion() -->
      <!-- ko if: queryStatus() == 'SUCCESS' -->
        ${ _('The query is compatible! Click to') } <a href="/notebook/editor?type=impala">${ _('execute') }</a> ${ _('with Impala') }.
      <!-- /ko -->
      <!-- ko if: errorDetail.errorString -->
        ${ _('Query is not compatible with Impala') }.
        </br>
        <span style="font-weight: bold;"></span><span data-bind="text: errorDetail.errorString"></span>
      <!-- /ko -->
      <!-- ko if: clauseStatus.From -->
        </br>
        <!-- ko if: clauseStatus.From.category -->
          <span style="font-weight: bold;"></span><span data-bind="text: clauseStatus.From.category"></span>
        <!-- /ko -->
        <!-- ko if: clauseStatus.From.suggestedFix -->
          <span style="font-weight: bold;"></span><span data-bind="text: clauseStatus.From.suggestedFix"></span>
        <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </div>
  <div class="row-fluid" style="margin-bottom: 5px">
    <div class="editor span12" data-bind="css: {'single-snippet-editor ace-container-resizable' : $root.editorMode }, clickForAceFocus: ace">
      <div class="ace-editor" data-bind="css: {'single-snippet-editor ace-editor-resizable' : $root.editorMode, 'active-editor': inFocus }, attr: { id: id() }, delayedOverflow, aceEditor: {
        snippet: $data,
        openIt: '${ _ko("Alt or Ctrl + Click to open it") }',
        expandStar: '${ _ko("Alt or Ctrl + Click to replace with all columns") }',
        onBlur: saveTemporarySnippet,
        highlightedRange: result.statement_range,
        aceOptions: {
          showLineNumbers: $root.editorMode,
          showGutter: $root.editorMode,
          maxLines: $root.editorMode ? null : 25,
          minLines: $root.editorMode ? null : 3
        }
      }"></div>
      <ul class="table-drop-menu hue-context-menu">
        <li class="editor-drop-value"><a href="javascript:void(0);">"<span class="editor-drop-identifier"></span>"</a></li>
        <li class="divider"></li>
        <li class="editor-drop-select"><a href="javascript:void(0);">${ _('SELECT FROM ') } <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-insert"><a href="javascript:void(0);">${ _('INSERT INTO') } <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-update"><a href="javascript:void(0);">${ _('UPDATE') } <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-delete"><a href="javascript:void(0);">${ _('DELETE FROM') } <span class="editor-drop-identifier"></span>...</a></li>
      </ul>
    </div>
    <div class="clearfix"></div>
    <ul data-bind="foreach: variables" class="unstyled inline">
        <li>
          <div class="input-prepend margin-top-10">
            <span class="muted add-on" data-bind="text: name"></span>
            <input class="input-medium" type="text" placeholder="${ _("Variable value") }" data-bind="value: value, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
          </div>
        </li>
      </ul>
  </div>
  <div class="clearfix"></div>

</script>

<script type="text/html" id="snippet-chart-settings">
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
</script>

<script type="text/html" id="snippet-grid-settings">
  <div style="overflow:auto">
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header pointer" data-bind="click: toggleResultSettings" title="${_('Hide columns')}">${_('columns')}</li>
    </ul>
    <ul class="unstyled" data-bind="foreach: result.meta">
      <li data-bind="visible: name != ''">
        <input type="checkbox" checked="checked" data-bind="event: { change: function(){toggleColumn($element, $index());}}" />
        <a class="pointer" data-bind="text: $data.name, click: function(){ scrollToColumn($element, $index()); }, attr: { title: $data.type + ' ' + '${ _('Click to scroll to data') }'}"></a>
      </li>
    </ul>
  </div>
</script>

<script type="text/html" id="snippet-settings-toggle">
  <div style="position:absolute;right:0;top:0;margin-top:130px;" data-bind="attr: { 'id': 'toggleResultSettingsGrid' + id() }, click: toggleResultSettings" class="hover-actions toggle-result-settings show-result-settings">
    <a class="inactive-action pointer" title="${_('Hide settings')}" data-bind="visible: isResultSettingsVisible">
      <i class="fa fa-chevron-left"></i>
    </a>
  </div>
</script>

<script type="text/html" id="snippet-explain">
  <pre class="no-margin-bottom" data-bind="text: result.explanation"></pre>
</script>

<script type="text/html" id="snippet-results">
  <div class="snippet-row" data-bind="slideVisible: result.hasSomeResults">
    <div class="snippet-left-bar">
      <!-- ko template: { if: result.type() == 'table' && result.hasSomeResults(), name: 'snippet-result-controls' }--><!-- /ko -->
    </div>
    <div class="result-body">
      <div class="row-fluid" data-bind="visible: result.type() != 'table'" style="display:none; max-height: 400px; margin: 10px 0; overflow-y: auto">
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

      <div class="row-fluid table-results" data-bind="visible: result.type() == 'table', style: {'min-height': $root.editorMode ? '230px' : '130px'}" style="display: none; max-height: 400px;">
        <div>
          <div data-bind="visible: isResultSettingsVisible, css:{'span2 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}" style="position:relative;padding-right:15px;white-space: nowrap;">
            <!-- ko template: { name: 'snippet-grid-settings', if: showGrid } --><!-- /ko -->
            <!-- ko template: { name: 'snippet-chart-settings', if: showChart } --><!-- /ko -->
            <!-- ko template: 'snippet-settings-toggle' --><!-- /ko -->
          </div>
          <div data-bind="css: {'span10': isResultSettingsVisible, 'span12 nomargin': ! isResultSettingsVisible() }">
            <div data-bind="visible: showGrid; delayedOverflow, css: resultsKlass" style="display: none;">
              <table class="table table-condensed table-striped resultTable">
                <thead>
                <tr data-bind="foreach: result.meta">
                  <th data-bind="html: ($index() == 0 ? '&nbsp;' : $data.name), css: { 'sort-numeric': isNumericColumn($data.type), 'sort-date': isDateTimeColumn($data.type), 'sort-string': isStringColumn($data.type)}, attr: {'width': ($index() == 0 ? '1%' : ''), title: $data.type }"></th>
                </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
            </div>

            <div data-bind="visible: showChart" class="chart-container" style="display:none;">
              <h1 class="empty" data-bind="visible: !hasDataForChart()">${ _('Select the chart parameters on the left') }</h1>

              <div data-bind="visible: hasDataForChart">
                <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]),
                      transformer: pieChartDataTransformer, maxWidth: 350, parentSelector: '.chart-container' }, visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>

                <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data}, fqs: ko.observableArray([]), hideSelection: true,
                      transformer: multiSerieDataTransformer, stacked: false, showLegend: true},  stacked: true, showLegend: true, visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>

                <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data},
                      transformer: multiSerieDataTransformer, showControls: false, enableSelection: false }, visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>

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
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="text-snippet-body">
  <div data-bind="attr:{'id': 'editor_' + id()}, html: statement_raw, value: statement_raw, medium: {}" data-placeHolder="${ _('Type your text here, select some text to format it') }" class="text-snippet"></div>
</script>


<script type="text/html" id="markdown-snippet-body">
  <!-- ko ifnot: $root.isPlayerMode() -->
  <div class="row-fluid">
    <div class="span6" data-bind="clickForAceFocus: ace">
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
  <!-- ko if: $root.isPlayerMode() -->
  <div data-bind="html: renderMarkdown(statement_raw(), id())"></div>
  <!-- /ko -->
</script>


<script type="text/html" id="executable-snippet-body">
  <div style="padding:10px;">
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
      <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Arguments') }', value: properties().arguments, title: '${ _ko('The YARN queue to submit to (Default: default)') }', placeholder: '${ _ko('e.g. -foo=bar') }', inline: false }} --><!-- /ko -->
    </form>
  </div>
</script>

<script type="text/html" id="snippet-execution-status">
  <div class="snippet-execution-status" data-bind="clickForAceFocus: ace">
    <div class="snippet-progress-container">
      <div class="progress active" data-bind="css: {
        'progress-starting': progress() == 0 && status() == 'running',
        'progress-warning': progress() > 0 && progress() < 100,
        'progress-success': progress() == 100,
        'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%">
        <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : Math.max(2,progress())) + '%'}"></div>
      </div>
    </div>
    <div class="snippet-error-container alert alert-error alert-error-gradient" style="margin-bottom: 0" data-bind="visible: errors().length > 0">
      <ul class="unstyled" data-bind="foreach: errors">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <div class="snippet-error-container alert alert-error alert-error-gradient" style="margin-bottom: 0" data-bind="visible: status() == 'canceled'">
      <ul class="unstyled">
        <li>${ _("The statement was canceled.") }</li>
      </ul>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-code-resizer">
  <div class="snippet-code-resizer" data-bind="aceResizer : { ace: ace, target: '.ace-container-resizable', onStart: hideFixedHeaders }">
    <i class="fa fa-ellipsis-h"></i>
  </div>
</script>

<script type="text/html" id="notebook-snippet-type-controls">
  <div class="inactive-action dropdown hover-actions">
    <a class="snippet-side-btn" style="padding-right: 0; padding-left: 2px;" data-toggle="dropdown" href="javascript: void(0);">
      <span data-bind="template: { name: 'snippetIcon', data: $data }"></span>
    </a>
    <a class="inactive-action dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0);">
      <i class="fa fa-caret-down"></i>
    </a>

    <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
      <li><a class="pointer" data-bind="click: function(){ $parent.type($data.type()); }, text: name"></a></li>
    </ul>
  </div>
</script>

<script type ="text/html" id="snippet-execution-controls">
  <div class="snippet-actions" style="position: absolute; bottom: 0">
    <a class="snippet-side-btn blue" style="cursor: default;" data-bind="visible: status() == 'loading'" title="${ _('Creating session') }">
      <i class="fa fa-fw fa-spinner fa-spin"></i>
    </a>
    <a class="snippet-side-btn" data-bind="click: reexecute, visible: $root.editorMode && result.handle() && result.handle().has_more_statements, css: {'blue': $parent.history().length == 0 || $root.editorMode, 'disabled': statement() === '' }" title="${ _('Restart from the first statement') }">
      <i class="fa fa-fw fa-repeat snippet-side-single"></i>
    </a>
    <div class="label label-info" data-bind="attr: {'title':'${ _ko('Showing results of the statement #')}' + (result.statement_id() + 1)}, visible: $root.editorMode && result.statements_count() > 1">
      <span data-bind="text: result.statement_id() + 1"></span>/<span data-bind="text: result.statements_count()"></span>
    </div>
    <a class="snippet-side-btn blue" data-bind="click: cancel, visible: status() == 'running'" title="${ _('Stop the currently running statement') }">
      <i class="fa fa-fw fa-stop snippet-side-single"></i>
    </a>
    <a class="snippet-side-btn" data-bind="attr: {'title': $root.editorMode && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: execute, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode, 'disabled': statement() === '' }">
      <i class="fa fa-fw fa-play snippet-side-single"></i>
    </a>
    <!-- ko if: isSqlDialect -->
    <div class="inactive-action dropdown hover-actions pointer" data-bind="css: {'disabled': statement() === '' || status() === 'running' || status() === 'loading' }">
      <a class="snippet-side-btn" style="padding-right:0; padding-left: 2px;" href="javascript: void(0)" data-bind="click: explain, css: {'disabled': statement() === '' || status() === 'running' || status() === 'loading', 'blue': currentQueryTab() == 'queryExplain' }" title="${ _('Explain the current SQL query') }">
        <i class="fa fa-fw fa-map-o"></i>
      </a>
      <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'disabled': statement() === '', 'blue': currentQueryTab() == 'queryExplain' }">
        <i class="fa fa-caret-down"></i>
      </a>

      <ul class="dropdown-menu less-padding">
        <li>
          <a href="javascript:void(0)" data-bind="click: explain, style: { color: statement() === '' || status() === 'running' || status() === 'loading' ? '#999' : ''}, css: {'disabled': statement() === '' || status() === 'running' || status() === 'loading' }" title="${ _('Explain the current SQL query') }">
            <i class="fa fa-fw fa-map-o"></i> ${_('Explain')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: format, css: {'disabled': statement() === '' }" title="${ _('Format the current SQL query') }">
            <i class="fa fa-fw fa-indent"></i> ${_('Format')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: clear, css: {'disabled': statement() === '' }" title="${ _('Clear the current editor') }">
            <i class="fa fa-fw fa-eraser"></i> ${_('Clear')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="click: queryCompatibility, visible: $root.isOptimizerEnabled" title="${ _('Get Impala compatibility hints') }">
            <i class="fa fa-fw fa-random"></i> ${_('Check Impala compatibility')}
          </a>
        </li>
      </ul>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="snippet-result-controls">
  <div class="snippet-actions" style="opacity:1">
    <div style="margin-top:25px;">
      <a class="snippet-side-btn" href="javascript: void(0)" data-bind="click: function() { $data.showGrid(true); huePubSub.publish('redraw.fixed.headers'); }, css: {'active': $data.showGrid}" title="${ _('Grid') }">
        <i class="fa fa-fw fa-th"></i>
      </a>
    </div>

    <div class="dropdown">
      <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="css: {'active': $data.showChart }, click: function() { $data.showChart(true); }">
        <i class="hcha fa-fw hcha-bar-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART"></i>
        <i class="hcha fa-fw hcha-line-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART"></i>
        <i class="hcha fa-fw hcha-pie-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART"></i>
        <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART"></i>
        <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP"></i>
        <i class="hcha fa-fw hcha-map-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP"></i>
      </a>
      <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'active': $data.showChart}">
        <i class="fa fa-caret-down"></i>
      </a>

      <ul class="dropdown-menu less-padding">
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

    <div>
      <a class="snippet-side-btn" href="javascript:void(0)" data-bind="click: function(){ isResultSettingsVisible(! isResultSettingsVisible()) }, css: { 'blue' : isResultSettingsVisible }"><i class="fa fa-fw fa-cog"></i></a>
    </div>

    <div data-bind="component: { name: 'downloadSnippetResults', params: { snippet: $data, notebook: $parent } }" style="display:inline-block;"></div>
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
    <a class="btn" data-bind="click: function() { $root.removeSnippetConfirmation(null); $('#removeSnippetModal').modal('hide'); }">${_('No')}</a>
    <input type="submit" value="${_('Yes')}" class="btn btn-danger" data-bind="click: function() { notebook.snippets.remove(snippet); redrawFixedHeaders(100); $root.removeSnippetConfirmation(null); $('#removeSnippetModal').modal('hide'); }" />
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
            <h4 data-bind="text: $root.getSnippetName(type())" style="clear:left; display: inline-block"></h4>
            <div class="session-actions">
              <a class="inactive-action pointer" title="${ _('Recreate session') }" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().restartSession($data) }"><i class="fa fa-refresh" data-bind="css: { 'fa-spin': restarting }"></i> ${ _('Recreate') }</a>
              <a class="inactive-action pointer margin-left-10" title="${ _('Close session') }" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().closeAndRemoveSession($data) }"><i class="fa fa-times"></i> ${ _('Close') }</a>
              <a class="inactive-action pointer margin-left-10" title="${ _('Save session settings as default') }" rel="tooltip" data-bind="click: function() { $root.selectedNotebook().saveDefaultUserProperties($data) }"><i class="fa fa-save"></i> ${ _('Set as default settings') }</a>
            </div>
            <!-- ko if: type()== 'impala' && typeof properties != 'undefined' -->

            <ul class="nav nav-list" style="border: none; padding: 0;">
              <li class="nav-header">${ _('address')}</li>
            </ul>
            <div style="margin: 2px" data-bind="with: ko.utils.arrayFirst(properties(), function(item) { return item.key() == 'http_addr' });">
              <a data-bind="attr: {'href': window.location.protocol + '//' + $data.value().replace(/^(https?):\/\//, '')}" target="_blank">
                <span data-bind="text: $data.value().replace(/^(https?):\/\//, '')"></span>
                <i class="fa fa-external-link"></i>
              </a>
            </div>
            <!-- /ko -->
            <div style="width:100%;">
                <!-- ko foreach: properties -->
                  <!-- ko template: {
                    name: 'property',
                    data: {
                      type: type(),
                      label: nice_name,
                      helpText: help_text,
                      value: value,
                      visibleObservable: ko.observable()
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
              </div>
              <!-- /ko -->
            <!-- /ko -->
            <br/>
          </fieldset>
        </form>
        <!-- /ko -->
      </div>
    </div>

  </div>
  <div style="position:absolute; width:100%; bottom: 0;"><a class="pointer demi-modal-chevron" data-dismiss="modal"><i class="fa fa-chevron-up"></i></a></div>
</div>


<div class="hoverMsg hide">
  <!-- ko if: $root.editorMode -->
  <p class="hoverText">${_('Drop a SQL file here')}</p>
  <!-- /ko -->
  <!-- ko ifnot: $root.editorMode -->
  <p class="hoverText">${_('Drop iPython/Zeppelin notebooks here')}</p>
  <!-- /ko -->
</div>


<div id="saveAsModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <!-- ko if: $root.editorMode -->
      <h3>${_('Save query as...')}</h3>
    <!-- /ko -->
    <!-- ko ifnot: $root.editorMode -->
      <h3>${_('Save notebook as...')}</h3>
    <!-- /ko -->
  </div>

  <!-- ko if: $root.selectedNotebook() -->
  <div class="modal-body">
    <form class="form-horizontal">
      <div class="control-group">
        <label class="control-label">${_('Name')}</label>
        <div class="controls">
          <input type="text" class="input-xlarge" data-bind="value: $root.selectedNotebook().name, valueUpdate:'afterkeydown'"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Description')}</label>
        <div class="controls">
          <input type="text" class="input-xlarge" data-bind="value: $root.selectedNotebook().description, valueUpdate:'afterkeydown'" placeholder="${ _('(optional)') }"/>
        </div>
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <input type="button" class="btn btn-primary disable-feedback" value="${_('Save')}" data-dismiss="modal" data-bind="click: saveAsNotebook, enable: $root.selectedNotebook().name().length > 0"></input>
  </div>
  <!-- /ko -->
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


<div id="clearHistoryModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Confirm History Clear')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to clear the query history?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger disable-feedback" data-bind="click: function() { $root.selectedNotebook().clearHistory(); }">${_('Yes')}</a>
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

  var hideHoverMsg = function (vm) {
    if (vm.editorMode){
      $(".hoverText").html("${_('Drop a SQL file here')}");
    }
    else {
      $(".hoverText").html("${_('Drop iPython/Zeppelin notebooks here')}");
    }
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

  function createDatatable(el, snippet, vm) {
    $(el).addClass("dt");
    var DATATABLES_MAX_HEIGHT = 330;
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
        if (vm.editorMode){
          DATATABLES_MAX_HEIGHT = $(window).height() - $(el).parent().offset().top - 40;
        }
        if (vm.editorMode) {
          $(el).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
          $(el).jHueTableExtender({
            fixedHeader: true,
            fixedFirstColumn: true,
            includeNavigator: false,
            parentId: 'snippet_' + snippet.id(),
            mainScrollable: '.right-panel',
            stickToTopPosition: vm.isPlayerMode() ? 1 : 73,
            clonedContainerPosition: "fixed"
          });
          $(el).jHueHorizontalScrollbar();
        }
        else {
          $(el).parents(".dataTables_wrapper").jHueTableScroller({
            maxHeight: DATATABLES_MAX_HEIGHT,
            heightAfterCorrection: 0
          });
          $(el).jHueTableExtender({
            fixedHeader: true,
            fixedFirstColumn: true,
            includeNavigator: false,
            mainScrollable: '.right-panel',
            parentId: 'snippet_' + snippet.id(),
            clonedContainerPosition: "absolute"
          });
        }
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

    if (vm.editorMode) {
      $(el).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
      $(el).jHueTableExtender({
        fixedHeader: true,
        fixedFirstColumn: true,
        includeNavigator: false,
        parentId: 'snippet_' + snippet.id(),
        mainScrollable: '.right-panel',
        stickToTopPosition: vm.isPlayerMode() ? (vm.isFullscreenMode() ? 48 : 0) : 73,
        clonedContainerPosition: "fixed"
      });
      $(el).jHueHorizontalScrollbar();
    }
    else {
      $(el).parents(".dataTables_wrapper").jHueTableScroller({
        maxHeight: DATATABLES_MAX_HEIGHT,
        heightAfterCorrection: 0,
        enableNiceScroll: true
      });
      $(el).jHueTableExtender({
        fixedHeader: true,
        fixedFirstColumn: true,
        includeNavigator: false,
        mainScrollable: '.right-panel',
        parentId: 'snippet_' + snippet.id(),
        clonedContainerPosition: "absolute"
      });
    }
    $(".dataTables_filter").hide();
    var dataTableEl = $(el).parents(".dataTables_wrapper");

    if (!vm.editorMode) {
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
    }

    var _scrollTimeout = -1;

    var scrollElement = dataTableEl;
    if (vm.editorMode) {
      scrollElement = $('.right-panel');
    }

    scrollElement.on('scroll', function () {
      var _lastScrollPosition = scrollElement.data("scrollPosition") != null ? scrollElement.data("scrollPosition") : 0;
      window.clearTimeout(_scrollTimeout);
      scrollElement.data("scrollPosition", scrollElement.scrollTop());
      _scrollTimeout = window.setTimeout(function () {
        if (vm.editorMode){
          _lastScrollPosition--; //hack for forcing fetching
        }
        if (_lastScrollPosition != scrollElement.scrollTop() && scrollElement.scrollTop() + scrollElement.outerHeight() + 20 >= scrollElement[0].scrollHeight && _dt && snippet.result.hasMore()) {
          dataTableEl.animate({opacity: '0.55'}, 200);
          snippet.fetchResult(100, false);
        }
      }, 100);
    });

    return _dt;
  }

  function toggleColumn(linkElement, index) {
    var _dt = $(linkElement).parents(".snippet").find("table.resultTable:eq(0)").dataTable();
    _dt.fnSetColumnVis(index, !_dt.fnSettings().aoColumns[index].bVisible);
  }

  function scrollToColumn(linkElement) {
    var _t = $(linkElement).parents(".snippet").find("table.resultTable:eq(0)");
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
        var val = item[_idxValue] * 1;
        if (isNaN(val)) {
          val = 0;
        }
        _data.push({
          label: hueUtils.html2text(item[_idxLabel]),
          value: val,
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
            label: hueUtils.html2text(item[_idxLabel]),
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
        var _isXDate = false;
        rawDatum.snippet.result.meta().forEach(function (icol, idx) {
          if (icol.name == rawDatum.snippet.chartX()) {
            _isXDate = icol.type.toUpperCase().indexOf('DATE') > -1;
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
              x: _isXDate ? moment(item[_idxLabel]) : hueUtils.html2text(item[_idxLabel]),
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

  function saveTemporarySnippet($element, value) {
    if ($element.data('last-active-editor')) {
      try {
        %if editor_type:
        $.totalStorage('hue.notebook.lastWrittenSnippet.${user}.${editor_type}', value);
        %endif
      }
      catch (e){} // storage quota exceeded with enormous editor content
    }
  }

  require([
    "knockout",
    "ko.charts",
    "notebook/js/notebook.ko",
    "assistPanel",
    "knockout-mapping",
    "knockout-sortable",
    "ko.editable",
    "ko.hue-bindings",
    "ko.switch-case"
  ], function (ko, charts, EditorViewModel) {

    ko.options.deferUpdates = true;

    var VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode }, {
      user: '${ user.username }',
      userId: ${ user.id },
      assistAvailable: true,
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
        oracle: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/oracle',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        pig: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/pig',
          snippetImage: '${ static("pig/art/icon_pig_48.png") }'
        },
        postgresql: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/pgsql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        solr: {
          placeHolder: '${ _("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space") }',
          aceMode: 'ace/mode/mysql',
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
        scala: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/scala',
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        spark: {
          placeHolder: '${ _("Example: 1 + 1, or press CTRL + space") }',
          aceMode: 'ace/mode/scala',
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        sqlite: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/sqlite',
          snippetIcon: 'fa-database',
          sqlDialect: true
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
      var currentNotebook = viewModel.selectedNotebook();
      currentNotebook.name(notebook.name);
      currentNotebook.description(notebook.description);
      currentNotebook.selectedSnippet(notebook.selectedSnippet);
      notebook.snippets.forEach(function(snippet){
        var newSnippet = currentNotebook.addSnippet({
          type: snippet.type,
          result: {}
        });
        newSnippet.statement_raw(snippet.statement);
      });
      hideHoverMsg(viewModel);
    };

    window.importExternalNotebook = importExternalNotebook;

    var hideFixedHeaders = function() {
      $(".jHueTableExtenderClonedContainer").hide();
      $(".jHueTableExtenderClonedContainerColumn").hide();
      $(".jHueTableExtenderClonedContainerCell").hide();
    };

    window.hideFixedHeaders = hideFixedHeaders;

    var redrawFixedHeaders = function (timeout) {
      var renderer = function() {
        if (! viewModel.selectedNotebook()) {
          return;
        }
        viewModel.selectedNotebook().snippets().forEach(function (snippet) {
          var _el = $("#snippet_" + snippet.id()).find(".resultTable");
          if (viewModel.editorMode) {
            _el.jHueTableExtender({
              fixedHeader: true,
              fixedFirstColumn: true,
              includeNavigator: false,
              mainScrollable: '.right-panel',
              stickToTopPosition: viewModel.isPlayerMode() ? 1 : 73,
              parentId: 'snippet_' + snippet.id(),
              clonedContainerPosition: "fixed"
            });
            _el.jHueHorizontalScrollbar();
          }
          else {
            _el.jHueTableExtender({
              fixedHeader: true,
              fixedFirstColumn: true,
              includeNavigator: false,
              mainScrollable: '.right-panel',
              parentId: 'snippet_' + snippet.id(),
              clonedContainerPosition: "absolute"
            });
          }
        });
      }
      if (timeout){
        window.setTimeout(renderer, timeout);
      }
      else {
        renderer();
      }
      $('.right-panel').jHueScrollUp();
    };

    var splitDraggableTimeout = -1;
    huePubSub.subscribe('split.draggable.position', function(){
      window.clearTimeout(splitDraggableTimeout);
      splitDraggableTimeout = window.setTimeout(function(){
        redrawFixedHeaders(100);
      }, 200);
    });

    huePubSub.subscribe('redraw.fixed.headers', function(){
      hideFixedHeaders();
      redrawFixedHeaders(200);
    });

    window.redrawFixedHeaders = redrawFixedHeaders;

    function addAce (content, snippetType) {
      var snip = viewModel.selectedNotebook().addSnippet({type: snippetType, result: {}}, true);
      snip.statement_raw(content);
      aceChecks++;
      snip.checkForAce = window.setInterval(function () {
        if (snip.ace()) {
          window.clearInterval(snip.checkForAce);
          aceChecks--;
          if (aceChecks == 0) {
            hideHoverMsg(viewModel);
          }
        }
      }, 100);
    }

    function replaceAce(content) {
      var snip = viewModel.selectedNotebook().snippets()[0];
      if (snip) {
        snip.statement_raw(content);
        snip.ace().setValue(content, 1);
      }
      hideHoverMsg(viewModel);
    }
    window.replaceAce = replaceAce;

    function addMarkdown (content) {
      var snip = viewModel.selectedNotebook().addSnippet({type: "markdown", result: {}}, true);
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
        if (viewModel.editorMode){
          replaceAce(raw);
        }
        else {
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
                  hideHoverMsg(viewModel);
                }
              }, 10);
            });
          }

          if (loaded.paragraphs) { //zeppelin
            if (loaded.name) {
              viewModel.selectedNotebook().name(loaded.name);
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
      }
      catch (e) {
        hideHoverMsg(viewModel);
        replaceAce(raw);
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
          hideHoverMsg(viewModel);
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
          hideHoverMsg(viewModel);
        }
      });
    }



    $(document).ready(function () {
      var i18n = {
        errorLoadingDatabases: "${ _('There was a problem loading the databases') }"
      }
      viewModel = new EditorViewModel(${ editor_id or 'null' }, ${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS, i18n);
      ko.applyBindings(viewModel);
      viewModel.init();

      if (viewModel.editorMode && window.location.getParameter('type') != '' && window.location.getParameter('new') == '') {
        viewModel.selectedNotebook().snippets()[0].statement_raw($.totalStorage('hue.notebook.lastWrittenSnippet.${user}.' + window.location.getParameter('type')));
        $.totalStorage('hue.notebook.lastWrittenSnippet.${user}.' + window.location.getParameter('type'), '');
      }

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

      var isAssistAvailable = viewModel.assistAvailable();
      var wasAssistVisible = viewModel.isLeftPanelVisible();

      function exitPlayerMode() {
        viewModel.isPlayerMode(false);
        viewModel.isFullscreenMode(false);
      }

      viewModel.isPlayerMode.subscribe(function (value) {
        if (value){
          $(".jHueNotify").hide();
          viewModel.assistAvailable(false);
          viewModel.isLeftPanelVisible(false);
          $(".navigator").hide();
          $(".add-snippet").hide();
          if (viewModel.isFullscreenMode()){
            $(".main-content").css("top", "50px");
          }
          else {
            $(".main-content").css("top", "1px");
          }
          $(window).bind("keydown", "esc", exitPlayerMode);
        }
        else {
          viewModel.isLeftPanelVisible(wasAssistVisible);
          viewModel.assistAvailable(isAssistAvailable);
          $(".navigator").show();
          $(".add-snippet").show();
          % if conf.CUSTOM.BANNER_TOP_HTML.get():
          $(".main-content").css("top", "112px");
          %else:
          $(".main-content").css("top", "82px");
          %endif
          redrawFixedHeaders(200);
          $(window).unbind("keydown", exitPlayerMode);
        }
      });

      huePubSub.subscribe('assist.set.manual.visibility', function () {
        wasAssistVisible = viewModel.isLeftPanelVisible();
      });

      viewModel.isLeftPanelVisible.subscribe(function (value) {
        redrawFixedHeaders(200);
      });

      $(document).on("updateResultHeaders", function (e) {
        hideFixedHeaders();
        redrawFixedHeaders(200);
      });

      $(document).on("showAuthModal", function (e, data) {
        viewModel.authSessionUsername('${ user.username }');
        viewModel.authSessionPassword('');
        viewModel.authSessionType(data['type']);
        viewModel.authSessionCallback(data['callback']);
        $("#authModal").modal("show");
      });

      $(document).on("hideHistoryModal", function (e) {
        $("#clearHistoryModal").modal("hide");
      });

      // Close the notebook snippets when leaving the page
      window.onbeforeunload = function (e) {
        viewModel.selectedNotebook().close();
      };
      $(window).data('beforeunload', window.onbeforeunload);

      $(".preview-sample").css("right", (10 + hueUtils.scrollbarWidth()) + "px");

      $(window).bind("keydown", "ctrl+s alt+s meta+s", function (e) {
        e.preventDefault();
        viewModel.saveNotebook();
        return false;
      });

      $(document).bind('keyup', function (e) {
        if (e.keyCode == 191 && !$(e.target).is('input') && !$(e.target).is('textarea')) {
          $('#helpModal').modal('show');
        }
      });

      if (!viewModel.editorMode) {
        $(window).bind("keydown", "ctrl+n alt+n meta+n", function (e) {
          e.preventDefault();
          viewModel.selectedNotebook().newSnippet();
          return false;
        });
      }

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
            $(".jHueTableExtenderClonedContainerColumn").hide();
            $(".jHueTableExtenderClonedContainerCell").hide();
          },
          stop: function (e, ui) {
            $(".jHueTableExtenderClonedContainer").show();
            $(".jHueTableExtenderClonedContainerColum").show();
            $(".jHueTableExtenderClonedContainerCell").show();
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
        var _newSize = _snippet.aceSize() + (ui.offset.top - initialResizePosition);
        _cm.setSize("99%", _newSize);
        if (setSize) {
          _snippet.aceSize(_newSize);
        }
      }

      $(document).on("toggleResultSettings", function (e, snippet) {
        window.setTimeout(function () {
          $("#snippet_" + snippet.id()).find(".chart").trigger("forceUpdate");
          redrawFixedHeaders();
        }, 10)
      });

      $(document).on("editorSizeChanged", function () {
        window.setTimeout(forceChartDraws, 50);
      });

      $(document).on("redrawResults", function () {
        window.setTimeout(forceChartDraws, 50);
      });

      $(document).on("executeStarted", function (e, snippet) {
        var _el = $("#snippet_" + snippet.id()).find(".resultTable");
        $("#snippet_" + snippet.id()).find(".progress").animate({
          height: "3px"
        }, 100);
        if (_el.hasClass("dt")) {
          _el.removeClass("dt");
          $("#eT" + snippet.id() + "jHueTableExtenderClonedContainer").remove();
          $("#eT" + snippet.id() + "jHueTableExtenderClonedContainerColumn").remove();
          $("#eT" + snippet.id() + "jHueTableExtenderClonedContainerCell").remove();
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
              _dt = createDatatable(_el, options.snippet, viewModel);
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
        }
        $("#snippet_" + options.snippet.id()).find("select").trigger('chosen:updated');
      });

      $(document).on("renderDataError", function (e, options) {
        var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
        _dtElement.animate({opacity: '1'}, 50);
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
          forceChartDraws();
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
        if (viewModel.selectedNotebook()) {
          viewModel.selectedNotebook().snippets().forEach(function (snippet) {
            if (snippet.result.data().length > 0) {
              var _elCheckerInterval = -1;
              _elCheckerInterval = window.setInterval(function () {
                var _el = $("#snippet_" + snippet.id()).find(".resultTable");
                if ($("#snippet_" + snippet.id()).find(".resultTable").length > 0) {
                  try {
                    var _dt = createDatatable(_el, snippet, viewModel);
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
        };
      }

      forceChartDraws();

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
