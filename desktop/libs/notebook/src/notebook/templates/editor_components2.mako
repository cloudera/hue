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
  <link rel="stylesheet" href="${ static('notebook/css/notebook2.css') }">
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
        var hiveQuery = QueryBuilder.buildHiveQuery();
        if (hiveQuery.status == "fail") {
          $("#invalidQueryBuilder${ suffix }").modal("show");
        } else {
          replaceAce(hiveQuery.query);
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
              <a data-bind="hueLink: '${ url('notebook:editor') }?type=' + editorType(), attr: { 'title': editorTitle() + '${ _(' Editor') }'}" style="cursor: pointer">
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
                <!-- ko case: $default --><span data-bind="text: editorTitle()"></span><!-- /ko -->
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
            <a href="javascript:void(0)" data-bind="click: function() { hueUtils.removeURLParameter('editor'); newNotebook($root.editorType(), null, selectedNotebook() ? $root.selectedNotebook().snippets()[0].currentQueryTab() : null); }, attr: { 'title': '${ _('New ') }' +  editorTitle() + '${ _(' Query') }' }">
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
            <a href="javascript:void(0)" class="share-link" data-bind="click: prepareShareModal,
              css: {'isShared': isShared()}">
              <i class="fa fa-fw fa-users"></i> ${ _('Share') }
            </a>
          </li>
          <!-- /ko -->
          <!-- /ko -->
          <li>
            <a href="javascript:void(0)" data-bind="click: showSessionPanel">
              <i class="fa fa-fw fa-cogs"></i> ${ _('Sessions') }
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
    <div class="vertical-full tab-pane row-fluid panel-container" data-bind="css: { active: selectedNotebook() === $data }, template: { name: 'notebook${ suffix }'}">
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
      <div class="row-fluid row-container sortable-snippets" data-bind="css: {'is-editing': $root.isEditing},
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
  </script>

  <script type="text/html" id="snippetIcon${ suffix }">
    <!-- ko if: viewSettings().snippetImage -->
    <img class="snippet-icon-image" data-bind="attr: { 'src': viewSettings().snippetImage }" alt="${ _('Snippet icon') }">
    <!-- /ko -->
    <!-- ko if: viewSettings().snippetIcon -->
    <i class="fa snippet-icon" data-bind="css: viewSettings().snippetIcon"></i>
    <!-- /ko -->
  </script>

  <script type="text/html" id="query-tabs${ suffix }">
    <div class="query-history-container" data-bind="onComplete: function(){ redrawFixedHeaders(200); }">
      <div data-bind="delayedOverflow: 'slow', css: resultsKlass" style="margin-top: 5px; position: relative;">
        <ul class="nav nav-tabs nav-tabs-editor">
          <li data-bind="click: function() { currentQueryTab('queryHistory'); }, css: { 'active': currentQueryTab() == 'queryHistory' }">
            <a class="inactive-action" style="display:inline-block" href="#queryHistory" data-toggle="tab">${_('Query History')}</a>
          </li>
          <li class="margin-right-20" data-bind="click: function(){ currentQueryTab('savedQueries'); }, css: { 'active': currentQueryTab() == 'savedQueries' }">
            <a class="inactive-action" style="display:inline-block" href="#savedQueries" data-toggle="tab">${_('Saved Queries')}</a>
          </li>
          % if ENABLE_QUERY_BUILDER.get():
            <!-- ko if: isSqlDialect -->
            <li style="margin-right: 25px;" data-bind="click: function(){ currentQueryTab('queryBuilderTab'); }, css: {'active': currentQueryTab() == 'queryBuilderTab'}"><a class="inactive-action" href="#queryBuilderTab" data-toggle="tab">${_('Query Builder')}</a></li>
            <!-- /ko -->
          % endif
          <li data-bind="click: function() { currentQueryTab('queryResults'); }, css: {'active': currentQueryTab() == 'queryResults'}">
            <a class="inactive-action" style="display:inline-block" href="#queryResults" data-toggle="tab">${_('Results')}
##               <!-- ko if: result.rows() != null  -->
##               (<span data-bind="text: result.rows().toLocaleString() + (dialect() == 'impala' && result.rows() == 1024 ? '+' : '')" title="${ _('Number of rows') }"></span>)
##               <!-- /ko -->
            </a>
          </li>
          <!-- ko if: explanation -->
          <li data-bind="click: function() { currentQueryTab('queryExplain'); }, css: {'active': currentQueryTab() == 'queryExplain'}"><a class="inactive-action" href="#queryExplain" data-toggle="tab">${_('Explain')}</a></li>
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

          <!-- ko if: HAS_WORKLOAD_ANALYTICS && dialect() === 'impala' -->
          <li data-bind="visible: showExecutionAnalysis, click: function(){ currentQueryTab('executionAnalysis'); }, css: {'active': currentQueryTab() == 'executionAnalysis'}"><a class="inactive-action" href="#executionAnalysis" data-toggle="tab" data-bind="click: function(){ $('a[href=\'#executionAnalysis\']').tab('show'); }, event: {'shown': fetchExecutionAnalysis }"><span>${_('Execution Analysis')} </span><span></span></a></li>
          <!-- /ko -->
        </ul>

        <div class="tab-content" style="border: none; overflow-x: hidden; min-height: 250px;">
          <div class="tab-pane" id="queryHistory" style="min-height: 80px;" data-bind="css: { 'active': currentQueryTab() === 'queryHistory' }">
            <!-- ko component: {
              name: 'query-history',
              params: {
                currentNotebook: parentNotebook,
                openFunction: parentVm.openNotebook.bind(parentVm),
                dialect: dialect
              }
            } --><!-- /ko -->
          </div>

          <div class="tab-pane" id="savedQueries" data-bind="css: { 'active': currentQueryTab() === 'savedQueries' }" style="overflow: hidden">
            <!-- ko component: {
              name: 'saved-queries',
              params: {
                currentNotebook: parentNotebook,
                openFunction: parentVm.openNotebook.bind(parentVm),
                dialect: dialect,
                currentTab: currentQueryTab
              }
            } --><!-- /ko -->
          </div>

          % if ENABLE_QUERY_BUILDER.get():
            <div class="tab-pane margin-top-10" id="queryBuilderTab" data-bind="css: { 'active': currentQueryTab() === 'queryBuilderTab' }">
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
            <!-- ko if: ['text', 'jar', 'py', 'markdown'].indexOf(dialect()) === -1 -->
              <!-- ko component: { name: 'snippet-results', params: {
                activeExecutable: activeExecutable,
                editorMode: parentVm.editorMode,
                id: id,
                isPresentationMode: parentNotebook.isPresentationMode,
                isResultFullScreenMode: parentVm.isResultFullScreenMode,
                resultsKlass: resultsKlass
              }} --><!-- /ko -->
            <!-- /ko -->
          </div>

          <!-- ko if: explanation -->
          <div class="tab-pane" id="queryExplain" data-bind="css: {'active': currentQueryTab() == 'queryExplain'}">
            <pre class="no-margin-bottom" data-bind="text: explanation"></pre>
          </div>
          <!-- /ko -->

          <!-- ko if: HAS_WORKLOAD_ANALYTICS && dialect() === 'impala' -->
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
##       <span class="execution-timer" data-bind="visible: dialect() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>

      <!-- ko template: { name: 'snippet-header-database-selection' } --><!-- /ko -->

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
##       <span class="execution-timer" data-bind="visible: dialect() != 'text' && status() != 'ready' && status() != 'loading', text: result.executionTime().toHHMMSS()" title="${ _('Execution time') }"></span>

      <!-- ko template: { name: 'snippet-header-database-selection' } --><!-- /ko -->

      <a class="inactive-action margin-left-10 pointer" title="${ _('Show editor help') }" data-toggle="modal" data-target="#helpModal${ suffix }"><i class="fa fa-question"></i></a>
    </div>
  </script>

  <script type="text/html" id="snippet-header-database-selection">
    <!-- ko if: isSqlDialect() || dialect() === 'spark2' -->
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

  <script type="text/html" id="snippet${ suffix }">
    <div data-bind="visibleOnHover: { override: inFocus() || settingsVisible() || dbSelectionVisible() || $root.editorMode() || saveResultsModalVisible(), selector: '.hover-actions' }">
      <div class="snippet-container row-fluid" data-bind="visibleOnHover: { override: $root.editorMode() || inFocus() || saveResultsModalVisible(), selector: '.snippet-actions' }">
        <div class="snippet card card-widget snippet-v2" data-bind="css: {'notebook-snippet' : ! $root.editorMode(), 'editor-mode': $root.editorMode(), 'active-editor': inFocus, 'snippet-text' : dialect() === 'text'}, attr: {'id': 'snippet_' + id()}, clickForAceFocus: ace.bind($data)">
          <div style="position: relative;">
            <div class="snippet-row" style="position: relative;">
              <div class="snippet-body" data-bind="clickForAceFocus: ace.bind($data), visible: ! $root.isResultFullScreenMode()">
                <h5 class="card-heading-print" data-bind="text: name, css: {'visible': name() != ''}"></h5>

                <h2 style="margin-left:5px;padding: 3px 0" class="card-heading simple" data-bind="dblclick: function(){ if (!$root.editorMode() && !$root.isPresentationMode()) { $parent.newSnippetAbove(id()) } }, clickForAceFocus: ace.bind($data)">
                  <!-- ko template: { if: $root.editorMode(), name: 'editor-snippet-header${ suffix }' } --><!-- /ko -->
                  <!-- ko template: { if: ! $root.editorMode(), name: 'notebook-snippet-header${ suffix }' } --><!-- /ko -->
                </h2>
                <!-- ko template: { if: ['text', 'jar', 'java', 'spark2', 'distcp', 'shell', 'mapreduce', 'py', 'markdown'].indexOf(dialect()) == -1, name: 'code-editor-snippet-body${ suffix }' } --><!-- /ko -->
                <!-- ko template: { if: dialect() == 'text', name: 'text-snippet-body${ suffix }' } --><!-- /ko -->
                <!-- ko template: { if: dialect() == 'markdown', name: 'markdown-snippet-body${ suffix }' } --><!-- /ko -->
                <!-- ko template: { if: ['java', 'distcp', 'shell', 'mapreduce', 'jar', 'py', 'spark2'].indexOf(dialect()) != -1, name: 'executable-snippet-body${ suffix }' } --><!-- /ko -->
              </div>
              <div style="position: absolute; top:25px; width: 100%" data-bind="style: { 'z-index': 400 - $index() }">
                <!-- ko template: 'snippet-settings${ suffix }' --><!-- /ko -->
              </div>
            </div>
            <!-- ko template: { if: ['text', 'markdown'].indexOf(dialect()) == -1, name: 'snippet-execution-status${ suffix }' } --><!-- /ko -->
            <!-- ko template: { if: $root.editorMode() && ! $root.isResultFullScreenMode() && ['jar', 'java', 'spark2', 'distcp', 'shell', 'mapreduce', 'py'].indexOf(dialect()) == -1, name: 'snippet-code-resizer${ suffix }' } --><!-- /ko -->
            <div class="snippet-footer-actions">
              <!-- ko template: { if: ! $root.editorMode() && ! $root.isPresentationMode() && ! $root.isResultFullScreenMode(), name: 'notebook-snippet-type-controls${ suffix }' } --><!-- /ko -->
              <!-- ko template: { if: ['text', 'markdown'].indexOf(dialect()) == -1 && ! $root.isResultFullScreenMode(), name: 'snippet-execution-controls${ suffix }' } --><!-- /ko -->
            </div>
            <!-- ko if: !$root.isResultFullScreenMode() -->
            <!-- ko component: { name: 'executable-logs', params: {
              activeExecutable: activeExecutable,
              showLogs: showLogs,
              resultsKlass: resultsKlass,
              isPresentationMode: parentNotebook.isPresentationMode,
              isHidingCode: parentNotebook.isHidingCode
            }} --><!-- /ko -->
            <!-- /ko -->
            <!-- ko if: $root.editorMode() -->
            <!-- ko template: 'query-tabs${ suffix }' --><!-- /ko -->
            <!-- /ko -->
            <!-- ko if: !$root.editorMode() && ['text', 'jar', 'java', 'distcp', 'shell', 'mapreduce', 'py', 'markdown'].indexOf(dialect()) === -1 -->
              <!-- ko component: { name: 'snippet-results', params: {
                activeExecutable: activeExecutable,
                editorMode: parentVm.editorMode,
                id: id,
                isPresentationMode: parentNotebook.isPresentationMode,
                isResultFullScreenMode: parentVm.isResultFullScreenMode,
                resultsKlass: resultsKlass
              }} --><!-- /ko -->
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
          % if ENABLE_EXTERNAL_STATEMENT.get():
            <!-- ko if: isSqlDialect -->
            <div class="config-property">
              <label class="config-label">${ _('Type') }</label>
              <div class="config-controls">
                <div style="padding-top: 4px; display: inline-block;" data-bind="component: { name: 'hue-drop-down', params: { value: statementType, entries: statementTypes, linkTitle: '${ _ko('Statement type') }' } }"></div>
              </div>
            </div>
            <!-- /ko -->
          % endif
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
    <!-- ko if: HAS_OPTIMIZER && (dialect() == 'impala' || dialect() == 'hive') && ! $root.isPresentationMode() && ! $root.isResultFullScreenMode() -->
    <div class="optimizer-container" data-bind="css: { 'active': showOptimizer }">
      <!-- ko if: hasSuggestion() -->
      <!-- ko with: suggestion() -->
      <!-- ko if: parseError -->
      <!-- ko if: $parent.compatibilityTargetPlatform().value === $parent.dialect() && $parent.compatibilitySourcePlatform().value === $parent.dialect() -->
      <div class="optimizer-icon error" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
        <i class="fa fa-exclamation"></i>
      </div>
      <!-- ko if: $parent.showOptimizer -->
      <span class="optimizer-explanation alert-error alert-neutral">${ _('The query has a parse error.') }</span>
      <!-- /ko -->
      <!-- /ko -->
      ## Oracle, MySQL compatibility... as they return a parseError and not encounteredString.
          <!-- ko if: $parent.compatibilityTargetPlatform().value !== $parent.dialect() || $parent.dialect() !== $parent.compatibilitySourcePlatform().value -->
      <div class="optimizer-icon warning" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
        <i class="fa fa-exclamation"></i>
      </div>
      <!-- ko if: $parent.showOptimizer -->
      <span class="optimizer-explanation alert-warning alert-neutral">${ _('This ') } <span data-bind="text: $parent.compatibilitySourcePlatform().name"></span> ${ _(' query is not compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.</span>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: !parseError() && ($parent.compatibilityTargetPlatform().value !== $parent.dialect() || $parent.compatibilitySourcePlatform().value !== $parent.dialect()) -->
      <!-- ko if: queryError.encounteredString().length == 0 -->
      <div class="optimizer-icon success" data-bind="click: function(){ $parent.showOptimizer(! $parent.showOptimizer()) }, attr: { 'title': $parent.showOptimizer() ? '${ _ko('Close Validator') }' : '${ _ko('Open Validator') }'}">
        <i class="fa fa-check"></i>
      </div>
      <!-- ko if: $parent.showOptimizer -->
      <span class="optimizer-explanation alert-success alert-neutral">
              ${ _('The ') } <div data-bind="component: { name: 'hue-drop-down', params: { value: $parent.compatibilitySourcePlatform, entries: $parent.compatibilitySourcePlatforms, labelAttribute: 'name' } }" style="display: inline-block"></div>
        <!-- ko if: $parent.compatibilitySourcePlatform().value === $parent.dialect() -->
        ${ _(' query is compatible with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span>.
                <a href="javascript:void(0)" data-bind="click: function() { $parent.dialect($parent.compatibilityTargetPlatform().value); }">${ _('Execute it with ') } <span data-bind="text: $parent.compatibilityTargetPlatform().name"></span></a>.
        <!-- /ko -->
        <!-- ko if: $parent.compatibilitySourcePlatform().value !== $parent.dialect() -->
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

      <div class="editor span12" data-bind="css: {'single-snippet-editor ace-container-resizable' : $root.editorMode() }, clickForAceFocus: ace.bind($data), visible: ! $root.isResultFullScreenMode() && ! ($root.isPresentationMode() && $root.isHidingCode())">
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
            <select placeholder="${ _('Search your documents...') }" data-bind="documentChooser: { loading: associatedDocumentLoading, value: associatedDocumentUuid, document: associatedDocument, type: dialect }"></select>
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

        <div class="ace-editor" data-bind="
            visible: statementType() === 'text' || statementType() !== 'text' && externalStatementLoaded(),
            css: {
              'single-snippet-editor ace-editor-resizable' : $root.editorMode(),
              'active-editor': inFocus
            },
            attr: {
              id: id
            },
            delayedOverflow: 'slow',
            aceEditor: {
              snippet: $data,
              contextTooltip: '${ _ko("Right-click for details") }',
              expandStar: '${ _ko("Right-click to expand with columns") }',
##               highlightedRange: result.statement_range,
              readOnly: $root.isPresentationMode(),
              aceOptions: {
                showLineNumbers: $root.editorMode(),
                showGutter: $root.editorMode(),
                maxLines: $root.editorMode() ? null : 25,
                minLines: $root.editorMode() ? null : 3
              }
            },
            style: {
              'opacity': statementType() !== 'text' || $root.isPresentationMode() ? '0.75' : '1',
              'min-height': $root.editorMode() ? '0' : '48px',
              'top': $root.editorMode() && statementType() !== 'text' ? '60px' : '0'
            }
          "></div>
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
##         <li>
##           <a class="pointer" data-bind="click: function() { $root.selectedNotebook().clearResults() }">
##             <i class="fa fa-fw fa-eraser"></i> ${ _('Clear results') }
##           </a>
##         </li>
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

  <script type="text/html" id="text-snippet-body${ suffix }">
    <div data-bind="attr: {'id': 'editor_' + id()}, html: statement_raw, value: statement_raw, medium: {}" data-placeHolder="${ _('Type your text here, select some text to format it') }" class="text-snippet"></div>
  </script>

  <script type="text/html" id="markdown-snippet-body${ suffix }">
    <!-- ko ifnot: $root.isPresentationMode() -->
    <div class="row-fluid">
      <div class="span6" data-bind="clickForAceFocus: ace.bind($data)">
        <div class="ace-editor" data-bind="attr: { id: id }, aceEditor: {
        snippet: $data,
        updateOnInput: true
      }"></div>
      </div>
      <div class="span6">
        <div data-bind="html: renderMarkdown, attr: {'id': 'liveMD' + id()}"></div>
      </div>
    </div>
    <!-- /ko -->
    <!-- ko if: $root.isPresentationMode() -->
    <div data-bind="html: renderMarkdown"></div>
    <!-- /ko -->
  </script>


  <script type="text/html" id="executable-snippet-body${ suffix }">
    <div style="padding:10px;">
      <form class="form-horizontal">
        <!-- ko if: dialect() == 'distcp' -->
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
        <!-- ko if: dialect() == 'shell' -->
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
        <!-- ko if: dialect() == 'mapreduce' -->
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
        <!-- ko if: dialect() === 'jar' || dialect() === 'java' -->
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
        <!-- ko if: dialect() === 'py'-->
        <div class="control-group">
          <label class="control-label">${_('Path')}</label>
          <div class="controls">
            <input type="text" class="input-xxlarge" data-bind="value: properties().py_file, valueUpdate: 'afterkeydown', filechooser: properties().py_file, filechooserOptions: { linkMarkup: true, skipInitialPathIfEmpty: true, openOnFocus: true, selectFolder: false }" placeholder="${ _('Path to python file, e.g. script.py') }"/>
          </div>
        </div>
        <!-- /ko -->
        <!-- ko if: dialect() === 'spark2' -->
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
    <div class="snippet-execution-status" data-bind="clickForAceFocus: ace.bind($data)">
      <a class="inactive-action pull-left snippet-logs-btn" href="javascript:void(0)" data-bind="
          visible: status() === 'running' && errors().length == 0,
          click: function() {
            huePubSub.publish('result.grid.hide.fixed.headers');
            $data.showLogs(!$data.showLogs());
          },
          css: {'blue': $data.showLogs}
        " title="${ _('Toggle Logs') }"><i class="fa fa-fw" data-bind="css: { 'fa-caret-right': !$data.showLogs(), 'fa-caret-down': $data.showLogs() }"></i></a>
      <div class="snippet-progress-container" data-bind="visible: status() != 'canceled' && status() != 'with-optimizer-report'">
        <!-- ko component: { name: 'executable-progress-bar', params: { activeExecutable: activeExecutable } } --><!-- /ko -->
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
    <div class="snippet-code-resizer" data-bind="
        aceResizer : {
          snippet: $data,
          target: '.ace-container-resizable',
          onStart: function () { huePubSub.publish('result.grid.hide.fixed.headers') },
          onStop: function () { huePubSub.publish('result.grid.redraw.fixed.headers') }
        }">
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
        <li><a class="pointer" data-bind="click: function(){ $parent.changeDialect($data.type()); }, text: name"></a></li>
      </ul>
    </div>
  </script>

  <script type ="text/html" id="snippet-execution-controls${ suffix }">
    <div class="snippet-actions clearfix">
      <div class="pull-left" data-bind="component: { name: 'executable-actions', params: { activeExecutable: activeExecutable, beforeExecute: beforeExecute } }"></div>
      <!-- ko if: isSqlDialect() && !$root.isPresentationMode() -->
      <div class="pull-right" data-bind="component: { name: 'snippet-editor-actions', params: { snippet: $data } }"></div>
      <!-- /ko -->
      <div class="pull-right">
        <!-- ko if: status() === 'loading' -->
        <i class="fa fa-fw fa-spinner fa-spin"></i> ${ _('Creating session') }
        <!-- /ko -->
##         <!-- ko if: status() !== 'loading' && $root.editorMode() && result.statements_count() > 1 -->
##         ${ _('Statement ')} <span data-bind="text: (result.statement_id() + 1) + '/' + result.statements_count()"></span>
##         <div style="display: inline-block"
##              class="label label-info"
##              data-bind="attr: {
##              'title':'${ _ko('Showing results of the statement #')}' + (result.statement_id() + 1)}">
##           <div class="pull-left" data-bind="text: (result.statement_id() + 1)"></div><div class="pull-left">/</div><div class="pull-left" data-bind="text: result.statements_count()"></div>
##         </div>
##         <!-- /ko -->
      </div>

##       TODO: Move to snippet execution-actions
##       <a class="snippet-side-btn" data-bind="click: reexecute, visible: $root.editorMode() && result.statements_count() > 1, css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }" title="${ _('Restart from the first statement') }">
##         <i class="fa fa-fw fa-repeat snippet-side-single"></i>
##       </a>
##       <!-- ko if: !isCanceling() -->
##       <a class="snippet-side-btn red" data-bind="click: cancel, visible: status() == 'running' || status() == 'starting'" title="${ _('Cancel operation') }">
##         <i class="fa fa-fw fa-stop snippet-side-single"></i>
##       </a>
##       <!-- /ko -->
##       <!-- ko if: isCanceling() -->
##       <a class="snippet-side-btn" style="cursor: default;" title="${ _('Canceling operation...') }">
##         <i class="fa fa-fw fa-spinner snippet-side-single fa-spin"></i>
##       </a>
##       <!-- /ko -->
##       <div style="display: inline-block" class="inactive-action dropdown hover-actions pointer" data-bind="css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }">
##         <!-- ko if: isBatchable() && wasBatchExecuted() -->
##         <a class="snippet-side-btn" style="padding-right:0; padding-left: 2px" href="javascript: void(0)" title="${ _('Submit all the queries as a background batch job.') }" data-bind="click: function() { wasBatchExecuted(true); execute(); }, visible: status() != 'running' && status() != 'loading', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }">
##           <i class="fa fa-fw fa-send"></i>
##         </a>
##         <!-- /ko -->
##         <!-- ko if: ! isBatchable() || ! wasBatchExecuted() -->
##         <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="attr: {'title': $root.editorMode() && result.statements_count() > 1 ? '${ _ko('Execute next statement')}' : '${ _ko('Execute or CTRL + ENTER') }'}, click: function() { wasBatchExecuted(false); execute(); }, visible: status() != 'running' && status() != 'loading' && status() != 'starting', css: {'blue': $parent.history().length == 0 || $root.editorMode(), 'disabled': ! isReady() }, style: {'padding-left': $parent.isBatchable() ? '2px' : '0' }">
##           <i class="fa fa-fw fa-play" data-bind="css: { 'snippet-side-single' : ! $parent.isBatchable() }"></i>
##         </a>
##         <!-- /ko -->
##         % if ENABLE_BATCH_EXECUTE.get():
##           <!-- ko if: isBatchable() && status() != 'running' && status() != 'loading' && ! $root.isPresentationMode() -->
##           <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: {'disabled': ! isReady(), 'blue': currentQueryTab() == 'queryExplain' }">
##             <i class="fa fa-caret-down"></i>
##           </a>
##           <ul class="dropdown-menu less-padding">
##             <li>
##               <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(false); $('.dropdown-toggle').dropdown('toggle'); execute(); }, style: { color: ! isReady() || status() === 'running' || status() === 'loading' ? '#999' : ''}, css: {'disabled': ! isReady() || status() === 'running' || status() === 'loading' }" title="${ _('Execute interactively the current statement') }">
##                 <i class="fa fa-fw fa-play"></i> ${_('Execute')}
##               </a>
##             </li>
##             <li>
##               <a href="javascript:void(0)" data-bind="click: function() { wasBatchExecuted(true); $('.dropdown-toggle').dropdown('toggle'); execute(); }, css: {'disabled': ! isReady() }" title="${ _('Submit all the queries as a background batch job.') }">
##                 <i class="fa fa-fw fa-send"></i> ${_('Batch')}
##               </a>
##             </li>
##           </ul>
##           <!-- /ko -->
##         % endif
##       </div>
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

    if (window.WEB_SOCKETS_ENABLED) {
      const prefix = location.protocol === 'https:' ? 'wss://' : 'ws://';
      var editorWs = new WebSocket(prefix + window.location.host + '/ws/editor/results/' + 'userA' + '/');

      editorWs.onopen = function(e) {
        console.info('Notification socket open.');
      };

      editorWs.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data['type'] == 'channel_name') {
          window.WS_CHANNEL = data['data'];
        } else if (data['type'] == 'query_result') {
          huePubSub.publish('editor.ws.query.fetch_result', data['data']);
        }
        console.log(data);
      };

      editorWs.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
      };
    }

    window.EDITOR_ENABLE_QUERY_SCHEDULING = '${ ENABLE_QUERY_SCHEDULING.get() }' === 'True';

    window.EDITOR_ID = ${ editor_id or 'null' };

    window.NOTEBOOKS_JSON = ${ notebooks_json | n,unicode };

    window.OPTIMIZER_AUTO_UPLOAD_QUERIES = '${ OPTIMIZER.AUTO_UPLOAD_QUERIES.get() }' === 'True';

    window.OPTIMIZER_AUTO_UPLOAD_DDL = '${ OPTIMIZER.AUTO_UPLOAD_DDL.get() }' === 'True';

    window.OPTIMIZER_QUERY_HISTORY_UPLOAD_LIMIT = ${ OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT.get() };
  </script>

</%def>
