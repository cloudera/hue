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
  from desktop.views import _ko
  from desktop.lib.i18n import smart_unicode
  from desktop.views import login_modal

  from dashboard.conf import IS_ENABLED as IS_DASHBOARD_ENABLED
  from metadata.conf import has_optimizer, OPTIMIZER
  from notebook.conf import SHOW_NOTEBOOKS
%>

<%namespace name="koComponents" file="/ko_components.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="hueIcons" file="/hue_icons.mako" />
<%namespace name="commonHeaderFooterComponents" file="/common_header_footer_components.mako" />

<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }"/>
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">

  ##   TODO: Get rid of hue3.css
  <link href="${ static('desktop/css/hue3.css') }" rel="stylesheet">

  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/jquery-ui.css') }" rel="stylesheet">

  ${ commonHeaderFooterComponents.header_i18n_redirection(user, is_s3_enabled, apps) }

  <script type="text/javascript">
    var IS_HUE_4 = true;
  </script>

</head>

<body>

% if is_demo:
  <ul class="side-labels unstyled">
    <li class="feedback"><a href="javascript:showClassicWidget()"><i class="fa fa-envelope-o"></i> ${_('Feedback')}</a></li>
  </ul>

  <!-- UserVoice JavaScript SDK -->
  <script>(function(){var uv=document.createElement('script');uv.type='text/javascript';uv.async=true;uv.src='//widget.uservoice.com/8YpsDfIl1Y2sNdONoLXhrg.js';var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(uv,s)})()</script>
  <script>
  UserVoice = window.UserVoice || [];
  function showClassicWidget() {
    UserVoice.push(['showLightbox', 'classic_widget', {
      mode: 'feedback',
      primary_color: '#338cb8',
      link_color: '#338cb8',
      forum_id: 247008
    }]);
  }
  </script>
% endif

<div id="jHueNotify" class="alert hide">
    <button class="close">&times;</button>
    <div class="message"></div>
</div>


${ hueIcons.symbols() }

<div class="main-page">
  <nav class="navbar">
    <div class="navbar-inner top-nav">
      <div class="top-nav-left">
        <a class="hamburger hamburger-hue pull-left" type="button" data-bind="toggle: leftNavVisible, css: { 'is-active': leftNavVisible }">
          <span class="hamburger-box"><span class="hamburger-inner"></span></span>
        </a>

        <a class="brand" data-bind="click: function () { onePageViewModel.currentApp('home') }" href="javascript: void(0);" title="${_('Homepage')}">
          <svg style="height: 24px; width: 120px;"><use xlink:href="#hue-logo"></use></svg>
        </a>

        <div class="compose-action btn-group">
          <button class="btn" data-bind="click: function(){ onePageViewModel.changeEditorType('hive'); onePageViewModel.currentApp('editor') }" title="${ _('Hive editor') }">${ _('Compose') }</button>
          <button class="btn dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
          </button>

          <ul class="dropdown-menu">
            % if 'beeswax' in apps and 'impala' in apps:
              <li class="dropdown-submenu">
                <a title="${_('Query editor')}" data-rel="navigator-tooltip" href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.changeEditorType('hive'); onePageViewModel.currentApp('editor') }"><i class="fa fa-fw fa-edit inline-block"></i> ${ _('Editor') }</a>
                <ul class="dropdown-menu">
                  % if 'impala' in apps:
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.changeEditorType('impala'); onePageViewModel.currentApp('editor') }"><img src="${ static(apps['impala'].icon_path) }" class="app-icon" alt="${ _('Impala icon') }"/> ${_('Impala Query')}</a></li>
                  % endif
                  % if 'beeswax' in apps:
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.changeEditorType('hive'); onePageViewModel.currentApp('editor') }"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon" alt="${ _('Hive icon') }"/> ${_('Hive Query')}</a></li>
                  % endif
                  % if SHOW_NOTEBOOKS.get():
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.currentApp('notebook') }"><i class="fa fa-fw fa-file-text-o inline-block"></i> ${ _('Notebook') }</a></li>
                  % endif
                  % if interpreters:
                  <li class="divider"></li>
                  <li class="dropdown-submenu">
                    <a title="${_('More...')}" data-rel="navigator-tooltip" href="#"><span class="dropdown-no-icon">${ _('More') }</span></a>
                    <ul class="dropdown-menu">
                      % for interpreter in interpreters:
                        % if interpreter['name'] != 'Hive' and interpreter['name'] != 'Impala':
                        <li><a  href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.changeEditorType('${ interpreter['type'] }'); onePageViewModel.currentApp('editor') }"><span class="dropdown-no-icon">${ interpreter['name'] }</span></a></li>
                        % endif
                      % endfor
                      % if user.is_superuser:
                        <li class="divider"></li>
                        <li><a href="gethue.com" class="dropdown-no-icon">${ _('Add more...') }</a></li>
                      % endif
                    </ul>
                  </li>
                  % endif
                </ul>
              </li>
            % endif
            % if IS_DASHBOARD_ENABLED.get():
              <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.currentApp('dashboard') }"><i class="fa fa-fw fa-area-chart"></i> ${ _('Dashboard') }</a></li>
            % endif
            % if 'oozie' in apps:
            % if not user.has_hue_permission(action="disable_editor_access", app="oozie") or user.is_superuser:
              <li class="dropdown-submenu">
                <a title="${_('Schedule with Oozie')}" data-rel="navigator-tooltip" href="#"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon"  alt="${ _('Oozie editor icon') }"/> ${ _('Workflow') }</a>
                <ul class="dropdown-menu">
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.currentApp('oozie_workflow') }"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflow')}</a></li>
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.currentApp('oozie_coordinator') }"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }" /> ${_('Schedule')}</a></li>
                  <li><a href="javascript: void(0)" data-bind="click: function(){ onePageViewModel.currentApp('oozie_bundle') }"/><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }" /> ${_('Bundle')}</a></li>
                </ul>
              </li>
            % endif
            % endif
          </ul>
        </div>
      </div>

      <div class="top-nav-middle">
        <div class="search-container">
          <input placeholder="${ _('Search all data and saved documents...') }" type="text"
            data-bind="autocomplete: {
                source: searchAutocompleteSource,
                itemTemplate: 'nav-search-autocomp-item',
                noMatchTemplate: 'nav-search-autocomp-no-match',
                classPrefix: 'nav-',
                showOnFocus: true,
                onEnter: performSearch,
                reopenPattern: /.*:$/
              },
              hasFocus: searchHasFocus,
              clearable: { value: searchInput, onClear: function () { searchActive(false); huePubSub.publish('autocomplete.close'); } },
              textInput: searchInput,
              valueUpdate: 'afterkeydown'">
          <a class="inactive-action" data-bind="click: performSearch"><i class="fa fa-search" data-bind="css: { 'blue': searchHasFocus() || searchActive() }"></i></a>
        </div>
      </div>

      <div class="top-nav-right">
        % if user.is_authenticated() and section != 'login':
        <div class="compose-action btn-group pull-right">
          <%
            view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or user.is_superuser
          %>
          <button class="btn"
          % if view_profile:
            ### <a href="${ url('useradmin.views.edit_user', username=user.username) }"
            data-bind="click: function(){ onePageViewModel.currentApp('jobbrowser') }" title="${ _('View Profile') if is_ldap_setup else _('Edit Profile') }"
          % endif
          >
          ${ user.username }
          </button>
          % if user.is_superuser:
            <button class="btn dropdown-toggle" data-toggle="dropdown">
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" >
              <li><a href="${ url('useradmin.views.edit_user', username=user.username) }"><i class="fa fa-key"></i> ${_('Profile')}</a></li>
              % if user.is_superuser:
              <li data-bind="click: function () { onePageViewModel.currentApp('useradmin_users') }"><a href="javascript: void(0);"><i class="fa fa-group"></i> ${_('Manage Users')}</a></li>
              % endif
              <li><a href="http://gethue.com"><span class="dropdown-no-icon">${_('Help')}</span></a></li>
              % if user.is_superuser:
              <li><a href="/about"><span class="dropdown-no-icon">${_('About Hue')}</span></a></li>
              % endif
              <li class="divider"></li>
              <li><a title="${_('Sign out')}" href="/accounts/logout/"><i class="fa fa-sign-out"></i> ${ _('Sign out') }</a></li>
            </ul>
          % endif
        </div>

        <!-- ko component: 'hue-history-panel' --><!-- /ko -->
        % if 'jobbrowser' in apps:
        <!-- ko component: { name: 'hue-job-browser-panel', params: { onePageViewModel: onePageViewModel }} --><!-- /ko -->
        % endif

        % endif
      </div>
    </div>
  </nav>

  <div class="content-wrapper">
    <div class="left-nav" data-bind="css: { 'left-nav-visible': leftNavVisible }, niceScroll">
      <ul class="left-nav-menu">
        <li class="header" style="padding-left: 4px; border-bottom: 1px solid #DDD; padding-bottom: 3px;">${ _('Analyse') }</li>
        <li data-bind="click: function () { onePageViewModel.currentApp('home') }"><a href="javascript: void(0);">Home</a></li>
        % if interpreters:
        <li data-bind="click: function () { onePageViewModel.changeEditorType('hive'); onePageViewModel.currentApp('editor') }"><a href="javascript: void(0);">Editor</a></li>
        % endif
        % if IS_DASHBOARD_ENABLED.get():
        <li data-bind="click: function () { onePageViewModel.currentApp('dashboard') }"><a href="javascript: void(0);">Dashboard</a></li>
        % endif
        % if SHOW_NOTEBOOKS.get():
        <li data-bind="click: function () { onePageViewModel.currentApp('notebook') }"><a href="javascript: void(0);">Notebook</a></li>
        % endif
        % if 'oozie' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('oozie_workflow') }"><a href="javascript: void(0);">Workflows</a></li>
        % endif
        <li class="header">&nbsp;</li>
        <li class="header" style="padding-left: 4px; border-bottom: 1px solid #DDD; padding-bottom: 3px;">${ _('Browse') }</li>
        % if 'filebrowser' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('filebrowser') }"><a href="javascript: void(0);">Files</a></li>
        % endif
        % if is_s3_enabled:
        <li data-bind="click: function () { onePageViewModel.currentApp('filebrowser_s3') }"><a href="javascript: void(0);">S3</a></li>
        % endif
        % if 'metastore' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('metastore') }"><a href="javascript: void(0);">Tables</a></li>
        % endif
        % if 'search' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('indexes') }"><a href="javascript: void(0);">Indexes</a></li>
        % endif
        % if 'jobbrowser' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('jobbrowser') }"><a href="javascript: void(0);">Jobs</a></li>
        % endif
        % if 'hbase' in apps:
        <li data-bind="click: function () { onePageViewModel.currentApp('hbase') }"><a href="javascript: void(0);">HBase</a></li>
        % endif
        % if 'security' in apps:
          <li data-bind="click: function () { onePageViewModel.currentApp('security_hive') }"><a href="javascript: void(0);">Security</a></li>
        % endif
        % if 'sqoop' in apps:
        <li><a href="/${apps['sqoop'].display_name}">${_('Sqoop')}</a></li>
        % endif
        % if other_apps:
        <li class="header">&nbsp;</li>
        <li class="header" style="padding-left: 4px; border-bottom: 1px solid #DDD; padding-bottom: 3px;">${ _('Apps') }</li>
          % for other in other_apps:
            <li><a href="/${ other.display_name }">${ other.nice_name }</a></li>
          % endfor
        </li>
        % endif
      </ul>
      <div class="left-nav-drop">
        <div data-bind="dropzone: {
            clickable: false,
            url: '/filebrowser/upload/file?dest=' + DropzoneGlobals.homeDir,
            params: { dest: DropzoneGlobals.homeDir },
            paramName: 'hdfs_file',
            onError: onePageViewModel.dropzoneError,
            onComplete: onePageViewModel.dropzoneComplete },
            click: function(){ onePageViewModel.currentApp('importer') }" class="pointer" title="${ _('Import data wizard') }">
          <div class="dz-message" data-dz-message><i class="fa fa-fw fa-cloud-upload"></i> ${ _('Drop files here') }</div>
        </div>
      </div>
    </div>

    <div class="left-panel" data-bind="css: { 'side-panel-closed': !leftAssistVisible() }, visibleOnHover: { selector: '.hide-left-side-panel' }">
      <a href="javascript:void(0);" style="z-index: 1000; display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-left-side-panel" data-bind="visible: ! leftAssistVisible(), toggle: leftAssistVisible"><i class="fa fa-chevron-right"></i></a>
      <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-left-side-panel" data-bind="visible: leftAssistVisible, toggle: leftAssistVisible"><i class="fa fa-chevron-left"></i></a>
      <!-- ko if: leftAssistVisible -->
      <div class="assist" data-bind="component: {
          name: 'assist-panel',
          params: {
            user: '${user.username}',
            sql: {
              navigationSettings: {
                openItem: false,
                showStats: true
              }
            },
            visibleAssistPanels: ['sql']
          }
        }"></div>
      <!-- /ko -->
    </div>

    <div id="leftResizer" class="resizer" data-bind="visible: leftAssistVisible(), splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.left-panel',
      sidePanelVisible: leftAssistVisible,
      orientation: 'left',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }"><div class="resize-bar">&nbsp;</div></div>


    <div class="page-content" data-bind="niceScroll: {horizrailenabled: false}">
      <!-- ko hueSpinner: { spin: isLoadingEmbeddable, center: true, size: 'xlarge' } --><!-- /ko -->
      <div id="embeddable_editor" class="embeddable"></div>
      <div id="embeddable_notebook" class="embeddable"></div>
      <div id="embeddable_metastore" class="embeddable"></div>
      <div id="embeddable_dashboard" class="embeddable"></div>
      <div id="embeddable_oozie_workflow" class="embeddable"></div>
      <div id="embeddable_oozie_coordinator" class="embeddable"></div>
      <div id="embeddable_oozie_bundle" class="embeddable"></div>
      <div id="embeddable_jobbrowser" class="embeddable"></div>
      <div id="embeddable_filebrowser" class="embeddable"></div>
      <div id="embeddable_filebrowser_s3" class="embeddable"></div>
      <div id="embeddable_fileviewer" class="embeddable"></div>
      <div id="embeddable_home" class="embeddable"></div>
      <div id="embeddable_indexer" class="embeddable"></div>
      <div id="embeddable_importer" class="embeddable"></div>
      <div id="embeddable_collections" class="embeddable"></div>
      <div id="embeddable_indexes" class="embeddable"></div>
      <div id="embeddable_useradmin_users" class="embeddable"></div>
      <div id="embeddable_useradmin_groups" class="embeddable"></div>
      <div id="embeddable_useradmin_permissions" class="embeddable"></div>
      <div id="embeddable_useradmin_configurations" class="embeddable"></div>
      <div id="embeddable_useradmin_newuser" class="embeddable"></div>
      <div id="embeddable_useradmin_addldap" class="embeddable"></div>
      <div id="embeddable_hbase" class="embeddable"></div>
      <div id="embeddable_security_hive" class="embeddable"></div>
      <div id="embeddable_security_hdfs" class="embeddable"></div>
      <div id="embeddable_security_hive2" class="embeddable"></div>
      <div id="embeddable_security_solr" class="embeddable"></div>
      <div id="embeddable_help" class="embeddable"></div>
      <div id="embeddable_admin_wizard" class="embeddable"></div>
      <div id="embeddable_logs" class="embeddable"></div>
      <div id="embeddable_dump_config" class="embeddable"></div>
    </div>

    <div id="rightResizer" class="resizer" data-bind="visible: rightAssistVisible() && rightAssistAvailable(), splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.right-panel',
      sidePanelVisible: rightAssistVisible,
      orientation: 'right',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }"><div class="resize-bar" style="right: 0">&nbsp;</div></div>

    <div class="right-panel" data-bind="css: { 'side-panel-closed': !rightAssistVisible() || !rightAssistAvailable() }, visibleOnHover: { selector: '.hide-right-side-panel' }">
      <a href="javascript:void(0);" style="display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-right-side-panel" data-bind="visible: ! rightAssistVisible() && rightAssistAvailable(), toggle: rightAssistVisible"><i class="fa fa-chevron-left"></i></a>
      <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-right-side-panel" data-bind="visible: rightAssistVisible() && rightAssistAvailable(), toggle: rightAssistVisible"><i class="fa fa-chevron-right"></i></a>

      <div data-bind="visible: rightAssistVisible() && rightAssistAvailable()" style="display: none; height: 100%; width: 100%; position: relative;">
        <ul class="right-panel-tabs nav nav-tabs">
          <li data-bind="css: { 'active' : activeRightTab() === 'assistant' }, visible: assistantAvailable"><a href="javascript: void(0);" data-bind="click: function() { activeRightTab('assistant'); }">${ _('Assistant') }</a></li>
          <li data-bind="css: { 'active' : activeRightTab() === 'functions' }"><a href="javascript: void(0);" data-bind="click: function() { activeRightTab('functions'); }">${ _('Functions') }</a></li>
          <li data-bind="css: { 'active' : activeRightTab() === 'schedules' }"><a href="javascript: void(0);" data-bind="click: function() { activeRightTab('schedules'); }">${ _('Schedule') }</a></li>
        </ul>

        <div class="right-panel-tab-content tab-content">
          <!-- ko if: activeRightTab() === 'assistant' -->
          <div data-bind="component: { name: 'assistant-panel' }"></div>
          <!-- /ko -->

          <!-- ko if: activeRightTab() === 'functions' -->
          <div data-bind="component: { name: 'functions-panel' }"></div>
          <!-- /ko -->

          <!-- ko if: activeRightTab() === 'schedules' -->
          <div>Schedules</div>
          <!-- /ko -->
        </div>
      </div>
    </div>

    <div class="context-panel" data-bind="css: { 'visible': contextPanelVisible }">
      <ul class="nav nav-tabs">
        <!-- ko if: sessionsAvailable -->
        <li class="active"><a href="#sessionsTab" data-toggle="tab" data-bind="visible: sessionsAvailable">${_('Sessions')}</a></li>
        <!-- /ko -->
      </ul>

      <div class="tab-content">
        <!-- ko if: sessionsAvailable -->
        <div class="tab-pane active" id="sessionsTab">
          <div class="row-fluid">
            <div class="span12" data-bind="template: { name: 'notebook-session-config-template', data: activeAppViewModel }"></div>
          </div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </div>
</div>

<script src="${ static('desktop/js/cui-bundle.js') }"></script>

<script src="${ static('desktop/js/jquery.migration.js') }"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
<script src="${ static('desktop/js/bootstrap-tooltip.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>
<script src="${ static('desktop/ext/js/fileuploader.js') }"></script>
<script src="${ static('desktop/ext/js/filesize.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.cookie.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.form.js') }"></script>
<script src="${ static('desktop/js/jquery.datatables.sorting.js') }"></script>

<script src="${ static('desktop/ext/js/jquery/plugins/jquery.basictable.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>

<script src="${ static('desktop/js/jquery.nicescroll.js') }"></script>

<script src="${ static('desktop/js/jquery.hiveautocomplete.js') }"></script>
<script src="${ static('desktop/js/jquery.hdfsautocomplete.js') }"></script>
<script src="${ static('desktop/js/jquery.filechooser.js') }"></script>
<script src="${ static('desktop/js/jquery.selector.js') }"></script>
<script src="${ static('desktop/js/jquery.delayedinput.js') }"></script>
<script src="${ static('desktop/js/jquery.rowselector.js') }"></script>
<script src="${ static('desktop/js/jquery.notify.js') }"></script>
<script src="${ static('desktop/js/jquery.titleupdater.js') }"></script>
<script src="${ static('desktop/js/jquery.horizontalscrollbar.js') }"></script>
<script src="${ static('desktop/js/jquery.tablescroller.js') }"></script>
<script src="${ static('desktop/js/jquery.tableextender.js') }"></script>
<script src="${ static('desktop/js/jquery.tableextender2.js') }"></script>
<script src="${ static('desktop/ext/js/d3.v3.js') }"></script>
<script src="${ static('desktop/ext/js/d3.v4.js') }"></script>
<script src="${ static('desktop/js/hue.colors.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout.validation.min.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('desktop/js/ko.switch-case.js') }"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }"></script>
<script src="${ static('desktop/js/sqlUtils.js') }"></script>
<script src="${ static('desktop/js/jquery.scrollleft.js') }"></script>
<script src="${ static('desktop/js/jquery.scrollup.js') }"></script>
<script src="${ static('desktop/js/jquery.tour.js') }"></script>
<script src="${ static('desktop/js/jquery.huedatatable.js') }"></script>
<script src="${ static('desktop/js/sqlFunctions.js') }"></script>
<script src="${ static('desktop/ext/js/selectize.min.js') }"></script>
<script src="${ static('desktop/js/ko.selectize.js') }"></script>
<script src="${ static('desktop/js/ace/ace.js') }"></script>
<script src="${ static('desktop/js/ace/mode-impala.js') }"></script>
<script src="${ static('desktop/js/ace/mode-hive.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>
<script src="${ static('desktop/ext/js/dropzone.min.js') }"></script>

# Task History
<script src="${ static('desktop/js/autocomplete/sql.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('notebook/js/notebook.ko.js') }"></script>


<script type="text/javascript">
(function () {
    var proxiedKoRegister = ko.components.register;
    var registeredComponents = [];
    ko.components.register = function () {
      // This guarantees a ko component is only registered once
      // Some currently get registered twice when switching between notebook and editor
      if (registeredComponents.indexOf(arguments[0]) === -1) {
        registeredComponents.push(arguments[0]);
        return proxiedKoRegister.apply(this, arguments);
      }
    };
  })();
</script>

${ koComponents.all() }

${ commonHeaderFooterComponents.header_pollers(user, is_s3_enabled, apps) }

${ assist.assistJSModels() }
${ assist.assistPanel() }

<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

<script type="text/javascript">

  $(document).ready(function () {
    $(document).on('hideHistoryModal', function (e) {
      $('#clearNotificationHistoryModal').modal('hide');
    });

    var onePageViewModel = (function () {

      var EMBEDDABLE_PAGE_URLS = {
        editor: '/notebook/editor_embeddable',
        notebook: '/notebook/notebook_embeddable',
        metastore: '/metastore/tables/?is_embeddable=true',
        dashboard: '/dashboard/embeddable/new_search',
        oozie_workflow: '/oozie/editor/workflow/new/?is_embeddable=true',
        oozie_coordinator: '/oozie/editor/coordinator/new/?is_embeddable=true',
        oozie_bundle: '/oozie/editor/bundle/new/?is_embeddable=true',
        jobbrowser: '/jobbrowser/apps?is_embeddable=true',
        filebrowser: '/filebrowser/?is_embeddable=true',
        filebrowser_s3: '/filebrowser/view=S3A://?is_embeddable=true',
        fileviewer: 'filebrowser/view=',
        home: '/home_embeddable',
        indexer: '/indexer/indexer/?is_embeddable=true',
        collections: '/dashboard/admin/collections?is_embeddable=true',
        indexes: '/indexer/?is_embeddable=true',
        importer: '/indexer/importer/?is_embeddable=true',
        useradmin_users: '/useradmin/users?is_embeddable=true',
        useradmin_groups: '/useradmin/groups?is_embeddable=true',
        useradmin_permissions: '/useradmin/permissions?is_embeddable=true',
        useradmin_configurations: '/useradmin/configurations?is_embeddable=true',
        useradmin_newuser: '/useradmin/users/new?is_embeddable=true',
        useradmin_addldap: 'useradmin/users/add_ldap_users?is_embeddable=true',
        hbase: '/hbase/?is_embeddable=true',
        security_hive: '/security/hive?is_embeddable=true',
        security_hdfs: '/security/hdfs?is_embeddable=true',
        security_hive2: '/security/hive2?is_embeddable=true',
        security_solr: '/security/solr?is_embeddable=true',
        help: '/help/?is_embeddable=true',
        admin_wizard: '/about/admin_wizard?is_embeddable=true',
        logs: '/logs?is_embeddable=true',
        dump_config: '/desktop/dump_config?is_embeddable=true',
      };

      var SKIP_CACHE = ['fileviewer', 'useradmin_users', 'useradmin_groups', 'useradmin_permissions', 'useradmin_configurations', 'useradmin_newuser', 'useradmin_addldap'];

      var OnePageViewModel = function () {
        var self = this;

        self.embeddable_cache = {};
        self.currentApp = ko.observable();
        self.isLoadingEmbeddable = ko.observable(false);
        self.extraEmbeddableURLParams = ko.observable('');

        self.getActiveAppViewModel = function (callback) {
          var checkInterval = window.setInterval(function () {
            var $koElement = $('#' + self.currentApp() + 'Components');
            if ($koElement.length > 0 && ko.dataFor($koElement[0])) {
              window.clearInterval(checkInterval);
              callback(ko.dataFor($koElement[0]));
            }
          }, 25);
        }

        self.changeEditorType = function (type) {
          self.extraEmbeddableURLParams('?type=' + type);
          hueUtils.changeURLParameter('type', type);
          self.getActiveAppViewModel(function (viewModel) {
            if (viewModel && viewModel.selectedNotebook && viewModel.selectedNotebook()) {
              viewModel.selectedNotebook().selectedSnippet(type);
              viewModel.editorType(type);
              viewModel.newNotebook();
            }
          })
        }

        self.currentApp.subscribe(function (newApp) {
          huePubSub.publish('set.current.app.name', newApp);
          self.getActiveAppViewModel(function (viewModel) {
            huePubSub.publish('set.current.app.view.model', viewModel);
          })
        })

        huePubSub.subscribe('get.current.app.view.model', function () {
          self.getActiveAppViewModel(function (viewModel) {
            huePubSub.publish('set.current.app.view.model', viewModel);
          })
        })

        huePubSub.subscribe('get.current.app.name', function () {
          huePubSub.publish('set.current.app.name', self.currentApp());
        });

        huePubSub.subscribe('open.fb.file', function (path) {
          self.extraEmbeddableURLParams(path + '?is_embeddable=true');
          hueUtils.changeURLParameter('path', path);
          self.currentApp('fileviewer');
        });

        huePubSub.subscribe('open.fb.folder', function (path) {
          hueUtils.removeURLParameter('path');
          self.currentApp('filebrowser');
          window.location.hash = path;
        });

        huePubSub.subscribe('open.editor.query', function (uuid) {
          self.currentApp('editor');
          self.getActiveAppViewModel(function (viewModel) {
            viewModel.openNotebook(uuid);
          })
        });

        huePubSub.subscribe('open.editor.query.external', function (statementOptions) {
          self.currentApp('editor');
          self.getActiveAppViewModel(function (viewModel) {
            viewModel.newNotebook(function() { // Uses default type of Editor
              viewModel.selectedNotebook().snippets()[0].statementType(statementOptions['statementType']);
              viewModel.selectedNotebook().snippets()[0].statementPath(statementOptions['statementPath']);
            });
          })
        });

        huePubSub.subscribe('open.link', function (href) {
          if (href.startsWith('/notebook/editor')){
            if (hueUtils.getSearchParameter(href, 'editor') !== '') {
              hueUtils.changeURLParameter('editor', hueUtils.getSearchParameter(href, 'editor'));
              self.currentApp('editor')
              self.getActiveAppViewModel(function (viewModel) {
                viewModel.openNotebook(hueUtils.getSearchParameter(href, 'editor'));
              })
            } else if (location.getParameter('type') !== ''){
              if (hueUtils.getSearchParameter(href, 'type') !== '' && hueUtils.getSearchParameter(href, 'type') !== location.getParameter('type')) {
                self.changeEditorType(hueUtils.getSearchParameter(href, 'type'));
              }
            } else {
              if (hueUtils.getSearchParameter(href, 'type') !== ''){
                self.changeEditorType(hueUtils.getSearchParameter(href, 'type'));
              } else {
                self.changeEditorType('hive');
              }
              self.currentApp('editor')
            }
          } else if (href.startsWith('/metastore')){
            self.currentApp('metastore');
            hueUtils.changeURLParameter('path', href.substring('/metastore'.length + 1));
            self.getActiveAppViewModel(function (metastoreViewModel) {
              metastoreViewModel.loadURL();
            });
          } else if (href.startsWith('/indexer/importer/prefill')){
              self.currentApp('importer');
              self.getActiveAppViewModel(function (viewModel) {
                var arguments = href.match(/\/indexer\/importer\/prefill\/?([^/]+)\/?([^/]+)\/?([^/]+)?/);
                if (! arguments) {
                  console.warn('Could not match ' + href)
                }
                viewModel.createWizard.prefill.source_type(arguments && arguments[1] ? arguments[1] : '');
                viewModel.createWizard.prefill.target_type(arguments && arguments[2] ? arguments[2] : '');
                viewModel.createWizard.prefill.target_path(arguments && arguments[3] ? arguments[3] : '');
              })
          } else if (href.startsWith('/notebook')){
            self.currentApp('notebook');
          } else if (href.startsWith('/pig')){
            self.changeEditorType('pig');
            self.currentApp('editor');
          } else if (href.startsWith('/indexer')){
            self.currentApp('indexes');
          } else if (href.startsWith('/dashboard/embeddable') || href.startsWith('/dashboard/new_search')){
            self.currentApp('dashboard');
          } else if (href.startsWith('/dashboard/admin/collections')){
            self.currentApp('collections');
          } else if (href.startsWith('/oozie/editor/workflow/new')){
            self.currentApp('oozie_workflow');
          } else if (href.startsWith('/oozie/editor/coordinator/new')){
            self.currentApp('oozie_coordinator');
          } else if (href.startsWith('/oozie/editor/bundle/new')){
            self.currentApp('oozie_bundle');
          } else if (href.startsWith('/filebrowser')){
            self.currentApp('filebrowser');
          } else if (href.startsWith('/useradmin/users/add_ldap_users')){
            self.currentApp('useradmin_addldap');
          } else if (href.startsWith('/useradmin/users/new')){
            self.currentApp('useradmin_newuser');
          } else if (href.startsWith('/useradmin/users')){
            self.currentApp('useradmin_users');
          } else if (href.startsWith('/useradmin/groups')){
            self.currentApp('useradmin_groups');
          } else if (href.startsWith('/useradmin/permissions')){
            self.currentApp('useradmin_permissions');
          } else if (href.startsWith('/useradmin/configurations')) {
            self.currentApp('useradmin_configurations');
          } else if (href.startsWith('/security/hive2')) {
            self.currentApp('security_hive2');
          } else if (href.startsWith('/security/hive')) {
            self.currentApp('security_hive');
          } else if (href.startsWith('/security/solr')) {
            self.currentApp('security_solr');
          } else if (href.startsWith('/security/hdfs')) {
            self.currentApp('security_hdfs');
          } else if (href.startsWith('/help')) {
            self.currentApp('help');
          } else if (href.startsWith('/about/admin_wizard')) {
            self.currentApp('admin_wizard');
          } else if (href.startsWith('/logs')) {
            self.currentApp('logs');
          } else if (href.startsWith('/desktop/dump_config')) {
            self.currentApp('dump_config');
          }
        });

        var loadedJs = [];
        var loadedCss = [];

        $('script[src]').each(function(){
          loadedJs.push($(this).attr('src'));
        });

        $('link[href]').each(function(){
          loadedCss.push($(this).attr('href'));
        });

        // Only load CSS and JS files that are not loaded before
        self.processHeaders = function(response){
          var r = $('<span>').html(response);
          r.find('link').each(function () {
            $(this).attr('href', $(this).attr('href') + '?' + Math.random())
          });
          r.find('script[src]').each(function () {
            var jsFile = $(this).attr('src').split('?')[0];
            if (loadedJs.indexOf(jsFile) === -1) {
              loadedJs.push(jsFile);
              $(this).clone().appendTo($('head'));
            }
            $(this).remove();
          });
          r.find('link[href]').each(function () {
            var cssFile = $(this).attr('href').split('?')[0];
            if (loadedCss.indexOf(cssFile) === -1) {
              loadedCss.push(cssFile);
              $(this).clone().appendTo($('head'));
            }
            $(this).remove();
          });
          r.unwrap('<span>');
          return r;
        }

        self.currentApp.subscribe(function (newVal) {
          hueUtils.changeURLParameter('app', newVal);
          if (newVal !== 'editor') {
            hueUtils.removeURLParameter('type');
          }
          self.isLoadingEmbeddable(true);
          if (typeof self.embeddable_cache[newVal] === 'undefined') {
            $.ajax({
              url: EMBEDDABLE_PAGE_URLS[newVal] + self.extraEmbeddableURLParams(),
              beforeSend: function (xhr) {
                xhr.setRequestHeader('X-Requested-With', 'Hue');
              },
              dataType: 'html',
              success: function (response) {
                self.extraEmbeddableURLParams('');
                var r = self.processHeaders(response);
                if (SKIP_CACHE.indexOf(newVal) === -1) {
                  self.embeddable_cache[newVal] = r;
                }
                $('#embeddable_' + newVal).html(r);
                self.isLoadingEmbeddable(false);
              }
            });
          } else {
            self.isLoadingEmbeddable(false);
          }
          $('.embeddable').hide();
          $('#embeddable_' + newVal).insertBefore($('.embeddable:first')).show();
        });

        var loadAppState = function () {
          if (window.location.getParameter('app') !== '' && EMBEDDABLE_PAGE_URLS[window.location.getParameter('app')]) {
            var app = window.location.getParameter('app');
            switch (app) {
              case 'fileviewer':
                if (window.location.getParameter('path') !== '') {
                  self.extraEmbeddableURLParams(window.location.getParameter('path') + '?is_embeddable=true');
                  self.currentApp(app);
                }
                else {
                  self.currentApp('filebrowser');
                }
                break;
              case 'filebrowser':
                var previousHash = window.location.hash;
                self.currentApp(app);
                window.location.hash = previousHash;
                break;
              case 'editor':
                if (window.location.getParameter('type') !== '') {
                  self.changeEditorType(window.location.getParameter('type'));
                }
                self.currentApp(app);
                break;
              default:
                self.currentApp(app);
            }
          }
          else {
            self.currentApp('editor');
          }
        }

        self.dropzoneError = function (filename) {
          self.currentApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(DropzoneGlobals.homeDir + '/' + filename);
          });
        }

        self.dropzoneComplete = function (path) {
          self.currentApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(path);
          });
        }

        loadAppState();

        window.onpopstate = function (event) {
          loadAppState();
        };

        huePubSub.subscribe('switch.app', function (name) {
          self.currentApp(name);
        });

      };

      var onePageViewModel = new OnePageViewModel();
      ko.applyBindings(onePageViewModel, $('.page-content')[0]);
      return onePageViewModel;
    })();

    var sidePanelViewModel = (function () {
      function SidePanelViewModel () {
        var self = this;
        self.apiHelper = ApiHelper.getInstance();
        self.leftAssistVisible = ko.observable();
        self.rightAssistVisible = ko.observable();
        self.rightAssistVisible.subscribe(function () {
          window.setTimeout(function () {
            huePubSub.publish('reposition.scroll.anchor.up')
          }, 0);
        });
        self.rightAssistAvailable = ko.observable(false);
        self.assistantAvailable = ko.observable(false);
        self.activeRightTab = ko.observable();
        self.activeAppViewModel = ko.observable();

        huePubSub.subscribe('set.current.app.name', function (appName) {
          self.rightAssistAvailable(appName === 'editor' || appName === 'notebook');
        });
        huePubSub.publish('get.current.app.name');


        self.contextPanelVisible = ko.observable(false);
        self.sessionsAvailable = ko.observable(false);

        self.activeAppViewModel.subscribe(function (viewModel) {
          self.sessionsAvailable(typeof viewModel.selectedNotebook !== 'undefined');
        })

        huePubSub.subscribe('context.panel.visible', function (visible) {
          self.contextPanelVisible(visible);
        })

        huePubSub.subscribe('active.snippet.type.changed', function (type) {
          if (type === 'hive' || type === 'impala') {
            if (!self.assistantAvailable() && self.activeRightTab() !== 'assistant') {
              self.activeRightTab('assistant');
            }
            self.assistantAvailable(true);
          } else {
            if (self.activeRightTab() === 'assistant') {
              self.activeRightTab('functions');
            }
            self.assistantAvailable(false);
          }
        });

        huePubSub.subscribe('set.current.app.view.model', self.activeAppViewModel);
        huePubSub.publish('get.current.app.view.model');

        if (!self.activeRightTab()) {
          self.activeRightTab('functions');
        }

        if (self.assistantAvailable()) {
          self.activeRightTab = ko.observable('assistant');
        }

        self.apiHelper.withTotalStorage('assist', 'left_assist_panel_visible', self.leftAssistVisible, true);
        self.apiHelper.withTotalStorage('assist', 'right_assist_panel_visible', self.rightAssistVisible, true);
      }

      var sidePanelViewModel = new SidePanelViewModel();
      ko.applyBindings(sidePanelViewModel, $('.left-panel')[0]);
      ko.applyBindings(sidePanelViewModel, $('#leftResizer')[0]);
      ko.applyBindings(sidePanelViewModel, $('#rightResizer')[0]);
      ko.applyBindings(sidePanelViewModel, $('.right-panel')[0]);
      ko.applyBindings(sidePanelViewModel, $('.context-panel')[0]);

      return sidePanelViewModel;
    })();

    var topNavViewModel = (function (onePageViewModel) {

      // TODO: Extract to common module (shared with nav search autocomplete)
      var SEARCH_FACET_ICON = 'fa-tags';
      var SEARCH_TYPE_ICONS = {
        'DATABASE': 'fa-database',
        'TABLE': 'fa-table',
        'VIEW': 'fa-eye',
        'FIELD': 'fa-columns',
        'PARTITION': 'fa-th',
        'SOURCE': 'fa-server',
        'OPERATION': 'fa-cogs',
        'OPERATION_EXECUTION': 'fa-cog',
        'DIRECTORY': 'fa-folder-o',
        'FILE': 'fa-file-o',
        'SUB_OPERATION': 'fa-code-fork',
        'COLLECTION': 'fa-search',
        'HBASE': 'fa-th-large',
        'HUE': 'fa-file-o'
      };

      function TopNavViewModel () {
        var self = this;
        self.onePageViewModel = onePageViewModel;
        self.leftNavVisible = ko.observable(false);
        self.leftNavVisible.subscribe(function (val) {
          huePubSub.publish('left.nav.open.toggle', val);
        });

        self.onePageViewModel.currentApp.subscribe(function () {
          self.leftNavVisible(false);
        });

        self.apiHelper = ApiHelper.getInstance();
        self.searchActive = ko.observable(false);
        self.searchHasFocus = ko.observable(false);
        self.searchInput = ko.observable();
        self.jobsPanelVisible = ko.observable(false);
        self.historyPanelVisible = ko.observable(false);

        self.searchAutocompleteSource = function (request, callback) {
          // TODO: Extract complete contents to common module (shared with nav search autocomplete)
          var facetMatch = request.term.match(/([a-z]+):\s*(\S+)?$/i);
          var isFacet = facetMatch !== null;
          var partialMatch = isFacet ? null : request.term.match(/\S+$/);
          var partial = isFacet && facetMatch[2] ? facetMatch[2] : (partialMatch ? partialMatch[0] : '');
          var beforePartial = request.term.substring(0, request.term.length - partial.length);

          self.apiHelper.globalSearchAutocomplete({
            query:  request.term,
            successCallback: function (data) {
              var values = [];
              var facetPartialRe = new RegExp(partial.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), 'i'); // Protect for 'tags:*axe'

              if (typeof data.resultsHuedocuments !== 'undefined') {
                data.resultsHuedocuments.forEach(function (result) {
                  values.push({ data: { label: result.hue_name, icon: SEARCH_TYPE_ICONS[result.type],  description: result.hue_description }, value: beforePartial + result.originalName });
                });
              }
              if (values.length > 0) {
                values.push({ divider: true });
              }

              if (isFacet && typeof data.facets !== 'undefined') { // Is typed facet, e.g. type: type:bla
                var facetInQuery = facetMatch[1];
                if (typeof data.facets[facetInQuery] !== 'undefined') {
                  $.map(data.facets[facetInQuery], function (count, value) {
                    if (facetPartialRe.test(value)) {
                      values.push({ data: { label: facetInQuery + ':' + value, icon: SEARCH_FACET_ICON, description: count }, value: beforePartial + value})
                    }
                  });
                }
              } else {
                if (typeof data.facets !== 'undefined') {
                  Object.keys(data.facets).forEach(function (facet) {
                    if (facetPartialRe.test(facet)) {
                      if (Object.keys(data.facets[facet]).length > 0) {
                        values.push({ data: { label: facet + ':', icon: SEARCH_FACET_ICON, description: $.map(data.facets[facet], function (key, value) { return value + ' (' + key + ')'; }).join(', ') }, value: beforePartial + facet + ':'});
                      } else { // Potential facet from the list
                        values.push({ data: { label: facet + ':', icon: SEARCH_FACET_ICON, description: '' }, value: beforePartial + facet + ':'});
                      }
                    } else if (partial.length > 0) {
                      Object.keys(data.facets[facet]).forEach(function (facetValue) {
                        if (facetValue.indexOf(partial) !== -1) {
                          values.push({ data: { label: facet + ':' + facetValue, icon: SEARCH_FACET_ICON, description: facetValue }, value: beforePartial + facet + ':' + facetValue });
                        }
                      });
                    }
                  });
                }
              }

              if (values.length > 0) {
                values.push({ divider: true });
              }
              if (typeof data.results !== 'undefined') {
                data.results.forEach(function (result) {
                  values.push({ data: { label: result.hue_name, icon: SEARCH_TYPE_ICONS[result.type],  description: result.hue_description }, value: beforePartial + result.originalName });
                });
              }

              if (values.length > 0 && values[values.length - 1].divider) {
                values.pop();
              }
              if (values.length === 0) {
                values.push({ noMatch: true });
              }
              callback(values);
            },
            silenceErrors: true,
            errorCallback: function () {
              callback([]);
            }
          });
        };
      }

      TopNavViewModel.prototype.performSearch = function () {
      };

      var topNavViewModel = new TopNavViewModel();
      ko.applyBindings(topNavViewModel, $('.top-nav')[0]);
      ko.applyBindings(topNavViewModel, $('.left-nav')[0]);

      return topNavViewModel;
    })(onePageViewModel);

    window.hueDebug = {
      viewModel: function (element) {
        return element ? ko.dataFor(element) : window.hueDebug.onePageViewModel;
      },
      onePageViewModel: onePageViewModel,
      sidePanelViewModel: sidePanelViewModel,
      topNavViewModel: topNavViewModel
    };
  });
</script>

${ commonHeaderFooterComponents.footer(messages) }

</body>
</html>
