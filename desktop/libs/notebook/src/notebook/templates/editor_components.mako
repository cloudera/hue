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

from webpack_loader.templatetags.webpack_loader import render_bundle

from desktop import conf
from desktop.auth.backend import is_admin
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko, antixss
from desktop.webpack_utils import get_hue_bundles

from metadata.conf import has_optimizer, OPTIMIZER

from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, ENABLE_BATCH_EXECUTE, ENABLE_EXTERNAL_STATEMENT, ENABLE_PRESENTATION
%>

<%def name="includes(is_embeddable=False, suffix='')">
<link rel="stylesheet" href="${ static('dashboard/css/common_dashboard.css') }">
% if not is_embeddable:
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
% endif
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">

<link rel="stylesheet" href="${ static('desktop/ext/css/medium-editor.min.css') }">
<link rel="stylesheet" href="${ static('desktop/css/bootstrap-medium-editor.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-datepicker.min.css') }">

% if not is_embeddable:
<script src="${ static('desktop/js/share2.vm.js') }"></script>
% endif

% if ENABLE_QUERY_SCHEDULING.get():
<script src="${ static('oozie/js/coordinator-editor.ko.js') }"></script>
<script src="${ static('oozie/js/list-oozie-coordinator.ko.js') }"></script>
% endif

<script src="${ static('desktop/js/ko.common-dashboard.js') }" type="text/javascript" charset="utf-8"></script>

%if ENABLE_QUERY_BUILDER.get():
<!-- For query builder -->
<link rel="stylesheet" href="${ static('desktop/ext/css/jquery.contextMenu.min.css') }">
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

% for bundle in get_hue_bundles('notebook'):
  ${ render_bundle(bundle) | n,unicode }
% endfor

<!--[if IE 9]>
  <script src="${ static('desktop/ext/js/classList.min.js') }" type="text/javascript" charset="utf-8"></script>
<![endif]-->

<%namespace name="dashboard" file="/common_dashboard.mako" />
<%namespace name="sqlSyntaxDropdown" file="/sql_syntax_dropdown.mako" />

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
          <li class="app-header" style="display:none" data-bind="visible: true">
            <!-- ko if: editorMode -->
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
                <!-- ko case: 'clickhouse' -->ClickHouse<!-- /ko -->
                <!-- ko case: $default --><span data-bind="text: editorTypeTitle()"></span><!-- /ko -->
              <!-- /ko -->
              <!-- ko component: { name: 'hue-favorite-app', params: { app: 'editor', interpreter: editorType() }} --><!-- /ko -->
              </a>
            <!-- /ko -->
            <!-- ko ifnot: editorMode -->
              <i class="fa fa-file-text-o app-icon" style="vertical-align: middle"></i>
                Notebook
              <!-- ko component: { name: 'hue-favorite-app', params: { app: 'notebook' }} --><!-- /ko -->
            <!-- /ko -->
          </li>

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
        </ul>
      </div>
    </div>
  </div>
</div>


<script type="text/html" id="notebook-menu-buttons-${ suffix }">
  <div class="pull-right margin-right-10">
  % if ENABLE_PRESENTATION.get():
    <!-- ko with: selectedNotebook() -->
      <div class="btn-group">
        <a class="btn" data-bind="click: function() { isPresentationMode(!isPresentationMode()); },
        css: {'btn-inverse': $root.isPresentationMode()}, attr: {title: isPresentationMode() ? '${ _ko('Exit presentation') }' : '${ _ko('View as a presentation') }'}">
          <i class="fa fa-line-chart"></i>
        </a>

        <!-- ko if: $root.canSave() -->
        <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)"><span class="caret"></span></a>
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

    <div class="btn-group">
      <a class="btn" rel="tooltip" data-placement="bottom" data-loading-text="${ _("Saving...") }" data-bind="click: function() { if ($root.canSave() ) { saveNotebook() } else { $('#saveAsModal${ suffix }').modal('show');} }, attr: { title: $root.canSave() ? '${ _ko('Save') }' : '${ _ko('Save As') }' }">
        <i class="fa fa-save"></i>
      </a>

      <!-- ko if: $root.canSave -->
      <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)"><span class="caret"></span></a>
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
          <a href="javascript:void(0)" data-bind="click: function() { hueUtils.removeURLParameter('editor'); newNotebook($root.editorType(), null, selectedNotebook() ? $root.selectedNotebook().snippets()[0].currentQueryTab() : null); }, attr: { 'title': '${ _('New ') }' +  editorTypeTitle() + '${ _(' Query') }' }">
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
          <a href="javascript:void(0)" data-bind="publish: { 'assist.show.documents': editorMode() ? 'query-' + editorType() : editorType() }">
            <svg class="hi hi-fw hi-bigger"><use xlink:href="#hi-documents"></use></svg> <span data-bind="text: editorMode() ? '${ _ko('Queries') }' : '${ _ko('Notebooks') }'"></span>
          </a>
        </li>
        <li class="divider"></li>
        <!-- ko if: $root.canSave -->
        <!-- ko if: sharingEnabled -->
        <li>
          <a class="share-link pointer" data-bind="click: prepareShareModal,
              css: {'isShared': isShared()}">
            <i class="fa fa-fw fa-users"></i> ${ _('Share') }
          </a>
        </li>
        <!-- /ko -->
        <!-- /ko -->
        <li>
          <a class="pointer" data-bind="publish: {'context.panel.visible': true}">
            <i class="fa fa-fw fa-cogs"></i> ${ _('Session') }
          </a>
        </li>
      </ul>
    </div>
    <!-- /ko -->
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
    <a href="javascript: void(0)" class="btn" data-dismiss="modal">${_('Close')}</a>
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
    <a href="javascript: void(0)" class="btn" data-dismiss="modal">${_('Close')}</a>
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
          <!-- ko if: type() == 'impala' && typeof http_addr != 'undefined' -->
            <a class="margin-left-10" data-bind="attr: {'href': http_addr()}" target="_blank">
              <span data-bind="text: http_addr().replace(/^(https?):\/\//, '')"></span> <i class="fa fa-external-link"></i>
            </a>
          <!-- /ko -->
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
  <div class="snippet-log-container margin-bottom-10" data-bind="visible: showLogs">
    <div data-bind="delayedOverflow: 'slow', css: resultsKlass" style="margin-top: 5px; position: relative;">
      <a href="javascript: void(0)" class="inactive-action close-logs-overlay" data-bind="click: function(){ showLogs(false) }">&times;</a>
      <ul data-bind="visible: jobs().length > 0, foreach: jobs" class="unstyled jobs-overlay">
        <li data-bind="attr: {'id': $data.name.substr(4)}">
          % if is_embeddable:
            <a class="pointer" data-bind="text: $.trim($data.name), click: function() { huePubSub.publish('show.jobs.panel', {id: $data.name, interface: $parent.type() == 'impala' ? 'queries' : 'jobs', compute: $parent.compute}); }, clickBubble: false"></a>
          % else:
            <a data-bind="text: $.trim($data.name), hueLink: $data.url"></a>
          % endif
          <!-- ko if: typeof percentJob === 'function' && percentJob() > -1 -->
          <div class="progress-job progress pull-left" style="background-color: #FFF; width: 100%" data-bind="css: {'progress-warning': percentJob() < 100, 'progress-success': percentJob() === 100}">
            <div class="bar" data-bind="style: {'width': percentJob() + '%'}"></div>
          </div>
          <!-- /ko -->
          <div class="clearfix"></div>
        </li>
      </ul>
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
          <a class="inactive-action" style="display:inline-block" href="#queryHistory" data-toggle="tab">${_('Query History')}</a>
          <div style="margin-left: -15px;" class="inline-block inactive-action pointer visible-on-hover" title="${_('Search the query history')}" data-bind="click: function(data, e){ $parent.historyFilterVisible(!$parent.historyFilterVisible()); if ($parent.historyFilterVisible()) { window.setTimeout(function(){ $(e.target).parent().siblings('input').focus(); }, 0); } else { $parent.historyFilter('') }}"><i class="snippet-icon fa fa-search"></i></div>
          <input class="input-small inline-tab-filter" type="text" data-bind="visible: $parent.historyFilterVisible, clearable: $parent.historyFilter, valueUpdate:'afterkeydown'" placeholder="${ _('Search...') }">
          <div class="dropdown inline-block inactive-action pointer visible-on-hover">
            <a class="" data-toggle="dropdown" href="javascript: void(0)">
              <i class="fa fa-fw fa-ellipsis-v"></i>
            </a>
            <ul class="dropdown-menu">
              <li data-bind="visible: $parent.history().length > 0">
                <!-- ko if: editorMode -->
                <a data-target="#clearHistoryModal${ suffix }" data-toggle="modal" rel="tooltip">
                  <i class="fa fa-fw fa-calendar-times-o"></i> Clear
                </a>
                <!-- /ko -->
                <!-- ko ifnot: editorMode --><!-- /ko -->
              </li>
              <li><a href="javascript:void(0);" data-bind="click: exportHistory.bind($data)"><i class="fa fa-fw fa-download"></i> ${_('Export')}</a></li>
              <li><a href="javascript:void(0);" data-bind="publish: { 'show.import.documents.modal': { importedCallback: refreshHistory.bind($data), isHistory: true }}"><i class="fa fa-fw fa-upload"></i> ${_('Import' )}</a></li>
            </ul>
          </div>
        </li>
        <li class="margin-right-20" data-bind="click: function(){ currentQueryTab('savedQueries'); }, css: {'active': currentQueryTab() == 'savedQueries'}, onClickOutside: function () { if (queriesFilterVisible() && queriesFilter() === '') { queriesFilterVisible(false) } }">
          <a class="inactive-action" style="display:inline-block" href="#savedQueries" data-toggle="tab">${_('Saved Queries')}</a>
          <div style="margin-left: -15px;" class="inline-block inactive-action pointer visible-on-hover" title="${_('Search the saved queries')}" data-bind="visible: !queriesHasErrors(), click: function(data, e){ queriesFilterVisible(!queriesFilterVisible()); if (queriesFilterVisible()) { window.setTimeout(function(){ $(e.target).parent().siblings('input').focus(); }, 0); } else { queriesFilter('') }}"><i class="snippet-icon fa fa-search"></i></div>
          <input class="input-small inline-tab-filter" type="text" data-bind="visible: queriesFilterVisible, clearable: queriesFilter, valueUpdate:'afterkeydown'" placeholder="${ _('Search...') }">
        </li>
        % if ENABLE_QUERY_BUILDER.get():
        <!-- ko if: isSqlDialect -->
        <li style="margin-right: 25px;" data-bind="click: function(){ currentQueryTab('queryBuilderTab'); }, css: {'active': currentQueryTab() == 'queryBuilderTab'}"><a class="inactive-action" href="#queryBuilderTab" data-toggle="tab">${_('Query Builder')}</a></li>
        <!-- /ko -->
        % endif
        <!-- ko if: result.hasSomeResults -->
        <li data-bind="click: function(){ currentQueryTab('queryResults'); }, css: {'active': currentQueryTab() == 'queryResults'}">
          <a class="inactive-action" style="display:inline-block" href="#queryResults" data-toggle="tab">${_('Results')}
            <!-- ko if: result.rows() != null  -->
              (<span data-bind="text: result.rows().toLocaleString() + (type() == 'impala' && result.rows() == 1024 ? '+' : '')" title="${ _('Number of rows') }"></span>)
            <!-- /ko -->
          </a>
          <div style="margin-left: -15px;" class="inline-block">
            <!-- ko if: showGrid -->
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Search the results')}" data-bind="click: function(data, e){ $(e.target).parents('.snippet').find('.resultTable').hueDataTable().fnShowSearch() }">
              <i class="snippet-icon fa fa-search"></i>
            </div>
            <!-- /ko -->
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Expand results')}" rel="tooltip" data-bind="css: { 'margin-left-10': !showGrid()}, visible: !$root.isResultFullScreenMode(), click: function(){ $root.isResultFullScreenMode(true); }">
              <i class="snippet-icon fa fa-expand"></i>
            </div>
            <div class="inline-block inactive-action pointer visible-on-hover" title="${_('Collapse results')}" rel="tooltip" data-bind="visible: $root.isResultFullScreenMode(), click: function(){ $root.isResultFullScreenMode(false); }">
              <i class="snippet-icon fa fa-compress"></i>
            </div>
          </div>
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

        <!-- ko if: HAS_WORKLOAD_ANALYTICS && type() === 'impala' -->
        <li data-bind="visible: showExecutionAnalysis, click: function(){ currentQueryTab('executionAnalysis'); }, css: {'active': currentQueryTab() == 'executionAnalysis'}"><a class="inactive-action" href="#executionAnalysis" data-toggle="tab" data-bind="click: function(){ $('a[href=\'#executionAnalysis\']').tab('show'); }, event: {'shown': fetchExecutionAnalysis }"><span>${_('Execution Analysis')} </span><span></span></a></li>
        <!-- /ko -->
      </ul>

      <div class="tab-content" style="border: none; overflow-x: hidden">
        <div class="tab-pane" style="min-height:80px;" id="queryHistory" data-bind="css: {'active': currentQueryTab() == 'queryHistory'}, style: { 'height' : $parent.historyInitialHeight() > 0 ? Math.max($parent.historyInitialHeight(), 40) + 'px' : '' }">
          <!-- ko if: $parent.loadingHistory -->
          <div class="margin-top-10 margin-left-10">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->

          <!-- ko ifnot: $parent.loadingHistory -->
            <!-- ko if: $parent.history().length === 0 && $parent.historyFilter() === '' -->
            <div class="margin-top-10 margin-left-10" style="font-style: italic">${ _("No queries to be shown.") }</div>
            <!-- /ko -->
            <!-- ko if: $parent.history().length === 0 && $parent.historyFilter() !== '' -->
            <div class="margin-top-10 margin-left-10" style="font-style: italic">${ _('No queries found for') } <strong data-bind="text: $parent.historyFilter"></strong>.</div>
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
          <div class="margin-top-10 margin-left-10">
            <i class="fa fa-spinner fa-spin muted"></i>
          </div>
          <!-- /ko -->
          <!-- ko if: queriesHasErrors() -->
          <div class="margin-top-10 margin-left-10" style="font-style: italic">${ _("Error loading my queries") }</div>
          <!-- /ko -->
          <!-- ko if: !queriesHasErrors() && !loadingQueries() && queries().length === 0 && queriesFilter() === '' -->
          <div class="margin-top-10 margin-left-10" style="font-style: italic">${ _("You don't have any saved queries.") }</div>
          <!-- /ko -->
          <!-- ko if: !queriesHasErrors() && !loadingQueries() && queries().length === 0 && queriesFilter() !== '' -->
          <div class="margin-top-10 margin-left-10" style="font-style: italic">${ _('No queries found for') } <strong data-bind="text: queriesFilter"></strong>.</div>
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

        <!-- ko if: HAS_WORKLOAD_ANALYTICS && type() === 'impala' -->
        <div class="tab-pane" id="executionAnalysis" data-bind="css: {'active': currentQueryTab() == 'executionAnalysis'}" style="padding: 10px;">
          <!-- ko component: { name: 'hue-execution-analysis' } --><!-- /ko -->
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
        connector: connector,
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
  % if ENABLE_EXTERNAL_STATEMENT.get():
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
          <!-- ko template: { if: $root.editorMode() && ! $root.isResultFullScreenMode() && ['jar', 'java', 'spark2', 'distcp', 'shell', 'mapreduce', 'py'].indexOf(type()) == -1, name: 'snippet-code-resizer${ suffix }' } --><!-- /ko -->
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
        readOnly: $root.isPresentationMode(),
        aceOptions: {
          showLineNumbers: $root.editorMode(),
          showGutter: $root.editorMode(),
          maxLines: $root.editorMode() ? null : 25,
          minLines: $root.editorMode() ? null : 3
        }
      }, style: {opacity: statementType() !== 'text' || $root.isPresentationMode() ? '0.75' : '1', 'min-height': $root.editorMode() ? '0' : '48px', 'top': $root.editorMode() && statementType() !== 'text' ? '60px' : '0'}"></div>
      <!-- ko component: { name: 'hueAceAutocompleter', params: { editor: ace.bind($data), snippet: $data } } --><!-- /ko -->
      <!-- ko component: { name: 'hue-editor-droppable-menu', params: { editor: ace.bind($data), parentDropTarget: '.editor' } } --><!-- /ko -->
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

    <a class="btn dropdown-toggle" data-toggle="dropdown" href="javascript: void(0)">
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
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
          <!-- ko if: meta.type() === 'text' -->
            <!-- ko if: meta.placeholder() -->
              <input class="input-medium" type="text" data-bind="value: value, attr: { value: value, type: type, placeholder: meta.placeholder() || '${ _ko('Variable value') }' }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
            <!-- /ko -->
            <!-- ko ifnot: meta.placeholder() -->
              <!-- ko if: type() == 'datetime-local' -->
              <input class="input-medium" type="text" data-bind="attr: { value: value }, value: value, datepicker: { momentFormat: 'YYYY-MM-DD HH:mm:ss.S' }">
              <!-- /ko -->
              <!-- ko if: type() == 'date' -->
              <input class="input-medium" type="text" data-bind="attr: { value: value }, value: value, datepicker: { momentFormat: 'YYYY-MM-DD' }">
              <!-- /ko -->
              <!-- ko if: type() == 'checkbox' -->
              <input class="input-medium" type="checkbox" data-bind="checked: value">
              <!-- /ko -->
              <!-- ko ifnot: (type() == 'datetime-local' || type() == 'date' || type() == 'checkbox') -->
              <input class="input-medium" type="text" value="true" data-bind="value: value, attr: { value: value,  type: type() || 'text', step: step }, valueUpdate: 'afterkeydown', event: { 'keydown': $parent.onKeydownInVariable }, autogrowInput: { minWidth: 150, maxWidth: 270, comfortZone: 15 }">
              <!-- /ko -->
            <!-- /ko -->
          <!-- /ko -->
          <!-- ko if: meta.type() === 'select' -->
            <select data-bind="
                selectize: sample,
                optionsText: 'text',
                optionsValue: 'value',
                selectizeOptions: {
                  create: function (input) {
                    sampleUser().push({ text: ko.observable(input), value: ko.observable(input) });
                    return { text: input, value: input };
                  }
                },
                value: value,
                event: { 'keydown': $parent.onKeydownInVariable }
              "></select>
          <!-- /ko -->
        </div>
      </li>
    </ul>
  </div>
</script>


<script type="text/html" id="snippet-chart-settings${ suffix }">
  <div>
    <!-- ko if: chartType() != '' && [window.HUE_CHARTS.TYPES.TIMELINECHART, window.HUE_CHARTS.TYPES.BARCHART].indexOf(chartType()) >= 0  -->
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

    <!-- ko if: chartType() != '' && chartType() === window.HUE_CHARTS.TYPES.PIECHART -->
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

    <!-- ko if: chartType() != '' && chartType() !== window.HUE_CHARTS.TYPES.PIECHART -->
    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li data-bind="visible: [window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartType()) == -1" class="nav-header">${_('x-axis')}</li>
      <li data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('region')}</li>
      <li data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('latitude')}</li>
    </ul>
    <div>
      <select data-bind="options: ([window.HUE_CHARTS.TYPES.BARCHART, window.HUE_CHARTS.TYPES.GRADIENTMAP, window.HUE_CHARTS.TYPES.TIMELINECHART].indexOf(chartType()) > -1) ? ( chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART ? result.cleanedDateTimeMeta : result.cleanedMeta ) : result.cleanedNumericMeta, value: chartX, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartX, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != ''">
      <li data-bind="visible: [window.HUE_CHARTS.TYPES.MAP, window.HUE_CHARTS.TYPES.GRADIENTMAP].indexOf(chartType()) == -1" class="nav-header">${_('y-axis')}</li>
      <li data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP" class="nav-header">${_('value')}</li>
      <li data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.MAP" class="nav-header">${_('longitude')}</li>
    </ul>

    <div style="max-height: 220px" data-bind="delayedOverflow, visible: chartType() != '' && ((chartType() == window.HUE_CHARTS.TYPES.BARCHART && !chartXPivot()) || chartType() == window.HUE_CHARTS.TYPES.LINECHART || chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART)">
      <ul class="unstyled" data-bind="foreach: result.cleanedNumericMeta" style="margin-bottom: 0">
        <li><label class="checkbox"><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></label></li>
      </ul>
    </div>
    <div data-bind="visible: (chartType() == window.HUE_CHARTS.TYPES.BARCHART && chartXPivot()) || chartType() == window.HUE_CHARTS.TYPES.MAP || chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP || chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP ? result.cleanedMeta : result.cleanedNumericMeta, value: chartYSingle, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartYSingle, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>
    <!-- /ko -->

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.BARCHART">
      <li class="nav-header">${_('group')}</li>
    </ul>
    <div data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.BARCHART">
      <select data-bind="options: result.cleanedMeta, value: chartXPivot, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column to pivot...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column to pivot...") }', update: chartXPivot, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF">
      <li class="nav-header">${_('limit')}</li>
    </ul>
    <div>
      <select data-bind="options: chartLimits, value: chartLimit, optionsCaption: '${_ko('Limit the number of results to...')}', select2: { width: '100%', placeholder: '${ _ko("Limit the number of results to...") }', update: chartLimit, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <!-- ko if: chartType() != '' && chartType() == window.HUE_CHARTS.TYPES.MAP -->
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

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART">
      <li class="nav-header">${_('scatter size')}</li>
    </ul>
    <div data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: result.cleanedNumericMeta, value: chartScatterSize, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterSize, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART">
      <li class="nav-header">${_('scatter group')}</li>
    </ul>
    <div data-bind="visible: chartType() != '' && chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART">
      <select data-bind="options: result.cleanedMeta, value: chartScatterGroup, optionsText: 'name', optionsValue: 'name', optionsCaption: '${_ko('Choose a column...')}', select2: { width: '100%', placeholder: '${ _ko("Choose a column...") }', update: chartScatterGroup, dropdownAutoWidth: true}" class="input-medium"></select>
    </div>

    <!-- ko if: chartType() != '' && chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP -->
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

    <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: chartType() != '' && chartType() != window.HUE_CHARTS.TYPES.MAP && chartType() != window.HUE_CHARTS.TYPES.GRADIENTMAP && chartType() != window.HUE_CHARTS.TYPES.SCATTERCHART">
      <li class="nav-header">${_('sorting')}</li>
    </ul>
    <div class="btn-group" data-toggle="buttons-radio" data-bind="visible: chartType() != '' && chartType() != window.HUE_CHARTS.TYPES.MAP && chartType() != window.HUE_CHARTS.TYPES.GRADIENTMAP && chartType() != window.HUE_CHARTS.TYPES.SCATTERCHART">
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
            <input class="all-meta-checked no-margin-top" type="checkbox" data-bind="enable: !result.isMetaFilterVisible() && result.filteredMeta().length > 0, event: { change: function(){ toggleAllResultColumns($element); result.clickFilteredMetaCheck() } }, checked: result.filteredMetaChecked" />
          </th>
          <th colspan="2" class="nav-header-like">
            <span class="meta-title pointer" data-bind="click: function() { result.isMetaFilterVisible(true); }, attr: { title: result.filteredColumnCount() }">${_('columns')}</span>
            (<span class="meta-title pointer" data-bind="click: function() { result.isMetaFilterVisible(true); }, text: result.filteredColumnCount()"></span>)
            <span class="inactive-action" href="javascript:void(0)" data-bind="click: function(){ result.isMetaFilterVisible(true); }, css: { 'blue' : result.isMetaFilterVisible }"><i class="pointer fa fa-search" title="${ _('Search') }"></i></span>
          </th>
        </tr>
        <tr data-bind="visible: result.isMetaFilterVisible">
          <td colspan="3">
            <div class="context-popover-inline-autocomplete" style="display: block;">
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
            </div>
          </td>
        </tr>
      </thead>
      <tbody class="unstyled filtered-meta" data-bind="foreach: result.filteredMeta">
        <tr data-bind="visible: name != ''">
          <td><input class="no-margin-top" type="checkbox" data-bind="event: { change: function() { $parent.toggleResultColumn($element, originalIndex);} }, checked: checked" /></td>
          <td><a class="pointer" data-bind="click: function(){ $parent.scrollToResultColumn($element); }, attr: { title: name + ' - ' + type}"><span data-bind="text: name"></span></a></td>
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
                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.PIECHART -->
                <div data-bind="attr:{'id': 'pieChart_'+id()}, pieChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]),
                      transformer: $root.ChartTransformers.pie, maxWidth: 350, parentSelector: '.chart-container' }, visible: chartType() == window.HUE_CHARTS.TYPES.PIECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.BARCHART -->
                <div data-bind="attr:{'id': 'barChart_'+id()}, barChart: {skipWindowResize: true, datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: hideStacked,
                      transformer: $root.ChartTransformers.multiSerie, stacked: false, showLegend: true, isPivot: typeof chartXPivot() !== 'undefined', type: chartTimelineType},  stacked: true, showLegend: true, visible: chartType() == window.HUE_CHARTS.TYPES.BARCHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.LINECHART -->
                <div data-bind="attr:{'id': 'lineChart_'+id()}, lineChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()},
                      transformer: $root.ChartTransformers.multiSerie, showControls: false, enableSelection: false }, visible: chartType() == window.HUE_CHARTS.TYPES.LINECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART -->
                <div data-bind="attr:{'id': 'timelineChart_'+id()}, timelineChart: {type: chartTimelineType, skipWindowResize: true, datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()}, fqs: ko.observableArray([]), hideSelection: true, enableSelection: false, hideStacked: hideStacked,
                      transformer: $root.ChartTransformers.timeline, stacked: false, showLegend: true}, visible: chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.MAP -->
                <div data-bind="attr:{'id': 'leafletMapChart_'+id()}, leafletMapChart: {datum: {counts: result.data, sorting: chartSorting(), snippet: $data, limit: chartLimit()},
                      transformer: $root.ChartTransformers.leafletMap, showControls: false, height: 380, visible: chartType() == window.HUE_CHARTS.TYPES.MAP, forceRedraw: true}" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP -->
                <div data-bind="attr:{'id': 'gradientMapChart_'+id()}, mapChart: {data: {counts: result.data, sorting: chartSorting(), snippet: $data, scope: chartScope(), limit: chartLimit()},
                      transformer: $root.ChartTransformers.map, isScale: true, showControls: false, height: 380, maxWidth: 750, parentSelector: '.chart-container', visible: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP}" class="chart"></div>
                <!-- /ko -->

                <!-- ko if: chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART -->
                <div data-bind="attr:{'id': 'scatterChart_'+id()}, scatterChart: {datum: {counts: result.data, snippet: $data, limit: chartLimit()},
                      transformer: $root.ChartTransformers.scatter, maxWidth: 350, y: chartYSingle(), x: chartX(), size: chartScatterSize(), group: chartScatterGroup() }, visible: chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART" class="chart"></div>
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
      <div class="ace-editor" data-bind="attr: { id: id }, aceEditor: {
        snippet: $data,
        updateOnInput: true
      }"></div>
    </div>
    <div class="span6">
      <div data-bind="html: renderMarkdown(), attr: {'id': 'liveMD' + id()}"></div>
    </div>
  </div>
  <!-- /ko -->
  <!-- ko if: $root.isPresentationMode() -->
  <div data-bind="html: renderMarkdown()"></div>
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
        'progress-starting': progress() == 0 && (status() == 'running' || status() == 'starting'),
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
    <a class="snippet-side-btn" data-bind="click: reexecute, visible: $root.editorMode() && result.statements_count() > 1, css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }" title="${ _('Restart from the first statement') }">
      <i class="fa fa-fw fa-repeat snippet-side-single"></i>
    </a>
    <div class="label label-info" data-bind="attr: {'title':'${ _ko('Showing results of the statement #')}' + (result.statement_id() + 1)}, visible: $root.editorMode() && result.statements_count() > 1">
      <div class="pull-left" data-bind="text: (result.statement_id() + 1)"></div><div class="pull-left">/</div><div class="pull-left" data-bind="text: result.statements_count()"></div>
    </div>
    <!-- ko if: !isCanceling() -->
    <a class="snippet-side-btn red" data-bind="click: cancel, visible: status() == 'running' || status() == 'starting'" title="${ _('Cancel operation') }">
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
      <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="attr: {'title': $root.editorMode() && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: function() { wasBatchExecuted(false); execute(); }, visible: status() != 'running' && status() != 'loading' && status() != 'starting', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }, style: {'padding-left': $parent.isBatchable() ? '2px' : '0' }">
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
        % if conf.ENABLE_GIST.get():
        <li>
          <a href="javascript:void(0)" data-bind="click: createGist, css: {'disabled': ! isReady() }" title="${ _('Share the query selection via a link') }">
            <i class="fa fa-fw fa-link"></i> ${_('Get shareable link')}
          </a>
        </li>
        % endif
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

    <!-- ko if: window.CUSTOM_DASHBOARD_URL -->
    <a class="snippet-side-btn" href="javascript: void(0)" data-bind="click: dashboardRedirect.bind($data)" title="${ _('Dashboard') }">
      <i class="hcha fa-fw hcha-bar-chart"></i>
    </a>
    <!-- /ko -->
    <!-- ko ifnot: window.CUSTOM_DASHBOARD_URL -->
    <div class="dropdown">
      <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="css: {'active': $data.showChart }, click: function() { $data.showChart(true); }" >
        <i class="hcha fa-fw hcha-bar-chart" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.BARCHART" title="${ _('Bars') }"></i>
        <i class="hcha fa-fw hcha-timeline-chart" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART" title="${ _('Time') }"></i>
        <i class="hcha fa-fw hcha-pie-chart" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.PIECHART" title="${ _('Pie') }"></i>
        <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART" title="${ _('Scatter') }"></i>
        <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.MAP" title="${ _('Marker Map') }"></i>
        <i class="hcha fa-fw hcha-map-chart" data-bind="visible: chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP" title="${ _('Gradient Map') }"></i>
      </a>
      <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'active': $data.showChart}">
        <i class="fa fa-caret-down"></i>
      </a>

      <ul class="dropdown-menu less-padding">
        <li>
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.BARCHART}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.BARCHART); }">
            <i class="hcha hcha-bar-chart"></i> ${_('Bars')}
          </a>
        </li>
        <li data-bind="visible: result.cleanedDateTimeMeta().length > 0">
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.TIMELINECHART); }">
            <i class="hcha hcha-timeline-chart"></i> ${_('Time')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.PIECHART}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.PIECHART); }">
            <i class="hcha hcha-pie-chart"></i> ${_('Pie')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.SCATTERCHART}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.SCATTERCHART); }">
            <i class="fa fa-fw fa-dot-circle-o chart-icon"></i> ${_('Scatter')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.MAP}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.MAP); }">
            <i class="fa fa-fw fa-map-marker chart-icon"></i> ${_('Marker Map')}
          </a>
        </li>
        <li>
          <a href="javascript:void(0)" data-bind="css: {'active': chartType() == window.HUE_CHARTS.TYPES.GRADIENTMAP}, click: function(){ $data.showChart(true); chartType(window.HUE_CHARTS.TYPES.GRADIENTMAP); }">
            <i class="hcha hcha-map-chart"></i> ${_('Gradient Map')}
          </a>
        </li>
      </ul>
    </div>
    <!-- /ko -->

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

    % if conf.ENABLE_DOWNLOAD.get():
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
    <!-- ko if: $root.authSessionMessage() -->
      <div class="row-fluid">
        <div class="alert-warning">
          <span data-bind="text: authSessionMessage"></span>
        </div>
      </div>
    <!-- /ko -->
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
  window.EDITOR_BINDABLE_ELEMENT = '#${ bindableElement }';

  window.EDITOR_SUFFIX = '${ suffix }';

  var HUE_PUB_SUB_EDITOR_ID = (window.location.pathname.indexOf('notebook') > -1) ? 'notebook' : 'editor';

  window.EDITOR_VIEW_MODEL_OPTIONS = $.extend(${ options_json | n,unicode,antixss }, {
    huePubSubId: HUE_PUB_SUB_EDITOR_ID,
    user: '${ user.username }',
    userId: ${ user.id },
    suffix: '${ suffix }',
    assistAvailable: true,
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
      presto: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/presto',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      elasticsearch: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/elasticsearch',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      druid: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/druid',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      bigquery: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/bigquery',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      phoenix: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/phoenix',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      ksql: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/ksql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      flink: {
        placeHolder: '${ _("Example: SELECT * FROM tablename, or press CTRL + space") }',
        aceMode: 'ace/mode/flink',
        snippetIcon: 'fa-database',
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

  window.EDITOR_ENABLE_QUERY_SCHEDULING = '${ ENABLE_QUERY_SCHEDULING.get() }' === 'True';

  window.EDITOR_ID = ${ editor_id or 'null' };

  window.NOTEBOOKS_JSON = ${ notebooks_json | n,unicode };

  window.OPTIMIZER_AUTO_UPLOAD_QUERIES = '${ OPTIMIZER.AUTO_UPLOAD_QUERIES.get() }' === 'True';

  window.OPTIMIZER_AUTO_UPLOAD_DDL = '${ OPTIMIZER.AUTO_UPLOAD_DDL.get() }' === 'True';

  window.OPTIMIZER_QUERY_HISTORY_UPLOAD_LIMIT = ${ OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() };
</script>

</%def>
