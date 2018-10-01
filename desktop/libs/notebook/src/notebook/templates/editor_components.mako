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
from django.utils.translation import ugettext as _

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko, antixss

from desktop.conf import IS_EMBEDDED
from metadata.conf import has_optimizer, OPTIMIZER
from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, ENABLE_BATCH_EXECUTE, ENABLE_EXTERNAL_STATEMENT, ENABLE_PRESENTATION
from desktop.auth.backend import is_admin
%>

<%def name="includes(is_embeddable=False, suffix='')">
<link rel="stylesheet" href="${ static('dashboard/css/common_dashboard.css') }">
% if not is_embeddable:
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
% endif
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">

<link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/medium-editor.min.css') }">
<link rel="stylesheet" href="${ static('desktop/css/bootstrap-medium-editor.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }">

<script src="${ static('desktop/ext/js/bootstrap-datepicker.min.js') }" type="text/javascript" charset="utf-8"></script>
% if not is_embeddable:
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('desktop/js/share2.vm.js') }"></script>
% endif

<script src="${ static('desktop/ext/js/clipboard.min.js') }"></script>
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/ext/js/selectize-plugin-clear.js') }"></script>
<script src="${ static('notebook/js/notebook.ko.js') }"></script>

% if ENABLE_QUERY_SCHEDULING.get():
<script src="${ static('oozie/js/coordinator-editor.ko.js') }"></script>
<script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>
% endif

<script src="${ static('desktop/js/ko.selectize.js') }"></script>
<script src="${ static('desktop/js/sqlFunctions.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sqlParseSupport.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sqlStatementsParser.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sqlAutocompleteParser.js') }"></script>
<script src="${ static('desktop/js/autocomplete/globalSearchParser.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter3.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('desktop/js/jquery.hdfstree.js') }"></script>
<script src="${ static('desktop/ext/js/markdown.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>


%if ENABLE_QUERY_BUILDER.get():
<!-- For query builder -->
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.contextMenu.min.css') }">
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
      $("#invalidQueryBuilder${ suffix }").modal("show");
    } else {
      replaceAce(result.query);
    }
  }

  window.setInterval(function(){
    if ($('#queryBuilder tbody').length > 0 && $('#queryBuilder tbody').find('tr').length > 0){
      $('.button-panel').show();
      $('#queryBuilder').show();
      $('#queryBuilderAlert').hide();
    } else {
      $('.button-panel').hide();
      $('#queryBuilder').hide();
      $('#queryBuilderAlert').show();
    }
  }, 500, 'editor' + (window.location.getParameter('type') ? '-' + window.location.getParameter('type') : ''));

</script>
<!-- End query builder imports -->
% endif

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/ext/select2/select2.min.js') }" type="text/javascript" charset="utf-8"></script>

<!--[if IE 9]>
  <script src="${ static('desktop/ext/js/classList.min.js') }" type="text/javascript" charset="utf-8"></script>
<![endif]-->
<script src="${ static('desktop/ext/js/medium-editor.min.js') }" type="text/javascript" charset="utf-8"></script>

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="sqlSyntaxDropdown" file="/sql_syntax_dropdown.mako" />

<script src="${ static('desktop/js/ko.common-dashboard.js') }" type="text/javascript" charset="utf-8"></script>

</%def>

<%def name="topBar(suffix='')">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .search-bar {
    top: 58px!important;
  }

  .show-assist,
  .show-assist-right {
    top: 110px!important;
  }

  .main-content {
    top: 112px!important;
  }

  .context-panel {
    height: calc(100% - 104px);
    top: 104px;
  }
% endif
</style>


${ sqlSyntaxDropdown.sqlSyntaxDropdown() }

<div class="navbar hue-title-bar" data-bind="visible: ! $root.isPresentationMode() && ! $root.isResultFullScreenMode()">
  <div class="navbar-inner">
    <div class="container-fluid">

      <!-- ko template: { name: 'notebook-menu-buttons-${ suffix }' } --><!-- /ko -->

      <div class="nav-collapse">
        <ul class="nav editor-nav">
          <li class="app-header">
            <!-- ko if: editorMode -->
              % if IS_EMBEDDED.get():
                <span>
                  <!-- ko template: { name: 'app-icon-template', data: { icon: editorType() } } --><!-- /ko -->
                  <!-- ko switch: editorType() -->
                  <!-- ko case: 'impala' -->Impala<!-- /ko -->
                  <!-- ko case: 'rdbms' -->DB Query<!-- /ko -->
                  <!-- ko case: 'pig' -->Pig<!-- /ko -->
                  <!-- ko case: 'java' -->Java<!-- /ko -->
                  <!-- ko case: 'spark2' -->Spark<!-- /ko -->
                  <!-- ko case: 'sqoop1' -->Sqoop 1<!-- /ko -->
                  <!-- ko case: 'distcp' -->DistCp<!-- /ko -->
                  <!-- ko case: 'shell' -->Shell<!-- /ko -->
                  <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                  <!-- ko case: ['beeswax', 'hive'] -->Hive<!-- /ko -->
                  <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                  <!-- ko case: 'spark' -->Scala<!-- /ko -->
                  <!-- ko case: 'pyspark' -->PySpark<!-- /ko -->
                  <!-- ko case: 'r' -->R<!-- /ko -->
                  <!-- ko case: 'jar' -->Spark Submit Jar<!-- /ko -->
                  <!-- ko case: 'py' -->Spark Submit Python<!-- /ko -->
                  <!-- ko case: 'solr' -->Solr SQL<!-- /ko -->
                  <!-- ko case: 'kafkasql' -->Kafka SQL<!-- /ko -->
                  <!-- ko case: 'markdown' -->Markdown<!-- /ko -->
                  <!-- ko case: 'text' -->Text<!-- /ko -->
                  <!-- ko case: $default -->SQL<!-- /ko -->
                  <!-- /ko -->
                </span>
              % else:
                <a data-bind="hueLink: '${ url('notebook:editor') }?type=' + editorType(), attr: { 'title': editorTypeTitle() + '${ _(' Editor') }'}" style="cursor: pointer">
              <!-- ko template: { name: 'app-icon-template', data: { icon: editorType() } } --><!-- /ko -->

              <!-- ko switch: editorType() -->
                <!-- ko case: 'impala' -->Impala<!-- /ko -->
                <!-- ko case: 'rdbms' -->DB Query<!-- /ko -->
                <!-- ko case: 'pig' -->Pig<!-- /ko -->
                <!-- ko case: 'java' -->Java<!-- /ko -->
                <!-- ko case: 'spark2' -->Spark<!-- /ko -->
                <!-- ko case: 'sqoop1' -->Sqoop 1<!-- /ko -->
                <!-- ko case: 'distcp' -->DistCp<!-- /ko -->
                <!-- ko case: 'shell' -->Shell<!-- /ko -->
                <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                <!-- ko case: ['beeswax', 'hive'] -->Hive<!-- /ko -->
                <!-- ko case: 'mapreduce' -->MapReduce<!-- /ko -->
                <!-- ko case: 'spark' -->Scala<!-- /ko -->
                <!-- ko case: 'pyspark' -->PySpark<!-- /ko -->
                <!-- ko case: 'r' -->R<!-- /ko -->
                <!-- ko case: 'jar' -->Spark Submit Jar<!-- /ko -->
                <!-- ko case: 'py' -->Spark Submit Python<!-- /ko -->
                <!-- ko case: 'solr' -->Solr SQL<!-- /ko -->
                <!-- ko case: 'kafkasql' -->Kafka SQL<!-- /ko -->
                <!-- ko case: 'markdown' -->Markdown<!-- /ko -->
                <!-- ko case: 'text' -->Text<!-- /ko -->
                <!-- ko case: $default -->SQL<!-- /ko -->
              <!-- /ko -->
              <!-- ko component: { name: 'hue-favorite-app', params: { hue4: IS_HUE_4, app: 'editor', interpreter: editorType() }} --><!-- /ko -->
              </a>
              % endif
            <!-- /ko -->
            <!-- ko ifnot: editorMode -->
              <i class="fa fa-file-text-o app-icon" style="vertical-align: middle"></i>
                Notebook
              <!-- ko component: { name: 'hue-favorite-app', params: { hue4: IS_HUE_4, app: 'notebook' }} --><!-- /ko -->
            <!-- /ko -->
          </li>

          % if not IS_EMBEDDED.get():
          <!-- ko with: selectedNotebook -->
          <li class="no-horiz-padding">
            <a>&nbsp;</a>
          </li>
          <li data-bind="visible: isHistory" style="display: none" class="no-horiz-padding muted">
            <a title="${ _('This is a history query') }"><i class="fa fa-fw fa-history"></i></a>
          </li>
          <li data-bind="visible: directoryUuid" style="display: none" class="no-horiz-padding muted">
            <a title="${ _('Open directory of this query') }" data-bind="hueLink: '/home/?uuid=' + directoryUuid()"
              class="pointer inactive-action" href="javascript:void(0)"><i class="fa fa-fw fa-folder-o"></i>
            </a>
          </li>
          <li data-bind="visible: parentSavedQueryUuid" style="display: none" class="no-horiz-padding muted">
            <a title="${ _('Click to open original saved query') }" data-bind="click: function() { $root.openNotebook(parentSavedQueryUuid()) }" class="pointer inactive-action">
              <i class="fa fa-fw fa-file-o"></i>
            </a>
          </li>
          <li data-bind="visible: isSaved() && ! isHistory() && ! parentSavedQueryUuid()" style="display: none" class="no-horiz-padding muted">
            <a title="${ _('This is a saved query') }"><i class="fa fa-fw fa-file-o"></i></a>
          </li>
          <li data-bind="visible: isSchedulerJobRunning" style="display: none" class="no-horiz-padding muted">
            <a title="${ _('Click to open original saved query') }" data-bind="click: function() { $root.openNotebook(parentSavedQueryUuid()) }" class="pointer inactive-action">
              ${ _("Scheduling on") }
            </a>
          </li>
          <li class="query-name no-horiz-padding skip-width-calculation">
            <a href="javascript:void(0)">
              <div class="notebook-name-desc" data-bind="editable: name, editableOptions: { inputclass: 'notebook-name-input', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a name...')}', tpl: '<input type=\'text\' maxlength=\'255\'>' }"></div>
            </a>
          </li>
          <li class="skip-width-calculation" data-bind="tooltip: { placement: 'bottom', title: description }">
            <a href="javascript:void(0)">
              <div class="notebook-name-desc" data-bind="editable: description, editableOptions: { type: 'textarea', enabled: true, placement: 'bottom', emptytext: '${_ko('Add a description...')}' }"></div>
            </a>
          </li>
          <!-- /ko -->
          % endif
        </ul>
      </div>
    </div>
  </div>
</div>


<script type="text/html" id="notebook-menu-buttons-${ suffix }">
  <div class="pull-right margin-right-10">
  % if ENABLE_PRESENTATION.get() and not IS_EMBEDDED.get():
    <!-- ko with: selectedNotebook() -->
      <div class="btn-group">
        <a class="btn" data-bind="click: function() { isPresentationMode(!isPresentationMode()); },
        css: {'btn-inverse': $root.isPresentationMode()}, attr: {title: isPresentationMode() ? '${ _ko('Exit presentation') }' : '${ _ko('View as a presentation') }'}">
          <i class="fa fa-line-chart"></i>
        </a>

        <!-- ko if: $root.canSave() -->
        <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
        <ul class="dropdown-menu pull-right">
          <li>
            <a class="pointer" title="${ _ko('Whether to open in presentation or editor mode by default') }" data-bind="click: function() { isPresentationModeDefault(!isPresentationModeDefault()); }">
              <i class="fa" data-bind="css: {'fa-toggle-on': isPresentationModeDefault(), 'fa-toggle-off': !isPresentationModeDefault()}"></i> ${ _('Open as presentation') }
            </a>
          </li>
        </ul>
        <!-- /ko -->
      </div>
    <!-- /ko -->
  % endif

    % if IS_EMBEDDED.get():
      <div class="btn-group">
        <a class="btn" rel="tooltip" data-bind="click: function() { newNotebook($root.editorType(), null, selectedNotebook() ? $root.selectedNotebook().snippets()[0].currentQueryTab() : null); }, attr: { 'title': '${ _('New ') }' +  editorTypeTitle() + '${ _(' Query') }' }">
          <i class="fa fa-fw fa-file-o"></i>
        </a>
      </div>
      <div class="btn-group">
        <a class="btn" rel="tooltip" data-bind="css: {'active': $root.isContextPanelVisible }, click: function() { $root.isContextPanelVisible(!$root.isContextPanelVisible()); }">
          <i class="fa fa-fw fa-cogs"></i>
        </a>
      </div>
    % else:
      <div class="btn-group">
        <a class="btn" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: function() { if ($root.canSave() ) { saveNotebook() } else { $('#saveAsModal${ suffix }').modal('show');} }, attr: { title: $root.canSave() ? '${ _ko('Save') }' : '${ _ko('Save As') }' }">
          <i class="fa fa-save"></i>
        </a>

        <!-- ko if: $root.canSave -->
        <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
        <ul class="dropdown-menu pull-right">
          <li>
            <a class="pointer" data-bind="click: function() { $('#saveAsModal${ suffix }').modal('show'); }">
              <i class="fa fa-fw fa-save"></i> ${ _('Save as...') }
            </a>
          </li>
        </ul>
        <!-- /ko -->
      </div>

      <!-- ko template: { ifnot: editorMode() || isPresentationMode(), name: 'notebook-actions' }--><!-- /ko -->

      <!-- ko ifnot: isPresentationMode() -->
      <div class="dropdown pull-right margin-left-10">
        <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
          <i class="fa fa-fw fa-ellipsis-v"></i>
        </a>
        <ul class="dropdown-menu pull-right">
          <li>
          <!-- ko if: editorMode -->
            <a href="javascript:void(0)" data-bind="click: function() { newNotebook($root.editorType(), null, selectedNotebook() ? $root.selectedNotebook().snippets()[0].currentQueryTab() : null); }, attr: { 'title': '${ _('New ') }' +  editorTypeTitle() + '${ _(' Query') }' }">
              <i class="fa fa-fw fa-file-o"></i> ${ _('New') }
            </a>
          <!-- /ko -->
          <!-- ko ifnot: editorMode -->
            <a href="javascript:void(0)" data-bind="click: newNotebook">
              <i class="fa fa-fw fa-file-o"></i> ${ _('New Notebook') }
            </a>
          <!-- /ko -->
          </li>
          <li>
            <!-- ko if: IS_HUE_4 -->
            <a href="javascript:void(0)" data-bind="publish: { 'assist.show.documents': editorMode() ? 'query-' + editorType() : editorType() }">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> <span data-bind="text: editorMode() ? '${ _ko('Queries') }' : '${ _ko('Notebooks') }'"></span>
            </a>
            <!-- /ko -->
            <!-- ko ifnot: IS_HUE_4 -->
            <a href="javascript:void(0)" class="btn" data-bind="hueLink: '${ url('notebook:notebooks') }?type=' + editorType()">
              <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> <span data-bind="text: editorMode() ? '${ _ko('Queries') }' : '${ _ko('Notebooks') }'"></span>
            </a>
            <!-- /ko -->
          </li>
          <li class="divider"></li>
          <!-- ko if: $root.canSave -->
          <li>
            <a class="share-link" data-bind="click: prepareShareModal,
              css: {'isShared': isShared()}">
              <i class="fa fa-fw fa-users"></i> ${ _('Share') }
            </a>
          </li>
          <!-- /ko -->
          <li>
            <a class="pointer" data-bind="css: {'active': $root.isContextPanelVisible }, click: function() { $root.isContextPanelVisible(!$root.isContextPanelVisible()); }">
              <i class="fa fa-fw fa-cogs"></i> ${ _('Session') }
            </a>
          </li>
        </ul>
      </div>
      <!-- /ko -->
    % endif
  </div>
</script>


<!-- ko if: $root.isResultFullScreenMode() -->
<a class="hueAnchor collapse-results" href="javascript:void(0)" title="${ _('Collapse results') }" data-bind="click: function(){ $root.isResultFullScreenMode(false); }">
  <i class="fa fa-times fa-fw"></i>
</a>
<!-- /ko -->

<!-- ko if: $root.isPresentationMode() -->
<a class="hueAnchor collapse-results" href="javascript:void(0)" title="${ _('Exit presentation') }" data-bind="click: function(){ $root.selectedNotebook().isPresentationMode(false); }">
  <i class="fa fa-times fa-fw"></i>
</a>
<!-- /ko -->

<div class="player-toolbar margin-top-10" data-bind="visible: $root.isPresentationMode()" style="display: none">
  <!-- ko if: $root.isPresentationMode() -->
    <!-- ko if: $root.selectedNotebook() -->
      <!-- ko if: $root.selectedNotebook().name() || $root.selectedNotebook().description() -->
        <h2 class="margin-left-30 margin-right-10 inline padding-left-5" data-bind="text: $root.selectedNotebook().name"></h2>
        <h2 class="muted inline" data-bind="text: $root.selectedNotebook().description"></h2>
        <div class="clearfix"></div>
      <!-- /ko -->

      <!-- ko template: { name: 'notebook-menu-buttons-${ suffix }' } --><!-- /ko -->

      <div class="margin-left-30 margin-top-10 padding-left-5 margin-bottom-20">
        <!-- ko template: { name: 'notebook-actions' } --><!-- /ko -->
        <!-- ko if: $root.preEditorTogglingSnippet -->
          <!-- ko template: { if: $root.isPresentationMode(), name: 'snippet-variables', data: $root.preEditorTogglingSnippet }--><!-- /ko -->
        <!-- /ko -->
      </div>

    <!-- /ko -->
  <!-- /ko -->
</div>
</%def>


<%def name="commonHTML(is_embeddable=False, suffix='')">

<div id="helpModal${ suffix }" class="modal transparent-modal hide" data-backdrop="true" style="width:980px;margin-left:-510px!important">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Editor help')}</h2>
  </div>
  <div class="modal-body">
    <!-- ko component: 'aceKeyboardShortcuts' --><!-- /ko -->
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>

<div id="combinedContentModal${ suffix }" class="modal hide" data-backdrop="true" style="width:780px;margin-left:-410px!important">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('All Notebook content')}</h2>
  </div>
  <div class="modal-body">
    <pre data-bind="oneClickSelect, text: combinedContent"></pre>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>

% if ENABLE_QUERY_BUILDER.get():
<div id="invalidQueryBuilder${ suffix }" class="modal hide">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Invalid Query')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Query requires a select or an aggregate.')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Close')}</a>
  </div>
</div>
% endif

% if not is_embeddable:
<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); huePubSub.publish('assist.set.manual.visibility'); }">
  <i class="fa fa-chevron-right"></i>
</a>
<a title="${_('Toggle Assist')}" class="pointer show-assist-right" data-bind="visible: !$root.isRightPanelVisible() && $root.isRightPanelAvailable(), click: function() { $root.isRightPanelVisible(true); huePubSub.publish('assist.set.manual.visibility'); }">
  <i class="fa fa-chevron-left"></i>
</a>
% endif


<div data-bind="css: {'main-content': true, 'editor-mode': $root.editorMode()}">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() || $root.isPresentationMode() || $root.isResultFullScreenMode() ? '0' : '20px' }" >
    <div class="vertical-full">
      <div class="vertical-full tab-pane row-fluid panel-container" data-bind="css: { active: selectedNotebook() === $data }, template: { name: 'notebook${ suffix }'}">
      </div>
    </div>
  </div>
</div>

<script type="text/html" id="notebook${ suffix }">
  % if not is_embeddable:
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
              showStats: true,
              pinEnabled: true
            },
          },
          visibleAssistPanels: editorMode() ? ['sql'] : []
        }
      }"></div>
  </div>
  <div class="resizer" data-bind="visible: isLeftPanelVisible() && assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: isLeftPanelVisible, rightPanelVisible: isRightPanelVisible, rightPanelAvailable: isRightPanelAvailable, onPosition: function(){ huePubSub.publish('split.draggable.position') } }"><div class="resize-bar">&nbsp;</div></div>
  % endif

  <div class="content-panel" data-bind="event: { scroll: function(){ var ls = $(MAIN_SCROLLABLE).data('lastScroll'); if (ls && ls != $(MAIN_SCROLLABLE).scrollTop()){ $(document).trigger('hideAutocomplete'); }; $(MAIN_SCROLLABLE).data('lastScroll', $(MAIN_SCROLLABLE).scrollTop()) } }, with: selectedNotebook">
    <div>
      <div class="row-fluid row-container sortable-snippets" data-bind="css: {'is-editing': $root.isEditing, 'margin-left-10': $root.isPresentationMode},
        sortable: {
          template: 'snippet${ suffix }',
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
              $element.find('.snippet-body').slideDown('fast', function () { $(MAIN_SCROLLABLE).scrollTop(lastWindowScrollPosition); });
            },
            'helper': function(event) {
              lastWindowScrollPosition = $(MAIN_SCROLLABLE).scrollTop();
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
            $('.snippet-body').slideDown('fast', function () { $(MAIN_SCROLLABLE).scrollTop(lastWindowScrollPosition); });
          }
        }">
      </div>
      % if hasattr(caller, "addSnippetHTML"):
        ${ caller.addSnippetHTML() }
      % endif
    </div>
  </div>

  % if not is_embeddable:
    <!-- ko if: isRightPanelAvailable -->
    <div class="resizer" data-bind="visible: isRightPanelVisible, splitDraggable : { isRightPanel: true, appName: 'notebook', leftPanelVisible: isLeftPanelVisible, rightPanelVisible: isRightPanelVisible, rightPanelAvailable: isRightPanelAvailable, onPosition: function(){ huePubSub.publish('split.draggable.position') } }" style="display: none;"><div class="resize-bar">&nbsp;</div></div>
    <!-- /ko -->
    <div class="assist-container right-panel" data-bind="visible: isRightPanelVisible() && isRightPanelAvailable()" style="display:none;">
      <a title="${_('Toggle Assist')}" class="pointer hide-assist-right" data-bind="click: function() { isRightPanelVisible(false); huePubSub.publish('assist.set.manual.visibility'); }">
        <i class="fa fa-chevron-right"></i>
      </a>
      <div class="assist" data-bind="component: {
          name: 'right-assist-panel',
          params: {
            rightAssistAvailable: isRightPanelAvailable
          }
        }" >
      </div>
    </div>
  % endif


  <div class="context-panel" data-bind="css: {'visible': isContextPanelVisible}" style="${ 'height: 100%' if not is_embeddable else '' }">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#sessionsTab" data-toggle="tab">${_('Sessions')}</a></li>
    </ul>

    <div class="tab-content" style="border: none">
      <div class="tab-pane active" id="sessionsTab">
        <div class="row-fluid">
          <div class="span12" data-bind="template: { name: 'notebook-session-config-template${ suffix }', data: $root }"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="notebook-session-config-template${ suffix }">
  <!-- ko with: selectedNotebook() -->
  <form class="form-horizontal session-config">
    <fieldset>
      <!-- ko ifnot: sessions().length -->
      <p>${ _('There are currently no active sessions, please reload the page.') }</p>
      <!-- /ko -->
      <!-- ko foreach: sessions -->
      <h4 style="clear:left; display: inline-block">
        <span data-bind="text: $parents[1].getSnippetName(type())"></span>
        <!-- ko if: typeof session_id != 'undefined' && session_id -->
          <span data-bind="text: session_id"></span>
        <!-- /ko -->
      </h4>
      <div class="session-actions">
        <a class="inactive-action pointer" title="${ _('Recreate session') }" rel="tooltip" data-bind="click: function() { $parent.restartSession($data) }">
          <i class="fa fa-refresh" data-bind="css: { 'fa-spin': restarting }"></i> ${ _('Recreate') }
        </a>
        <a class="inactive-action pointer margin-left-10" title="${ _('Close session') }" rel="tooltip" data-bind="click: function() { $parent.closeAndRemoveSession($data) }">
          <i class="fa fa-times"></i> ${ _('Close') }
        </a>
        % if conf.USE_DEFAULT_CONFIGURATION.get():
          <a class="inactive-action pointer margin-left-10" title="${ _('Save session settings as default') }" rel="tooltip" data-bind="click: function() { $parent.saveDefaultUserProperties($data) }"><i class="fa fa-save"></i> ${ _('Set as default settings') }</a>
        % endif
        % if not IS_EMBEDDED.get():
        <!-- ko if: type() == 'impala' && typeof http_addr != 'undefined' -->
          <a class="margin-left-10" data-bind="attr: {'href': http_addr()}" target="_blank">
            <span data-bind="text: http_addr().replace(/^(https?):\/\//, '')"></span> <i class="fa fa-external-link"></i>
          </a>
        <!-- /ko -->
        % endif
      </div>
      % if conf.USE_DEFAULT_CONFIGURATION.get():
      <div style="width:100%;">
        <!-- ko component: { name: 'property-selector', params: { properties: properties } } --><!-- /ko -->
      </div>
      % endif
      <div style="clear:both; padding-left: 120px;">
        <!-- ko if: availableNewProperties().length -->
        <a class="pointer" style="padding:5px;" data-bind="click: selectedSessionProperty() && function() {
                    properties.push(ko.mapping.fromJS({'name': selectedSessionProperty(), 'value': ''}));
                    selectedSessionProperty('');
                   }" style="margin-left:10px;vertical-align: text-top;">
        </a>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- /ko -->
      <br/>
    </fieldset>
  </form>
  <!-- /ko -->
</script>

<script type="text/html" id="snippetIcon${ suffix }">
  <!-- ko if: viewSettings().snippetImage -->
  <img class="snippet-icon-image" data-bind="attr: { 'src': viewSettings().snippetImage }" alt="${ _('Snippet icon') }">
  <!-- /ko -->
  <!-- ko if: viewSettings().snippetIcon -->
  <i class="fa snippet-icon" data-bind="css: viewSettings().snippetIcon"></i>
  <!-- /ko -->
</script>

<script type="text/html" id="snippet-log${ suffix }">
  <div class="snippet-log-container margin-bottom-10">
    <div data-bind="delayedOverflow: 'slow', css: resultsKlass" style="margin-top: 5px; position: relative;">
      <a href="javascript: void(0)" class="inactive-action close-logs-overlay" data-bind="click: function(){ showLogs(false) }">&times;</a>
      %if not IS_EMBEDDED.get():
      <ul data-bind="visible: jobs().length > 0, foreach: jobs" class="unstyled jobs-overlay">
        <li data-bind="attr: {'id': $data.name.substr(4)}">
          %if is_embeddable:
            <a class="pointer" data-bind="text: $.trim($data.name), click: function() { huePubSub.publish('show.jobs.panel', {id: $data.name, interface: $parent.type() == 'impala' ? 'queries' : 'jobs'}); }, clickBubble: false"></a>
          %else:
            <a data-bind="text: $.trim($data.name), hueLink: $data.url"></a>
          %endif
          <!-- ko if: typeof percentJob === 'function' && percentJob() > -1 -->
          <div class="progress-job progress pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': percentJob() < 100, 'progress-success': percentJob() === 100}">
            <div class="bar" data-bind="style: {'width': percentJob() + '%'}"></div>
          </div>
          <!-- /ko -->
          <div class="clearfix"></div>
        </li>
      </ul>
      %endif
      <span data-bind="visible: !$root.isPresentationMode() || !$root.isHidingCode()">
        <pre data-bind="visible: (!result.logs() || result.logs().length == 0) && jobs().length > 0" class="logs logs-bigger">${ _('No logs available at this moment.') }</pre>
        <pre data-bind="visible: result.logs() && result.logs().length > 0, text: result.logs, logScroller: result.logs, logScrollerVisibilityEvent: showLogs" class="logs logs-bigger logs-populated"></pre>
      </span>
    </div>
    <div class="snippet-log-resizer" data-bind="visible: result.logs().length > 0, logResizer: {parent: '.snippet-log-container', target: '.logs-populated', mainScrollable: MAIN_SCROLLABLE, onStart: hideFixedHeaders, onResize: function(){ hideFixedHeaders(); redrawFixedHeaders(500); }, minHeight: 50}">
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

    <!-- ko if: status() == 'available' && ! result.fetchedOnce() -->
    <div data-bind="css: resultsKlass">
      <pre class="margin-top-10 no-margin-bottom"><i class="fa fa-spin fa-spinner"></i> ${ _('Loading...') }</pre>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="query-tabs${ suffix }">
  <div class="query-history-container" data-bind="onComplete: function(){ redrawFixedHeaders(200); }">
    <div data-bind="delayedOverflow: 'slow', css: resultsKlass" style="margin-top: 5px; position: relative;">
      <ul class="nav nav-tabs nav-tabs-editor">
        <li data-bind="click: function(){ currentQueryTab('queryHistory'); }, css: {'active': currentQueryTab() == 'queryHistory'}, onClickOutside: function () { if ($parent.historyFilterVisible() && $parent.historyFilter() === '') { $parent.historyFilterVisible(false) } }">
          <a class="inactive-action" href="#queryHistory" data-toggle="tab">${_('Query History')}
            <div class="inline-block inactive-action margin-left-10 pointer visible-on-hover" title="${_('Search the query history')}" data-bind="click: function(data, e){ $parent.historyFilterVisible(!$parent.historyFilterVisible()); if ($parent.historyFilterVisible()) { window.setTimeout(function(){ $(e.target).parent().siblings('input').focus(); }, 0); } else { $parent.historyFilter('') }}"><i class="snippet-icon fa fa-search"></i></div>
            <input class="input-small inline-tab-filter" type="text" data-bind="visible: $parent.historyFilterVisible, clearable: $parent.historyFilter, valueUpdate:'afterkeydown'" placeholder="${ _('Search...') }">
            % if not IS_EMBEDDED.get():
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Clear the query history')}" data-target="#clearHistoryModal${ suffix }" data-toggle="modal" rel="tooltip" data-bind="visible: $parent.history().length > 0"><i class="snippet-icon fa fa-calendar-times-o"></i></div>
            %endif
          </a>
        </li>
        % if not IS_EMBEDDED.get():
        <li data-bind="click: function(){ currentQueryTab('savedQueries'); }, css: {'active': currentQueryTab() == 'savedQueries'}, onClickOutside: function () { if (queriesFilterVisible() && queriesFilter() === '') { queriesFilterVisible(false) } }">
          <a class="inactive-action" href="#savedQueries" data-toggle="tab">${_('Saved Queries')}
            <div class="inline-block inactive-action margin-left-10 pointer visible-on-hover" title="${_('Search the saved queries')}" data-bind="visible: !queriesHasErrors(), click: function(data, e){ queriesFilterVisible(!queriesFilterVisible()); if (queriesFilterVisible()) { window.setTimeout(function(){ $(e.target).parent().siblings('input').focus(); }, 0); } else { queriesFilter('') }}"><i class="snippet-icon fa fa-search"></i></div>
            <input class="input-small inline-tab-filter" type="text" data-bind="visible: queriesFilterVisible, clearable: queriesFilter, valueUpdate:'afterkeydown'" placeholder="${ _('Search...') }">
          </a>
        </li>
        % endif
        % if ENABLE_QUERY_BUILDER.get():
        <!-- ko if: isSqlDialect -->
        <li data-bind="click: function(){ currentQueryTab('queryBuilderTab'); }, css: {'active': currentQueryTab() == 'queryBuilderTab'}"><a class="inactive-action" href="#queryBuilderTab" data-toggle="tab">${_('Query Builder')}</a></li>
        <!-- /ko -->
        % endif
        <!-- ko if: result.hasSomeResults -->
        <li data-bind="click: function(){ currentQueryTab('queryResults'); }, css: {'active': currentQueryTab() == 'queryResults'}">
          <a class="inactive-action" href="#queryResults" data-toggle="tab">${_('Results')}
            <!-- ko if: result.rows() != null  -->
              (<span data-bind="text: result.rows().toLocaleString() + (type() == 'impala' && result.rows() == 1024 ? '+' : '')" title="${ _('Number of rows') }"></span>)
            <!-- /ko -->
            <!-- ko if: showGrid -->
            <div class="inline-block inactive-action pointer margin-left-10 visible-on-hover" title="${_('Search the results')}" data-bind="click: function(data, e){ $(e.target).parents('.snippet').find('.resultTable').hueDataTable().fnShowSearch() }">
              <i class="snippet-icon fa fa-search"></i>
            </div>
            <!-- /ko -->
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Expand results')}" rel="tooltip" data-bind="css: { 'margin-left-10': !showGrid()}, visible: !$root.isResultFullScreenMode(), click: function(){ $root.isResultFullScreenMode(true); }">
              <i class="snippet-icon fa fa-expand"></i>
            </div>
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Collapse results')}" rel="tooltip" data-bind="visible: $root.isResultFullScreenMode(), click: function(){ $root.isResultFullScreenMode(false); }">
              <i class="snippet-icon fa fa-compress"></i>
            </div>
          </a>
        </li>
        <!-- /ko -->
        <!-- ko if: result.explanation().length > 0 -->
        <li data-bind="click: function(){ currentQueryTab('queryExplain'); }, css: {'active': currentQueryTab() == 'queryExplain'}"><a class="inactive-action" href="#queryExplain" data-toggle="tab">${_('Explain')}</a></li>
        <!-- /ko -->
        <!-- ko foreach: pinnedContextTabs -->
        <li data-bind="click: function() { $parent.currentQueryTab(tabId) }, css: { 'active': $parent.currentQueryTab() === tabId }">
          <a class="inactive-action" data-toggle="tab" data-bind="attr: { 'href': '#' + tabId }">
            <i class="snippet-icon fa" data-bind="css: iconClass"></i> <span data-bind="text: title"></span>
            <div class="inline-block inactive-action margin-left-10 pointer" data-bind="click: function () { $parent.removeContextTab($data); }">
              <i class="snippet-icon fa fa-times"></i>
            </div>
          </a>
        </li>
        <!-- /ko -->
      </ul>
      <div class="tab-content" style="border: none; overflow-x: hidden">
        <div class="tab-pane" id="queryHistory" data-bind="css: {'active': currentQueryTab() == 'queryHistory'}, style: { 'height' : $parent.historyInitialHeight() > 0 ? Math.max($parent.historyInitialHeight(), 40) + 'px' : '' }">
          <!-- ko if: $parent.loadingHistory -->
          <div style="padding: 20px">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->

          <!-- ko ifnot: $parent.loadingHistory -->

            <!-- ko if: $parent.history().length === 0 && $parent.historyFilter() === '' -->
            <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("No queries to be shown.") }</div>
            <!-- /ko -->
            <!-- ko if: $parent.history().length === 0 && $parent.historyFilter() !== '' -->
            <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _('No queries found for') } <strong data-bind="text: $parent.historyFilter"></strong>.</div>
            <!-- /ko -->


            <!-- ko if: $parent.history().length > 0 -->
            <table class="table table-condensed margin-top-10 history-table">
              <tbody data-bind="foreach: { data: $parent.history, afterRender: function(){ huePubSub.publish('editor.calculate.history.height'); } }">
                <tr data-bind="click: function() { if (uuid() != $root.selectedNotebook().uuid()) { $root.openNotebook(uuid()); } }, css: { 'highlight': uuid() == $root.selectedNotebook().uuid(), 'pointer': uuid() != $root.selectedNotebook().uuid() }">
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
                  <td data-bind="style: {'border-top-width': $index() == 0 ? '0' : ''}, click: function(){ if (window.getSelection().toString() === '' && uuid() != $root.selectedNotebook().uuid()) { $root.openNotebook(uuid()) }  }, clickBubble: false"><div data-bind="highlight: { value: query, dialect: $parent.type }"></div></td>
                </tr>
              </tbody>
            </table>
            <!-- /ko -->
            <!-- ko with: $parent -->
            <div class="pagination" data-bind="visible: historyTotalPages() > 1">
            <ul>
              <li data-bind="css: { 'disabled' : historyCurrentPage() === 1 }"><a href="javascript: void(0);" data-bind="click: function() { prevHistoryPage(); }">${ _("Prev") }</a></li>
              <li class="active"><span data-bind="text: historyCurrentPage() + '/' + historyTotalPages()"></span></li>
              <li data-bind="css: { 'disabled' : historyCurrentPage() === historyTotalPages() }"><a href="javascript: void(0);" data-bind="click: function() { nextHistoryPage(); }">${ _("Next") }</a></li>
            </ul>
            </div>
            <!-- /ko -->
          <!-- /ko -->
        </div>

        <div class="tab-pane" id="savedQueries" data-bind="css: {'active': currentQueryTab() == 'savedQueries'}" style="overflow: hidden">
          <!-- ko if: loadingQueries -->
          <div style="padding: 20px">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->
          <!-- ko if: queriesHasErrors() -->
          <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("Error loading my queries") }</div>
          <!-- /ko -->
          <!-- ko if: !queriesHasErrors() && !loadingQueries() && queries().length === 0 && queriesFilter() === '' -->
          <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _("You don't have any saved query.") }</div>
          <!-- /ko -->
          <!-- ko if: !queriesHasErrors() && !loadingQueries() && queries().length === 0 && queriesFilter() !== '' -->
          <div class="margin-top-20 margin-left-10" style="font-style: italic">${ _('No queries found for') } <strong data-bind="text: queriesFilter"></strong>.</div>
          <!-- /ko -->
          <!-- ko if: !queriesHasErrors() && !loadingQueries() && queries().length > 0 -->
          <table class="table table-condensed margin-top-10 history-table">
            <thead>
              <tr>
                <th style="width: 16%">${ _("Name") }</th>
                <th style="width: 50%">${ _("Description") }</th>
                <th style="width: 18%">${ _("Owner") }</th>
                <th style="width: 16%">${ _("Last Modified") }</th>
              </tr>
            </thead>
            <tbody data-bind="foreach: queries">
            <tr data-bind="click: function() { if (uuid() != $root.selectedNotebook().uuid()) { $root.openNotebook(uuid(), 'savedQueries'); } }, css: { 'highlight': uuid() == $root.selectedNotebook().uuid(), 'pointer': uuid() != $root.selectedNotebook().uuid() }">
              <td style="width: 16%"><span data-bind="ellipsis: {data: name(), length: 50}"></span></td>
              <td style="width: 50%; white-space: normal"><span data-bind="text: description"></span></td>
              <td style="width: 18%"><span data-bind="text: owner"></span></td>
              <td style="width: 16%"><span data-bind="text: localeFormat(last_modified())"></span></td>
            </tr>
            </tbody>
          </table>
          <!-- /ko -->
          <div class="pagination" data-bind="visible: queriesTotalPages() > 1">
            <ul>
              <li data-bind="css: { 'disabled' : queriesCurrentPage() === 1 }"><a href="javascript: void(0);" data-bind="click: prevQueriesPage">${ _("Prev") }</a></li>
              <li class="active"><span data-bind="text: queriesCurrentPage() + '/' + queriesTotalPages()"></span></li>
              <li data-bind="css: { 'disabled' : queriesCurrentPage() === queriesTotalPages() }"><a href="javascript: void(0);" data-bind="click: nextQueriesPage">${ _("Next") }</a></li>
            </ul>
          </div>
        </div>

        % if ENABLE_QUERY_BUILDER.get():
        <div class="tab-pane margin-top-10" id="queryBuilderTab" data-bind="css: {'active': currentQueryTab() == 'queryBuilderTab'}">
          <div id="queryBuilderAlert" style="display: none" class="alert">${ _('There are currently no rules defined. To get started, right click on any table column in the SQL Assist panel.') }</div>
          <table id="queryBuilder" class="table table-condensed">
            <thead>
              <tr>
                <th width="10%">${ _('Table') }</th>
                <th>${ _('Column') }</th>
                <th width="10%">${ _('Operation') }</th>
                <th width="5%">&nbsp;</th>
                <th width="1%">&nbsp;</th>
              </tr>
            </thead>
          </table>
          <div class="button-panel">
            <button class="btn btn-primary disable-feedback" data-bind="click: generateQuery">${_('Build query')}</button>
          </div>
        </div>
        % endif

        <div class="tab-pane" id="queryResults" data-bind="css: {'active': currentQueryTab() == 'queryResults'}">
          <!-- ko template: { if: ['text', 'jar', 'py', 'markdown'].indexOf(type()) == -1, name: 'snippet-results${ suffix }' } --><!-- /ko -->
        </div>
        <!-- ko if: result.explanation().length > 0 -->
        <div class="tab-pane" id="queryExplain" data-bind="css: {'active': currentQueryTab() == 'queryExplain'}">
          <!-- ko template: { name: 'snippet-explain${ suffix }' } --><!-- /ko -->
        </div>
        <!-- /ko -->

        <!-- ko foreach: pinnedContextTabs -->
        <div class="tab-pane" style="height: 300px; position: relative; overflow: hidden;" data-bind="attr: { 'id': tabId }, css: {'active': $parent.currentQueryTab() === tabId }">
          <div style="display: flex; flex-direction: column; margin-top: 10px; overflow: hidden; height: 100%; position: relative;" data-bind="template: 'context-popover-contents'"></div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="doc-search-autocomp-item">
  <a>
    <div>
      <strong style="font-size: 14px;" data-bind="html: name"></strong>
      <div style="width: 190px; overflow: hidden; white-space: nowrap; text-overflow:ellipsis; font-size: 12px;" class="muted" data-bind="text: description"></div>
    </div>
  </a>
</script>

<script type="text/html" id="longer-operation${ suffix }">
  <div rel="tooltip" data-placement="bottom" data-bind="tooltip, fadeVisible: showLongOperationWarning" title="${ _('The query is hanging and taking longer than expected.') }" class="inline-block margin-right-10">
    <i class="fa fa-exclamation-triangle warning"></i>
  </div>
</script>

<script type="text/html" id="query-redacted${ suffix }">
  <div rel="tooltip" data-placement="bottom" data-bind="tooltip, fadeVisible: is_redacted" title="${ _('The current query has been redacted to hide sensitive information.') }" class="inline-block margin-right-10">
    <i class="fa fa-low-vision warning"></i>
  </div>
</script>

<script type="text/html" id="notebook-snippet-header${ suffix }">
  <!-- ko if: $root.isPresentationMode() || $root.isResultFullScreenMode() -->
  <div class="inline">
    <!-- ko if: name() -->
      <span data-bind="text: name"></span>
    <!-- /ko -->
    <!-- ko if: !name() && !$root.isHidingCode() -->
      <span>${ _("Add -- comments on top of the SQL statement to display a title") }</span>
    <!-- /ko -->
  </div>
  <!-- /ko -->

  <!-- ko if: ! $root.isPresentationMode() && ! $root.isResultFullScreenMode() -->
  <div class="inactive-action hover-actions inline">
    <span class="inactive-action" data-bind="css: { 'empty-title': name() === '' }, editable: name, editableOptions: { emptytext: '${_ko('My Snippet')}', mode: 'inline', enabled: true, placement: 'right' }" style="border:none;color: #DDD"></span>
  </div>
  <div class="hover-actions inline pull-right" style="font-size: 15px;">
    <!-- ko template: { name: 'query-redacted${ suffix }' } --><!-- /ko -->
    <!-- ko template: { name: 'longer-operation${ suffix }' } --><!-- /ko -->
    <span class="execution-timer" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>

    <!-- ko template: { name: 'snippet-header-database-selection' } --><!-- /ko -->
    <!-- ko template: { name: 'snippet-header-statement-type${ suffix }' } --><!-- /ko -->

    <a class="inactive-action move-widget" href="javascript:void(0)"><i class="fa fa-arrows"></i></a>
    <a class="inactive-action" href="javascript:void(0)" data-bind="toggle: settingsVisible, visible: hasProperties, css: { 'blue' : settingsVisible }" title="${ _('Snippet settings') }"><i class="fa fa-cog"></i></a>
    <a class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ $root.removeSnippet($parent, $data); }"><i class="fa fa-times"></i></a>
  </div>
  <!-- /ko -->
</script>

<script type="text/html" id="editor-snippet-header${ suffix }">
  <div class="hover-actions inline pull-right" style="font-size: 15px; position: relative;" data-bind="style: { 'marginRight': $root.isPresentationMode() || $root.isResultFullScreenMode() ? '40px' : '0' }">
    <!-- ko template: { name: 'query-redacted${ suffix }' } --><!-- /ko -->
    <!-- ko template: { name: 'longer-operation${ suffix }' } --><!-- /ko -->
    <span class="execution-timer" data-bind="visible: type() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>

    <!-- ko template: { name: 'snippet-header-database-selection' } --><!-- /ko -->
    <!-- ko template: { name: 'snippet-header-statement-type${ suffix }' } --><!-- /ko -->

    <a class="inactive-action margin-left-10" href="javascript:void(0)" data-bind="toggle: settingsVisible, visible: hasProperties, css: { 'blue' : settingsVisible }" title="${ _('Query settings') }"><i class="fa fa-cog"></i></a>
    <a class="inactive-action margin-left-10 pointer" title="${ _('Show editor help') }" data-toggle="modal" data-target="#helpModal${ suffix }"><i class="fa fa-question"></i></a>
  </div>
</script>

<script type="text/html" id="snippet-header-database-selection">
  <!-- ko if: isSqlDialect() || type() == 'spark2' -->
    <!-- ko component: {
      name: 'hue-context-selector',
      params: {
        sourceType: type,
        compute: compute,
        namespace: namespace,
        availableDatabases: availableDatabases,
        database: database,
        hideDatabases: !isSqlDialect()
      }
    } --><!-- /ko -->
  <!-- /ko -->
</script>

<script type="text/html" id="snippet-header-statement-type${ suffix }">
  % if ENABLE_EXTERNAL_STATEMENT.get() and not IS_EMBEDDED.get():
  <!-- ko if: isSqlDialect() -->
    <span class="editor-header-title">${ _('Type') }</span>
    <div data-bind="component: { name: 'hue-drop-down', params: { value: statementType, entries: statementTypes, linkTitle: '${ _ko('Statement type') }' } }" style="display: inline-block"></div>
  <!-- /ko -->
  % endif
</script>

<script type="text/html" id="snippet${ suffix }">
  <div data-bind="visibleOnHover: { override: inFocus() || settingsVisible() || dbSelectionVisible() || $root.editorMode() || saveResultsModalVisible(), selector: '.hover-actions' }">
    <div class="snippet-container row-fluid" data-bind="visibleOnHover: { override: $root.editorMode() || inFocus() || saveResultsModalVisible(), selector: '.snippet-actions' }">
      <div class="snippet card card-widget" data-bind="css: {'notebook-snippet' : ! $root.editorMode(), 'editor-mode': $root.editorMode(), 'active-editor': inFocus, 'snippet-text' : type() == 'text'}, attr: {'id': 'snippet_' + id()}, clickForAceFocus: ace">
        <div style="position: relative;">
          <div class="snippet-row" style="position: relative;">
            <div class="snippet-left-bar">
              <!-- ko template: { if: ! $root.editorMode() && ! $root.isPresentationMode() && ! $root.isResultFullScreenMode(), name: 'notebook-snippet-type-controls${ suffix }' } --><!-- /ko -->
              <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1 && ! $root.isResultFullScreenMode(), name: 'snippet-execution-controls${ suffix }' } --><!-- /ko -->
            </div>
            <div class="snippet-body" data-bind="clickForAceFocus: ace, visible: ! $root.isResultFullScreenMode()">
              <h5 class="card-heading-print" data-bind="text: name, css: {'visible': name() != ''}"></h5>

              <h2 style="margin-left:5px;padding: 3px 0" class="card-heading simple" data-bind="dblclick: function(){ if (!$root.editorMode() && !$root.isPresentationMode()) { $parent.newSnippetAbove(id()) } }, clickForAceFocus: ace">
                <!-- ko template: { if: $root.editorMode(), name: 'editor-snippet-header${ suffix }' } --><!-- /ko -->
                <!-- ko template: { if: ! $root.editorMode(), name: 'notebook-snippet-header${ suffix }' } --><!-- /ko -->
              </h2>
              <!-- ko template: { if: ['text', 'jar', 'java', 'spark2', 'distcp', 'shell', 'mapreduce', 'py', 'markdown'].indexOf(type()) == -1, name: 'code-editor-snippet-body${ suffix }' } --><!-- /ko -->
              <!-- ko template: { if: type() == 'text', name: 'text-snippet-body${ suffix }' } --><!-- /ko -->
              <!-- ko template: { if: type() == 'markdown', name: 'markdown-snippet-body${ suffix }' } --><!-- /ko -->
              <!-- ko template: { if: ['java', 'distcp', 'shell', 'mapreduce', 'jar', 'py', 'spark2'].indexOf(type()) != -1, name: 'executable-snippet-body${ suffix }' } --><!-- /ko -->
            </div>
            <div style="position: absolute; top:25px; margin-left:35px; width: calc(100% - 35px)" data-bind="style: { 'z-index': 400 - $index() }">
              <!-- ko template: 'snippet-settings${ suffix }' --><!-- /ko -->
            </div>
          </div>
          <!-- ko template: { if: ['text', 'markdown'].indexOf(type()) == -1, name: 'snippet-execution-status${ suffix }' } --><!-- /ko -->
          <!-- ko template: { if: $root.editorMode() && ! $root.isResultFullScreenMode() && ['jar', 'java', 'spark2', 'distcp', 'shell', 'mapreduce'].indexOf(type()) == -1, name: 'snippet-code-resizer${ suffix }' } --><!-- /ko -->
          <!-- ko if: !$root.isResultFullScreenMode() -->
            <!-- ko template: 'snippet-log${ suffix }' --><!-- /ko -->
          <!-- /ko -->
          <!-- ko if: $root.editorMode() -->
            <!-- ko template: 'query-tabs${ suffix }' --><!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: $root.editorMode() -->
            <!-- ko template: { if: ['text', 'jar', 'java', 'distcp', 'shell', 'mapreduce', 'py', 'markdown'].indexOf(type()) == -1, name: 'snippet-results${ suffix }' } --><!-- /ko -->
          <!-- /ko -->

          <div class="clearfix"></div>
        </div>
      </div>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-settings${ suffix }">
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

        <!-- ko template: { if: typeof properties().spark_opts != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Spark Arguments') }', value: properties().spark_opts, title: '${ _ko('Names and values of Spark parameters') }', placeholder: '${ _ko('e.g. --executor-memory 20G --num-executors 50') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().parameters != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Parameters') }', value: properties().parameters, title: '${ _ko('Names and values of Pig parameters and options') }', placeholder: '${ _ko('e.g. input /user/data, -param input=/user/data, -optimizer_off SplitFilter, -verbose') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv', label: '${ _ko('Hadoop properties') }', value: properties().hadoopProperties, title: '${ _ko('Name and values of Hadoop properties') }', placeholder: '${ _ko('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        <!-- ko template: { if: typeof properties().resources != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Resources') }', value: properties().resources, title: '${ _ko('HDFS Files or compressed files') }', placeholder: '${ _ko('e.g. /tmp/file, /tmp.file.zip') }'}} --><!-- /ko -->

        <!-- ko template: { if: typeof properties().capture_output != 'undefined', name: 'property', data: { type: 'boolean', label: '${ _ko('Capture output') }', value: properties().capture_output, title: '${ _ko('If capturing the output of the shell script') }' }} --><!-- /ko -->
      </form>
    </div>
    <a class="pointer demi-modal-chevron" data-bind="click: function() { settingsVisible(! settingsVisible()) }"><i class="fa fa-chevron-up"></i></a>
  </div>
</script>

<script type="text/html" id="code-editor-snippet-body${ suffix }">
  <!-- ko if: HAS_OPTIMIZER && (type() == 'impala' || type() == 'hive') && ! $root.isPresentationMode() && ! $root.isResultFullScreenMode() -->
  <div class="optimizer-container" data-bind="css: { 'active': showOptimizer }">
    <!-- ko if: hasSuggestion() -->
      <!-- ko with: suggestion() -->
        <!-- ko if: parseError -->
          <!-- ko if: $parent.compatibilityTargetPlatform().value === $parent.type() && $parent.compatibilitySourcePlatform().value === $parent.type() -->
            <div class="optimizer-icon error" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
              <i class="fa fa-exclamation"></i>
            </div>
            <!-- ko if: $parent.showOptimizer -->
              <span class="optimizer-explanation alert-error alert-neutral">${ _('The query has a parse error.') }</span>
            <!-- /ko -->
          <!-- /ko -->
          ## Oracle, MySQL compatibility... as they return a parseError and not encounteredString.
          <!-- ko if: $parent.compatibilityTargetPlatform().value !== $parent.type() || $parent.type() !== $parent.compatibilitySourcePlatform().value -->
            <div class="optimizer-icon warning" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
              <i class="fa fa-exclamation"></i>
            </div>
            <!-- ko if: $parent.showOptimizer -->
              <span class="optimizer-explanation alert-warning alert-neutral">${ _('This ') } <span data-bind="text: $parent.compatibilitySourcePlatform().name"></span> ${ _(' query is not compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.</span>
            <!-- /ko -->
          <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: !parseError() && ($parent.compatibilityTargetPlatform().value !== $parent.type() || $parent.compatibilitySourcePlatform().value !== $parent.type()) -->
          <!-- ko if: queryError.encounteredString().length == 0 -->
            <div class="optimizer-icon success" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
              <i class="fa fa-check"></i>
            </div>
            <!-- ko if: $parent.showOptimizer -->
            <span class="optimizer-explanation alert-success alert-neutral">
              ${ _('The ') } <div data-bind="component: { name: 'hue-drop-down', params: { value: $parent.compatibilitySourcePlatform, entries: $parent.compatibilitySourcePlatforms, labelAttribute: 'name' } }" style="display: inline-block"></div>
              <!-- ko if: $parent.compatibilitySourcePlatform().value === $parent.type() -->
                ${ _(' query is compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.
                <a href="javascript:void(0)" data-bind="click: function() { $parent.type($parent.compatibilityTargetPlatform().value); }">${ _('Execute it with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span></a>.
              <!-- /ko -->
              <!-- ko if: $parent.compatibilitySourcePlatform().value !== $parent.type() -->
                ${ _(' query is compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.
              <!-- /ko -->
            </span>
          <!-- /ko -->
        <!-- /ko -->
        <!-- ko ifnot: queryError.encounteredString().length == 0 -->
          <div class="optimizer-icon warning" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
            <i class="fa fa-exclamation"></i>
          </div>
          <!-- ko if: $parent.showOptimizer -->
            <span class="optimizer-explanation alert-warning alert-neutral">${ _('This query is not compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.</span>
          <!-- /ko -->
        <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: ! hasSuggestion() && topRisk() -->
      <!-- ko if: topRisk().risk === 'low' -->
        <div class="optimizer-icon success" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some low risks were detected, see the assistant for details.') }">
          <i class="fa fa-check"></i>
        </div>
      <!-- /ko -->
      <!-- ko if: topRisk().risk == 'medium' -->
        <div class="optimizer-icon warning" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some medium risks were detected, see the assistant for details.') }">
          <i class="fa fa-exclamation"></i>
        </div>
      <!-- /ko -->
      <!-- ko if: topRisk().risk == 'high' -->
        <div class="optimizer-icon error" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Some high risks were detected, see the assistant for details.') }">
          <i class="fa fa-exclamation"></i>
        </div>
      <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: hasSuggestion() == '' && ! topRisk() -->
      <div class="optimizer-icon success" data-bind="click: function () { huePubSub.publish('assist.highlight.risk.suggestions'); }, tooltip: { placement: 'bottom' }" title="${ _('Query validated, no issues found.') }">
        <i class="fa fa-check"></i>
      </div>
    <!-- /ko -->
  </div>
  <!-- /ko -->


  <div class="row-fluid" style="margin-bottom: 5px">

    <div class="editor span12" data-bind="css: {'single-snippet-editor ace-container-resizable' : $root.editorMode() }, clickForAceFocus: ace, visible: ! $root.isResultFullScreenMode() && ! ($root.isPresentationMode() && $root.isHidingCode())">
      <!-- ko if: statementType() == 'file' -->
        <div class="margin-top-10">
          <label class="pull-left" style="margin-top: 6px;margin-right: 10px;">${_('Query File')}</label>
          <input type="text" class="pull-left input-xxlarge filechooser-input" data-bind="value: statementPath, valueUpdate: 'afterkeydown', filechooser: statementPath, filechooserOptions: { skipInitialPathIfEmpty: true, linkMarkup: true }" placeholder="${ _('Path to file, e.g. /user/hue/sample.sql') }"/>
          <!-- ko if: statementPath() -->
          <div class="inline-block" style="margin-top: 4px">
            <a data-bind="hueLink: '/filebrowser/view=' + statementPath()" title="${ _('Open') }">
              <i class="fa fa-external-link-square"></i>
            </a>
          </div>
          <a class="btn" data-bind="click: function() { getExternalStatement(); }"><i class="fa fa-lg fa-refresh"></i></a>
          ##<a class="btn" data-bind="tooltip: { placement: 'bottom', title: 'Save content back to file' }, click: function() { huePubSub.publish('show.saveToFile.modal'); }"><i class="fa fa-save"></i></a>
          <!-- /ko -->
        </div>
        <div class="clearfix margin-bottom-20"></div>
      <!-- /ko -->

      <!-- ko if: statementType() == 'document' -->
        <div class="margin-top-10">
          <!-- ko if: associatedDocumentLoading -->
          <i class="fa fa-spinner fa-spin muted"></i>
          <!-- /ko -->
          <label class="pull-left" style="margin-top: 6px;margin-right: 10px;" data-bind="visible: !associatedDocumentLoading()">${_('Document')}</label>
          <div class="selectize-wrapper" style="width: 300px;" data-bind="visible: !associatedDocumentLoading()">
            <select placeholder="${ _('Search your documents...') }" data-bind="documentChooser: { loading: associatedDocumentLoading, value: associatedDocumentUuid, document: associatedDocument, type: type }"></select>
          </div>
          <!-- ko if: associatedDocument() -->
            <div class="pull-left" style="margin-top: 4px">
              <a data-bind="hueLink: associatedDocument().absoluteUrl" title="${ _('Open') }">
                <i class="fa fa-external-link-square"></i>
              </a>
              <span data-bind='text: associatedDocument().description' style="padding: 3px; margin-top: 2px" class="muted"></span>
            </div>
          <!-- /ko -->
        </div>
        <div class="clearfix margin-bottom-20"></div>
      <!-- /ko -->

      <div class="ace-editor" data-bind="visible: statementType() === 'text' || statementType() !== 'text' && externalStatementLoaded(), css: {'single-snippet-editor ace-editor-resizable' : $root.editorMode(), 'active-editor': inFocus }, attr: { id: id() }, delayedOverflow: 'slow', aceEditor: {
        snippet: $data,
        contextTooltip: '${ _ko("Right-click for details") }',
        expandStar: '${ _ko("Right-click to expand with columns") }',
        highlightedRange: result.statement_range,
        useNewAutocompleter: $root.useNewAutocompleter,
        readOnly: $root.isPresentationMode(),
        aceOptions: {
          showLineNumbers: $root.editorMode(),
          showGutter: $root.editorMode(),
          maxLines: $root.editorMode() ? null : 25,
          minLines: $root.editorMode() ? null : 3
        }
      }, style: {opacity: statementType() !== 'text' || $root.isPresentationMode() ? '0.75' : '1', 'min-height': $root.editorMode() ? '0' : '48px', 'top': $root.editorMode() && statementType() !== 'text' ? '60px' : '0'}"></div>
      % if conf.USE_NEW_AUTOCOMPLETER.get():
      <!-- ko component: { name: 'hueAceAutocompleter', params: { editor: ace, snippet: $data } } --><!-- /ko -->
      % endif


      <ul class="table-drop-menu hue-context-menu">
        <li class="editor-drop-value"><a href="javascript:void(0);">"<span class="editor-drop-identifier"></span>"</a></li>
        <li class="divider"></li>
        <li class="editor-drop-select"><a href="javascript:void(0);">SELECT FROM <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-insert"><a href="javascript:void(0);">INSERT INTO <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-update"><a href="javascript:void(0);">UPDATE <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-drop"><a href="javascript:void(0);">DROP TABLE <span class="editor-drop-identifier"></span>...</a></li>
        <li class="editor-drop-view"><a href="javascript:void(0);">DROP VIEW <span class="editor-drop-identifier"></span>...</a></li>
      </ul>
    </div>

    <div class="clearfix"></div>
    <!-- ko template: { if: ! $root.isPresentationMode() && ! $root.isResultFullScreenMode(), name: 'snippet-variables' }--><!-- /ko -->
  </div>
  <div class="clearfix"></div>
</script>


<script type="text/html" id="notebook-actions">
  <div class="btn-group">
    <!-- ko if: $root.selectedNotebook() -->
    <!-- ko with: $root.selectedNotebook() -->
      <a class="btn" rel="tooltip" data-placement="bottom" title="${ _("Execute all") }" data-bind="visible: ! isExecutingAll(), click: function() { executeAll(); }">
        <i class="fa fa-fw fa-play"></i>
      </a>
      <!-- ko if: ! (snippets()[executingAllIndex()] && snippets()[executingAllIndex()].isCanceling()) -->
      <a class="btn red" rel="tooltip" data-placement="bottom" title="${ _("Stop all") }" data-bind="visible: isExecutingAll(), click: function() { cancelExecutingAll(); }">
        <i class="fa fa-fw fa-stop"></i>
      </a>
      <!-- /ko -->
      <!-- ko if: snippets()[executingAllIndex()] && snippets()[executingAllIndex()].isCanceling() -->
      <a class="btn" style="cursor: default;" title="${ _('Canceling operation...') }">
        <i class="fa fa-fw fa-spinner snippet-side-single fa-spin"></i>
      </a>
      <!-- /ko -->
    <!-- /ko -->

    <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu pull-right">
      <li>
        <a class="pointer" rel="tooltip" data-placement="bottom" data-bind="click: function() { $root.selectedNotebook().isHidingCode(! $root.isHidingCode()); }, attr: { 'title': $root.isHidingCode() ? '${ _ko('Show the logic') }' : '${ _ko('Hide the logic') }' }">
          <i class="fa fa-fw" data-bind="css: { 'fa-expand': $root.isHidingCode(), 'fa-compress': ! $root.isHidingCode() }"></i>
          <span data-bind="visible: $root.isHidingCode">${ _('Show the code') }</span>
          <span data-bind="visible: ! $root.isHidingCode()">${ _('Hide the code') }</span>
        </a>
      </li>
      <li>
        <a class="pointer" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
          <i class="fa fa-fw fa-eraser"></i> ${ _('Clear results') }
        </a>
      </li>
      <li>
        <a href="javascript:void(0)" data-bind="click: displayCombinedContent, visible: ! $root.isPresentationMode() ">
          <i class="fa fa-fw fa-file-text-o"></i> ${ _('Show all content') }
        </a>
      </li>
    </ul>
    <!-- /ko -->
  </div>
</script>


<script type="text/html" id="snippet-variables">
  <div class="variables">
    <ul data-bind="foreach: variables" class="unstyled inline">
      <li>
        <div class="input-prepend margin-top-10">
          <!-- ko ifnot: path() -->
          <span class="muted add-on" data-bind="text: name"></span>
          <!-- /ko -->
          <!-- ko if: path() -->
          <a href="javascript:void(0);" data-bind="click: $root.showContextPopover" style="float: left"> <span class="muted add-on" data-bind="text: name"></span></a>
          <!-- /ko -->
          <!-- ko if: meta.type() == 'text' -->
            <!-- ko if: meta.placeholder() -->
              <input class="input-medium" type="text" data-bind="value: value, attr: { type: type, placeholder: meta.placeholder() || '${ _ko('Variable value') }' }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
            <!-- /ko -->
            <!-- ko ifnot: meta.placeholder() -->
              <!-- ko if: type() == 'datetime-local' -->
              <input class="input-medium" type="text" data-bind="value: value, datepicker: { momentFormat: 'YYYY-MM-DD HH:mm:ss.S' }">
              <!-- /ko -->
              <!-- ko if: type() == 'date' -->
              <input class="input-medium" type="text" data-bind="value: value, datepicker: { momentFormat: 'YYYY-MM-DD' }">
              <!-- /ko -->
              <!-- ko if: type() == 'checkbox' -->
              <input class="input-medium" type="checkbox" data-bind="checked: value">
              <!-- /ko -->
              <!-- ko ifnot: (type() == 'datetime-local' || type() == 'date' || type() == 'checkbox') -->
              <input class="input-medium" type="text" value="true" data-bind="value: value, attr: { type: type() || 'text', step: step }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
              <!-- /ko -->
            <!-- /ko -->
          <!-- /ko -->
          <!-- ko if: meta.type() == 'select' -->
          <select data-bind="selectize: sample, optionsText: 'text', optionsValue: 'value', selectizeOptions: { create: function (input) { sampleUser().push({ text: ko.observable(input), value: ko.observable(input) }); return { text: input, value: input }; } }, value: value, event: { 'keydown': $parent.onKeydownInVariable }"/>
          <!-- /ko -->
        </div>
      </li>
    </ul>
  </div>
</script>


<script type="text/html" id="snippet-chart-settings${ suffix }">
  <div>
    <!-- ko if: chartType() != '' && [ko.HUE_CHARTS.TYPES.TIMELINECHART, ko.HUE_CHARTS.TYPES.BARCHART].indexOf(chartType()) >= 0  -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('type')}</li>
    </ul>
    <div data-bind="visible: chartType() != ''">
      <select data-bind="selectedOptions: chartTimelineType, optionsCaption: '${_ko('Choose a type...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a type...") }', update: chartTimelineType, dropdownAutoWidth: true}">
        <option value="bar">${ _("Bars") }</option>
        <option value="line">${ _("Lines") }</option>
      </select>
    </div>
    <!-- /ko -->

    <!-- ko if: chartType() != '' && chartType() === ko.HUE_CHARTS.TYPES.PIECHART -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li class="nav-header">${_('value')}</li>
    </ul>
    <div>
      <select data-bind="options: result.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartYSingle, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li class="nav-header">${_('legend')}</li>
    </ul>
    <div>
      <select data-bind="options: result.cleanedMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartX, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <!-- /ko -->

    <!-- ko if: chartType() != '' && chartType() !== ko.HUE_CHARTS.TYPES.PIECHART -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartType()) == -1" class="nav-header">${_('x-axis')}</li>
      <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('region')}</li>
      <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
    </ul>
    <div>
      <select data-bind="options: ([ko.HUE_CHARTS.TYPES.BARCHART, ko.HUE_CHARTS.TYPES.GRADIENTMAP, ko.HUE_CHARTS.TYPES.TIMELINECHART].indexOf(chartType()) > -1) ? ( chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART ? result.cleanedDateTimeMeta : result.cleanedMeta ) : result.cleanedNumericMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartX, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li data-bind="visible: [ko.HUE_CHARTS.TYPES.MAP, ko.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartType()) == -1" class="nav-header">${_('y-axis')}</li>
      <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('value')}</li>
      <li data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
    </ul>

    <div style="max-height: 220px" data-bind="delayedOverflow, visible: chartType() != '' && ((chartType() == ko.HUE_CHARTS.TYPES.BARCHART && !chartXPivot()) || chartType() == ko.HUE_CHARTS.TYPES.LINECHART || chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART)">
      <ul class="unstyled" data-bind="foreach: result.cleanedNumericMeta" style="margin-bottom: 0">
        <li><label class="checkbox"><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></label></li>
      </ul>
    </div>
    <div data-bind="visible: (chartType() == ko.HUE_CHARTS.TYPES.BARCHART && chartXPivot()) || chartType() == ko.HUE_CHARTS.TYPES.MAP || chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP || chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP ? result.cleanedMeta : result.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartYSingle, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <!-- /ko -->

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() === ko.HUE_CHARTS.TYPES.BARCHART">
      <li class="nav-header">${_('group')}</li>
    </ul>
    <div data-bind="visible: chartType() === ko.HUE_CHARTS.TYPES.BARCHART">
      <select data-bind="options: result.cleanedMeta, value: chartXPivot, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column to pivot...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column to pivot...") }', update: chartXPivot, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('limit')}</li>
    </ul>
    <div>
      <select data-bind="options: chartLimits, value: chartLimit, optionsCaption: '${_ko('Limit the number of results to...')}', select2: { width: '100%', placeholder: '${ _ko("Limit the number of results to...") }', update: chartLimit, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <!-- ko if: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.MAP -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('type')}</li>
    </ul>
    <div data-bind="visible: chartType() != ''">
      <select data-bind="selectedOptions: chartMapType, optionsCaption: '${_ko('Choose a type...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a type...") }', update: chartMapType, dropdownAutoWidth: true}">
        <option value="marker">${ _("Markers") }</option>
        <option value="heat">${ _("Heatmap") }</option>
      </select>
    </div>

    <!-- ko if: chartMapType() == 'marker' -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('label')}</li>
    </ul>
    <div>
      <select data-bind="options: result.cleanedMeta, value: chartMapLabel, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartMapLabel, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <!-- /ko -->

    <!-- ko if: chartMapType() == 'heat' -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('intensity')}</li>
    </ul>
    <div>
      <select data-bind="options: result.cleanedNumericMeta, value: chartMapHeat, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartMapHeat, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <!-- /ko -->
    <!-- /ko -->

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
      <li class="nav-header">${_('scatter size')}</li>
    </ul>
    <div data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: result.cleanedNumericMeta, value: chartScatterSize, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterSize, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
      <li class="nav-header">${_('scatter group')}</li>
    </ul>
    <div data-bind="visible: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: result.cleanedMeta, value: chartScatterGroup, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterGroup, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <!-- ko if: chartType() != '' && chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('scope')}</li>
    </ul>
    <div data-bind="visible: chartType() != ''">
      <select data-bind="selectedOptions: chartScope, optionsCaption: '${_ko('Choose a scope...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a scope...") }', update: chartScope, dropdownAutoWidth: true}">
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

<script type="text/html" id="snippet-grid-settings${ suffix }">
  <div class="snippet-grid-settings" data-bind="delayedOverflow">
    <table class="table table-condensed margin-top-10 no-border">
      <thead>
        <tr>
          <th width="16">
            <input class="all-meta-checked no-margin-top" type="checkbox" data-bind="enable: !result.isMetaFilterVisible() && result.filteredMeta().length > 0, event: { change: function(){ toggleAllColumns($element, $data); result.clickFilteredMetaCheck() } }, checked: result.filteredMetaChecked" />
          </th>
          <th colspan="2" class="nav-header-like">
            <span class="meta-title pointer" data-bind="click: function(){ result.isMetaFilterVisible(true); }, attr: {title: result.filteredMeta().length }">${_('columns')}</span>
            (<span class="meta-title pointer" data-bind="click: function(){ result.isMetaFilterVisible(true); }, text: result.filteredMeta().length"></span>)
            <span class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ result.isMetaFilterVisible(true); }, css: { 'blue' : result.isMetaFilterVisible }"><i class="pointer fa fa-search" title="${ _('Search') }"></i></span>
          </th>
        </tr>
        <tr data-bind="visible: result.isMetaFilterVisible">
          <td colspan="3" class="context-popover-inline-autocomplete">
            <!-- ko component: {
              name: 'inline-autocomplete',
              params: {
                placeHolder: '${ _ko('Filter columns...') }',
                querySpec: result.metaFilter,
                facets: Object.keys(SQL_COLUMNS_KNOWN_FACET_VALUES),
                knownFacetValues: SQL_COLUMNS_KNOWN_FACET_VALUES,
                autocompleteFromEntries: result.autocompleteFromEntries
              }
            } --><!-- /ko -->
            ##<input class="meta-filter" type="text" data-bind="blurHide: result.isMetaFilterVisible, clearable: result.metaFilter, valueUpdate:'afterkeydown'" placeholder="${ _('Filter columns...') }" title="${ _('Type column:xxx or type:yyy for specific filters.') }" style="width: 257px" />
          </td>
        </tr>
      </thead>
      <tbody class="unstyled filtered-meta" data-bind="foreach: result.filteredMeta">
        <tr data-bind="visible: name != ''">
          <td><input class="no-margin-top" type="checkbox" data-bind="event: { change: function(){ toggleColumn($element, originalIndex, $parent);} }, checked: checked" /></td>
          <td><a class="pointer" data-bind="click: function(){ scrollToColumn($element, $data.originalIndex); }, attr: { title: name + ' - ' + type}"><span data-bind="text: name"></span></a></td>
          <td><span data-bind="text: type" class="muted margin-left-20"></span></td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td colspan="3">
            <div class="margin-top-10 muted meta-noresults" data-bind="visible: result.filteredMeta().length === 0">
              ${ _('No results found') }
            </div>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</script>

<script type="text/html" id="snippet-explain${ suffix }">
  <pre class="no-margin-bottom" data-bind="text: result.explanation"></pre>
</script>

<script type="text/html" id="snippet-results${ suffix }">
  <div class="snippet-row" data-bind="slideVisible: result.hasSomeResults">
    <div class="snippet-left-bar">
      <!-- ko template: { if: result.type() == 'table' && result.hasSomeResults(), name: 'snippet-result-controls${ suffix }' }--><!-- /ko -->
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
            <img data-bind="attr: {'src': 'data:image/png;base64,' + $data}" class="margin-bottom-10"  alt="${ _('Result image') }"/>
          </li>
        </ul>
        <!-- /ko -->
      </div>

      <div class="row-fluid table-results" data-bind="visible: result.type() == 'table'" style="display: none; max-height: 400px; min-height: 290px;">
        <div>
          <div class="column-side" data-bind="visible: isResultSettingsVisible, css:{'span3 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible()}" style="position:relative;white-space: nowrap;">
            <!-- ko template: { name: 'snippet-grid-settings${ suffix }', if: showGrid } --><!-- /ko -->
            <!-- ko template: { name: 'snippet-chart-settings${ suffix }', if: showChart } --><!-- /ko -->
            <div class="resize-bar" style="top: 0; right: -10px; cursor: col-resize;"></div>
          </div>
          <div class="grid-side" data-bind="css: {'span9': isResultSettingsVisible, 'span12 nomargin': ! isResultSettingsVisible() }">
            <div data-bind="visible: showGrid, delayedOverflow: 'slow', css: resultsKlass" style="display: none;">
              <table class="table table-condensed resultTable">
                <thead>
                <tr data-bind="foreach: result.meta">
                  <th class="sorting" data-bind="text: ($index() == 0 ? '&nbsp;' : $data.name), css: typeof cssClass != 'undefined' ? cssClass : 'sort-string', attr: {title: $data.type }, style:{'width': $index() == 0 ? '1%' : '', 'height': $index() == 0 ? '32px' : ''}, click: function(obj, e){ $(e.target).parents('table').trigger('sort', obj); }"></th>
                </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
              <div data-bind="visible: status() == 'expired' && result.data() && result.data().length > 99, css: resultsKlass" style="display:none;">
                <pre class="margin-top-10"><i class="fa fa-check muted"></i> ${ _("Results have expired, rerun the query if needed.") }</pre>
              </div>
            </div>

            <div data-bind="visible: showChart" class="chart-container" style="display:none;">
              <h1 class="empty" data-bind="visible: !hasDataForChart()">${ _('Select the chart parameters on the left') }</h1>

              <div data-bind="visible: hasDataForChart">
                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.PIECHART -->
                <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]),
                      transformer: editorPieChartDataTransformer, maxWidth: 350, parentSelector: '.chart-container' }, visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.BARCHART -->
                <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {skipWindowResize: true, datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: hideStacked,
                      transformer: editorMultiSerieDataTransformer, stacked: false, showLegend: true, isPivot: typeof chartXPivot() !== 'undefined', type: chartTimelineType},  stacked: true, showLegend: true, visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.LINECHART -->
                <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()},
                      transformer: editorMultiSerieDataTransformer, showControls: false, enableSelection: false }, visible: chartType() == ko.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART -->
                <div data-bind="attr:{'id': 'timelineChart_'+id()}, timelineChart: {type: chartTimelineType, skipWindowResize: true, datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: hideStacked,
                      transformer: editorTimelineChartDataTransformer, stacked: false, showLegend: true}, visible: chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.MAP -->
                <div data-bind="attr:{'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()},
                      transformer: editorLeafletMapChartDataTransformer, showControls: false, height: 380, visible: chartType() == ko.HUE_CHARTS.TYPES.MAP, forceRedraw: true}" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP -->
                <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data, scope: chartScope(), limit: chartLimit()},
                      transformer: editorMapChartDataTransformer, isScale: true, showControls: false, height: 380, maxWidth: 750, parentSelector: '.chart-container', visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP}" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART -->
                <div data-bind="attr:{'id': 'scatterChart_'+id()}, scatterChart: {datum: {counts: result.data, snippet: $data, limit: chartLimit()},
                      transformer: editorScatterChartDataTransformer, maxWidth: 350, y: chartYSingle(), x: chartX(), size: chartScatterSize(), group: chartScatterGroup() }, visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART" class="chart"></div>
                <!-- /ko -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</script>


<script type="text/html" id="text-snippet-body${ suffix }">
  <div data-bind="attr: {'id': 'editor_' + id()}, html: statement_raw, value: statement_raw, medium: {}" data-placeHolder="${ _('Type your text here, select some text to format it') }" class="text-snippet"></div>
</script>


<script type="text/html" id="markdown-snippet-body${ suffix }">
  <!-- ko ifnot: $root.isPresentationMode() -->
  <div class="row-fluid">
    <div class="span6" data-bind="clickForAceFocus: ace">
      <div class="ace-editor" data-bind="attr: { id: id() }, aceEditor: {
        snippet: $data,
        updateOnInput: true
      }"></div>
    </div>
    <div class="span6">
      <div data-bind="html: renderMarkdown(statement_raw(), id()), attr: {'id': 'liveMD' + id()}"></div>
    </div>
  </div>
  <!-- /ko -->
  <!-- ko if: $root.isPresentationMode() -->
  <div data-bind="html: renderMarkdown(statement_raw(), id())"></div>
  <!-- /ko -->
</script>


<script type="text/html" id="executable-snippet-body${ suffix }">
  <div style="padding:10px;">
    <form class="form-horizontal">
      <!-- ko if: type() == 'distcp' -->
      <div class="control-group">
        <label class="control-label">${_('Source')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().source_path, valueUpdate: 'afterkeydown', filechooser: properties().source_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true }" placeholder="${ _('Source path to copy, e.g. ${nameNode1}/path/to/input.txt') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Destination')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().destination_path, valueUpdate: 'afterkeydown', filechooser: properties().destination_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true }" placeholder="${ _('Destination path, e.g. ${nameNode2}/path/to/output.txt') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().distcp_parameters != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().distcp_parameters, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'shell' -->
      <div class="control-group">
        <label class="control-label">${_('Script path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().command_path, valueUpdate: 'afterkeydown', filechooser: properties().command_path, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Source path to the command') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().arguments, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
          <!-- ko template: { if: typeof properties().env_var != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Environment") }', value: properties().env_var, title: '${ _ko("Environment variable for the script") }', placeholder: '${ _ko("e.g. CLASSPATH=/path/file.jar") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'mapreduce' -->
      <div class="control-group">
        <label class="control-label">${_('Jar path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().app_jar, valueUpdate: 'afterkeydown', filechooser: properties().app_jar, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Source path to the main MapReduce jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Properties')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().hadoopProperties != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Hadoop Properties') }', value: properties().hadoopProperties, title: '${ _ko('Name and values of Hadoop properties') }', placeholder: '${ _ko('e.g. mapred.job.queue.name=production, mapred.map.tasks.speculative.execution=false') }'}} --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'jar' || type() == 'java' -->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge filechooser-input" data-bind="value: properties().app_jar, valueUpdate: 'afterkeydown', filechooser: properties().app_jar, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Path to application jar, e.g. hdfs://localhost:8020/user/hue/oozie-examples.jar') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Class')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().class, valueUpdate: 'afterkeydown'" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${_('Variables')}</label>
        <div class="controls">
          <!-- ko template: { if: typeof properties().arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko("Arguments") }', value: properties().arguments, title: '${ _ko("Arguments for the script") }', placeholder: '${ _ko("e.g. MAX=10, PATH=$PATH:/user/path") }' } } --><!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'py'-->
      <div class="control-group">
        <label class="control-label">${_('Path')}</label>
        <div class="controls">
          <input type="text" class="input-xxlarge" data-bind="value: properties().py_file, valueUpdate: 'afterkeydown', filechooser: properties().py_file, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Path to python file, e.g. script.py') }"/>
        </div>
      </div>
      <!-- /ko -->
      <!-- ko if: type() == 'spark2' -->
      <div class="control-group">
        <!-- ko template: { if: typeof properties().jars != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Libs') }', value: properties().jars, title: '${ _ko('Path to jar or python files.') }', placeholder: '${ _ko('e.g. /user/hue/pi.py') }'}} --><!-- /ko -->
      </div>
      <!-- ko if: $.grep(properties().jars(), function(val, index) { return val.toLowerCase().endsWith('.jar'); }).length > 0 -->
        <div class="control-group">
          <label class="control-label">
            ${_('Class')}
          </label>
          <div class="controls">
            <input type="text" class="input-xxlarge" data-bind="value: properties().class, valueUpdate: 'afterkeydown'" placeholder="${ _('Class name of application, e.g. org.apache.oozie.example.SparkFileCopy') }"/>
          </div>
        </div>
      <!-- /ko -->
      <div class="control-group">
        <!-- ko template: { if: typeof properties().spark_arguments != 'undefined', name: 'property', data: { type: 'csv-hdfs-files', label: '${ _ko('Arguments') }', value: properties().spark_arguments, title: '${ _ko('Arguments to the application.') }', placeholder: '${ _ko('e.g. 10, /user/hue/input') }'}} --><!-- /ko -->
      </div>
      <!-- /ko -->
    </form>
  </div>
</script>

<script type="text/html" id="snippet-execution-status${ suffix }">
  <div class="snippet-execution-status" data-bind="clickForAceFocus: ace">
    <a class="inactive-action pull-left snippet-logs-btn" href="javascript:void(0)" data-bind="visible: status() === 'running' && errors().length == 0, click: function() { hideFixedHeaders(); $data.showLogs(!$data.showLogs());}, css: {'blue': $data.showLogs}" title="${ _('Toggle Logs') }"><i class="fa fa-fw" data-bind="css: { 'fa-caret-right': !$data.showLogs(), 'fa-caret-down': $data.showLogs() }"></i></a>
    <div class="snippet-progress-container" data-bind="visible: status() != 'canceled' && status() != 'with-optimizer-report'">
      <div class="progress-snippet progress" data-bind="css: {
        'progress-starting': progress() == 0 && status() == 'running',
        'progress-warning': progress() > 0 && progress() < 100,
        'progress-success': progress() == 100,
        'progress-danger': progress() == 0 && errors().length > 0}" style="background-color: #FFF; width: 100%">
        <div class="bar" data-bind="style: {'width': (errors().length > 0 ? 100 : Math.max(2, progress())) + '%'}"></div>
      </div>
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: errors().length > 0">
      <ul class="unstyled" data-bind="foreach: errors">
        <li data-bind="text: message"></li>
        <!-- ko if: help -->
        <li><a href="javascript:void(0)" data-bind="click: function() {
          huePubSub.publish('editor.settings.update', {
            key: $data.help.setting.name,
            value: $data.help.setting.value
          });
          $parent.settingsVisible(true);
        }">${ _("Update max_row_size setting.") }</a></li>
        <!-- /ko -->
      </ul>
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: aceErrors().length > 0">
      <ul class="unstyled" data-bind="foreach: aceErrors">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <div class="snippet-error-container alert" style="margin-bottom: 0" data-bind="visible: aceWarnings().length > 0">
      <ul class="unstyled" data-bind="foreach: aceWarnings">
        <li data-bind="text: message"></li>
      </ul>
    </div>
    <div class="snippet-error-container alert alert-error" style="margin-bottom: 0" data-bind="visible: status() == 'canceled', click: function() { status('ready'); }" title="${ _('Click to hide') }">
      <ul class="unstyled">
        <li>${ _("The statement was canceled.") }</li>
      </ul>
    </div>
  </div>
</script>

<script type="text/html" id="snippet-code-resizer${ suffix }">
  <div class="snippet-code-resizer" data-bind="aceResizer : { snippet: $data, target: '.ace-container-resizable', onStart: hideFixedHeaders, onStop: redrawFixedHeaders }">
    <i class="fa fa-ellipsis-h"></i>
  </div>
</script>

<script type="text/html" id="notebook-snippet-type-controls${ suffix }">
  <div class="inactive-action dropdown hover-actions">
    <a class="snippet-side-btn" style="padding-right: 0; padding-left: 2px;" data-toggle="dropdown" href="javascript: void(0);">
      <span data-bind="template: { name: 'snippetIcon${ suffix }', data: $data }"></span>
    </a>
    <a class="inactive-action dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0);">
      <i class="fa fa-caret-down"></i>
    </a>

    <ul class="dropdown-menu" data-bind="foreach: $root.availableSnippets">
      <li><a class="pointer" data-bind="click: function(){ $parent.type($data.type()); }, text: name"></a></li>
    </ul>
  </div>
</script>

<script type ="text/html" id="snippet-execution-controls${ suffix }">
  <div class="snippet-actions" style="position: absolute; bottom: 0">
    <!-- ko if: status() == 'loading' -->
    <a class="snippet-side-btn blue" style="cursor: default;" title="${ _('Creating session') }">
      <i class="fa fa-fw fa-spinner fa-spin"></i>
    </a>
    <!-- /ko -->
    <a class="snippet-side-btn" data-bind="click: reexecute, visible: $root.editorMode() && result.handle() && result.handle().has_more_statements, css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }" title="${ _('Restart from the first statement') }">
      <i class="fa fa-fw fa-repeat snippet-side-single"></i>
    </a>
    <div class="label label-info" data-bind="attr: {'title':'${ _ko('Showing results of the statement #')}' + (result.statement_id() + 1)}, visible: $root.editorMode() && result.statements_count() > 1">
      <div class="pull-left" data-bind="text: (result.statement_id() + 1)"></div><div class="pull-left">/</div><div class="pull-left" data-bind="text: result.statements_count()"></div>
    </div>
    <!-- ko if: !isCanceling() -->
    <a class="snippet-side-btn red" data-bind="click: cancel, visible: status() == 'running'" title="${ _('Cancel operation') }">
      <i class="fa fa-fw fa-stop snippet-side-single"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: isCanceling() -->
    <a class="snippet-side-btn" style="cursor: default;" title="${ _('Canceling operation...') }">
      <i class="fa fa-fw fa-spinner snippet-side-single fa-spin"></i>
    </a>
    <!-- /ko -->
    <div class="inactive-action dropdown hover-actions pointer" data-bind="css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }">
      <!-- ko if: isBatchable() && wasBatchExecuted() -->
      <a class="snippet-side-btn" style="padding-right:0; padding-left: 2px" href="javascript: void(0)" title="${ _('Submit all the queries as a background batch job.') }" data-bind="click: function() { wasBatchExecuted(true); execute(); }, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }">
        <i class="fa fa-fw fa-send"></i>
      </a>
      <!-- /ko -->
      <!-- ko if: ! isBatchable() || ! wasBatchExecuted() -->
      <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="attr: {'title': $root.editorMode() && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: function() { wasBatchExecuted(false); execute(); }, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }, style: {'padding-left': $parent.isBatchable() ? '2px' : '0' }">
        <i class="fa fa-fw fa-play" data-bind="css: { 'snippet-side-single' : ! $parent.isBatchable() }"></i>
      </a>
      <!-- /ko -->
      % if ENABLE_BATCH_EXECUTE.get():
      <!-- ko if: isBatchable() && status() != 'running' && status() != 'loading' && ! $root.isPresentationMode() -->
        <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'disabled': ! isReady(), 'blue': currentQueryTab() == 'queryExplain' }">
          <i class="fa fa-caret-down"></i>
        </a>
        <ul class="dropdown-menu less-padding">
          <li>
            <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(false); $('.dropdown-toggle').dropdown('toggle'); execute(); }, style: { color: ! isReady() || status() === 'running' || status() === 'loading' ? '#999' : ''}, css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }" title="${ _('Execute interactively the current statement') }">
              <i class="fa fa-fw fa-play"></i> ${_('Execute')}
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(true); $('.dropdown-toggle').dropdown('toggle'); execute(); }, css: {'disabled': ! isReady() }" title="${ _('Submit all the queries as a background batch job.') }">
              <i class="fa fa-fw fa-send"></i> ${_('Batch')}
            </a>
          </li>
        </ul>
      <!-- /ko -->
      % endif
    </div>

    <!-- ko if: isSqlDialect && ! $root.isPresentationMode() -->
    <div class="inactive-action dropdown hover-actions pointer" data-bind="css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }">
      <a class="snippet-side-btn" style="padding-right:0; padding-left: 2px;" href="javascript: void(0)" data-bind="click: explain, css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading', 'blue': currentQueryTab() == 'queryExplain' }" title="${ _('Explain the current SQL query') }">
        <i class="fa fa-fw fa-map-o"></i>
      </a>
      <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'disabled': ! isReady(), 'blue': currentQueryTab() == 'queryExplain' }">
        <i class="fa fa-caret-down"></i>
      </a>
      <ul class="dropdown-menu less-padding">
        <li>
          <a href="javascript:void(0)" data-bind="click: explain, style: { color: ! isReady() || status() === 'running' || status() === 'loading' ? '#999' : ''}, css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }" title="${ _('Explain the current SQL query') }">
            <i class="fa fa-fw fa-map-o"></i> ${_('Explain')}
          </a>
        </li>
        <!-- ko if: formatEnabled -->
        <li>
          <a href="javascript:void(0)" data-bind="click: format, css: {'disabled': ! isReady() }" title="${ _('Format the current SQL query') }">
            <i class="fa fa-fw fa-indent"></i> ${_('Format')}
          </a>
        </li>
        <!-- /ko -->
        <li>
          <a href="javascript:void(0)" data-bind="click: clear, css: {'disabled': ! isReady() }" title="${ _('Clear the current editor') }">
            <i class="fa fa-fw fa-eraser"></i> ${_('Clear')}
          </a>
        </li>
        <!-- ko if: HAS_OPTIMIZER -->
        <li class="divider"></li>
        <li>
          <a href="javascript:void(0)" data-bind="click: checkCompatibility, visible: type() == 'hive' || type() == 'impala'" title="${ _('Get hints on how to port SQL from other databases') }">
            <i class="fa fa-fw fa-random"></i> ${_('Check compatibility')}
          </a>
        </li>
        % if conf.DJANGO_DEBUG_MODE.get() and is_admin(user):
        <li>
          <a href="javascript:void(0)" data-bind="click: function() { huePubSub.publish('editor.upload.history'); }" title="${ _('Load recent queries in order to improve recommendations') }">
            <i class="fa fa-fw fa-cloud-upload"></i> ${_('Upload history')}
          </a>
        </li>
        % endif
        <!-- /ko -->
      </ul>
    </div>
    <!-- /ko -->
  </div>
</script>

<script type="text/html" id="snippet-result-controls${ suffix }">
  <div class="snippet-actions" style="opacity:1">
    <div style="margin-top:25px;">
      <a class="snippet-side-btn" href="javascript: void(0)" data-bind="click: function() { $data.showGrid(true); huePubSub.publish('redraw.fixed.headers'); huePubSub.publish('table.extender.redraw'); }, css: {'active': $data.showGrid}" title="${ _('Grid') }">
        <i class="fa fa-fw fa-th"></i>
      </a>
    </div>

    <div class="dropdown">
      <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="css: {'active': $data.showChart }, click: function() { $data.showChart(true); }" >
        <i class="hcha fa-fw hcha-bar-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.BARCHART" title="${ _('Bars') }"></i>
        <i class="hcha fa-fw hcha-timeline-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART" title="${ _('Time') }"></i>
        <i class="hcha fa-fw hcha-pie-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.PIECHART" title="${ _('Pie') }"></i>
        <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.SCATTERCHART" title="${ _('Scatter') }"></i>
        <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.MAP" title="${ _('Marker Map') }"></i>
        <i class="hcha fa-fw hcha-map-chart" data-bind="visible: chartType() == ko.HUE_CHARTS.TYPES.GRADIENTMAP" title="${ _('Gradient Map') }"></i>
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
        <li data-bind="visible: result.cleanedDateTimeMeta().length > 0">
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART}, click: function(){ $data.showChart(true); chartType(ko.HUE_CHARTS.TYPES.TIMELINECHART); }">
            <i class="hcha hcha-timeline-chart"></i> ${_('Time')}
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
      <a class="snippet-side-btn" href="javascript:void(0)" data-bind="click: function(){ huePubSub.publish('chart.hard.reset'); isResultSettingsVisible(! isResultSettingsVisible()) }, css: { 'blue' : isResultSettingsVisible }" title="${ _('Columns') }">
        <!-- ko if: isResultSettingsVisible() -->
        <i class="fa fa-fw fa-chevron-left"></i>
        <!-- /ko -->
        <!-- ko ifnot: isResultSettingsVisible() -->
        <i class="fa fa-fw fa-columns"></i>
        <!-- /ko -->
      </a>
    </div>

    % if conf.ENABLE_DOWNLOAD.get() and not IS_EMBEDDED.get():
    <div data-bind="component: { name: 'downloadSnippetResults', params: { gridSideBtn: false, snippet: $data, notebook: $parent } }" style="display:inline-block;"></div>
    % endif
  </div>
</script>

<div class="ace-filechooser" style="display:none;">
  <div class="ace-filechooser-close">
    <a class="pointer" data-bind="click: function(){ $('.ace-filechooser').hide(); }"><i class="fa fa-times"></i></a>
  </div>
  <div class="ace-filechooser-content">
  </div>
</div>

<div id="removeSnippetModal${ suffix }" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Confirm Remove')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to remove this snippet?')}</p>
  </div>
  <div class="modal-footer" data-bind="with: $root.removeSnippetConfirmation">
    <a class="btn" data-bind="click: function() { $root.removeSnippetConfirmation(null); $('#removeSnippetModal${ suffix }').modal('hide'); }">${_('No')}</a>
    <input type="submit" value="${_('Yes')}" class="btn btn-danger" data-bind="click: function() { notebook.snippets.remove(snippet); redrawFixedHeaders(100); $root.removeSnippetConfirmation(null); $('#removeSnippetModal${ suffix }').modal('hide'); }" />
  </div>
</div>


<div class="hoverMsg hide">
  <!-- ko if: $root.editorMode() -->
  <p class="hoverText">${_('Drop a SQL file here')}</p>
  <!-- /ko -->
  <!-- ko ifnot: $root.editorMode() -->
  <p class="hoverText">${_('Drop iPython/Zeppelin notebooks here')}</p>
  <!-- /ko -->
</div>


<div id="saveAsModal${ suffix }" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <!-- ko if: $root.editorMode() -->
    <h2 class="modal-title">${_('Save query as...')}</h2>
    <!-- /ko -->
    <!-- ko ifnot: $root.editorMode() -->
    <h2 class="modal-title">${_('Save notebook as...')}</h2>
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
    <input type="button" class="btn btn-primary disable-feedback" value="${_('Save')}" data-dismiss="modal" data-bind="click: saveAsNotebook, enable: $root.selectedNotebook().name().length > 0"/>
  </div>
  <!-- /ko -->
</div>

<div id="saveToFileModal${ suffix }" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Are you sure you want to save back to File?')}</h2>
  </div>

  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <input type="button" class="btn btn-primary disable-feedback" value="${_('Save')}" data-dismiss="modal" data-bind="click: function() { huePubSub.publish('save.snippet.to.file'); }"/>
  </div>
</div>


<div id="authModal${ suffix }" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Connect to the data source')}</h2>
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


<div id="clearHistoryModal${ suffix }" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Confirm History Clear')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to clear the query history?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a class="btn btn-danger disable-feedback" data-bind="click: function() { $root.selectedNotebook().clearHistory(); }">${_('Yes')}</a>
  </div>
</div>

<!-- ko if: $root.selectedNotebook() -->
  <!-- ko with: $root.selectedNotebook() -->
  <div id="retryModal${ suffix }" class="modal hide fade" data-keyboard="false" data-backdrop="static">
    <div class="modal-header">
      <h2 class="modal-title">${_('Operation timed out')}</h2>
    </div>
    <div class="modal-body">
      <p>${_('The operation timed out. Do you want to retry?')}</p>
    </div>
    <div class="modal-footer">
      <a class="btn" data-bind="click: retryModalCancel">${_('No')}</a>
      <a class="btn btn-primary disable-feedback" data-bind="click: retryModalConfirm">${_('Yes, retry')}</a>
    </div>
  </div>
  <!-- /ko -->
<!-- /ko -->

<div class="submit-modal-editor modal hide"></div>

</%def>


<%def name="commonJS(is_embeddable=False, bindableElement='editorComponents', suffix='')">

<script type="text/javascript">
  var HUE_PUB_SUB_EDITOR_ID = (window.location.pathname.indexOf('notebook') > -1) ? 'notebook' : 'editor';
  % if is_embeddable:
  var MAIN_SCROLLABLE = '.page-content';
  % else:
  var MAIN_SCROLLABLE = '.content-panel';
  var shareViewModel = initSharing("#documentShareModal");
  % endif

  var isLeftNavOpen = false;
  huePubSub.subscribe('left.nav.open.toggle', function (val) {
    isLeftNavOpen = val;
  }, HUE_PUB_SUB_EDITOR_ID);

  huePubSub.subscribe('split.panel.resized', function (val) {
    huePubSub.publish('recalculate.name.description.width');
  }, HUE_PUB_SUB_EDITOR_ID);

  var showHoverMsg = function (e) {
    var dt = null;
    if (e) {
      dt = e.dataTransfer;
    }
    if (!isLeftNavOpen && (!dt || (dt.types && (dt.types.indexOf ? dt.types.indexOf('Files') != -1 : dt.types.contains('Files'))))) {
      $('#${ bindableElement }').find(".hoverMsg").removeClass("hide");
    }
  };

  var hideHoverMsg = function (vm) {
    if (vm.editorMode()){
      $('#${ bindableElement }').find(".hoverText").html("${_('Drop a SQL file here')}");
    } else {
      $('#${ bindableElement }').find(".hoverText").html("${_('Drop iPython/Zeppelin notebooks here')}");
    }
    $('#${ bindableElement }').find(".hoverMsg").addClass("hide");
  };

  function renderMarkdown(text, snippetId) {
    text = text.replace(/([^$]*)([$]+[^$]*[$]+)?/g, function (a, text, code) {
      return markdown.toHTML(text).replace(/^<p>|<\/p>$/g, '') + (code ? code : '');
    });
    return text;
  }

  function prepareShareModal () {
    var selectedNotebookUuid = this.selectedNotebook() && this.selectedNotebook().uuid();
    shareViewModel.setDocUuid(this.selectedNotebook().uuid());
    openShareModal();
  };

  function createHueDatatable(el, snippet, vm) {
    var DATATABLES_MAX_HEIGHT = 330;
    var invisibleRows = 10;
    if (snippet.result && snippet.result.data() && snippet.result.data().length) {
      var cols = snippet.result.data()[0].length;
      invisibleRows = cols > 200 ? 10 : (cols > 30 ? 50 : 100);
    }
    var _dt = $(el).hueDataTable({
      i18n: {
        NO_RESULTS: "${_('No results found.')}",
        OF: "${_('of')}"
      },
      fnDrawCallback: function (oSettings) {
        if (vm.editorMode()) {
          $('#queryResults').removeAttr('style');
          DATATABLES_MAX_HEIGHT = $(window).height() - $(el).parent().offset().top - 40;
          $(el).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
          $(el).jHueHorizontalScrollbar();
          $(el).parents('.dataTables_wrapper').jHueScrollLeft();
        }
        else {
          if ($(el).data('fnDraws') === 1) {
            $(el).parents(".dataTables_wrapper").jHueTableScroller({
              maxHeight: DATATABLES_MAX_HEIGHT,
              heightAfterCorrection: 0
            });
          }
        }
      },
      scrollable: vm.editorMode() && !vm.isPresentationMode() ? MAIN_SCROLLABLE : '.dataTables_wrapper',
      contained: !vm.editorMode() || vm.isPresentationMode(),
      forceInvisible: invisibleRows
    });

    window.setTimeout(function () {
      if (vm.editorMode()) {
        $(el).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
        % if conf.CUSTOM.BANNER_TOP_HTML.get():
          var bannerTopHeight = 30;
        % else:
          var bannerTopHeight = 0;
        % endif
        $(el).jHueTableExtender2({
          mainScrollable: MAIN_SCROLLABLE,
          fixedFirstColumn: vm.editorMode(),
          % if is_embeddable:
          stickToTopPosition: 48 + bannerTopHeight + ${ conf.CUSTOM.BANNER_TOP_HTML.get() and '0' or '2' },
          % else:
          stickToTopPosition: function() { return vm.isPresentationMode() || vm.isResultFullScreenMode() ? 1 + bannerTopHeight : 76 + bannerTopHeight },
          % endif
          parentId: 'snippet_' + snippet.id(),
          clonedContainerPosition: 'fixed',
          app: 'editor'
        });
        $(el).jHueHorizontalScrollbar();
      } else {
        $(el).jHueTableExtender2({
          mainScrollable: $(el).parents('.dataTables_wrapper')[0],
          fixedFirstColumn: vm.editorMode(),
          parentId: 'snippet_' + snippet.id(),
          clonedContainerPosition: 'absolute',
          app: 'editor'
        });
      }
    }, 0);


    return _dt;
  }

  function createDatatable(el, snippet, vm) {
    var parent = $(el).parent();
    // When executing few columns -> many columns -> few columns we have to clear the style
    $(el).removeAttr('style');
    if ($(el).hasClass('table-huedatatable')) {
      $(el).removeClass('table-huedatatable');
      if (parent.hasClass('dataTables_wrapper')) {
        $(el).unwrap();
      }
    }
    $(el).addClass("dt");

    var _dt = createHueDatatable(el, snippet, vm);

    var dataTableEl = $(el).parents(".dataTables_wrapper");

    if (!vm.editorMode()) {
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
    if (vm.editorMode()) {
      scrollElement = $(MAIN_SCROLLABLE);
    }

    if (scrollElement.data('scrollFnDtCreation')) {
      scrollElement.off('scroll', scrollElement.data('scrollFnDtCreation'));
    }

    var resultFollowTimeout = -1;
    var dataScroll = function () {
      if (vm.editorMode()) {
        var snippetEl = $('#snippet_' + snippet.id());
        if (snippetEl.find('.dataTables_wrapper').length > 0 && snippet.showGrid()) {
          window.clearTimeout(resultFollowTimeout);
          resultFollowTimeout = window.setTimeout(function () {
            var topCoord = vm.isPresentationMode() || vm.isResultFullScreenMode() ? 50 : 73;
            var offsetTop = 0;
            if (snippetEl.find('.dataTables_wrapper').length > 0 && snippetEl.find('.dataTables_wrapper').offset()){
              offsetTop = (snippetEl.find('.dataTables_wrapper').offset().top - topCoord) * -1;
            }
            var margin = Math.max(offsetTop, 0);
            %if conf.CUSTOM.BANNER_TOP_HTML.get():
              margin += 31;
            %endif
            if (snippet.isResultSettingsVisible()) {
              snippetEl.find('.snippet-grid-settings').css({
                "height": vm.isPresentationMode() || !vm.editorMode() ? '330px' : Math.max(100, Math.ceil($(window).height() - Math.max($('#queryResults').offset().top, topCoord)))+ 'px'
              });
              snippetEl.find('.result-settings').css({
                'marginTop': margin
              });
            }
            snippetEl.find('.snippet-actions').css({
              'marginTop': margin + 25
            });
          }, 100);
        }
      }
      if (!vm.editorMode() || (vm.editorMode() && snippet.currentQueryTab() === 'queryResults' && snippet.showGrid())) {
        var _lastScrollPosition = scrollElement.data("scrollPosition") != null ? scrollElement.data("scrollPosition") : 0;
        window.clearTimeout(_scrollTimeout);
        scrollElement.data("scrollPosition", scrollElement.scrollTop());
        _scrollTimeout = window.setTimeout(function () {
          if (vm.editorMode()) {
            _lastScrollPosition--; //hack for forcing fetching
          }
          if (_lastScrollPosition != scrollElement.scrollTop() && scrollElement.scrollTop() + scrollElement.outerHeight() + 20 >= scrollElement[0].scrollHeight && _dt && snippet.result.hasMore()) {
            huePubSub.publish('editor.snippet.result.gray', snippet);
            snippet.fetchResult(100, false);
          }
        }, 100);
      }
    };
    scrollElement.data('scrollFnDtCreation', dataScroll);
    scrollElement.on('scroll', dataScroll);
    snippet.isResultSettingsVisible.subscribe(function (newValue) {
      if (newValue) {
        dataScroll();
      }
    });

    huePubSub.subscribeOnce('chart.hard.reset', function(){
      // hard reset once the default opened chart
      var oldChartX = snippet.chartX();
      snippet.chartX(null);
      window.setTimeout(function(){
        snippet.chartX(oldChartX);
      }, 0)
    });

    return _dt;
  }

  function toggleAllColumns(linkElement, snippet) {
    var $t = $(linkElement).parents(".snippet").find("table.resultTable:eq(0)");
    var dt = $t.hueDataTable();
    dt.fnToggleAllCols(linkElement.checked);
    dt.fnDraw();
  }

  function toggleColumn(linkElement, index, snippet) {
    var $t = $(linkElement).parents(".snippet").find("table.resultTable:eq(0)");
    var dt = $t.hueDataTable();
    dt.fnSetColumnVis(index, linkElement.checked);
  }

  function scrollToColumn(linkElement, index) {
    var $resultTable = $(linkElement).parents(".snippet").find("table.resultTable:eq(0)");
    var _text = $.trim($(linkElement).text());
    var _col = $resultTable.find("th").filter(function () {
      return $.trim($(this).text()) == _text;
    });
    $resultTable.find(".columnSelected").removeClass("columnSelected");
    var _colSel = $resultTable.find("tr th:nth-child(" + (_col.index() + 1) + ")");
    if (_colSel.length > 0) {
      $resultTable.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
      $resultTable.parent().scrollLeft(_colSel.position().left + $resultTable.parent().scrollLeft() - $resultTable.parent().offset().left - 30);
      $resultTable.data('scrollToCol', _col.index());
      $resultTable.data('scrollToRow', null);
      $resultTable.data('scrollAnimate', true);
      $resultTable.parent().trigger('scroll');
    }
  }

  function isNotNullForCharts(val) {
    return val !== 'NULL' && val !== null;
  }

  function editorPieChartDataTransformer(rawDatum) {
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
      var colors = HueColors.cuiD3Scale();
      $(rawDatum.counts()).each(function (cnt, item) {
        if (isNotNullForCharts(item[_idxValue])) {
          var val = item[_idxValue] * 1;
          if (isNaN(val)) {
            val = 0;
          }
          _data.push({
            label: hueUtils.html2text(item[_idxLabel]),
            value: val,
            color: colors[cnt % colors.length],
            obj: item
          });
        }
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

    if (rawDatum.snippet.chartLimit()) {
      _data = _data.slice(0, rawDatum.snippet.chartLimit());
    }

    return _data;
  }

  function editorMapChartDataTransformer(rawDatum) {
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
        if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxRegion])) {
          _data.push({
            label: item[_idxRegion],
            value: item[_idxValue],
            obj: item
          });
        }
      });
    }

    if (rawDatum.snippet.chartLimit()) {
      _data = _data.slice(0, rawDatum.snippet.chartLimit());
    }

    return _data;
  }

  // The leaflet map can freeze the browser with numbers outside the map
  var MIN_LAT = -90;
  var MAX_LAT = 90;
  var MIN_LNG = -180;
  var MAX_LNG = 180;

  function editorLeafletMapChartDataTransformer(rawDatum) {
    var _data = [];
    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      var _idxLat = -1;
      var _idxLng = -1;
      var _idxLabel = -1;
      var _idxHeat = -1;
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
        if (col.name == rawDatum.snippet.chartMapHeat()) {
          _idxHeat = idx;
        }
      });
      if (rawDatum.snippet.chartMapLabel() != null) {
        $(rawDatum.counts()).each(function (cnt, item) {
          if (isNotNullForCharts(item[_idxLat]) && isNotNullForCharts(item[_idxLng])) {
            _data.push({
              lat: Math.min(Math.max(MIN_LAT, item[_idxLat]), MAX_LAT),
              lng: Math.min(Math.max(MIN_LNG, item[_idxLng]), MAX_LNG),
              label: hueUtils.html2text(item[_idxLabel]),
              isHeat: rawDatum.snippet.chartMapType() === 'heat',
              intensity: _idxHeat > -1 ? (item[_idxHeat]*1 != NaN ? item[_idxHeat]*1 : null) : null,
              obj: item
            });
          }
        });
      } else {
        $(rawDatum.counts()).each(function (cnt, item) {
          if (isNotNullForCharts(item[_idxLat]) && isNotNullForCharts(item[_idxLng])) {
            _data.push({
              lat: Math.min(Math.max(MIN_LAT, item[_idxLat]), MAX_LAT),
              lng: Math.min(Math.max(MIN_LNG, item[_idxLng]), MAX_LNG),
              isHeat: rawDatum.snippet.chartMapType() === 'heat',
              intensity: _idxHeat > -1 ? (item[_idxHeat]*1 != NaN ? item[_idxHeat]*1 : null) : null,
              obj: item
            });
          }
        });
      }
    }

    if (rawDatum.snippet.chartLimit()) {
      _data = _data.slice(0, rawDatum.snippet.chartLimit());
    }

    return _data;
  }


  function editorTimelineChartDataTransformer(rawDatum) {
    var _datum = [];
    var _plottedSerie = 0;

    rawDatum.snippet.result.meta().forEach(function (meta) {
      if (rawDatum.snippet.chartYMulti().indexOf(meta.name) > -1) {
        var col = meta.name;
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
          var colors = HueColors.cuiD3Scale();
          $(rawDatum.counts()).each(function (cnt, item) {
            if (isNotNullForCharts(item[_idxLabel]) && isNotNullForCharts(item[_idxValue])) {
              _data.push({
                series: _plottedSerie,
                x: new Date(moment(hueUtils.html2text(item[_idxLabel])).valueOf()),
                y: item[_idxValue] * 1,
                color: colors[_plottedSerie % colors.length],
                obj: item
              });
            }
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
          if (rawDatum.snippet.chartLimit()) {
            _data = _data.slice(0, rawDatum.snippet.chartLimit() );
          }
          _datum.push({
            key: col,
            values: _data
          });
          _plottedSerie++;
        }
      }
    });

    return _datum;
  }

  function editorMultiSerieDataTransformer(rawDatum) {
    var _datum = [];

    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYMulti().length > 0) {
      var _plottedSerie = 0;

      if (typeof rawDatum.snippet.chartXPivot() !== 'undefined') {
        var _idxValue = -1;
        var _idxLabel = -1;
        var _isXDate = false;

        rawDatum.snippet.result.meta().forEach(function (icol, idx) {
          if (icol.name == rawDatum.snippet.chartX()) {
            _isXDate = icol.type.toUpperCase().indexOf('DATE') > -1;
            _idxLabel = idx;
          }
          if (icol.name == rawDatum.snippet.chartYSingle()) {
            _idxValue = idx;
          }
        });

        rawDatum.snippet.result.meta().forEach(function (meta, cnt) {
          if (rawDatum.snippet.chartXPivot() === meta.name) {
            var _idxPivot = cnt;
            var colors = HueColors.cuiD3Scale();
            var pivotValues = $.map(rawDatum.counts(), function (p) {
              return p[_idxPivot];
            });
            pivotValues = pivotValues.filter(function (item, pos) {
              return pivotValues.indexOf(item) === pos;
            });
            pivotValues.forEach(function (val, pivotCnt) {
              var _data = [];
              $(rawDatum.counts()).each(function (cnt, item) {
                if (item[_idxPivot] === val) {
                  if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxLabel])) {
                    _data.push({
                      x: _isXDate ? moment(item[_idxLabel]) : hueUtils.html2text(item[_idxLabel]),
                      y: item[_idxValue] * 1,
                      color: colors[pivotCnt % colors.length],
                      obj: item
                    });
                  }
                }
              });
              _datum.push({
                key: hueUtils.html2text(val),
                values: _data
              });
            });
          }
        });

        // fills in missing values
        var longest = 0;
        var allXValues = [];
        _datum.forEach(function (d) {
          d.values.forEach(function (val) {
            if (allXValues.indexOf(val.x) === -1) {
              allXValues.push(val.x);
            }
          });
        });

        _datum.forEach(function (d) {
          allXValues.forEach(function (val) {
            if (!d.values.some(function (item) {
                  return item.x === val
                })) {
              var zeroObj = jQuery.extend({}, d.values[0]);
              zeroObj.y = 0;
              zeroObj.x = val;
              d.values.push(zeroObj)
            }
          });
          if (d.values.length > longest) {
            longest = d.values.length;
          }
        });


        // this is to avoid D3 js errors when the data the user is trying to display is bogus
        if (allXValues.length < longest) {
          _datum.forEach(function (d) {
            for (var i = d.values.length; i < longest; i++) {
              var zeroObj = jQuery.extend({}, d.values[0]);
              zeroObj.y = 0;
              zeroObj.x = '';
              d.values.push(zeroObj)
            }
          });
        }

        if (rawDatum.snippet.chartLimit()) {
          _datum = _datum.slice(0, rawDatum.snippet.chartLimit());
        }

        if (rawDatum.sorting == "desc") {
          _datum.forEach(function (d) {
            d.values.sort(function (a, b) {
              if (a.x > b.x) return -1;
              if (a.x < b.x) return 1;
              return 0;
            });
          });
        }
        else {
          _datum.forEach(function (d) {
            d.values.sort(function (a, b) {
              if (a.x > b.x) return 1;
              if (a.x < b.x) return -1;
              return 0;
            });
          });
        }
      }
      else {
        rawDatum.snippet.result.meta().forEach(function (meta) {
          if (rawDatum.snippet.chartYMulti().indexOf(meta.name) > -1) {
            var col = meta.name;
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
              var colors = HueColors.cuiD3Scale();
              $(rawDatum.counts()).each(function (cnt, item) {
                if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxLabel])) {
                  _data.push({
                    series: _plottedSerie,
                    x: _isXDate ? moment(item[_idxLabel]) : hueUtils.html2text(item[_idxLabel]),
                    y: item[_idxValue] * 1,
                    color: colors[cnt % colors.length],
                    obj: item
                  });
                }
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
              if (rawDatum.snippet.chartLimit()) {
                _data = _data.slice(0, rawDatum.snippet.chartLimit());
              }
              _datum.push({
                key: col,
                values: _data
              });
              _plottedSerie++;
            }
          }
        });
      }
    }
    return _datum;
  }

  function editorScatterChartDataTransformer(rawDatum) {
    var datum = {};

    if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
      var idxX = -1;
      var idxY = -1;
      var idxSize = -1;
      var idxGroup = -1;
      rawDatum.snippet.result.meta().forEach(function (icol, idx) {
        if (icol.name == rawDatum.snippet.chartX()) {
          idxX = idx;
        }
        if (icol.name == rawDatum.snippet.chartYSingle()) {
          idxY = idx;
        }
        if (icol.name == rawDatum.snippet.chartScatterSize()) {
          idxSize = idx;
        }
        if (icol.name == rawDatum.snippet.chartScatterGroup()) {
          idxGroup = idx;
        }
      });

      if (idxX > -1 && idxY > -1) {

        function createAndAddToArray(key, item) {
          if (!datum[key]) {
            datum[key] = [];
          }
          if (isNotNullForCharts(item[idxX]) && isNotNullForCharts(item[idxY])) {
            datum[key].push({
              x: item[idxX],
              y: item[idxY],
              shape: 'circle',
              size: idxSize > -1 ? item[idxSize] : 100,
              obj: item
            });
          }
        }

        if (idxGroup > -1) {
          $(rawDatum.counts()).each(function (cnt, item) {
            createAndAddToArray(item[idxGroup], item)
          });
        }
        else {
          $(rawDatum.counts()).each(function (cnt, item) {
            createAndAddToArray('distro', item)
          });
        }
      }
    }

    var returndDatum = [];
    Object.keys(datum).forEach(function (key) {
      returndDatum.push({
        key: key,
        values: rawDatum.snippet.chartLimit() ? datum[key].slice(0, rawDatum.snippet.chartLimit()) : datum[key]
      });
    });

    return returndDatum;
  }

  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    var VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode,antixss }, {
      huePubSubId: HUE_PUB_SUB_EDITOR_ID,
      user: '${ user.username }',
      userId: ${ user.id },
      suffix: '${ suffix }',
      % if is_embeddable:
      hue4: true,
      % endif
      assistAvailable: true,
      % if conf.USE_NEW_AUTOCOMPLETER.get():
      useNewAutocompleter: true,
      % endif
      autocompleteTimeout: AUTOCOMPLETE_TIMEOUT,
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
        kafkasql: {
          placeHolder: '${ _("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space") }',
          aceMode: 'ace/mode/mysql',
          snippetIcon: 'fa-database',
          sqlDialect: true
        },
        java : {
          snippetIcon: 'fa-file-code-o'
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
        spark2: {
          snippetImage: '${ static("spark/art/icon_spark_48.png") }'
        },
        mapreduce: {
          snippetIcon: 'fa-file-archive-o'
        },
        shell: {
          snippetIcon: 'fa-terminal'
        },
        sqoop1: {
          placeHolder: '${ _("Example: import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1") }',
          snippetImage: '${ static("sqoop/art/icon_sqoop_48.png") }'
        },
        distcp: {
          snippetIcon: 'fa-files-o'
        },
        sqlite: {
          placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
          aceMode: 'ace/mode/sql',
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
      $('.jHueTableExtenderClonedContainer').hide();
      $('.jHueTableExtenderClonedContainerColumn').hide();
      $('.jHueTableExtenderClonedContainerCell').hide();
      $('.fixed-header-row').hide();
      $('.fixed-first-cell').hide();
      $('.fixed-first-column').hide();
    };

    window.hideFixedHeaders = hideFixedHeaders;

    var redrawTimeout = -1;
    var redrawFixedHeaders = function (timeout) {
      var renderer = function() {
        if (! viewModel.selectedNotebook()) {
          return;
        }
        viewModel.selectedNotebook().snippets().forEach(function (snippet) {
          if (snippet.result.meta().length > 0) {
            var tableExtender = $("#snippet_" + snippet.id() + ' .resultTable').data('plugin_jHueTableExtender2');
            if (typeof tableExtender !== 'undefined') {
              tableExtender.repositionHeader();
              tableExtender.drawLockedRows();
            }
            $(MAIN_SCROLLABLE).data('lastScroll', $(MAIN_SCROLLABLE).scrollTop());
            $(MAIN_SCROLLABLE).trigger('scroll');
          }
        });
        $(".jHueTableExtenderClonedContainer").show();
        $(".jHueTableExtenderClonedContainerColumn").show();
        $(".jHueTableExtenderClonedContainerCell").show();
        $('.fixed-header-row').show();
        $('.fixed-first-cell').show();
        $('.fixed-first-column').show();
      };

      if (timeout){
        window.clearTimeout(redrawTimeout);
        redrawTimeout = window.setTimeout(renderer, timeout);
      } else {
        renderer();
      }
      %if not is_embeddable:
      $(MAIN_SCROLLABLE).jHueScrollUp();
      %endif
    };

    var splitDraggableTimeout = -1;
    huePubSub.subscribe('split.draggable.position', function () {
      window.clearTimeout(splitDraggableTimeout);
      splitDraggableTimeout = window.setTimeout(function () {
        redrawFixedHeaders(100);
      }, 200);
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('redraw.fixed.headers', function () {
      hideFixedHeaders();
      redrawFixedHeaders(200);
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('app.gained.focus', function (app) {
      if (app === 'editor') {
        huePubSub.publish('redraw.fixed.headers');
        huePubSub.publish('hue.scrollleft.show');
        huePubSub.publish('active.snippet.type.changed', viewModel.editorType());
      }
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('show.saveToFile.modal', function () {
      $('#saveToFileModal${ suffix }').modal('show');
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('tab.switched', function (tab) {
      if (tab !== 'queryResults') {
        $('.hue-datatable-search').hide();
      }
      if (tab === 'queryHistory') {
        hueUtils.waitForRendered($('#queryHistory .history-table'), function(el) { return el.is(':visible') }, function() {
          viewModel.selectedNotebook().forceHistoryInitialHeight(true);
          huePubSub.publish('editor.calculate.history.height');
        });
      }
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('detach.scrolls', function (snippet) {
      var scrollElement = $('#snippet_' + snippet.id()).find('.dataTables_wrapper');
      if (viewModel.editorMode()) {
        scrollElement = $(MAIN_SCROLLABLE);
      }
      if (scrollElement.data('scrollFnDt')) {
        scrollElement.off('scroll', scrollElement.data('scrollFnDt'));
      }
    }, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe('editor.calculate.history.height', function () {
      if (viewModel.editorMode() && (viewModel.selectedNotebook().historyInitialHeight() === 0 || viewModel.selectedNotebook().forceHistoryInitialHeight())) {
        var h = $('#queryHistory .history-table').height();
        if (h === 0) {
          h = viewModel.selectedNotebook().history().length * 32;
        }
        viewModel.selectedNotebook().historyInitialHeight(h + 80); // add pagination too
        viewModel.selectedNotebook().forceHistoryInitialHeight(false);
      }
    }, HUE_PUB_SUB_EDITOR_ID);

    window.redrawFixedHeaders = redrawFixedHeaders;

    function addAce(content, snippetType) {
      var snip = viewModel.selectedNotebook().addSnippet({type: snippetType, result: {}}, true);
      snip.statement_raw(content);
      aceChecks++;
      snip.checkForAce = window.setInterval(function () {
        if (snip.ace()) {
          window.clearInterval(snip.checkForAce);
          aceChecks--;
          if (aceChecks == 0) {
            hideHoverMsg(viewModel);
            redrawFixedHeaders(200);
          }
        }
      }, 100);
    }

    function replaceAce(content) {
      var snip = viewModel.selectedNotebook().snippets()[0];
      if (snip) {
        snip.statement_raw(content);
        snip.result.statements_count(1);
        snip.ace().setValue(content, 1);
        snip.result.statement_range({
          start: {
            row: 0,
            column: 0
          },
          end: {
            row: 0,
            column: 0
          }
        });
        snip.ace()._emit('focus');
      }
      hideHoverMsg(viewModel);
      redrawFixedHeaders(200);
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
        if (viewModel.editorMode()){
          replaceAce(raw);
        } else {
          var loaded = typeof raw == "string" ? JSON.parse(raw) : raw;
          if (loaded.nbformat) { //ipython
            var cells = [];
            if (loaded.nbformat == 3) {
              cells = loaded.worksheets[0].cells;
            } else if (loaded.nbformat == 4) {
              cells = loaded.cells;
            }
            cells.forEach(function (cell, cellCnt) {
              window.setTimeout(function () {
                if (cell.cell_type == "code") {
                  if (loaded.nbformat == 3) {
                    addPySpark($.isArray(cell.input) ? cell.input.join("") : cell.input);
                  } else {
                    addPySpark($.isArray(cell.source) ? cell.source.join("") : cell.source);
                  }
                }
                if (cell.cell_type == "heading") {
                  var heading = $.isArray(cell.source) ? cell.source.join("") : cell.source;
                  if (cell.level == 1) {
                    heading += "\n====================";
                  } else if (cell.level == 2) {
                    heading += "\n--------------------";
                  } else {
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
                } else if (content[0].indexOf("%sql") > -1 || content[0].indexOf("%hive") > -1) {
                  content.shift();
                  addSql(content.join("\n"));
                } else if (content[0].indexOf("%pyspark") > -1) {
                  content.shift();
                  addPySpark(content.join("\n"));
                } else {
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
        } else {
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

      var dropZone = $('#${ bindableElement }')[0];
      dropZone.addEventListener("dragenter", showHoverMsg, false);
      dropZone.addEventListener("dragover", handleDragOver, false);
      dropZone.addEventListener("drop", handleFileSelect, false);

      var isDraggingOverText = false;

      $('#${ bindableElement }').find(".hoverText").on("dragenter", function (e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        isDraggingOverText = true;
      });

      $('#${ bindableElement }').find(".hoverText").on("dragleave", function (e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        isDraggingOverText = false;
      });

      $('#${ bindableElement }').find(".hoverMsg").on("dragleave", function (e) {
        if (!isDraggingOverText) {
          hideHoverMsg(viewModel);
        }
      });
    }


    $(document).ready(function () {
      % if ENABLE_QUERY_SCHEDULING.get():
      viewModel = new EditorViewModel(${ editor_id or 'null' }, ${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS, CoordinatorEditorViewModel, RunningCoordinatorModel);
      % else:
      viewModel = new EditorViewModel(${ editor_id or 'null' }, ${ notebooks_json | n,unicode }, VIEW_MODEL_OPTIONS);
      % endif
      ko.applyBindings(viewModel, $('#${ bindableElement }')[0]);
      viewModel.init();

      var attachEntryResolver = function (location, sourceType, namespace, compute) {
        location.resolveCatalogEntry = function(options) {
          if (!options) {
            options = {};
          }
          if (location.resolvePathPromise && !location.resolvePathPromise.cancelled) {
            DataCatalog.applyCancellable(location.resolvePathPromise, options);
            return location.resolvePathPromise;
          }

          if (!location.identifierChain && !location.colRef && !location.colRef.identifierChain) {
            if (!location.resolvePathPromise) {
              location.resolvePathPromise = $.Deferred().reject().promise();
            }
            return location.resolvePathPromise;
          }

          var promise = SqlUtils.resolveCatalogEntry({
            sourceType: sourceType,
            namespace: namespace,
            compute: compute,
            cancellable: options.cancellable,
            cachedOnly: options.cachedOnly,
            identifierChain: location.identifierChain || location.colRef.identifierChain,
            tables: location.tables || (location.colRef && location.colRef.tables)
          });

          if (!options.cachedOnly) {
            location.resolvePathPromise = promise;
          }
          return promise;
        }
      };


      % if not IS_EMBEDDED.get():
        if (window.Worker) {
          // It can take a while before the worker is active
          var whenWorkerIsReady = function (worker, message) {
            if (!worker.isReady) {
              window.clearTimeout(worker.pingTimeout);
              worker.postMessage({ ping: true });
              worker.pingTimeout = window.setTimeout(function () {
                whenWorkerIsReady(worker, message);
              }, 500);
            } else {
              worker.postMessage(message);
            }
          };

          // For syntax checking
          var aceSqlSyntaxWorker = new Worker('/desktop/workers/aceSqlSyntaxWorker.js?v=' + HUE_VERSION);
          aceSqlSyntaxWorker.onmessage = function (e) {
            if (e.data.ping) {
              aceSqlSyntaxWorker.isReady = true;
            } else {
              huePubSub.publish('ace.sql.syntax.worker.message', e);
            }
          };

          huePubSub.subscribe('ace.sql.syntax.worker.post', function (message) {
            whenWorkerIsReady(aceSqlSyntaxWorker, message);
          });

          // For location marking
          var aceSqlLocationWorker = new Worker('/desktop/workers/aceSqlLocationWorker.js?v=' + HUE_VERSION);
          aceSqlLocationWorker.onmessage = function (e) {
            if (e.data.ping) {
              aceSqlLocationWorker.isReady = true;
            } else {
              if (e.data.locations) {
                e.data.locations.forEach(function (location) {
                  attachEntryResolver(location, e.data.sourceType, e.data.namespace, e.data.compute);
                })
              }
              huePubSub.publish('ace.sql.location.worker.message', e);
            }
          };

          huePubSub.subscribe('ace.sql.location.worker.post', function (message) {
            whenWorkerIsReady(aceSqlLocationWorker, message);
          });
        }
      % else:
        var iframe = document.createElement("iframe");
        iframe.src = (typeof adaptHueEmbeddedUrls !== 'undefined' ? adaptHueEmbeddedUrls('/notebook/workers_embedded?v=') : '/notebook/workers_embedded?v=') + HUE_VERSION;
        iframe.name = "workerFrame";
        iframe.setAttribute('style', 'display: none;');
        document.body.appendChild(iframe);

        window.addEventListener("message", function (event) {
          if (event.data.locationWorkerResponse) {
            if (event.data.locationWorkerResponse.locations) {
              event.data.locationWorkerResponse.locations.forEach(function (location) {
                attachEntryResolver(location, event.data.locationWorkerResponse.sourceType, event.data.locationWorkerResponse.namespace, event.data.locationWorkerResponse.compute);
              })
            }
            huePubSub.publish('ace.sql.location.worker.message', { data: event.data.locationWorkerResponse });
          }
          if (event.data.syntaxWorkerResponse) {
            huePubSub.publish('ace.sql.syntax.worker.message', { data: event.data.syntaxWorkerResponse });
          }
        }, false);

        huePubSub.subscribe('ace.sql.location.worker.post', function (message) {
          iframe.contentWindow.postMessage({ locationWorkerRequest: message }, '*')
        });

        huePubSub.subscribe('ace.sql.syntax.worker.post', function (message) {
          iframe.contentWindow.postMessage({ syntaxWorkerRequest: message }, '*')
        });
      % endif

      if (viewModel.isOptimizerEnabled()) {
        % if OPTIMIZER.AUTO_UPLOAD_QUERIES.get():
        huePubSub.subscribe("editor.upload.query", function (query_id) {
          viewModel.selectedNotebook().snippets()[0].uploadQuery(query_id);
        }, HUE_PUB_SUB_EDITOR_ID);
        % endif

        % if OPTIMIZER.AUTO_UPLOAD_DDL.get():
        huePubSub.subscribe('editor.upload.table.stats', function (options) {
          viewModel.selectedNotebook().snippets()[0].uploadTableStats(options);
        }, HUE_PUB_SUB_EDITOR_ID);
        % endif

        % if OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() != 0:
        huePubSub.subscribe("editor.upload.history", function () {
          viewModel.selectedNotebook().snippets()[0].uploadQueryHistory(5);
        }, HUE_PUB_SUB_EDITOR_ID);
        % endif
      }

      viewModel.selectedNotebook.subscribe(function (newVal) {
        huePubSub.publish('selected.notebook.changed', newVal);
      });

      huePubSub.subscribe('get.selected.notebook', function () {
        huePubSub.publish('set.selected.notebook', viewModel.selectedNotebook());
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('left.assist.show', function () {
        if (!viewModel.isLeftPanelVisible() && viewModel.assistAvailable()) {
          viewModel.isLeftPanelVisible(true);
        }
      }, HUE_PUB_SUB_EDITOR_ID);

      var wasResultFullScreenMode = false;
      var isAssistAvailable = viewModel.assistAvailable();
      var wasLeftPanelVisible = viewModel.isLeftPanelVisible();
      var wasRightPanelVisible = viewModel.isRightPanelVisible();

      function exitPlayerMode() {
        if (! wasResultFullScreenMode) {
          viewModel.selectedNotebook().isPresentationMode(false);
        } else {
          viewModel.isResultFullScreenMode(false);
        }
        wasResultFullScreenMode = false;
      }

      huePubSub.subscribe('editor.presentation.operate.toggle', function (value) {
        viewModel.isEditing(! viewModel.isEditing());
        if (value) {
          $(".jHueNotify").remove();
          isAssistAvailable = viewModel.assistAvailable();
          wasLeftPanelVisible = viewModel.isLeftPanelVisible();
          wasRightPanelVisible = viewModel.isRightPanelVisible();

          if (wasResultFullScreenMode) {
            huePubSub.publish('both.assists.hide', true);
          } else {
            huePubSub.publish('right.assist.hide', true);
          }

          viewModel.assistWithoutStorage(true);
          viewModel.assistAvailable(false);
          viewModel.isLeftPanelVisible(true);
          viewModel.isRightPanelVisible(false);
          window.setTimeout(function(){
            viewModel.assistWithoutStorage(false);
          }, 0);
          $(".navigator").hide();
          $(".add-snippet").hide();
          % if conf.CUSTOM.BANNER_TOP_HTML.get():
            $(".main-content").attr("style", "top: 31px!important");
          % else:
            $(".main-content").css("top", "1px");
          % endif
          redrawFixedHeaders(200);
          $(window).bind("keydown", "esc", exitPlayerMode);
        } else {
          hideFixedHeaders();
          huePubSub.publish('both.assists.show', true);
          viewModel.assistWithoutStorage(true);
          viewModel.isLeftPanelVisible(wasLeftPanelVisible);
          viewModel.isRightPanelVisible(wasRightPanelVisible);
          viewModel.assistAvailable(isAssistAvailable);
          window.setTimeout(function(){
            viewModel.assistWithoutStorage(false);
          }, 0);
          $(".navigator").show();
          $(".add-snippet").show();
          % if conf.CUSTOM.BANNER_TOP_HTML.get():
          $(".main-content").css("top", "112px");
          % else:
          $(".main-content").css("top", "74px");
          % endif
          redrawFixedHeaders(200);
          $(window).unbind("keydown", exitPlayerMode);
        }
      }, HUE_PUB_SUB_EDITOR_ID);

      viewModel.isResultFullScreenMode.subscribe(function(newValue) {
        wasResultFullScreenMode = newValue;
        huePubSub.publish('editor.presentation.operate.toggle', newValue);
      });

      huePubSub.subscribe('assist.set.manual.visibility', function () {
        wasLeftPanelVisible = viewModel.isLeftPanelVisible();
        wasRightPanelVisible = viewModel.isRightPanelVisible();
      }, HUE_PUB_SUB_EDITOR_ID);

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
        $("#authModal${ suffix }").modal("show");
      });

      $(document).on("hideHistoryModal", function (e) {
        $("#clearHistoryModal${ suffix }").modal("hide");
      });

      huePubSub.subscribe('show.retry.modal', function (data) {
        $('#retryModal${ suffix }').modal('show');
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('hide.retry.modal', function (data) {
        $('#retryModal${ suffix }').modal('hide');
      }, HUE_PUB_SUB_EDITOR_ID);

      // Close the notebook snippets when leaving the page
      window.onbeforeunload = function (e) {
        if (!viewModel.selectedNotebook().avoidClosing) {
          viewModel.selectedNotebook().close();
        }
      };
      $(window).data('beforeunload', window.onbeforeunload);

      $(".preview-sample").css("right", (10 + hueUtils.scrollbarWidth()) + "px");

      function saveKeyHandler() {
        if (viewModel.canSave()) {
          viewModel.saveNotebook();
        }
        else {
          $('#saveAsModal${ suffix }').modal('show');
        }
      }

      huePubSub.subscribe('open.link', function(link) {
        $(window).unbind("keydown.editor");
        if (link.indexOf("editor") >= 0) {
          initKeydownBindings();
        }
      });

      function initKeydownBindings() {
        $(window).bind("keydown.editor", "ctrl+s alt+s meta+s", function (e) {
          e.preventDefault();
          saveKeyHandler();
          return false;
        });
        $(window).bind("keydown.editor", "ctrl+shift+p alt+shift+p meta+shift+p", function (e) {
          e.preventDefault();
          huePubSub.publish('editor.presentation.toggle');
          return false;
        });
        $(window).bind("keydown.editor", "ctrl+e alt+e meta+e", function (e) {
          e.preventDefault();
          newKeyHandler();
          return false;
        });
      }

      if (document.location.href.indexOf("editor") >= 0) {
        initKeydownBindings();
      }

      huePubSub.subscribe('editor.presentation.toggle', function () {
        viewModel.selectedNotebook().isPresentationMode(!viewModel.isPresentationMode());
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.save', saveKeyHandler, HUE_PUB_SUB_EDITOR_ID);

      $(document).bind('keyup', function (e) {
        if (e.keyCode == 191 && e.shiftKey && !$(e.target).is('input') && !$(e.target).is('textarea')) {
          $('#helpModal${ suffix }').modal('show');
        }

        if (e.keyCode == 191 && !e.shiftKey && !$(e.target).is('input') && !$(e.target).is('textarea')) {
          if (viewModel.editorMode() && viewModel.selectedNotebook().snippets()[0].currentQueryTab() == 'queryResults') {
            e.preventDefault();
            var $t = $("#snippet_" + viewModel.selectedNotebook().snippets()[0].id()).find(".resultTable");
            $t.hueDataTable().fnShowSearch();
            return false;
          }
        }
      });

      function newKeyHandler() {
        if (!viewModel.editorMode()) {
          viewModel.selectedNotebook().newSnippet();
        }
        else {
          viewModel.newNotebook(viewModel.editorType(), null, viewModel.selectedNotebook() ? viewModel.selectedNotebook().snippets()[0].currentQueryTab() : null);
        }
      }

      huePubSub.subscribe('editor.create.new', newKeyHandler, HUE_PUB_SUB_EDITOR_ID);

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
            $('.fixed-header-row').hide();
            $('.fixed-first-cell').hide();
            $('.fixed-first-column').hide();
          },
          stop: function (e, ui) {
            $(".jHueTableExtenderClonedContainer").show();
            $(".jHueTableExtenderClonedContainerColum").show();
            $(".jHueTableExtenderClonedContainerCell").show();
            $('.fixed-header-row').show();
            $('.fixed-first-cell').show();
            $('.fixed-first-column').show();
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

      function resetResultsResizer(snippet) {
        $("#snippet_" + snippet.id()).find('.table-results .column-side').width(hueUtils.bootstrapRatios.span3() + '%').data('newWidth', hueUtils.bootstrapRatios.span3());
        if (snippet.isResultSettingsVisible()){
          $("#snippet_" + snippet.id()).find('.table-results .grid-side').data('newWidth', hueUtils.bootstrapRatios.span9()).width(hueUtils.bootstrapRatios.span9() + '%');
        }
        else {
          $("#snippet_" + snippet.id()).find('.table-results .grid-side').data('newWidth', 100).width('100%');
        }
        $("#snippet_" + snippet.id()).find('.resize-bar').css('left', '');
        try {
          $("#snippet_" + snippet.id()).find('.resize-bar').draggable('destroy');
        }
        catch (e){}

        var initialPosition = 0;

        $("#snippet_" + snippet.id()).find('.resize-bar').draggable({
          axis: "x",
          containment: $("#snippet_" + snippet.id()).find('.table-results'),
          create: function (event, ui) {
            initialPosition = $("#snippet_" + snippet.id()).find('.resize-bar').position().left;
            $("#snippet_" + snippet.id()).find('.table-results .column-side').data('newWidth', hueUtils.bootstrapRatios.span3());
            $("#snippet_" + snippet.id()).find('.meta-filter').width($("#snippet_" + snippet.id()).find('.table-results .column-side').width() - 28)
          },
          drag: function (event, ui) {
            if (initialPosition == 0){
              initialPosition = $("#snippet_" + snippet.id()).find('.resize-bar').position().left;
            }
            ui.position.left = Math.max(150, ui.position.left);
            var newSpan3Width = ui.position.left * hueUtils.bootstrapRatios.span3() / initialPosition;
            var newSpan9Width = 100 - newSpan3Width - hueUtils.bootstrapRatios.margin();
            $("#snippet_" + snippet.id()).find('.table-results .column-side').width(newSpan3Width + '%').data('newWidth', newSpan3Width);
            $("#snippet_" + snippet.id()).find('.table-results .grid-side').width(newSpan9Width + '%').data('newWidth', newSpan9Width);
            $("#snippet_" + snippet.id()).find('.meta-filter').width($("#snippet_" + snippet.id()).find('.table-results .column-side').width() - 28)
          },
          stop: function () {
            redrawFixedHeaders();
            huePubSub.publish('resize.leaflet.map');
          }
        });
      }

      $(document).on("toggleResultSettings", function (e, snippet) {
        window.setTimeout(function () {
          $('#snippet_' + snippet.id()).find('.chart').trigger("forceUpdate");
          $('#snippet_' + snippet.id()).find('.snippet-grid-settings').scrollLeft(0);
          if (snippet.isResultSettingsVisible()){
            $("#snippet_" + snippet.id()).find('.table-results .grid-side').width((100 - $("#snippet_" + snippet.id()).find('.table-results .column-side').data('newWidth') - hueUtils.bootstrapRatios.margin()) + '%');
          }
          else {
            $("#snippet_" + snippet.id()).find('.table-results .grid-side').width('100%');
          }
          redrawFixedHeaders();
          $(window).trigger('resize');
        }, 10)
      });

      $(document).on("editorSizeChanged", function () {
        window.setTimeout(forceChartDraws, 50);
      });

      $(document).on("redrawResults", function () {
        window.setTimeout(forceChartDraws, 50);
      });

      $(document).on("executeStarted", function (e, options) {
        var $el = $("#snippet_" + options.snippet.id()).find(".resultTable");
        if (options.vm.editorMode()) {
          $('#queryResults').css({
            height: $el.height() + 'px'
          });
        }
        $el.data('scrollToCol', null);
        $el.data('scrollToRow', null);
        $("#snippet_" + options.snippet.id()).find(".progress-snippet").animate({
          height: "3px"
        }, 100);
        if ($el.hasClass("dt")) {
          $el.removeClass("dt");
          $("#eT" + options.snippet.id() + "jHueTableExtenderClonedContainer").remove();
          $("#eT" + options.snippet.id() + "jHueTableExtenderClonedContainerColumn").remove();
          $("#eT" + options.snippet.id() + "jHueTableExtenderClonedContainerCell").remove();
          if ($el.hueDataTable()) {
            $el.hueDataTable().fnDestroy();
          }
          $el.find("thead tr").empty();
          $el.data('lockedRows', {});
        }
      });

      function resizeToggleResultSettings (snippet, initial) {
        var _dtElement;
        if (snippet.showGrid()) {
          _dtElement = $("#snippet_" + snippet.id()).find(".dataTables_wrapper");
          var topCoord = viewModel.isPresentationMode() || viewModel.isResultFullScreenMode() ? ${ conf.CUSTOM.BANNER_TOP_HTML.get() and '31' or '1' } : 73;
          $("#snippet_" + snippet.id()).find(".snippet-grid-settings").css({
            "height": viewModel.isPresentationMode() || !viewModel.editorMode() ? '330px' : Math.ceil($(window).height() - Math.max($('.result-settings').length > 0 ? $('.result-settings').offset().top : 0, topCoord)) + 'px'
          });
        } else {
          _dtElement = $("#snippet_" + snippet.id()).find(".chart:visible");
        }
        if (_dtElement.length == 0) {
          _dtElement = $("#snippet_" + snippet.id()).find(".table-results");
        }
        _dtElement.parents(".snippet-body").find(".toggle-result-settings").css({
          "height": (_dtElement.height() - 30) + "px",
          "line-height": (_dtElement.height() - 30) + "px"
        });
        if (initial) {
          $('#snippet_' + snippet.id()).find('.result-settings').css({
            'marginTop': 0
          });
          $('#snippet_' + snippet.id()).find('.snippet-actions').css({
            'marginTop': 0
          });
          huePubSub.publish('resize.leaflet.map');
        }
      }

      huePubSub.subscribe('editor.render.data', function (options) {
        var _el = $("#snippet_" + options.snippet.id()).find(".resultTable");
        if (options.data.length > 0) {
          window.setTimeout(function () {
            var _dt;
            if (options.initial) {
              options.snippet.result.meta.notifySubscribers();
              $("#snippet_" + options.snippet.id()).find("select").trigger("chosen:updated");
              _dt = createDatatable(_el, options.snippet, viewModel);
              resetResultsResizer(options.snippet);
            } else {
              _dt = _el.hueDataTable();
            }
            try {
              _dt.fnAddData(options.data);
            } catch (e) {}
            var _dtElement = $("#snippet_" + options.snippet.id()).find(".dataTables_wrapper");
            huePubSub.publish('editor.snippet.result.normal', options.snippet);
            _dtElement.scrollTop(_dtElement.data("scrollPosition"));
            redrawFixedHeaders();
            resizeToggleResultSettings(options.snippet, options.initial);
          }, 300);
        } else {
          huePubSub.publish('editor.snippet.result.normal', options.snippet);
        }
        $("#snippet_" + options.snippet.id()).find("select").trigger('chosen:updated');
        $('#snippet_' + options.snippet.id()).find('.snippet-grid-settings').scrollLeft(0);
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.redraw.data', function (options) {
        hueUtils.waitForRendered("#snippet_" + options.snippet.id() + " .resultTable", function (el) {
          return el.is(':visible')
        }, function () {
          var $el = $("#snippet_" + options.snippet.id()).find(".resultTable");
          var dt = createDatatable($el, options.snippet, viewModel);
          dt.fnAddData(options.snippet.result.data());
        });
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.snippet.result.gray', function (snippet) {
        var $snippet = $("#snippet_" + snippet.id());
        $snippet.find(".dataTables_wrapper .fixed-first-column").css({opacity: '0'});
        $snippet.find(".dataTables_wrapper .fixed-header-row").css({opacity: '0'});
        $snippet.find(".dataTables_wrapper .fixed-first-cell").css({opacity: '0'});
        $snippet.find(".dataTables_wrapper .resultTable").css({opacity: '0.55'});
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.snippet.result.normal', function (snippet) {
        var $snippet = $("#snippet_" + snippet.id());
        $snippet.find(".dataTables_wrapper .fixed-first-column").css({opacity: '1'});
        $snippet.find(".dataTables_wrapper .fixed-header-row").css({opacity: '1'});
        $snippet.find(".dataTables_wrapper .fixed-first-cell").css({opacity: '1'});
        $snippet.find(".dataTables_wrapper .resultTable").css({opacity: '1'});
      }, HUE_PUB_SUB_EDITOR_ID);

      $(document).on("renderDataError", function (e, options) {
        huePubSub.publish('editor.snippet.result.normal', options.snippet);
      });

      $(document).on("progress", function (e, options) {
        if (options.data == 100) {
          window.setTimeout(function () {
            $("#snippet_" + options.snippet.id()).find(".progress-snippet").animate({
              height: "0"
            }, 100, function () {
              options.snippet.progress(0);
              redrawFixedHeaders();
            });
          }, 2000);
        }
      });

      huePubSub.subscribe('render.jqcron', function(){
        if (typeof renderJqCron !== 'undefined'){
          renderJqCron();
        }
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('submit.popup.return', function (data) {
        viewModel.selectedNotebook().viewSchedulerId(data.job_id);
        $('.submit-modal-editor').modal('hide');
        huePubSub.publish('show.jobs.panel', {id: data.job_id, interface: 'workflows'});
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('jobbrowser.data', function (jobs) {
        var snippet = viewModel.selectedNotebook().snippets()[0];
        if (!snippet || snippet.type() === 'impala') {
          return;
        }
        if (jobs.length > 0) {
          jobs.forEach(function (job) {
            if ($("#" + job.shortId).length > 0) {
              var _job = ko.dataFor($("#" + job.shortId)[0]);
              if (!isNaN(parseInt(job.mapsPercentComplete))) {
                _job.percentJob(parseInt(job.mapsPercentComplete));
              }
            }
          });
        } else {
          if (viewModel.selectedNotebook()) {
            viewModel.selectedNotebook().snippets().forEach(function (snippet) {
              snippet.jobs().forEach(function (job) {
                job.percentJob(100);
              });
            });
          }
        }
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.get.active.risks', function (callback) {
        var result = {
          editor: undefined,
          risks : {}
        };
        if (viewModel.selectedNotebook()) {
          if (viewModel.selectedNotebook().snippets().length === 1) {
            result.editor = viewModel.selectedNotebook().snippets()[0].ace();
            result.risks = viewModel.selectedNotebook().snippets()[0].complexity() || {};
          } else {
            var notFound = viewModel.selectedNotebook().snippets().every(function (snippet) {
              if (snippet.inFocus()) {
                result.editor = snippet.ace();
                result.risks = snippet.complexity() || {};
                return false;
              }
              return true;
            });
          }
        }
        callback(result);
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.grid.shown', function (snippet) {
        hueUtils.waitForRendered('#snippet_' + snippet.id() + ' .dataTables_wrapper', function (el) {
          return el.is(':visible')
        }, function () {
          resizeToggleResultSettings(snippet, true);
          forceChartDraws();
          $('#snippet_' + snippet.id()).find('.snippet-grid-settings').scrollLeft(0);
        });
      }, HUE_PUB_SUB_EDITOR_ID);

      huePubSub.subscribe('editor.chart.shown', function (snippet) {
        resizeToggleResultSettings(snippet, true);
      }, HUE_PUB_SUB_EDITOR_ID);

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
          var $aceAutocomplete = $(".ace_editor.ace_autocomplete");
          if ($aceAutocomplete.is(":visible")) {
            $aceAutocomplete.hide();
          }
        }, 100);
      });

      function forceChartDraws(initial) {
        if (viewModel.selectedNotebook()) {
          viewModel.selectedNotebook().snippets().forEach(function (snippet) {
            if (snippet.result.data().length > 0) {
              var _elCheckerInterval = -1;
              var _el = $("#snippet_" + snippet.id());
              _elCheckerInterval = window.setInterval(function () {
                if (_el.find(".resultTable").length > 0) {
                  try {
                    resizeToggleResultSettings(snippet, initial);
                    resetResultsResizer(snippet);
                    $(document).trigger("forceChartDraw", snippet);
                  } catch (e) { }
                  window.clearInterval(_elCheckerInterval);
                }
              }, 200)
            }
          });
        }
      }

      forceChartDraws(true);

      huePubSub.subscribe('recalculate.name.description.width', function () {
        hueUtils.waitForRendered('.editorComponents .hue-title-bar .query-name', function(el){ return el.is(':visible') }, function(){
          var cumulativeWidth = 0;
          $('.editorComponents .hue-title-bar ul li:not(.skip-width-calculation)').each(function(){
            cumulativeWidth += $(this).outerWidth();
          });
          $('.notebook-name-desc').css('max-width', (($('.editorComponents .hue-title-bar').width() - cumulativeWidth - $('.editorComponents .hue-title-bar .pull-right').width() - 120)/2) + 'px');
        });
      }, HUE_PUB_SUB_EDITOR_ID);

      var _resizeTimeout = -1;
      $(window).on("resize", function () {
        huePubSub.publish('recalculate.name.description.width');
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(function () {
          forceChartDraws();
        }, 200);
      });
    });
  })();
</script>

</%def>
