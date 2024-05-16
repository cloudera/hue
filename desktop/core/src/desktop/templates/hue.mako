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
  import sys

  from desktop import conf
  from desktop.auth.backend import is_admin
  from desktop.conf import ENABLE_HUE_5, has_multi_clusters
  from desktop.lib.i18n import smart_unicode
  from desktop.models import hue_version
  from desktop.views import _ko, commonshare, login_modal
  from desktop.webpack_utils import get_hue_bundles

  from webpack_loader.templatetags.webpack_loader import render_bundle

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="hueIcons" file="/hue_icons.mako" />
<%namespace name="commonHeaderFooterComponents" file="/common_header_footer_components.mako" />
<%namespace name="jbCommon" file="/job_browser_common.mako" />

<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>

  % if conf.COLLECT_USAGE.get():
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=${conf.GTAG_ID.get()}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', '${ conf.GTAG_ID.get()}', { 
        // Prevent GA from accidentally passing client meta data present in urls
        send_page_view: false, 
        page_location: 'redacted',
        page_referrer: 'redacted',
        allow_google_signals: false
        });
    </script>
  % endif

  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  % if conf.CUSTOM.LOGO_SVG.get():
    <link rel="icon" type="image/x-icon" href="${ static('desktop/art/custom-branding/favicon.ico') }"/>
  % else:
    <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }"/>
  % endif
  <meta name="description" content="Open source SQL Query Assistant for Databases/Warehouses.">
  <meta name="author" content="Hue Team">

  <link href="${ static('desktop/css/roboto.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/jquery-ui.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/home.css') }" rel="stylesheet">
  <link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/select2/select2.css') }">

  <link rel="stylesheet" href="${ static('desktop/ext/css/hue-charts.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.markercluster.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/leaflet.zoombox.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/nv.d3.min.css') }">
  <link rel="stylesheet" href="${ static('desktop/css/nv.d3.css') }">
  <link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-fileupload.css') }" >

  <%
    global_constants_url = '/desktop/globalJsConstants.js?v=' + hue_version()
  %>
  <script src="${global_constants_url}"></script>

  % if not conf.DEV.get():
  <script src="${ static('desktop/js/hue.errorcatcher.js') }"></script>
  % endif
</head>

<body>

<hue-icons-web-component></hue-icons-web-component>

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

${ hueIcons.symbols() }

<!-- fake fields are a workaround for chrome autofill getting the wrong fields, readonly needed for 1password -->
<input style="display:none" readonly autocomplete="false" type="text" name="fakeusernameremembered"/>
<input style="display:none" readonly autocomplete="false" type="password" name="fakepasswordremembered"/>

<div class="hue-page">
  <hue-sidebar-web-component style="flex: 1 1 auto"></hue-sidebar-web-component>

  <div class="main-page">
    <AppBanner data-reactcomponent='AppBanner'></AppBanner>
    <AlertComponent data-reactcomponent='AlertComponent'></AlertComponent>
    <WelcomeTour data-reactcomponent='WelcomeTour'></WelcomeTour>

    <nav class="navbar navbar-default">
      <div class="navbar-inner top-nav">
        <div class="top-nav-left"></div>

        <div class="top-nav-middle">
          <div class="search-container-top" data-bind="component: 'hue-global-search'"></div>
        </div>

        <div class="top-nav-right">
          % if has_multi_clusters():
            <select data-bind="options: clusters, optionsText: 'name', value: 'id'" class="input-small" style="margin-top:8px">
            </select>
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

    <div class="content-wrapper">
      <div class="left-panel" data-bind="css: { 'side-panel-closed': !leftAssistVisible() }, visibleOnHover: { selector: '.hide-left-side-panel' }">
        <a href="javascript:void(0);" style="z-index: 1002; display: none;" title="${_('Show Assist')}" class="pointer side-panel-toggle show-left-side-panel" data-bind="visible: !leftAssistVisible(), toggle: leftAssistVisible"><i class="fa fa-chevron-right"></i></a>
        <a href="javascript:void(0);" style="display: none; opacity: 0;" title="${_('Hide Assist')}" class="pointer side-panel-toggle hide-left-side-panel" data-bind="visible: leftAssistVisible, toggle: leftAssistVisible"><i class="fa fa-chevron-left"></i></a>
        <!-- ko if: window.USE_NEW_ASSIST_PANEL -->
% if conf.USE_NEW_ASSIST_PANEL.get():
          <assist-panel-web-component></assist-panel-web-component>
% endif
        <!-- /ko -->
        <!-- ko ifnot: window.USE_NEW_ASSIST_PANEL -->
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
        <!-- /ko -->
      </div>

      <div id="leftResizer" class="resizer" data-bind="visible: leftAssistVisible(), splitFlexDraggable : {
        containerSelector: '.content-wrapper',
        sidePanelSelector: '.left-panel',
        sidePanelVisible: leftAssistVisible,
        orientation: 'left',
        onPosition: function() { huePubSub.publish('split.draggable.position') }
      }"><div class="resize-bar"></div></div>

      <div class="page-content">
        <!-- ko if: window.ENABLE_HUE_5 -->
        <!-- ko component: 'session-panel' --><!-- /ko -->
        <!-- /ko -->
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
        <div id="embeddable_useradmin_organizations" class="embeddable"></div>
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
        <div id="embeddable_taskserver" class="embeddable"></div>
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

      %if not ENABLE_HUE_5.get():
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
            ${_('There is currently no information about the sessions.')}
            <!-- /ko -->
          </div>
        </div>
        <a class="pointer demi-modal-chevron" style="position: absolute; bottom: 0" data-bind="click: function () { huePubSub.publish('context.panel.visible', false); }"><i class="fa fa-chevron-up"></i></a>
      </div>
      %endif
    </div>
  </div>
</div>
${ commonshare() | n,unicode }

% for bundle in get_hue_bundles('hue'):
  ${ render_bundle(bundle) | n,unicode }
% endfor

<script src="${ static('desktop/js/polyfills.js') }"></script>
<script src="${ static('desktop/ext/js/tether.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }"></script>
<script src="${ static('desktop/ext/js/tzdetect.js') }"></script>

<script src="${ static('desktop/ext/js/bootstrap-fileupload.js') }"></script>
<script src="${ static('desktop/js/bootstrap-tooltip.js') }"></script>
<script src="${ static('desktop/js/bootstrap-typeahead-touchscreen.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>

<script src="${ static('desktop/js/share2.vm.js') }"></script>

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

% if request is not None:
${ smart_unicode(login_modal(request).content) | n,unicode }
% endif


<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

${ commonHeaderFooterComponents.footer(messages) }

## This includes common knockout templates that are shared with the Job Browser page and the mini job browser panel
## available in the upper right corner throughout Hue
%if 'jobbrowser' in apps:
${ jbCommon.include() }
%endif

<div class="monospace-preload" style="opacity: 0; height: 0; width: 0;">
  ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
  <b>Query. Explore. Repeat.</b>
</div>

</body>
</html>
