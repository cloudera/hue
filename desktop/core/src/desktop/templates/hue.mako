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
  from desktop.conf import IS_EMBEDDED
  from desktop.conf import DEV_EMBEDDED
  from desktop.views import _ko, commonshare, login_modal
  from desktop.lib.i18n import smart_unicode
  from desktop.models import PREFERENCE_IS_WELCOME_TOUR_SEEN, ANALYTIC_DB

  from dashboard.conf import IS_ENABLED as IS_DASHBOARD_ENABLED
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_optimizer, OPTIMIZER
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

% if DEV_EMBEDDED.get():
  <style>
    html {
      height: 100%;
      width: 100%;
      margin: 0;
      font-size: 1em;
    }

    body {
      position: relative;
      height: 100%;
      width: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background-color: pink;
    }

    .hue-embedded-container {
      position: absolute !important;
      top: 60px !important;
      left: 60px !important;
      bottom: 60px !important;
      right: 60px !important;
    }
  </style>
% endif

  <link href="${ static('desktop/css/roboto.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
% if IS_EMBEDDED.get():
  <link href="${ static('desktop/css/hue-bootstrap-embedded.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue-embedded.css') }" rel="stylesheet">
% else:
  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/jquery-ui.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/home.css') }" rel="stylesheet">
% endif
  <script type="text/javascript">
    window.IS_HUE_4 = true;
  </script>

  ${ commonHeaderFooterComponents.header_i18n_redirection() }

  <script src="/desktop/globalJsConstants.js"></script>

  % if not conf.DEV.get():
  <script src="${ static('desktop/js/hue.errorcatcher.js') }"></script>
  % endif
  <script src="${ static('desktop/js/hue4.utils.js') }"></script>
</head>

<body>

% if IS_EMBEDDED.get():
<div class="hue-embedded-container">
% endif

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
  % if banner_message or conf.CUSTOM.BANNER_TOP_HTML.get():
    <div class="banner">
      ${ banner_message or conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
    </div>
  % endif
  <nav class="navbar ${ '' if IS_EMBEDDED.get() else 'navbar-default' }">
    <div class="navbar-inner top-nav">
      <div class="top-nav-left">
        % if not IS_EMBEDDED.get():
        <a class="hamburger hamburger-hue pull-left" data-bind="toggle: leftNavVisible, css: { 'is-active': leftNavVisible }">
          <span class="hamburger-box"><span class="hamburger-inner"></span></span>
        </a>

        <a class="brand" data-bind="hueLink: '/home/'" href="javascript: void(0);" title="${_('Documents')}">
          <svg style="height: 24px; width: 120px;"><use xlink:href="#hi-logo"></use></svg>
        </a>
        % endif

        <div class="btn-group" data-bind="visible: true" style="display:none; margin-top: 8px">
          <!-- ko if: mainQuickCreateAction -->
          <!-- ko with: mainQuickCreateAction -->
          <a class="btn btn-primary disable-feedback hue-main-create-btn" data-bind="hueLink: url, attr: {title: tooltip}, style: { borderBottomRightRadius: $parent.quickCreateActions().length > 1 ? '0px' : '4px', borderTopRightRadius: $parent.quickCreateActions().length > 1 ? '0px' : '4px' }">
            <span data-bind="text: displayName"></span>
          </a>
          <!-- /ko -->
          <!-- /ko -->
          <button class="btn btn-primary dropdown-toggle hue-main-create-btn-dropdown" data-toggle="dropdown" data-bind="visible: quickCreateActions().length > 1 || (quickCreateActions().length == 1 && quickCreateActions()[0].children && quickCreateActions()[0].children.length > 1)">
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
          <li data-bind="css: { 'dropdown-submenu': item.isCategory && item.children.length > 1 }">
            <!-- ko if: item.url -->
             <a href="javascript: void(0);" data-bind="hueLink: item.url">
                <!-- ko if: item.icon -->
                <!-- ko template: { name: 'app-icon-template', data: item } --><!-- /ko -->
                <!-- /ko -->
                <span data-bind="css: { 'dropdown-no-icon': !item.icon }, text: item.displayName"></span>
              </a>
            <!-- /ko -->
            <!-- ko if: item.href -->
              <a data-bind="attr: { href: item.href }, text: item.displayName" target="_blank"></a>
            <!-- /ko -->
            <!-- ko if: item.isCategory && item.children.length > 1 -->
            <ul class="dropdown-menu" data-bind="foreach: { data: item.children, as: 'item' }">
              <!-- ko template: 'quick-create-item-template' --><!-- /ko -->
            </ul>
            <!-- /ko -->
          </li>
        </script>
      </div>


      <div class="top-nav-middle">

        <!-- ko if: cluster.clusters().length > 1 && cluster.clusters()[0].type() != ANALYTIC_DB -->
        <div class="btn-group pull-right" style="display: none;" data-bind="visible: cluster.clusters().length > 1">
          <button class="btn" data-bind="text: cluster.cluster().name() + (cluster.cluster().interface ? ' ' + cluster.cluster().interface() : '')"></button>
          <button class="btn dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
          </button>

          <ul class="dropdown-menu">
            <!-- ko foreach: cluster.clusters -->
              <!-- ko if: ['dataeng', 'cm'].indexOf(type()) != -1 && interfaces().length > 0 -->
                <li class="dropdown-submenu">
                  <a data-rel="navigator-tooltip" href="javascript: void(0)">
                    <i class="fa fa-fw fa-th-large inline-block"></i> <span data-bind="text: name"></span>
                  </a>
                  <ul class="dropdown-menu">
                    <li data-bind="visible: type() == 'dataeng'">
                      <a data-rel="navigator-tooltip" href="#">
                        <span class="dropdown-no-icon"><i class="fa fa-fw fa-plus inline-block"></i></span>
                      </a>
                    </li>
                    <!-- ko foreach: interfaces -->
                      <li>
                        <a href="javascript: void(0)" data-bind="click: function() { $root.cluster.cluster($data) }">
                          <span class="dropdown-no-icon" data-bind="text: interface"></span>
                        </a>
                      </li>
                    <!-- /ko -->
                  </ul>
                </li>
                <!-- /ko -->
                <!-- ko if: ['dataeng', 'cm'].indexOf(type()) == -1 || interfaces().length == 0 -->
                  <li><a href="javascript: void(0)" data-bind="click: function(){  $root.cluster.cluster($data) }">
                    <i class="fa fa-fw fa-square"></i> <span data-bind="text: name"></span></a>
                  </li>
                <!-- /ko -->
              <!-- /ko -->
            <!-- /ko -->
          </ul>
        </div>
        <!-- /ko -->

        <div class="search-container-top" data-bind="component: 'hue-global-search'"></div>
      </div>

      <div class="top-nav-right">

        % if user.is_authenticated() and section != 'login' and cluster != ANALYTIC_DB:
        <div class="dropdown navbar-dropdown pull-right">
          <%
            view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or user.is_superuser
          %>
          <button class="btn btn-flat" data-toggle="dropdown" data-bind="click: function(){ huePubSub.publish('hide.jobs.panel'); huePubSub.publish('hide.history.panel'); }">
            <i class="fa fa-user"></i> ${ user.username } <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            % if view_profile:
            <li><a href="javascript:void(0)" data-bind="hueLink: '/useradmin/users/edit/${ user.username }'" title="${ _('View Profile') if is_ldap_setup else _('Edit Profile') }"><i class="fa fa-fw fa-user"></i> ${_('My Profile')}</a></li>
            % endif
            % if user.is_superuser:
            <li data-bind="hueLink: '/useradmin/users/'"><a href="javascript: void(0);"><i class="fa fa-fw fa-group"></i> ${_('Manage Users')}</a></li>
            % endif
            % if not conf.DISABLE_HUE_3.get():
            <li><a href="javascript:void(0)" onclick="huePubSub.publish('set.hue.version', 3)"><i class="fa fa-fw fa-exchange"></i> ${_('Switch to Hue 3')}</a></li>
            % endif
            <li><a href="http://gethue.com" target="_blank"><span class="dropdown-no-icon">${_('Help')}</span></a></li>
            <li><a href="javascript:void(0)" onclick="huePubSub.publish('show.welcome.tour')"><span class="dropdown-no-icon">${_('Welcome Tour')}</span></a></li>
            % if user.is_superuser:
            <li><a href="/about/"><span class="dropdown-no-icon">${_('Hue Administration')}</span></a></li>
            % endif
            <li class="divider"></li>
            <li><a title="${_('Sign out')}" href="/accounts/logout/"><i class="fa fa-fw fa-sign-out"></i> ${ _('Sign out') }</a></li>
          </ul>
        </div>
        % endif

        <!-- ko component: 'hue-history-panel' --><!-- /ko -->
        <!-- ko if: hasJobBrowser -->
          <!-- ko component: { name: 'hue-job-browser-links', params: { onePageViewModel: onePageViewModel }} --><!-- /ko -->
        <!-- /ko -->
      </div>

    </div>
  </nav>

  <div id="jobsPanel" class="jobs-panel" style="display: none;">
    <a class="pointer inactive-action pull-right" onclick="huePubSub.publish('hide.jobs.panel')"><i class="fa fa-fw fa-times"></i></a>
    <a class="pointer inactive-action pull-right" onclick="huePubSub.publish('mini.jb.expand'); huePubSub.publish('hide.jobs.panel')"><i class="fa fa-fw fa-expand" title="${ _('Open Job Browser') }"></i></a>
    <ul class="nav nav-pills">
      % if cluster != ANALYTIC_DB:
      <li class="active" data-interface="jobs"><a href="javascript:void(0)" onclick="huePubSub.publish('mini.jb.navigate', 'jobs')">${_('Jobs')}</a></li>
      % endif
      % if 'jobbrowser' in apps:
      <% from jobbrowser.conf import ENABLE_QUERY_BROWSER %>
      % if ENABLE_QUERY_BROWSER.get():
        <li data-interface="queries" class="${ 'active' if cluster == ANALYTIC_DB else '' }"><a href="javascript:void(0)" onclick="huePubSub.publish('mini.jb.navigate', 'queries')">${_('Queries')}</a></li>
      % endif
      % endif
      % if cluster != ANALYTIC_DB:
        <li data-interface="workflows"><a href="javascript:void(0)" onclick="huePubSub.publish('mini.jb.navigate', 'workflows')">${_('Workflows')}</a></li>
        <li data-interface="schedules"><a href="javascript:void(0)" onclick="huePubSub.publish('mini.jb.navigate', 'schedules')">${_('Schedules')}</a></li>
      % endif
    </ul>
    <div id="mini_jobbrowser"></div>
  </div>

  <div class="content-wrapper">

    <script type="text/html" id="hue-tmpl-sidebar-link">
      <a role="button" class="hue-sidebar-item" data-bind="hueLink: item.url, attr: { title: item.displayName }">
        <span class="hue-sidebar-item-name" data-bind="text: item.displayName"></span>
      </a>
    </script>

    <div class="hue-sidebar hue-sidebar-below-top-bar" data-bind="visible: leftNavVisible" style="display:none;">
      <div class="hue-sidebar-content">
        <!-- ko foreach: {data: items, as: 'item'} -->
          <!-- ko if: item.isCategory -->
             <h4 class="hue-sidebar-category-item" data-bind="text: item.displayName"></h4>
             <!-- ko template: {name: 'hue-tmpl-sidebar-link', foreach: item.children, as: 'item'} --><!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: item.isCategory -->
             <!-- ko template: { name: 'hue-tmpl-sidebar-link' } --><!-- /ko -->
          <!-- /ko -->
        <!-- /ko -->
      </div>
      <div class="hue-sidebar-footer-panel">
        <div data-bind="dropzone: {
            clickable: false,
            url: '/filebrowser/upload/file?dest=' + DROPZONE_HOME_DIR,
            params: { dest: DROPZONE_HOME_DIR },
            paramName: 'hdfs_file',
            onError: onePageViewModel.dropzoneError,
            onComplete: onePageViewModel.dropzoneComplete },
            click: function(){ page('/indexer/importer/') }" class="pointer" title="${ _('Import data wizard') }">
          <div class="dz-message" data-dz-message><i class="fa fa-fw fa-cloud-upload"></i> ${ _('Click or Drop files here') }</div>
        </div>
      </div>
    </div>

    <div class="left-panel" data-bind="css: { 'side-panel-closed': !leftAssistVisible() }, visibleOnHover: { selector: '.hide-left-side-panel' }">
      <a href="javascript:void(0);" style="z-index: 1000; display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-left-side-panel" data-bind="visible: ! leftAssistVisible(), toggle: leftAssistVisible"><i class="fa fa-chevron-right"></i></a>
      <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-left-side-panel" data-bind="visible: leftAssistVisible, toggle: leftAssistVisible"><i class="fa fa-chevron-left"></i></a>
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
        }, visible: leftAssistVisible" style="display:none;"></div>
    </div>

    <div id="leftResizer" class="resizer" data-bind="visible: leftAssistVisible(), splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.left-panel',
      sidePanelVisible: leftAssistVisible,
      orientation: 'left',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }"><div class="resize-bar"></div></div>


    <div class="page-content">
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
      <div id="embeddable_threads" class="embeddable"></div>
      <div id="embeddable_metrics" class="embeddable"></div>
      <div id="embeddable_403" class="embeddable"></div>
      <div id="embeddable_404" class="embeddable"></div>
      <div id="embeddable_500" class="embeddable"></div>
      <div id="embeddable_sqoop" class="embeddable"></div>
      <div id="embeddable_jobsub" class="embeddable"></div>
      % if other_apps:
        % for other in other_apps:
          <div id="embeddable_${ other.display_name }" class="embeddable"></div>
        % endfor
      % endif
    </div>

    <div id="rightResizer" class="resizer" data-bind="visible: rightAssistVisible() && rightAssistAvailable(), splitFlexDraggable : {
      containerSelector: '.content-wrapper',
      sidePanelSelector: '.right-panel',
      sidePanelVisible: rightAssistVisible,
      orientation: 'right',
      onPosition: function() { huePubSub.publish('split.draggable.position') }
    }"><div class="resize-bar" style="right: 0">&nbsp;</div></div>

    <div class="right-panel side-panel-closed" data-bind="visible: rightAssistAvailable, css: { 'side-panel-closed': !rightAssistVisible() || !rightAssistAvailable() }, visibleOnHover: { selector: '.hide-right-side-panel' }" style="display:none;">
      <a href="javascript:void(0);" style="display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-right-side-panel" data-bind="visible: rightAssistAvailable() && !rightAssistVisible(), toggle: rightAssistVisible"><i class="fa fa-chevron-left"></i></a>
      <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-right-side-panel" data-bind="visible: rightAssistAvailable() && rightAssistVisible(), toggle: rightAssistVisible"><i class="fa fa-chevron-right"></i></a>

      <div class="assist" data-bind="component: {
          name: 'right-assist-panel',
          params: {
            rightAssistAvailable: rightAssistAvailable
          }
        }, visible: rightAssistAvailable() && rightAssistVisible()" style="display: none;">
      </div>
    </div>

    <div class="context-panel" data-bind="slideVisible: contextPanelVisible">
      <div class="margin-top-10 padding-left-10 padding-right-10">
        <h4 class="margin-bottom-30"><i class="fa fa-cogs"></i> ${_('Session')}</h4>
        <div class="context-panel-content">
          <!-- ko if: sessionsAvailable() && templateApp() -->
          <div class="row-fluid">
            <div class="span11" data-bind="template: { name: 'notebook-session-config-template' + templateApp(), data: activeAppViewModel }"></div>
          </div>
          <!-- /ko -->

          <!-- ko ifnot: sessionsAvailable() && templateApp() -->
          ${_('There are currently no information about the sessions.')}
          <!-- /ko -->
        </div>
      </div>
      <a class="pointer demi-modal-chevron" style="position: absolute; bottom: 0" data-bind="click: function () { huePubSub.publish('context.panel.visible.editor', false); }"><i class="fa fa-chevron-up"></i></a>
    </div>
  </div>
</div>

${ commonshare() | n,unicode }

<script src="${ static('desktop/js/hue-bundle.js') }"></script>
% if IS_EMBEDDED.get():
<script src="${ static('desktop/ext/js/page.js') }"></script>
% endif

<script src="${ static('desktop/js/jquery.migration.js') }"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
<script src="${ static('desktop/ext/js/tether.js') }"></script>
<script src="${ static('desktop/ext/js/shepherd.min.js') }"></script>
<script src="${ static('desktop/js/bootstrap-tooltip.js') }"></script>
<script src="${ static('desktop/js/bootstrap-typeahead-touchscreen.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>
<script src="${ static('desktop/ext/js/fileuploader.js') }"></script>
<script src="${ static('desktop/ext/js/filesize.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/tzdetect.js') }" type="text/javascript" charset="utf-8"></script>
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
% if IS_EMBEDDED.get():
<script src="${ static('desktop/js/jquery.tableextender3.js') }"></script>
% else:
<script src="${ static('desktop/js/jquery.tableextender2.js') }"></script>
% endif
<script src="${ static('desktop/js/hue.colors.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
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
<script>
  ace.config.set("basePath", "/static/desktop/js/ace");
</script>

<script src="${ static('desktop/ext/js/dropzone.min.js') }"></script>

<script src="${ static('desktop/js/autocomplete/sqlParseSupport.js') }"></script>
<script src="${ static('desktop/js/autocomplete/sqlAutocompleteParser.js') }"></script>
<script src="${ static('desktop/js/autocomplete/globalSearchParser.js') }"></script>
<script src="${ static('desktop/js/autocomplete/solrQueryParser.js') }"></script>
<script src="${ static('desktop/js/autocomplete/solrFormulaParser.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter2.js') }"></script>
<script src="${ static('desktop/js/sqlAutocompleter3.js') }"></script>
<script src="${ static('desktop/js/hdfsAutocompleter.js') }"></script>
<script src="${ static('desktop/js/autocompleter.js') }"></script>
<script src="${ static('desktop/js/hue.json.js') }"></script>
<script src="${ static('notebook/js/notebook.ko.js') }"></script>
<script src="${ static('metastore/js/metastore.model.js') }"></script>

<script src="${ static('desktop/js/share2.vm.js') }"></script>
<script>
  var shareViewModel = initSharing("#documentShareModal");
</script>

<%namespace name="charting" file="/charting.mako" />
<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />

${ charting.import_charts() }
${ configKoComponents.config() }
${ notebookKoComponents.aceKeyboardShortcuts() }
${ notebookKoComponents.downloadSnippetResults() }
${ hueAceAutocompleter.hueAceAutocompleter() }


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

## clusterConfig makes an Ajax call so it needs to be after commonHeaderFooterComponents
<script src="${ static('desktop/js/clusterConfig.js') }"></script>

${ assist.assistJSModels() }
${ assist.assistPanel() }

% if request is not None:
${ smart_unicode(login_modal(request).content) | n,unicode }
% endif

<div class="shepherd-backdrop"></div>

<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

<script type="text/javascript">

  $(document).ready(function () {

    var onePageViewModel = (function () {

      var EMBEDDABLE_PAGE_URLS = {
        403: { url: '/403', title: '403' },
        404: { url: '/404', title: '404' },
        500: { url: '/500', title: '500' },
        editor: { url: '/editor', title: '${_('Editor')}' },
        notebook: { url: '/notebook', title: '${_('Notebook')}' },
        metastore: { url: '/metastore/*', title: '${_('Table Browser')}' },
        dashboard: { url: '/dashboard/*', title: '${_('Dashboard')}' },
        oozie_workflow: { url: '/oozie/editor/workflow/*', title: '${_('Workflow')}' },
        oozie_coordinator: { url: '/oozie/editor/coordinator/*', title: '${_('Schedule')}' },
        oozie_bundle: { url: '/oozie/editor/bundle/*', title: '${_('Bundle')}' },
        oozie_info: { url: '/oozie/list_oozie_info', title: '${_('Oozie')}' },
        jobbrowser: { url: '/jobbrowser/apps', title: '${_('Job Browser')}' },
        filebrowser: { url: '/filebrowser/view=*', title: '${_('File Browser')}' },
        home: { url: '/home*', title: '${_('Home')}' },
        indexer: { url: '/indexer/indexer/', title: '${_('Indexer')}' },
        collections: { url: '/dashboard/admin/collections', title: '${_('Search')}' },
        % if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
        indexes: { url: '/indexer/indexes/*', title: '${_('Indexes')}' },
        % else:
        indexes: { url: '/indexer/', title: '${_('Indexes')}' },
        % endif
        importer: { url: '/indexer/importer/', title: '${_('Importer')}' },
        useradmin_users: { url: '/useradmin/users', title: '${_('User Admin - Users')}' },
        useradmin_groups: { url: '/useradmin/groups', title: '${_('User Admin - Groups')}' },
        useradmin_newgroup: { url: '/useradmin/groups/new', title: '${_('User Admin - New Group')}' },
        useradmin_editgroup: { url: '/useradmin/groups/edit/:group', title: '${_('User Admin - Edit Group')}' },
        useradmin_permissions: { url: '/useradmin/permissions', title: '${_('User Admin - Permissions')}' },
        useradmin_editpermission: { url: '/useradmin/permissions/edit/*', title: '${_('User Admin - Edit Permission')}' },
        useradmin_configurations: { url: '/useradmin/configurations', title: '${_('User Admin - Configurations')}' },
        useradmin_newuser: { url: '/useradmin/users/new', title: '${_('User Admin - New User')}' },
        useradmin_addldapusers: { url: '/useradmin/users/add_ldap_users', title: '${_('User Admin - Add LDAP User')}' },
        useradmin_edituser: { url: '/useradmin/users/edit/:user', title: '${_('User Admin - Edit User')}' },
        useradmin_addldapgroups: { url: '/useradmin/users/add_ldap_groups', title: '${_('User Admin - Add LDAP Groups')}' },
        hbase: { url: '/hbase/', title: '${_('HBase Browser')}' },
        security_hive: { url: '/security/hive', title: '${_('Security - Hive')}' },
        security_hdfs: { url: '/security/hdfs', title: '${_('Security - HDFS')}' },
        security_hive2: { url: '/security/hive2', title: '${_('Security - Hive')}' },
        security_solr: { url: '/security/solr', title: '${_('Security - SOLR')}' },
        help: { url: '/help/', title: '${_('Help')}' },
        admin_wizard: { url: '/about/admin_wizard', title: '${_('Admin Wizard')}' },
        logs: { url: '/logs', title: '${_('Logs')}' },
        dump_config: { url: '/desktop/dump_config', title: '${_('Dump Configuration')}' },
        threads: { url: '/desktop/debug/threads', title: '${_('Threads')}' },
        metrics: { url: '/desktop/metrics', title: '${_('Metrics')}' },
        sqoop: { url: '/sqoop', title: '${_('Sqoop')}' },
        jobsub: { url: '/jobsub/not_available', title: '${_('Job Designer')}' },
        % if other_apps:
          % for other in other_apps:
            ${ other.display_name }: { url: '/${ other.display_name }', title: '${ other.nice_name }' },
          % endfor
        % endif
      };

      var SKIP_CACHE = [
          'home', 'oozie_workflow', 'oozie_coordinator', 'oozie_bundle', 'dashboard', 'metastore',
          'filebrowser', 'useradmin_users', 'useradmin_groups', 'useradmin_newgroup', 'useradmin_editgroup',
          'useradmin_permissions', 'useradmin_editpermission', 'useradmin_configurations', 'useradmin_newuser',
          'useradmin_addldapusers', 'useradmin_addldapgroups', 'useradmin_edituser', 'importer',
          'security_hive', 'security_hdfs', 'security_hive2', 'security_solr', 'logs',
          % if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
            'indexes',
          % endif
          % if other_apps:
            % for other in other_apps:
              '${ other.display_name }',
            % endfor
          % endif
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

        huePubSub.subscribe('resize.form.actions', function () {
          document.styleSheets[0].addRule('.form-actions','width: ' + $('.page-content').width() + 'px');
          if ($('.content-panel:visible').length > 0) {
            document.styleSheets[0].addRule('.form-actions','margin-left: -11px !important');
          }
        });

        huePubSub.subscribe('split.panel.resized', function() {
          huePubSub.publish('resize.form.actions');
          huePubSub.publish('resize.plotly.chart');
        });

        huePubSub.publish('resize.form.actions');


        huePubSub.subscribe('open.editor.new.query', function (statementOptions) {
          self.loadApp('editor'); // Should open in Default

          self.getActiveAppViewModel(function (viewModel) {
            var editorType = statementOptions['type'] || 'hive'; // Next: use file extensions and default type of Editor for SQL
            viewModel.newNotebook(editorType, function() {
              self.changeEditorType(editorType);

              if (statementOptions['statementPath']) {
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

        huePubSub.subscribe('hue4.add.global.js', function ($el) {
          var jsFile = $el.attr('src').split('?')[0];
          if (loadedJs.indexOf(jsFile) === -1) {
            loadedJs.push(jsFile);
            $.ajaxSetup({ cache: true });
            $el.clone().appendTo($('head'));
            $.ajaxSetup({ cache: false });
          }
          $el.remove();
        });

        huePubSub.subscribe('hue4.add.global.css', function ($el) {
          var cssFile = $el.attr('href').split('?')[0];
          if (loadedCss.indexOf(cssFile) === -1) {
            loadedCss.push(cssFile);
            $.ajaxSetup({ cache: true });
            $el.clone().appendTo($('head'));
            $.ajaxSetup({ cache: false });
          }
          $el.remove();
        });

        huePubSub.subscribe('hue4.get.globals', function(callback){
          callback(loadedJs, loadedCss);
        });

        // Only load CSS and JS files that are not loaded before
        self.processHeaders = function(response){
          var r = $('<span>').html(response);
          % if conf.DEV.get():
          r.find('link').each(function () {
            $(this).attr('href', $(this).attr('href') + '?' + Math.random())
          });
          r.find('script[src]').each(function () {
            $(this).attr('src', $(this).attr('src') + '?' + Math.random())
          });
          % endif
          r.find('script[src]').each(function () {
            huePubSub.publish('hue4.add.global.js', $(this));
          });
          r.find('link[href]').each(function () {
            huePubSub.publish('hue4.add.global.css', $(this));
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

        huePubSub.subscribe('hue4.process.headers', function(opts){
          opts.callback(self.processHeaders(opts.response));
        });

        self.loadApp = function(app, loadDeep) {
          if (self.currentApp() == 'editor' && $('#editorComponents').length) {
            var vm = ko.dataFor($('#editorComponents')[0]);
            if (vm.isPresentationMode()) {
              vm.isPresentationMode(false);
            }
          }

          self.currentApp(app);
          if (!app.startsWith('security')) {
            self.lastContext = null;
          }
          SKIP_CACHE.forEach(function (skipped) {
            $('#embeddable_' + skipped).html('');
          });
          self.isLoadingEmbeddable(true);
          loadedApps.forEach(function (loadedApp) {
            window.pauseAppIntervals(loadedApp);
            huePubSub.pauseAppSubscribers(loadedApp);
          });
          $('.tooltip').hide();
          huePubSub.publish('hue.datatable.search.hide');
          huePubSub.publish('nicescroll.resize');
          huePubSub.publish('hue.scrollleft.hide');
          huePubSub.publish('context.panel.visible', false);
          huePubSub.publish('context.panel.visible.editor', false);
          if (app === 'filebrowser') {
            $(window).unbind('hashchange.fblist');
          }
          if (app.startsWith('oozie')) {
            huePubSub.clearAppSubscribers('oozie');
          }
          if (app.startsWith('security')) {
            $('#embeddable_security_hive').html('');
            $('#embeddable_security_hdfs').html('');
            $('#embeddable_security_hive2').html('');
            $('#embeddable_security_solr').html('');
          }
          if (typeof self.embeddable_cache[app] === 'undefined') {
            if (loadedApps.indexOf(app) == -1){
              loadedApps.push(app);
            }
            var baseURL = EMBEDDABLE_PAGE_URLS[app].url;
            if (self.currentContextParams() !== null) {
              if (loadDeep && self.currentContextParams()[0]) {
                baseURL += self.currentContextParams()[0];
              }
              else {
                var route = new page.Route(baseURL);
                route.keys.forEach(function (key) {
                  if (key.name === 0) {
                    if (typeof self.currentContextParams()[key.name] !== 'undefined') {
                      baseURL = baseURL.replace('*', self.currentContextParams()[key.name]);
                    }
                    else {
                      baseURL = baseURL.replace('*', '');
                    }
                  }
                  else {
                    baseURL = baseURL.replace(':' + key.name, self.currentContextParams()[key.name]);
                  }
                });
              }
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
              success: function(response, status, xhr){
                var type = xhr.getResponseHeader('Content-Type');
                if (type.indexOf('text/') > -1) {
                  window.clearAppIntervals(app);
                  huePubSub.clearAppSubscribers(app);
                  self.extraEmbeddableURLParams('');
                  var r = self.processHeaders(response);
                  if (SKIP_CACHE.indexOf(app) === -1) {
                    self.embeddable_cache[app] = r;
                  }
                  $('#embeddable_' + app).html(r);
                  huePubSub.publish('app.dom.loaded', app);
                }
                else {
                  window.location.href = baseURL;
                }
                self.isLoadingEmbeddable(false);
              },
              error: function (xhr) {
                console.error('Route loading problem', xhr);
                if ((xhr.status === 401 || xhr.status === 403) && app !== '403') {
                  self.loadApp('403');
                }
                else if (app !== '500') {
                  self.loadApp('500');
                }
                else {
                  $.jHueNotify.error("${ _('It looks like you are offline or an unknown error happened. Please refresh the page.') }")
                }
              }
            });
          } else {
            self.isLoadingEmbeddable(false);
          }
          window.document.title = 'Hue - ' + EMBEDDABLE_PAGE_URLS[app].title;
          window.resumeAppIntervals(app);
          huePubSub.resumeAppSubscribers(app);
          $('.embeddable').hide();
          $('#embeddable_' + app).show();
          huePubSub.publish('app.gained.focus', app);
          huePubSub.publish('resize.form.actions');
        };

        self.dropzoneError = function (filename) {
          self.loadApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(DROPZONE_HOME_DIR + '/' + filename);
          });
          $('.dz-drag-hover').removeClass('dz-drag-hover');
        };

        var openImporter = function (path) {
          self.loadApp('importer');
          self.getActiveAppViewModel(function (vm) {
            vm.createWizard.source.path(path);
          });
        };

        self.dropzoneComplete = function (path) {
          if (path.toLowerCase().endsWith('.csv')){
            openImporter(path);
          }
          else {
            huePubSub.publish('open.link', '/filebrowser/view=' + path);
          }
          $('.dz-drag-hover').removeClass('dz-drag-hover');
        };

        huePubSub.subscribe('open.in.importer', openImporter);

        // prepend /hue to all the link on this page
        $('a[href]').each(function () {
          var link = $(this).attr('href');
          if (link.startsWith('/') && !link.startsWith('/hue')){
            link = '/hue' + link;
          }
          $(this).attr('href', link);
        });

        page.base(typeof HUE_EMBEDDED_BASE_URL !== 'undefined' ? HUE_EMBEDDED_BASE_URL : '/hue');

        self.lastContext = null;

        var pageMapping = [
          { url: '/403', app: '403' },
          { url: '/500', app: '500' },
          { url: '/about/', app: 'admin_wizard' },
          { url: '/about/admin_wizard', app: 'admin_wizard' },
          { url: '/accounts/logout', app: function () {
            location.href = '/accounts/logout';
          }},
          { url: '/dashboard/admin/collections', app: function (ctx) {
            page('/home/?type=search-dashboard');
          }},
          { url: '/dashboard/*', app: 'dashboard' },
          { url: '/desktop/dump_config', app: 'dump_config' },
          { url: '/desktop/debug/threads', app: 'threads' },
          { url: '/desktop/metrics', app: 'metrics' },
          { url: '/desktop/download_logs', app: function () {
            location.href = '/desktop/download_logs';
          }},
          { url: '/editor', app: function () {
            // Defer to allow window.location param update
            _.defer(function () {
              if (typeof self.embeddable_cache['editor'] === 'undefined'){
                if (window.location.getParameter('editor') !== '') {
                  self.extraEmbeddableURLParams('&editor=' + window.location.getParameter('editor'));
                } else if (window.location.getParameter('type') !== '' && window.location.getParameter('type') !== 'notebook') {
                  self.extraEmbeddableURLParams('&type=' + window.location.getParameter('type'));
                }
                self.loadApp('editor');
              } else {
                self.loadApp('editor');
                if (window.location.getParameter('editor') !== '') {
                  self.getActiveAppViewModel(function (viewModel) {
                    viewModel.openNotebook(window.location.getParameter('editor'));
                  });
                } else if (window.location.getParameter('type') !== '') {
                  self.changeEditorType(window.location.getParameter('type'));
                }
              }
            });
          }},
          { url: '/notebook/editor', app: function (ctx) {
            page('/editor?' + ctx.querystring);
          }},
          { url: '/filebrowser/view=*', app: 'filebrowser' },
          { url: '/filebrowser/download=*', app: 'filebrowser' },
          { url: '/filebrowser/*', app: function () {
            page('/filebrowser/view=' + DROPZONE_HOME_DIR);
          }},
          { url: '/hbase/', app: 'hbase' },
          { url: '/help', app: 'help' },
          { url: '/home2*', app: function (ctx) {
            page(ctx.path.replace(/home2/gi, 'home'));
          }},
          { url: '/home*', app: 'home' },
          { url: '/indexer/indexes/*', app: 'indexes' },
          { url: '/indexer/', app: 'indexes' },
          { url: '/indexer/importer/', app: 'importer' },
          { url: '/indexer/importer/prefill/*', app: function (ctx) {
            self.loadApp('importer');
            self.getActiveAppViewModel(function (viewModel) {
              var _params = ctx.path.match(/\/indexer\/importer\/prefill\/?([^/]+)\/?([^/]+)\/?([^/]+)?/);
              if (! _params) {
                console.warn('Could not match ' + href);
              }
              hueUtils.waitForVariable(viewModel.createWizard, function(){
                hueUtils.waitForVariable(viewModel.createWizard.prefill, function(){
                  viewModel.createWizard.prefill.source_type(_params && _params[1] ? _params[1] : '');
                  viewModel.createWizard.prefill.target_type(_params && _params[2] ? _params[2] : '');
                  viewModel.createWizard.prefill.target_path(_params && _params[3] ? _params[3] : '');
                });
              });
            })
          }},
          { url: '/jobbrowser/jobs/job_*', app: function (ctx) {
            page.redirect('/jobbrowser#!id=application_' + _.trimRight(ctx.params[0], '/').split('/')[0]);
          }},
          { url: '/jobbrowser/jobs/application_*', app: function (ctx) {
            page.redirect('/jobbrowser#!id=application_' + _.trimRight(ctx.params[0], '/').split('/')[0]);
          }},
          { url: '/jobbrowser*', app: 'jobbrowser'},
          { url: '/logs', app: 'logs' },
          { url: '/metastore', app: function () {
            page('/metastore/tables');
          }},
          { url: '/metastore/*', app: 'metastore' },
          { url: '/notebook', app: function (ctx) {
            self.loadApp('notebook');
            var notebookId = hueUtils.getSearchParameter('?' + ctx.querystring, 'notebook');
            if (notebookId !== '') {
              self.getActiveAppViewModel(function (viewModel) {
                viewModel.openNotebook(notebookId);
              });
            } else {
              self.getActiveAppViewModel(function (viewModel) {
                viewModel.newNotebook('notebook');
              });
            }
          }},
          { url: '/notebook/notebook', app: function (ctx) {
            page('/notebook?' + ctx.querystring);
          }},
          { url: '/notebook/notebooks', app: function (ctx) {
            page('/home/?' + ctx.querystring);
          }},
          { url: '/oozie/editor/bundle/list', app: function (ctx) {
            page('/home/?type=oozie-bundle');
          }},
          { url: '/oozie/editor/bundle/*', app: 'oozie_bundle' },
          { url: '/oozie/editor/coordinator/list', app: function (ctx) {
            page('/home/?type=oozie-coordinator');
          }},
          { url: '/oozie/editor/coordinator/*', app: 'oozie_coordinator' },
          { url: '/oozie/editor/workflow/list', app: function (ctx) {
            page('/home/?type=oozie-workflow');
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
          { url: '/security/hdfs', app: function (ctx) {
            if (self.lastContext == null || ctx.path !== self.lastContext.path) {
              self.loadApp('security_hdfs');
            }
            self.lastContext = ctx;
          }},
          { url: '/security/hive', app: function (ctx) {
            if (self.lastContext == null || ctx.path !== self.lastContext.path) {
              self.loadApp('security_hive');
            }
            self.lastContext = ctx;
          }},
          { url: '/security/hive2', app: function (ctx) {
            if (self.lastContext == null || ctx.path !== self.lastContext.path) {
              self.loadApp('security_hive2');
            }
            self.lastContext = ctx;
          }},
          { url: '/security/solr', app: function (ctx) {
            if (self.lastContext == null || ctx.path !== self.lastContext.path) {
              self.loadApp('security_solr');
            }
            self.lastContext = ctx;
          }},
          { url: '/security', app: function () {
            page('/security/hive');
          }},
          { url: '/sqoop', app: 'sqoop' },
          { url: '/jobsub', app: 'jobsub' },
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
          % if other_apps:
            % for other in other_apps:
              { url: '/${ other.display_name }*', app: function (ctx) {
                self.currentContextParams(ctx.params);
                self.currentQueryString(ctx.querystring);
                self.loadApp('${ other.display_name }', true)
              }}
            % endfor
          % endif
        ];

        if (typeof HUE_EMBEDDED_PAGE_MAPPINGS !== 'undefined') {
          pageMapping = pageMapping.concat(HUE_EMBEDDED_PAGE_MAPPINGS)
        }

        pageMapping.forEach(function (mapping) {
          page(mapping.url, _.isFunction(mapping.app) ? mapping.app : function (ctx) {
            self.currentContextParams(ctx.params);
            self.currentQueryString(ctx.querystring);
            self.loadApp(mapping.app);
          })
        });

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          page('/', function() { page(clusterConfig['main_button_action'].page); });
          page('*', function (ctx) {
            console.error('Route not found', ctx);
            self.loadApp('404');
          });
          page();
        });

        huePubSub.subscribe('open.link', function (href) {
          if (href) {
            if (href.startsWith('/') && !href.startsWith('/hue')){
              page('/hue' + href);
            } else {
              page(href);
            }
          }
          else {
            console.warn('Received an open.link without href.')
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
        self.assistWithoutStorage = ko.observable(false);
        self.leftAssistVisible = ko.observable(self.apiHelper.getFromTotalStorage('assist', 'left_assist_panel_visible', true));
        self.leftAssistVisible.subscribe(function (val) {
          if (!self.assistWithoutStorage()){
            self.apiHelper.setInTotalStorage('assist', 'left_assist_panel_visible', val);
          }
          hueAnalytics.convert('hue', 'leftAssistVisible/' + val);
          window.setTimeout(function () {
            huePubSub.publish('split.panel.resized');
            $(window).trigger('resize');
          }, 0);
        });

        self.rightAssistVisible = ko.observable(self.apiHelper.getFromTotalStorage('assist', 'right_assist_panel_visible', true));
        self.rightAssistVisible.subscribe(function (val) {
          if (!self.assistWithoutStorage()){
            self.apiHelper.setInTotalStorage('assist', 'right_assist_panel_visible', val);
          }
          hueAnalytics.convert('hue', 'rightAssistVisible/' + val)
          window.setTimeout(function () {
            huePubSub.publish('reposition.scroll.anchor.up');
            huePubSub.publish('nicescroll.resize');
            huePubSub.publish('split.panel.resized');
            $(window).trigger('resize');
          }, 0);
        });
        self.rightAssistAvailable = ko.observable(false);

        huePubSub.subscribe('assist.highlight.risk.suggestions', function () {
          if (self.rightAssistAvailable() && !self.rightAssistVisible()) {
            self.rightAssistVisible(true);
          }
        });

        self.activeAppViewModel = ko.observable();
        self.currentApp = ko.observable('');
        self.templateApp = ko.pureComputed(function(){
          if (['editor', 'notebook'].indexOf(self.currentApp()) > -1){
            return self.currentApp()
          }
          else {
            return '';
          }
        });

        self.contextPanelVisible = ko.observable(false);
        self.contextPanelVisible.subscribe(function () {
          var $el = $('.snippet .ace-editor:visible');
          if ($el.length === 0) {
            $el = $('.content-panel:visible');
          }
          $('.context-panel').width($el.width()).css('left', $el.offset().left);
        });

        self.sessionsAvailable = ko.observable(false);

        self.activeAppViewModel.subscribe(function (viewModel) {
          self.sessionsAvailable(typeof viewModel.selectedNotebook !== 'undefined');
        });

        huePubSub.subscribe('context.panel.visible', function (visible) {
          self.contextPanelVisible(visible);
        });

        huePubSub.subscribe('set.current.app.view.model', self.activeAppViewModel);
        huePubSub.subscribe('app.dom.loaded', self.currentApp);

        huePubSub.publish('get.current.app.view.model');

        var previousVisibilityValues = {};
        huePubSub.subscribe('side.panels.hide', function(withoutStorage){
          previousVisibilityValues = {
            left: self.leftAssistVisible(),
            right: self.rightAssistVisible()
          };
          self.assistWithoutStorage(withoutStorage);
          self.leftAssistVisible(false);
          self.rightAssistVisible(false);
          window.setTimeout(function(){
            self.assistWithoutStorage(false);
          }, 0);
        });

        huePubSub.subscribe('side.panels.show', function(withoutStorage){
          self.assistWithoutStorage(withoutStorage);
          self.leftAssistVisible(previousVisibilityValues.left);
          self.rightAssistVisible(previousVisibilityValues.right);
          window.setTimeout(function(){
            self.assistWithoutStorage(false);
          }, 0);
        });

        huePubSub.subscribe('left.assist.show', function () {
          if (!self.leftAssistVisible()) {
            self.leftAssistVisible(true);
          }
        })
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

      function TopNavViewModel (onePageViewModel) {
        var self = this;
        self.onePageViewModel = onePageViewModel;
        self.leftNavVisible = ko.observable(false);
        self.leftNavVisible.subscribe(function (val) {
          huePubSub.publish('left.nav.open.toggle', val);
          hueAnalytics.convert('hue', 'leftNavVisible/' + val);
          if (val) {
            // Defer or it will be triggered by the open click
            window.setTimeout(function () {
              $(document).one('click', function () {
                if (self.leftNavVisible()) {
                  self.leftNavVisible(false);
                }
              })
            }, 0);
          }
        });

        self.onePageViewModel.currentApp.subscribe(function () {
          self.leftNavVisible(false);
        });

        self.mainQuickCreateAction = ko.observable();
        self.quickCreateActions = ko.observableArray();

        self.hasJobBrowser = ko.observable(true);

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          if (clusterConfig && clusterConfig['main_button_action']) {
            var topApp = clusterConfig['main_button_action'];
            self.mainQuickCreateAction({
              displayName: topApp.buttonName,
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
              var toAddDivider = false;
              var dividerAdded = false;
              var lastInterpreter = null;
              $.each(app['interpreters'], function(index, interpreter) {
                // Promote the first catagory of interpreters
                if (! dividerAdded) {
                  toAddDivider = (app.name === 'editor' || app.name === 'dashboard') && (lastInterpreter != null && lastInterpreter.is_sql != interpreter.is_sql);
                }
                interpreters.push({
                  displayName: interpreter.displayName,
                  dividerAbove: toAddDivider,
                  icon: interpreter.type,
                  url: interpreter.page
                });
                lastInterpreter = interpreter;
                if (toAddDivider) {
                  dividerAdded = true;
                  toAddDivider = false;
                }
              });

              % if user.is_superuser and cluster != ANALYTIC_DB:
                if (app.name === 'editor') {
                  interpreters.push({
                    displayName: '${ _('Add more...') }',
                    dividerAbove: true,
                    href: 'http://gethue.com/sql-editor/'
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

          self.hasJobBrowser(clusterConfig && clusterConfig['app_config'] && clusterConfig['app_config']['browser'] && (clusterConfig['app_config']['browser']['interpreter_names'].indexOf('yarn') != -1 || clusterConfig['app_config']['browser']['interpreter_names'].indexOf('dataeng') != -1));
        });

        huePubSub.subscribe('hue.new.default.app', function () {
          huePubSub.publish('cluster.config.refresh.config');
        });

        var ClusterPanelViewModel = function() {
          var self = this;
          self.apiHelper = ApiHelper.getInstance();

          self.clusters = ko.mapping.fromJS(${ clusters_config_json | n,unicode });
          self.cluster = ko.observable(self.clusters().length > 0 ? self.clusters()[${ default_cluster_index }] : self.clusters()[0]);
          self.cluster.subscribe(function(newValue) {
            new ClusterConfig({'cluster': ko.mapping.toJSON(newValue)});
          });

          self.contextPanelVisible = ko.observable(false);

          self._loadInterface = function() {
            var interfaces = self.cluster().interfaces().filter(function (i) {return i.interface() == '${ default_cluster_interface }'});
            if (interfaces.length > 0) {
              self.cluster(interfaces[0]);
            }
          };
          var dataEngCluster = $.grep(self.clusters(), function(cluster) {
            return cluster.type() == 'dataeng';
          });
          if (dataEngCluster.length > 0) {
            $.post("/jobbrowser/api/jobs", {
              interface: ko.mapping.toJSON('dataeng-clusters'),
              filters: ko.mapping.toJSON([]),
            }, function (data) {
              if (data.status == 0) {
                var interfaces = [];
                if (data && data.apps) {
                  data.apps.forEach(function(cluster) {
                    interfaces.push(ko.mapping.fromJS({'name': dataEngCluster[0].name(), 'type': 'dataeng', 'interface': cluster.name, 'id': cluster.id}));
                  });
                }
                dataEngCluster[0]['interfaces'](interfaces);

                if (dataEngCluster[0].type() == 'dataeng') {
                  self._loadInterface();
                }
              } else {
                $(document).trigger("error", data.message);
              }
            });
          }
          if (self.cluster().type() != 'dataeng') {
            self._loadInterface();
          }
        };
        self.cluster = new ClusterPanelViewModel();
      }

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
            if (appConfig['editor']) {
              var editor = null;
              if (clusterConfig['main_button_action'] && clusterConfig['main_button_action'].page.indexOf('/editor') === 0) {
                editor = clusterConfig['main_button_action'];
              }

              if (!editor) {
                var defaultEditor = appConfig['editor']['default_sql_interpreter'];
                if (defaultEditor) {
                  var foundEditor = appConfig['editor']['interpreters'].filter(function (interpreter) {
                    return interpreter.type === defaultEditor;
                  });
                  if (foundEditor.length === 1) {
                    editor = foundEditor[0];
                  }
                }
              }

              if (!editor && appConfig['editor']['interpreters'].length > 1) {
                editor = appConfig['editor']['interpreters'][1];
              }

              if (editor) {
                appsItems.push({
                  displayName: '${ _("Editor") }',
                  url: editor['page'],
                  icon: 'editor'
                });
              } else {
                appsItems.push({
                  displayName: appConfig['editor']['displayName'],
                  url: appConfig['editor']['page'],
                  icon: 'editor'
                });
              }
            }
            ['dashboard', 'scheduler'].forEach(function(appName) {
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
              url: '/home/',
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
      ko.applyBindings(sidebarViewModel, $('.hue-sidebar')[0]);
    })(onePageViewModel, topNavViewModel);

    huePubSub.publish('cluster.config.get.config');

    $(document).on('hideHistoryModal', function (e) {
      $('#clearNotificationHistoryModal').modal('hide');
    });

    huePubSub.subscribe('query.and.watch', function (query) {
      $.post(query['url'], {
        format: "json",
        sourceType: query['sourceType']
      },function(resp) {
        if (resp.history_uuid) {
          huePubSub.publish('open.editor.query', resp.history_uuid);
        } else if (resp.message) {
          $(document).trigger("error", resp.message);
        }
      }).fail(function (xhr) {
        $(document).trigger("error", xhr.responseText);
      });
    });

    var hideJobsPanels = function (e) {
      if ($(e.target).parents('.navbar-default').length > 0 && $(e.target).closest('.history-panel').length === 0 && $(e.target).closest('.btn-toggle-jobs-panel').length === 0 && $(e.target).closest('.hamburger-hue').length === 0 && $('.jobs-panel').is(':visible')) {
        huePubSub.publish('hide.jobs.panel');
        huePubSub.publish('hide.history.panel');
      }
    };

    var clickThrottle = -1;
    $(window).click(function (e) {
      window.clearTimeout(clickThrottle);
      clickThrottle = window.setTimeout(function () {
        hideJobsPanels(e);
      }, 10);
    });

    $('.page-content').jHueScrollUp();

    window.hueDebug = {
      viewModel: function (element) {
        if (typeof element !== 'undefined' && typeof element === 'string') {
          element = $(element)[0];
        }
        return element ? ko.dataFor(element) : window.hueDebug.onePageViewModel;
      },
      onePageViewModel: onePageViewModel,
      sidePanelViewModel: sidePanelViewModel,
      topNavViewModel: topNavViewModel
    };

    var tour = new Shepherd.Tour({
      defaults: {
        classes: 'shepherd-theme-hue',
        showCancelLink: true
      }
    });

    tour.addStep('welcome', {
      text: '<b>${ _ko('Welcome to Hue 4!') }</b><br><br>${ _ko('We want to introduce you to the new interface. It takes less than a minute. Ready? ') }'
    });

    tour.addStep('topnav', {
      text: '${ _ko('A new nav bar and big blue button!') }<br><br>${ _ko('Open Hue to your favorite app, select other apps from the blue button, do global search, and view notification panels at right.') }',
      attachTo: '.navbar-default bottom'
    });

    %if user.is_superuser:
      tour.addStep('admin', {
        text: '${ _ko('As a superuser, you can check system configuration from the username drop down and install sample data and jobs for your users.') }',
        attachTo: '.top-nav-right .dropdown bottom'
      });
    %endif

    tour.addStep('leftpanel', {
      text: '${ _ko('Discover data sources with the improved data assist panel. Remember to right-click for more!') }',
      attachTo: '.left-panel right'
    });

    tour.addStep('pagecontent', {
      text: '${ _ko('This is the main attraction, where your selected app runs.') }<br>${ _ko('Hover on the app name to star it as your favorite application.') }',
      attachTo: '.page-content center'
    });

    tour.addStep('rightpanel', {
      text: '${ _ko('Some apps have a right panel with additional information to assist you in your data discovery.') }',
      attachTo: '.right-panel left'
    });

    tour.addStep('bye', {
      text: '${ _ko('This ends the tour. To see it again, click Welcome Tour from the username drop down.') }<br><br>${ _ko('And now go ') }<b>${ _ko('Query, Explore, Repeat') }</b>!'
    });

    var closeTourOnEsc = function (e) {
      if (e.keyCode === 27) {
        tour.cancel();
      }
    };

    % if is_demo or not user_preferences.get(PREFERENCE_IS_WELCOME_TOUR_SEEN):
      $(document).on('keyup', closeTourOnEsc);
      $(document).on('click', '.shepherd-backdrop', tour.cancel);
      tour.start();
    % endif


    tour.on('complete', function () {
      $.post('/desktop/api2/user_preferences/${ PREFERENCE_IS_WELCOME_TOUR_SEEN }', {
        'set': 'seen'
      });
      $(document).off('keyup', closeTourOnEsc);
    });

    tour.on('cancel', function () {
      $.post('/desktop/api2/user_preferences/${ PREFERENCE_IS_WELCOME_TOUR_SEEN }', {
        'set': 'seen'
      });
      $(document).off('keyup', closeTourOnEsc);
    });

    huePubSub.subscribe('show.welcome.tour', function () {
      $(document).on('keyup', closeTourOnEsc);
      tour.start();
    });

  });
</script>

${ commonHeaderFooterComponents.footer(messages) }

% if IS_EMBEDDED.get():
</div>
% endif

</body>
</html>
