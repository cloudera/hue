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
  from desktop.conf import IS_EMBEDDED, DEV_EMBEDDED, IS_MULTICLUSTER_ONLY, has_multi_cluster
  from desktop.views import _ko, commonshare, login_modal
  from desktop.lib.i18n import smart_unicode
  from desktop.models import PREFERENCE_IS_WELCOME_TOUR_SEEN, ANALYTIC_DB, hue_version

  from dashboard.conf import IS_ENABLED as IS_DASHBOARD_ENABLED
  from filebrowser.conf import SHOW_UPLOAD_BUTTON
  from indexer.conf import ENABLE_NEW_INDEXER
  from metadata.conf import has_optimizer, OPTIMIZER

  from desktop.auth.backend import is_admin
  from webpack_loader.templatetags.webpack_loader import render_bundle
%>

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
      left: 0 !important;
      bottom: 0 !important;
      right: 0 !important;
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
  <link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">

  <link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.markercluster.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.zoombox.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/nv.d3.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/nv.d3.css') }">

  <script type="text/javascript">
% if IS_EMBEDDED.get():
  // Bootstrap 2.3.2 relies on the hide css class presence for modals but doesn't remove it when opened for fade type
  // modals, a parent container might have it set to !important which will prevent the modal from showing. This
  // redefines all .hide definitions to exclude .modal.fade
  try {
    for (var i = 0; i < document.styleSheets.length; i++) {
      if (document.styleSheets[i] && document.styleSheets[i].cssRules) {
        for (var j = document.styleSheets[i].cssRules.length - 1; j > 0; j--) {
          if (document.styleSheets[i] && document.styleSheets[i].cssRules[j] && document.styleSheets[i].cssRules[j].selectorText === '.hide') {
            var originalCssText = document.styleSheets[i].cssRules[j].cssText;
            if (originalCssText.indexOf('!important') !== -1) {
              document.styleSheets[i].deleteRule(j);
              document.styleSheets[i].insertRule(originalCssText.replace('.hide', '.hide:not(.modal):not(.fade)'));
            }
          }
        }
      }
    }
  } catch (e) {
    console.warn(e);
  }

  // Add modified URL for .clearable background
  var originalClearableImgUrl = '${ static('desktop/art/clearField@2x.png') }';
  var clearableImgUrl = typeof adaptHueEmbeddedUrls !== 'undefined' ? adaptHueEmbeddedUrls(originalClearableImgUrl) : originalClearableImgUrl;

  var style = document.createElement('style');
  style.type = 'text/css';
  style.appendChild(document.createTextNode('.clearable { background: url(' + clearableImgUrl + ') no-repeat right -10px center; }'));
  document.head.appendChild(style);
% endif
  </script>

  ${ commonHeaderFooterComponents.header_i18n_redirection() }
  <%
    global_constants_url = '/desktop/globalJsConstants.js?v=' + hue_version()
  %>
  <script src="${global_constants_url}"></script>

  % if not conf.DEV.get():
  <script src="${ static('desktop/js/hue.errorcatcher.js') }"></script>
  % endif
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

<!-- fake fields are a workaround for chrome autofill getting the wrong fields, readonly needed for 1password -->
<input style="display:none" readonly autocomplete="false" type="text" name="fakeusernameremembered"/>
<input style="display:none" readonly autocomplete="false" type="password" name="fakepasswordremembered"/>

<div class="main-page">
  % if banner_message or conf.CUSTOM.BANNER_TOP_HTML.get():
    <div class="banner">
      ${ banner_message or conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
    </div>
  % endif

  % if not IS_EMBEDDED.get():
  <nav class="navbar navbar-default">
    <div class="navbar-inner top-nav">
      <div class="top-nav-left">
        % if not IS_EMBEDDED.get():
          % if not (IS_MULTICLUSTER_ONLY.get() and has_multi_cluster()):
          <a class="hamburger hamburger-hue pull-left" data-bind="toggle: leftNavVisible, css: { 'is-active': leftNavVisible }">
            <span class="hamburger-box"><span class="hamburger-inner"></span></span>
          </a>

          <a class="brand" data-bind="hueLink: '/home/'" href="javascript: void(0);" title="${_('Documents')}">
              <svg style="height: 24px; width: 120px;"><use xlink:href="#hi-logo"></use></svg>
          </a>
          % endif
        % endif

        % if not IS_MULTICLUSTER_ONLY.get():
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
        % endif

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
        <div class="search-container-top" data-bind="component: 'hue-global-search'"></div>
      </div>

      <div class="top-nav-right">
        % if user.is_authenticated() and section != 'login' and (cluster != ANALYTIC_DB or IS_MULTICLUSTER_ONLY.get()):
        <div class="dropdown navbar-dropdown pull-right">
          % if IS_MULTICLUSTER_ONLY.get():
            ##<!-- ko component: { name: 'hue-app-switcher', params: { onPrem: ko.observable(false) } } --><!-- /ko -->
          % endif

          <%
            view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or is_admin(user)
          %>
          <button class="btn btn-flat" data-toggle="dropdown" data-bind="click: function(){ huePubSub.publish('hide.jobs.panel'); huePubSub.publish('hide.history.panel'); }">
            <i class="fa fa-user"></i> ${ user.username } <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            % if view_profile:
            <li><a href="javascript:void(0)" data-bind="hueLink: '/useradmin/users/edit/${ user.username }'" title="${ _('View Profile') if is_ldap_setup else _('Edit Profile') }"><i class="fa fa-fw fa-user"></i> ${_('My Profile')}</a></li>
            % endif
            % if is_admin(user):
            <li data-bind="hueLink: '/useradmin/users/'"><a href="javascript: void(0);"><i class="fa fa-fw fa-group"></i> ${_('Manage Users')}</a></li>
            % endif
            % if is_admin(user):
            <li><a data-bind="hueLink: '/about/'" href="javascript: void(0);"><span class="dropdown-no-icon">${_('Administration')}</span></a></li>
            % endif
            <li><a href="javascript:void(0)" onclick="huePubSub.publish('show.welcome.tour')"><span class="dropdown-no-icon">${_('Welcome Tour')}</span></a></li>
            <li><a href="http://gethue.com" target="_blank"><span class="dropdown-no-icon">${_('Help')}</span></a></li>
            <li class="divider"></li>
            <li><a title="${_('Sign out')}" data-bind="hueLink: '/accounts/logout'" href="javascript: void(0);"><i class="fa fa-fw fa-sign-out"></i> ${ _('Sign out') }</a></li>
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
    <div style="position: absolute; right: 0px; padding: 5px 10px;">
      <a class="pointer inactive-action pull-right" onclick="huePubSub.publish('hide.jobs.panel')"><i class="fa fa-fw fa-times"></i></a>
      <a class="pointer inactive-action pull-right" onclick="huePubSub.publish('mini.jb.expand'); huePubSub.publish('hide.jobs.panel')" title="${ _('Open in Job Browser') }">
        <i class="fa fa-fw fa-expand"></i>
      </a>
    </div>
    <div id="mini_jobbrowser"></div>
  </div>
  % endif

  <div class="content-wrapper">

    <script type="text/html" id="hue-tmpl-sidebar-link">
      <a role="button" class="hue-sidebar-item" data-bind="hueLink: item.url, attr: { title: item.displayName }">
        <span class="hue-sidebar-item-name" data-bind="text: item.displayName"></span>
      </a>
    </script>

    <div class="hue-sidebar hue-sidebar-below-top-bar" data-bind="visible: leftNavVisible" style="display:none;">
      % if IS_MULTICLUSTER_ONLY.get():
        <!-- ko component: { name: 'hue-multi-cluster-sidebar' } --><!-- /ko -->
      % else:
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
          % if hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get():
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
          % endif
        </div>
      % endif
    </div>

    % if IS_MULTICLUSTER_ONLY.get():
    <div class="hue-dw-sidebar-container collapsed" data-bind="component: { name: 'hue-dw-sidebar', params: { items: items, pocClusterMode: pocClusterMode } }"></div>
    % endif

    <div class="left-panel" data-bind="css: { 'side-panel-closed': !leftAssistVisible() }, visibleOnHover: { selector: '.hide-left-side-panel' }">
      <a href="javascript:void(0);" style="z-index: 1002; display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-left-side-panel" data-bind="visible: !leftAssistVisible(), toggle: leftAssistVisible"><i class="fa fa-chevron-right"></i></a>
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
      <!-- ko hueSpinner: { spin: isLoadingEmbeddable, center: true, size: 'xlarge', blackout: true } --><!-- /ko -->
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
      <div id="embeddable_catalog" class="embeddable"></div>
      <div id="embeddable_indexer" class="embeddable"></div>
      <div id="embeddable_kafka" class="embeddable"></div>
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
      <div id="embeddable_connectors" class="embeddable"></div>
      <div id="embeddable_analytics" class="embeddable"></div>
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

    <div class="right-panel" data-bind="css: { 'right-assist-minimized': !rightAssistVisible() }, visible: rightAssistAvailable, component: {
        name: 'right-assist-panel',
        params: {
          visible: rightAssistVisible
        }
      }" style="display: none;"></div>

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

${ render_bundle('vendors~hue~notebook') | n,unicode }
${ render_bundle('vendors~hue') | n,unicode }
${ render_bundle('hue~notebook') | n,unicode }
${ render_bundle('hue') | n,unicode }

<script src="${ static('desktop/js/polyfills.js') }"></script>
<script src="${ static('desktop/ext/js/tether.js') }"></script>
<script src="${ static('desktop/ext/js/shepherd.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/tzdetect.js') }" type="text/javascript" charset="utf-8"></script>

<script src="${ static('desktop/js/bootstrap-tooltip.js') }"></script>
<script src="${ static('desktop/js/bootstrap-typeahead-touchscreen.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>

<script src="${ static('desktop/js/ace/ace.js') }"></script>
<script src="${ static('desktop/js/ace/mode-impala.js') }"></script>
<script src="${ static('desktop/js/ace/mode-hive.js') }"></script>
<script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
<script src="${ static('desktop/js/ace.extended.js') }"></script>
<script>ace.config.set("basePath", "${ static('desktop/js/ace') }");</script>

<script src="${ static('desktop/js/share2.vm.js') }"></script>
<script src="${ static('metastore/js/metastore.model.js') }"></script>

<script>
  var shareViewModel = initSharing("#documentShareModal");
</script>

<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />

${ configKoComponents.config() }
${ notebookKoComponents.aceKeyboardShortcuts() }
${ notebookKoComponents.downloadSnippetResults() }
${ hueAceAutocompleter.hueAceAutocompleter() }

${ commonHeaderFooterComponents.header_pollers(user, is_s3_enabled, apps) }

## clusterConfig makes an Ajax call so it needs to be after commonHeaderFooterComponents
<script src="${ static('desktop/js/clusterConfig.js') }"></script>

${ assist.assistPanel() }

% if request is not None:
${ smart_unicode(login_modal(request).content) | n,unicode }
% endif

<div class="shepherd-backdrop"></div>

<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

<script type="text/javascript">

  window.EMBEDDABLE_PAGE_URLS = {
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
    catalog: { url: '/catalog', title: '${_('Catalog')}' },
    indexer: { url: '/indexer/indexer/', title: '${_('Indexer')}' },
    kafka: { url: '/indexer/topics/', title: '${_('Streams')}' },
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
    connectors: { url: '/desktop/connectors', title: '${_('Connectors')}' },
    analytics: { url: '/desktop/analytics', title: '${_('Analytics')}' },
    sqoop: { url: '/sqoop', title: '${_('Sqoop')}' },
    jobsub: { url: '/jobsub/not_available', title: '${_('Job Designer')}' },
    % if other_apps:
      % for other in other_apps:
        ${ other.display_name }: { url: '/${ other.display_name }', title: '${ other.nice_name }' },
      % endfor
    % endif
  }

  window.SKIP_CACHE = [
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

  window.OTHER_APPS = [];
  % if other_apps:
    % for other in other_apps:
      window.OTHER_APPS.push('${ other.display_name }');
    % endfor
  % endif

  % if is_admin(user) and cluster != ANALYTIC_DB:
  window.SHOW_ADD_MORE_EDITORS = true;
  % endif


  $(document).ready(function () {

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

    %if is_admin(user):
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

    % if is_demo or (not user_preferences.get(PREFERENCE_IS_WELCOME_TOUR_SEEN) and not IS_EMBEDDED.get()):
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

<div class="monospace-preload" style="opacity: 0; height: 0; width: 0;">
  ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
  <b>Query. Explore. Repeat.</b>
</div>

</body>
</html>
