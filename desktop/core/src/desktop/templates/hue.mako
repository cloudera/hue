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

  <link href="${ static('desktop/css/roboto.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/bootstrap-tour.min.css') }" rel="stylesheet">

  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/jquery-ui.css') }" rel="stylesheet">

  ${ commonHeaderFooterComponents.header_i18n_redirection(user, is_s3_enabled, apps) }

  <script type="text/javascript">
    var IS_HUE_4 = true;
  </script>

  <script src="${ static('desktop/js/hue4.utils.js') }"></script>
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

% if banner_message or conf.CUSTOM.BANNER_TOP_HTML.get():
<div class="banner">
  ${ banner_message or conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
</div>
% endif

<div class="main-page">
  <nav class="navbar navbar-default">
    <div class="navbar-inner top-nav">
      <div class="top-nav-left">
        <a class="hamburger hamburger-hue pull-left" data-bind="toggle: leftNavVisible, css: { 'is-active': leftNavVisible }">
          <span class="hamburger-box"><span class="hamburger-inner"></span></span>
        </a>

        <a class="brand" data-bind="hueLink: '/home'" href="javascript: void(0);" title="${_('Documents')}">
          <svg style="height: 24px; width: 120px;"><use xlink:href="#hi-logo"></use></svg>
        </a>


        <div class="btn-group" data-bind="visible: true" style="display:none; margin-top: 8px">
          <!-- ko if: mainQuickCreateAction -->
          <!-- ko with: mainQuickCreateAction -->
          <button class="btn btn-primary disable-feedback hue-main-create-btn" data-bind="hueLink: url, attr: {title: tooltip}, style: { borderBottomRightRadius: $parent.quickCreateActions().length > 1 ? '0px' : '4px', borderTopRightRadius: $parent.quickCreateActions().length > 1 ? '0px' : '4px' }">
            <span data-bind="text: displayName"></span>
          </button>
          <!-- /ko -->
          <!-- /ko -->
          <button class="btn btn-primary dropdown-toggle hue-main-create-btn-dropdown" data-toggle="dropdown" data-bind="visible: quickCreateActions().length > 1">
            <!-- ko ifnot: mainQuickCreateAction -->${ _('More') } <!-- /ko -->
            <span class="caret"></span>
          </button>
          <ul class="dropdown-menu hue-main-create-dropdown" data-bind="foreach: { data: quickCreateActions, as: 'item' }">
            <!-- ko template: 'quick-create-item-template' --><!-- /ko -->
          </ul>
        </div>

        <script type="text/html" id="quick-create-item-template">
          <!-- ko if: item.dividerAbove -->
          <li class="divider"></li>
          <!-- /ko -->
          <li data-bind="css: { 'dropdown-submenu': item.isCategory }"><a href="javascript: void(0);" data-bind="hueLink: item.url">
            <!-- ko if: item.icon -->
            <!-- ko template: { name: 'app-icon-template', data: item } --><!-- /ko -->
            <!-- /ko -->
            <span data-bind="css: { 'dropdown-no-icon': !item.icon }, text: item.displayName"></span></a>
            <!-- ko if: item.isCategory -->
            <ul class="dropdown-menu" data-bind="foreach: { data: item.children, as: 'item' }">
              <!-- ko template: 'quick-create-item-template' --><!-- /ko -->
            </ul>
            <!-- /ko -->
          </li>
        </script>
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
        <div class="dropdown navbar-dropdown pull-right">
          <%
            view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or user.is_superuser
          %>
          <button class="btn btn-flat" data-toggle="dropdown">
            <i class="fa fa-user"></i> ${ user.username } <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            % if view_profile:
            <li><a href="javascript:void(0)" data-bind="hueLink: '/useradmin/users/edit/${ user.username }'" title="${ _('View Profile') if is_ldap_setup else _('Edit Profile') }"><i class="fa fa-fw fa-user"></i> ${_('My Profile')}</a></li>
            % endif
            % if user.is_superuser:
            <li data-bind="hueLink: '/useradmin/users/'"><a href="javascript: void(0);"><i class="fa fa-fw fa-group"></i> ${_('Manage Users')}</a></li>
            % endif
            <li><a href="javascript:void(0)" onclick="huePubSub.publish('set.hue.version', 3)"><i class="fa fa-fw fa-exchange"></i> ${_('Switch to Hue 3')}</a></li>
            <li><a href="http://gethue.com" target="_blank"><span class="dropdown-no-icon">${_('Help')}</span></a></li>
            % if user.is_superuser:
            <li><a href="/about/"><span class="dropdown-no-icon">${_('About Hue')}</span></a></li>
            % endif
            <li class="divider"></li>
            <li><a title="${_('Sign out')}" href="/accounts/logout/"><i class="fa fa-fw fa-sign-out"></i> ${ _('Sign out') }</a></li>
          </ul>
        </div>
        % endif

        <!-- ko component: 'hue-history-panel' --><!-- /ko -->
        <!-- ko if: hasJobBrowser -->
          <!-- ko component: { name: 'hue-job-browser-panel', params: { onePageViewModel: onePageViewModel }} --><!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </nav>

  <div class="content-wrapper">

    <script type="text/html" id="tmpl-sidebar-link">
      <a role="button" class="sidebar-item" data-bind="hueLink: item.url, attr: { title: item.displayName }">
        <span class="sidebar-item-name" data-bind="text: item.displayName"></span>
      </a>
    </script>

    <div class="sidebar sidebar-below-top-bar" data-bind="visible: leftNavVisible" style="display:none;">
      <div class="sidebar-content">
        <!-- ko foreach: {data: items, as: 'item'} -->
          <!-- ko if: item.isCategory -->
             <h4 class="sidebar-category-item" data-bind="text: item.displayName"></h4>
             <!-- ko template: {name: 'tmpl-sidebar-link', foreach: item.children, as: 'item'} --><!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: item.isCategory -->
             <!-- ko template: { name: 'tmpl-sidebar-link' } --><!-- /ko -->
          <!-- /ko -->
        <!-- /ko -->
      </div>
      <div class="sidebar-footer-panel">
        <div data-bind="dropzone: {
            clickable: false,
            url: '/filebrowser/upload/file?dest=' + DropzoneGlobals.homeDir,
            params: { dest: DropzoneGlobals.homeDir },
            paramName: 'hdfs_file',
            onError: onePageViewModel.dropzoneError,
            onComplete: onePageViewModel.dropzoneComplete },
            click: function(){ page('/indexer/importer/') }" class="pointer" title="${ _('Import data wizard') }">
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
    }"><div class="resize-bar"></div></div>


    <div class="page-content" data-bind="niceScroll: {horizrailenabled: false}">
      <!-- ko hueSpinner: { spin: isLoadingEmbeddable, center: true, size: 'xlarge' } --><!-- /ko -->
      <div id="embeddable_editor" class="embeddable"></div>
      <div id="embeddable_notebook" class="embeddable"></div>
      <div id="embeddable_metastore" class="embeddable"></div>
      <div id="embeddable_dashboard" class="embeddable"></div>
      <div id="embeddable_oozie_workflow" class="embeddable"></div>
      <div id="embeddable_oozie_coordinator" class="embeddable"></div>
      <div id="embeddable_oozie_bundle" class="embeddable"></div>
      <div id="embeddable_oozie_info" class="embeddable"></div>
      <div id="embeddable_jobbrowser" class="embeddable"></div>
      <div id="embeddable_filebrowser" class="embeddable"></div>
      <div id="embeddable_home" class="embeddable"></div>
      <div id="embeddable_indexer" class="embeddable"></div>
      <div id="embeddable_importer" class="embeddable"></div>
      <div id="embeddable_collections" class="embeddable"></div>
      <div id="embeddable_indexes" class="embeddable"></div>
      <div id="embeddable_useradmin_users" class="embeddable"></div>
      <div id="embeddable_useradmin_groups" class="embeddable"></div>
      <div id="embeddable_useradmin_newgroup" class="embeddable"></div>
      <div id="embeddable_useradmin_editgroup" class="embeddable"></div>
      <div id="embeddable_useradmin_permissions" class="embeddable"></div>
      <div id="embeddable_useradmin_editpermission" class="embeddable"></div>
      <div id="embeddable_useradmin_configurations" class="embeddable"></div>
      <div id="embeddable_useradmin_newuser" class="embeddable"></div>
      <div id="embeddable_useradmin_addldapusers" class="embeddable"></div>
      <div id="embeddable_useradmin_addldapgroups" class="embeddable"></div>
      <div id="embeddable_useradmin_edituser" class="embeddable"></div>
      <div id="embeddable_hbase" class="embeddable"></div>
      <div id="embeddable_security_hive" class="embeddable"></div>
      <div id="embeddable_security_hdfs" class="embeddable"></div>
      <div id="embeddable_security_hive2" class="embeddable"></div>
      <div id="embeddable_security_solr" class="embeddable"></div>
      <div id="embeddable_help" class="embeddable"></div>
      <div id="embeddable_admin_wizard" class="embeddable"></div>
      <div id="embeddable_logs" class="embeddable"></div>
      <div id="embeddable_dump_config" class="embeddable"></div>
      <div id="embeddable_404" class="embeddable"></div>
      <div id="embeddable_500" class="embeddable"></div>
      <div id="embeddable_sqoop" class="embeddable"></div>
    </div>

    <div id="rightResizer" class="resizer" data-bind="visible: rightAssistVisible() && rightAssistAvailable(), splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.right-panel',
      sidePanelVisible: rightAssistVisible,
      orientation: 'right',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }"><div class="resize-bar" style="right: 0">&nbsp;</div></div>

    <div class="right-panel side-panel-closed" data-bind="css: { 'side-panel-closed': !rightAssistVisible() || !rightAssistAvailable() }, visibleOnHover: { selector: '.hide-right-side-panel' }">
      <!-- ko if: rightAssistAvailable -->
      <a href="javascript:void(0);" style="display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-right-side-panel" data-bind="visible: ! rightAssistVisible(), toggle: rightAssistVisible"><i class="fa fa-chevron-left"></i></a>
      <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-right-side-panel" data-bind="visible: rightAssistVisible(), toggle: rightAssistVisible"><i class="fa fa-chevron-right"></i></a>

      <!-- ko if: rightAssistVisible -->
      <div class="assist" data-bind="component: {
          name: 'right-assist-panel',
          params: {}
        }">
      </div>
      <!-- /ko -->
      <!-- /ko -->
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

<script src="${ static('desktop/js/hue-bundle.js') }"></script>

<script src="${ static('desktop/js/jquery.migration.js') }"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-tour.min.js') }"></script>
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

<script src="${ static('desktop/js/autocomplete/sqlParseSupport.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sql.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('notebook/js/notebook.ko.js') }"></script>
<script src="${ static('metastore/js/metastore.model.js') }"></script>


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

## clusterConfig makes an ajax call so it needs to be after commonHeaderFooterComponents
<script src="${ static('desktop/js/clusterConfig.js') }"></script>

${ assist.assistJSModels() }
${ assist.assistPanel() }

% if request is not None:
${ smart_unicode(login_modal(request).content) | n,unicode }
% endif

<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

<script type="text/javascript">

  $(document).ready(function () {

    var onePageViewModel = (function () {

      var EMBEDDABLE_PAGE_URLS = {
        404: '/404',
        500: '/500',
        editor: '/editor',
        notebook: '/notebook',
        metastore: '/metastore/*',
        dashboard: '/dashboard/*',
        oozie_workflow: '/oozie/editor/workflow/*',
        oozie_coordinator: '/oozie/editor/coordinator/*',
        oozie_bundle: '/oozie/editor/bundle/*',
        oozie_info: '/oozie/list_oozie_info',
        jobbrowser: '/jobbrowser/apps',
        filebrowser: '/filebrowser/view=*',
        home: '/home*',
        indexer: '/indexer/indexer/',
        collections: '/dashboard/admin/collections',
        indexes: '/indexer/',
        importer: '/indexer/importer/',
        useradmin_users: '/useradmin/users',
        useradmin_groups: '/useradmin/groups',
        useradmin_newgroup: '/useradmin/groups/new',
        useradmin_editgroup: '/useradmin/groups/edit/:group',
        useradmin_permissions: '/useradmin/permissions',
        useradmin_editpermission: '/useradmin/permissions/edit/*',
        useradmin_configurations: '/useradmin/configurations',
        useradmin_newuser: '/useradmin/users/new',
        useradmin_addldapusers: '/useradmin/users/add_ldap_users',
        useradmin_edituser: '/useradmin/users/edit/:user',
        useradmin_addldapgroups: '/useradmin/users/add_ldap_groups',
        hbase: '/hbase/',
        security_hive: '/security/hive',
        security_hdfs: '/security/hdfs',
        security_hive2: '/security/hive2',
        security_solr: '/security/solr',
        help: '/help/',
        admin_wizard: '/about/admin_wizard',
        logs: '/logs',
        dump_config: '/desktop/dump_config',
        sqoop: '/sqoop',
      };

      var SKIP_CACHE = [
          'home', 'oozie_workflow', 'oozie_coordinator', 'oozie_bundle', 'dashboard',
          'filebrowser', 'useradmin_users', 'useradmin_groups', 'useradmin_newgroup', 'useradmin_editgroup',
          'useradmin_permissions', 'useradmin_editpermission', 'useradmin_configurations', 'useradmin_newuser',
          'useradmin_addldapusers', 'useradmin_addldapgroups', 'useradmin_edituser'
      ];

      var OnePageViewModel = function () {
        var self = this;

        self.embeddable_cache = {};
        self.currentApp = ko.observable();
        self.currentContextParams = ko.observable(null);
        self.currentQueryString = ko.observable(null);
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
        };

        self.changeEditorType = function (type) {
          self.getActiveAppViewModel(function (viewModel) {
            if (viewModel && viewModel.selectedNotebook) {
              hueUtils.waitForObservable(viewModel.selectedNotebook, function(){
                if (viewModel.editorType() !== type) {
                  viewModel.selectedNotebook().selectedSnippet(type);
                  viewModel.editorType(type);
                  viewModel.newNotebook(type);
                }
              });
            }
          })
        };

        self.currentApp.subscribe(function (newApp) {
          huePubSub.publish('set.current.app.name', newApp);
          self.getActiveAppViewModel(function (viewModel) {
            huePubSub.publish('set.current.app.view.model', viewModel);
          })
        });

        huePubSub.subscribe('get.current.app.view.model', function () {
          self.getActiveAppViewModel(function (viewModel) {
            huePubSub.publish('set.current.app.view.model', viewModel);
          })
        });

        huePubSub.subscribe('get.current.app.name', function () {
          huePubSub.publish('set.current.app.name', self.currentApp());
        });

        huePubSub.subscribe('open.editor.query', function (uuid) {
          self.loadApp('editor');
          self.getActiveAppViewModel(function (viewModel) {
            viewModel.openNotebook(uuid);
          })
        });

        huePubSub.subscribe('open.editor.new.query', function (statementOptions) {
          self.loadApp('editor');

          self.getActiveAppViewModel(function (viewModel) {
            var editorType = statementOptions['type'] || 'hive'; // Next: use file extensions and default type of Editor for SQL
            viewModel.newNotebook(editorType, function() {
              if (statementOptions['statementType']) {
                viewModel.selectedNotebook().snippets()[0].statementType(statementOptions['statementType']);
                viewModel.selectedNotebook().snippets()[0].statementPath(statementOptions['statementPath']);
              }
              if (statementOptions['directoryUuid']) {
                viewModel.selectedNotebook().directoryUuid(statementOptions['directoryUuid']);
              }
            });
          })
        });

        var loadedJs = [];
        var loadedCss = [];
        var loadedApps = [];

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
          r.find('a[href]').each(function () {
            var link = $(this).attr('href');
            if (link.startsWith('/') && !link.startsWith('/hue')){
              link = '/hue' + link;
            }
            $(this).attr('href', link);
          });
          r.unwrap('<span>');
          return r;
        };

        self.loadApp = function(app){
          self.currentApp(app);
          self.isLoadingEmbeddable(true);
          loadedApps.forEach(function (loadedApp) {
            window.pauseAppIntervals(loadedApp);
            huePubSub.pauseAppSubscribers(loadedApp);
          });
          huePubSub.publish('hue.datatable.search.hide');
          huePubSub.publish('nicescroll.resize');
          if (typeof self.embeddable_cache[app] === 'undefined') {
            if (loadedApps.indexOf(app) == -1){
              loadedApps.push(app);
            }
            var baseURL = EMBEDDABLE_PAGE_URLS[app];
            if (self.currentContextParams() !== null) {
              var route = new page.Route(baseURL);
              route.keys.forEach(function (key) {
                if (key.name === 0){
                  baseURL = baseURL.replace('*', self.currentContextParams()[key.name]);
                }
                else {
                  baseURL = baseURL.replace(':' + key.name, self.currentContextParams()[key.name]);
                }
              });
              self.currentContextParams(null);
            }
            if (self.currentQueryString() !== null) {
              baseURL += (baseURL.indexOf('?') > -1 ? '&' : '?') + self.currentQueryString();
              self.currentQueryString(null);
            }
            $.ajax({
              url: baseURL + (baseURL.indexOf('?') > -1 ? '&' : '?') +'is_embeddable=true' + self.extraEmbeddableURLParams(),
              beforeSend: function (xhr) {
                xhr.setRequestHeader('X-Requested-With', 'Hue');
              },
              dataType: 'html',
              success: function (response) {
                window.clearAppIntervals(app);
                huePubSub.clearAppSubscribers(app);
                self.extraEmbeddableURLParams('');
                var r = self.processHeaders(response);
                if (SKIP_CACHE.indexOf(app) === -1) {
                  self.embeddable_cache[app] = r;
                }
                $('#embeddable_' + app).html(r);
                self.isLoadingEmbeddable(false);
              },
              error: function () {
                page('/500');
              }
            });
          } else {
            self.isLoadingEmbeddable(false);
          }
          window.resumeAppIntervals(app);
          huePubSub.resumeAppSubscribers(app);
          $('.embeddable').hide();
          $('#embeddable_' + app).insertBefore($('.embeddable:first')).show();
          huePubSub.publish('app.gained.focus', app);
        };

        self.dropzoneError = function (filename) {
          self.loadApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(DropzoneGlobals.homeDir + '/' + filename);
          });
        };

        self.dropzoneComplete = function (path) {
          self.loadApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(path);
          });
        };

        // prepend /hue to all the link on this page
        $('a[href]').each(function () {
          var link = $(this).attr('href');
          if (link.startsWith('/') && !link.startsWith('/hue')){
            link = '/hue' + link;
          }
          $(this).attr('href', link);
        });

        page.base('/hue');

        var pageMapping = [
          { url: '/500', app: '500' },
          { url: '/about/', app: 'admin_wizard' },
          { url: '/about/admin_wizard', app: 'admin_wizard' },
          { url: '/accounts/logout', app: function () {
            location.href = '/accounts/logout';
          }},
          { url: '/dashboard/admin/collections', app: function (ctx) {
            page('/home?type=dashboard');
          }},
          { url: '/dashboard/*', app: 'dashboard' },
          { url: '/desktop/dump_config', app: 'dump_config' },
          { url: '/desktop/download_logs', app: function () {
            location.href = '/desktop/download_logs';
          }},
          { url: '/editor', app: function () {
            // Defer to allow window.location param update
            _.defer(function () {
              self.loadApp('editor');
              if (window.location.getParameter('editor') !== '') {
                self.getActiveAppViewModel(function (viewModel) {
                  viewModel.openNotebook(window.location.getParameter('editor'));
                });
              } else if (window.location.getParameter('type') !== '') {
                self.changeEditorType(window.location.getParameter('type'));
              }
            });
          }},
          { url: '/notebook/editor', app: function (ctx) {
            page('/editor?' + ctx.querystring);
          }},
          { url: '/filebrowser/view=*', app:  'filebrowser' },
          { url: '/filebrowser/*', app: function () {
            page('/filebrowser/view=' + DropzoneGlobals.homeDir);
          }},
          { url: '/hbase/', app: 'hbase' },
          { url: '/help', app: 'help' },
          { url: '/home*', app: 'home' },
          { url: '/indexer/', app: 'indexes' },
          { url: '/indexer/importer/', app: 'importer' },
          { url: '/indexer/importer/prefill/*', app: function (ctx) {
            self.loadApp('importer');
            self.getActiveAppViewModel(function (viewModel) {
              var arguments = ctx.path.match(/\/indexer\/importer\/prefill\/?([^/]+)\/?([^/]+)\/?([^/]+)?/);
              if (! arguments) {
                console.warn('Could not match ' + href);
              }
              hueUtils.waitForVariable(viewModel.createWizard, function(){
                hueUtils.waitForVariable(viewModel.createWizard.prefill, function(){
                  viewModel.createWizard.prefill.source_type(arguments && arguments[1] ? arguments[1] : '');
                  viewModel.createWizard.prefill.target_type(arguments && arguments[2] ? arguments[2] : '');
                  viewModel.createWizard.prefill.target_path(arguments && arguments[3] ? arguments[3] : '');
                });
              });
            })
          }},
          { url: '/jobbrowser/jobs/job_*', app: function (ctx) {
            page.redirect('/jobbrowser#!id=application_' + _.trimRight(ctx.params[0], '/'));
          }},
          { url: '/jobbrowser*', app: function (ctx) {
            self.loadApp('jobbrowser');
            self.getActiveAppViewModel(function (viewModel) {
              hueUtils.waitForVariable(viewModel.selectInterface, function(){
                hueUtils.waitForVariable(viewModel.selectInterface, function(){
                  viewModel.load();
                });
              });
            });
          }},
          { url: '/logs', app: 'logs' },
          { url: '/metastore', app: function () {
            page('/metastore/tables');
          }},
          { url: '/metastore/*', app: 'metastore' },
          { url: '/notebook', app: function () {
            self.loadApp('notebook');
            if (window.location.getParameter('notebook') !== '') {
              self.getActiveAppViewModel(function (viewModel) {
                viewModel.openNotebook(window.location.getParameter('notebook'));
              });
            } else {
              self.getActiveAppViewModel(function (viewModel) {
                viewModel.newNotebook('notebook');
              });
            }
          }},
          { url: '/notebook/editor', app: function (ctx) {
            page('/notebook?' + ctx.querystring);
          }},
          { url: '/notebook/notebooks', app: function (ctx) {
            page('/home?' + ctx.querystring);
          }},
          { url: '/oozie/editor/bundle/list', app: function (ctx) {
            page('/home?type=oozie-bundle');
          }},
          { url: '/oozie/editor/bundle/*', app: 'oozie_bundle' },
          { url: '/oozie/editor/coordinator/list', app: function (ctx) {
            page('/home?type=oozie-coordinator');
          }},
          { url: '/oozie/editor/coordinator/*', app: 'oozie_coordinator' },
          { url: '/oozie/editor/workflow/list', app: function (ctx) {
            page('/home?type=oozie-workflow');
          }},
          { url: '/oozie/editor/workflow/*', app: 'oozie_workflow' },
          { url: '/oozie/list_oozie_info', app: 'oozie_info' },
          { url: '/oozie/list_oozie_sla', app: function() {
            page.redirect('/jobbrowser/#!slas');
          }},
          { url: '/pig', app: function () {
            self.loadApp('editor');
            self.changeEditorType('pig');
          }},
          { url: '/search/*', app: 'dashboard' },
          { url: '/security/hdfs', app: 'security_hdfs' },
          { url: '/security/hive', app: 'security_hive' },
          { url: '/security/hive2', app: 'security_hive2' },
          { url: '/security/solr', app: 'security_solr' },
          { url: '/security', app: 'security_hive' },
          { url: '/sqoop', app: 'sqoop' },
          { url: '/useradmin/configurations/', app: 'useradmin_configurations' },
          { url: '/useradmin/groups/', app: 'useradmin_groups' },
          { url: '/useradmin/groups/new', app: 'useradmin_newgroup' },
          { url: '/useradmin/groups/edit/:group', app: 'useradmin_editgroup' },
          { url: '/useradmin/permissions/', app: 'useradmin_permissions' },
          { url: '/useradmin/permissions/edit/*', app: 'useradmin_editpermission' },
          { url: '/useradmin/users/', app: 'useradmin_users' },
          { url: '/useradmin/users/add_ldap_users', app: 'useradmin_addldapusers' },
          { url: '/useradmin/users/add_ldap_groups', app: 'useradmin_addldapgroups' },
          { url: '/useradmin/users/edit/:user', app: 'useradmin_edituser' },
          { url: '/useradmin/users/new', app: 'useradmin_newuser' },
          { url: '/useradmin/users/', app: 'useradmin_users' },
          { url: '/useradmin', app: 'useradmin_users' },
        ];

        pageMapping.forEach(function (mapping) {
          page(mapping.url, _.isFunction(mapping.app) ? mapping.app : function (ctx) {
            self.currentContextParams(ctx.params);
            self.currentQueryString(ctx.querystring);
            self.loadApp(mapping.app);
          })
        });

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          page('/', function() {  page(clusterConfig['main_button_action'].page); });
          page('*', function (ctx) {
            console.error('Route not found', ctx);
            self.loadApp('404');
          });
          page({
            popstate: false
          });
        });

        huePubSub.subscribe('open.link', function (href) {
          if (href.startsWith('/') && !href.startsWith('/hue')){
            page('/hue' + href);
          } else {
            page(href);
          }
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
            huePubSub.publish('reposition.scroll.anchor.up');
            huePubSub.publish('nicescroll.resize');
          }, 0);
        });
        self.rightAssistAvailable = ko.observable(false);
        self.activeAppViewModel = ko.observable();

        huePubSub.subscribe('set.current.app.name', function (appName) {
          self.rightAssistAvailable(appName === 'editor' || appName === 'notebook');
        });
        huePubSub.publish('get.current.app.name');

        self.contextPanelVisible = ko.observable(false);
        self.sessionsAvailable = ko.observable(false);

        self.activeAppViewModel.subscribe(function (viewModel) {
          self.sessionsAvailable(typeof viewModel.selectedNotebook !== 'undefined');
        });

        huePubSub.subscribe('context.panel.visible', function (visible) {
          self.contextPanelVisible(visible);
        });

        huePubSub.subscribe('set.current.app.view.model', self.activeAppViewModel);
        huePubSub.publish('get.current.app.view.model');

        var previousVisibilityValues = {};
        huePubSub.subscribe('side.panels.hide', function(){
          previousVisibilityValues = {
            left: self.leftAssistVisible(),
            right: self.rightAssistVisible()
          }
          self.leftAssistVisible(false);
          self.rightAssistVisible(false);
        });

        huePubSub.subscribe('side.panels.show', function(){
          self.leftAssistVisible(previousVisibilityValues.left);
          self.rightAssistVisible(previousVisibilityValues.right);
        });

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

      function TopNavViewModel (onePageViewModel) {
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

        self.mainQuickCreateAction = ko.observable();
        self.quickCreateActions = ko.observableArray();

        self.hasJobBrowser = ko.observable(true);

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          if (clusterConfig && clusterConfig['main_button_action']) {
            var topApp = clusterConfig['main_button_action'];
            self.mainQuickCreateAction({
              displayName: topApp.type === 'hive' || topApp.type === 'impala' ? '${ _("Query") }' : topApp.displayName,
              icon: topApp.type,
              tooltip: topApp.tooltip,
              url: topApp.page
            });
          } else {
            self.mainQuickCreateAction(undefined);
          }

          if (clusterConfig && clusterConfig['button_actions']) {
            var apps = [];
            var buttonActions = clusterConfig['button_actions'];
              buttonActions.forEach(function(app) {
              var interpreters = [];
              $.each(app['interpreters'], function(index, interpreter) {
                interpreters.push({
                  displayName: interpreter.displayName,
                  % if SHOW_NOTEBOOKS.get():
                    dividerAbove: app.name === 'editor' && index === 1,
                  % endif
                  icon: interpreter.type,
                  url: interpreter.page
                });
              });

              % if user.is_superuser:
                if (app.name === 'editor') {
                  interpreters.push({
                    displayName: '${ _('Add more...') }',
                    dividerAbove: true,
                    click: function () {
                      window.open('http://gethue.com/sql-editor/', '_blank');
                    }
                  });
                }
              % endif

              apps.push({
                displayName: app.displayName,
                icon: app.name,
                isCategory: interpreters.length > 0,
                children: interpreters,
                url: app.page
              });
            });

            self.quickCreateActions(apps);
          } else {
            self.quickCreateActions([]);
          }

          self.hasJobBrowser(clusterConfig && clusterConfig['app_config'] && clusterConfig['app_config']['browser']);
        });

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

      TopNavViewModel.prototype.performSearch = function () { };

      var topNavViewModel = new TopNavViewModel(onePageViewModel);
      ko.applyBindings(topNavViewModel, $('.top-nav')[0]);

      return topNavViewModel;
    })(onePageViewModel);


    (function (onePageViewModel, topNavViewModel) {

      function SideBarViewModel (onePageViewModel, topNavViewModel) {
        var self = this;

        self.items = ko.observableArray();

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          var items = [];

          if (clusterConfig && clusterConfig['app_config']) {
            var appsItems = [];
            var appConfig = clusterConfig['app_config'];
            ['editor', 'dashboard', 'scheduler'].forEach(function(appName) {
              if (appConfig[appName]) {
                appsItems.push({
                  displayName: appConfig[appName]['displayName'],
                  url: appConfig[appName]['page'],
                  icon: appName
                });
              }
            });
            if (appsItems.length > 0) {
              items.push({
                isCategory: true,
                displayName: '${ _('Apps') }',
                children: appsItems
              })
            }

            var browserItems = [];
            browserItems.push({
              displayName: '${ _('Documents') }',
              url: '/home',
              icon: 'documents'
            });
            if (appConfig['browser'] && appConfig['browser']['interpreters']) {
              appConfig['browser']['interpreters'].forEach(function(browser) {
                browserItems.push({
                  displayName: browser.displayName,
                  url: browser.page,
                  icon: browser.type
                });
              });
            }
            if (browserItems.length > 0) {
              items.push({
                isCategory: true,
                displayName: '${ _('Browsers') }',
                children: browserItems
              })
            }

            var sdkItems = [];
            if (appConfig['sdkapps'] && appConfig['sdkapps']['interpreters']) {
              appConfig['sdkapps']['interpreters'].forEach(function(browser) {
                sdkItems.push({
                  displayName: browser['displayName'],
                  url: browser['page']
                });
              });
            }
            if (sdkItems.length > 0) {
              items.push({
                isCategory: true,
                displayName: appConfig['sdkapps']['displayName'],
                children: sdkItems
              })
            }
          }

          self.items(items);
        });

        self.leftNavVisible = topNavViewModel.leftNavVisible;
        self.onePageViewModel = onePageViewModel;
      }

      var sidebarViewModel = new SideBarViewModel(onePageViewModel, topNavViewModel);
      ko.applyBindings(sidebarViewModel, $('.sidebar')[0]);
    })(onePageViewModel, topNavViewModel);

    huePubSub.publish('cluster.config.get.config');

    $(document).on('hideHistoryModal', function (e) {
      $('#clearNotificationHistoryModal').modal('hide');
    });

    var hideJobsPanels = function (e) {
      if ($(e.target).closest('.jobs-panel').length === 0 && $(e.target).closest('.btn-toggle-jobs-panel').length === 0 && $('.jobs-panel').is(':visible')) {
        huePubSub.publish('hide.jobs.panel');
        huePubSub.publish('hide.history.panel');
      }
    }

    var clickThrottle = -1;
    $(window).click(function (e) {
      window.clearTimeout(clickThrottle);
      clickThrottle = window.setTimeout(function () {
        hideJobsPanels(e);
      }, 10);
    });

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
