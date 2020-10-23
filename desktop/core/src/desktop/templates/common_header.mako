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

from metadata.conf import has_optimizer, OPTIMIZER

from desktop import conf
from desktop.auth.backend import is_admin
from desktop.conf import USE_NEW_EDITOR
from desktop.models import hue_version
from desktop.lib.i18n import smart_unicode
from desktop.webpack_utils import get_hue_bundles

home_url = url('desktop_views_home')
if USE_NEW_EDITOR.get():
  home_url = url('desktop_views_home2')
%>

<%namespace name="commonHeaderFooterComponents" file="/common_header_footer_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />
<%namespace name="hueIcons" file="/hue_icons.mako" />

<!DOCTYPE html>
<%def name="is_selected(selected)">
  %if selected:
    class="active"
  %endif
</%def>

<%def name="get_nice_name(app, section)">
  % if app and section == app.display_name:
    - ${app.nice_name}
  % endif
</%def>

<%def name="get_title(title)">
  % if title:
    - ${smart_unicode(title)}
  % endif
</%def>

<html lang="en">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue ${ get_nice_name(current_app, section) } ${ get_title(title) }</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  % if conf.CUSTOM.LOGO_SVG.get():
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/custom-branding/favicon.ico') }"/>
  % else:
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }"/>
  % endif

  <meta name="twitter:image" content="${ static('desktop/art/hue-login-logo-ellie.png') }">
  <meta name="twitter:card" content="summary">
  <meta property="og:site_name" content="${ _('Hue - SQL Editor') }" />
  <meta property="og:title" content="${ _('Hue - SQL Editor') }" />
  <meta property="og:description" content="${ _('Let anybody query, write SQL, explore data and share results.') }">
  <meta property="og:image" content="${ static('desktop/art/hue-login-logo-ellie.png') }" />
  <meta name="description" content="${ _('Let anybody query, write SQL, explore data and share results.') }">
  <meta name="keywords" content="${ _('query, sql, data warehouse, database, sharing, catalog, scheduler, optimize, dashboard') }" />

  <link href="${ static('desktop/css/roboto.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">

  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue3.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue3-extra.css') }" rel="stylesheet">

  <style type="text/css">
    % if banner_message or conf.CUSTOM.BANNER_TOP_HTML.get():
      body {
        display: none;
        visibility: hidden;
        padding-top: ${str(int(padding[:-2]) + 30) + 'px'};
      }
      .banner {
        height: 30px;
        width: 100%;
        padding: 0;
        position: fixed;
        top: 0;
        background-color: #F9F9F9;
        z-index: 1033;
      }
      .main-content {
        top: 106px!important;
      }
      .navigator {
        top: 30px!important;
      }
      .hue-title-bar {
        top: 58px!important;
      }
      % if current_app == "sqoop":
      .top-bar {
        top: 58px!important;
      }
      % endif

      % if current_app == "spark":
      .search-bar {
        top: 58px!important;
      }
      .show-assist {
        top: 110px!important;
      }
      % endif

    % else:
      body {
        display: none;
        visibility: hidden;
        padding-top: ${padding};
      }
    % endif
  </style>

  ${ commonHeaderFooterComponents.header_i18n_redirection() }

  % if user.is_authenticated():
  <%
    global_constants_url = '/desktop/globalJsConstants.js?v=' + hue_version()
  %>
  <script src="${global_constants_url}"></script>
  % endif

  % if not conf.DEV.get():
  <script src="${ static('desktop/js/hue.errorcatcher.js') }"></script>
  % endif

  % for bundle in get_hue_bundles('login' if section == 'login' else 'hue', 'LOGIN' if section == 'login' else 'DEFAULT'):
    ${ render_bundle(bundle, config='LOGIN' if section == 'login' else 'DEFAULT') | n,unicode }
  % endfor

  <script src="${ static('desktop/js/bootstrap-tooltip.js') }"></script>
  <script src="${ static('desktop/js/bootstrap-typeahead-touchscreen.js') }"></script>
  <script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>
  <script src="${ static('desktop/js/popover-extra-placements.js') }"></script>
  <script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
  <script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/tzdetect.js') }" type="text/javascript" charset="utf-8"></script>

% if user.is_authenticated():
  ${ hueAceAutocompleter.hueAceAutocompleter() }
%endif

  ${ commonHeaderFooterComponents.header_pollers(user, is_s3_enabled, apps) }

% if user.is_authenticated():
  <script src="${ static('desktop/ext/js/localforage.min.js') }"></script>

  <script type="text/javascript">
    $(document).ready(function () {
      localforage.config({
        version: 1.0,
        storeName: 'hue_store',
      });

      huePubSub.subscribe('get.current.app.name', function () {
        var appName = '';
        if ('${ 'metastore' in apps }' === 'True' && location.href.indexOf('${"metastore" in apps and apps["metastore"].display_name}') !== -1) {
          appName = 'metastore';
        } else if (location.href.indexOf('editor') !== -1) {
          appName = 'editor'
        }
        huePubSub.publish('set.current.app.name', appName);
      });

      huePubSub.subscribe('open.link', function (href) {
        location.href = href;
      });
    });
  </script>
%endif
</head>

<body>
${ hueIcons.symbols() }


% if hasattr(request, 'environ') and request.environ.get("PATH_INFO").find("/hue/") < 0:
  <script>
    window.location.replace("/");
  </script>
% endif

% if banner_message or conf.CUSTOM.BANNER_TOP_HTML.get():
  <div class="banner">
    ${ banner_message or conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
  </div>
% endif

<%
  def count_apps(apps, app_list):
    count = 0
    found_app = ""
    for app in app_list:
      if app in apps:
        found_app = app
        count += 1
    return found_app, count
%>

% if not skip_topbar:
<div class="navigator">
  <div class="pull-right">

  % if user.is_authenticated() and section != 'login':
  <ul class="nav nav-pills">
    <li class="divider-vertical"></li>
    % if 'filebrowser' in apps:
      % if not is_s3_enabled and not is_adls_enabled:
      <li class="hide1380">
        <a title="${_('Manage HDFS')}" data-rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}">
          <i class="fa fa-file"></i>&nbsp;${_('File Browser')}&nbsp;
        </a>
      </li>
      % else:
        <li class="dropdown hide1380">
          <a title="${_('File Browsers')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
            <i class="fa fa-file"></i>&nbsp;${_('File Browsers')} <b class="caret"></b>
          </a>
          <ul role="menu" class="dropdown-menu">
            <li><a href="/${apps['filebrowser'].display_name}">
              <i class="fa fa-fw fa-file" style="vertical-align: middle"></i>${_('HDFS Browser')}</a>
            </li>
            % if is_s3_enabled:
            <li><a href="/${apps['filebrowser'].display_name}/view=S3A://">
              <i class="fa fa-fw fa-cubes" style="vertical-align: middle"></i>${_('S3 Browser')}</a>
            </li>
            % endif
            % if is_adls_enabled:
            <li><a href="/${apps['filebrowser'].display_name}/view=adl:/">
              <span class="fa fa-fw" style="font-size:20px;vertical-align: middle;"><svg class="hi"><use xlink:href='#hi-adls'></use></svg></span>${_('ADLS Browser')}</a>
            </li>
            % endif
          </ul>
        </li>
      % endif
      <li class="hideMoreThan1380">
        <a title="${_('HDFS Browser')}" data-rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}">
          <i class="fa fa-file"></i>
        </a>
      </li>
      <li class="hideMoreThan1380">
        % if is_s3_enabled:
          <a title="${_('S3 Browser')}" data-rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}/view=S3A://">
            <i class="fa fa-cubes"></i>
          </a>
        % endif
      </li>
      <li class="hideMoreThan1380">
        % if is_adls_enabled:
          <a title="${_('ADLS Browser')}" data-rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}/view=adl:/">
            <span style="font-size:15px;vertical-align: middle;"><svg class="hi"><use xlink:href='#hi-adls'></use></svg></span>
          </a>
        % endif
      </li>
    % endif
    % if 'jobbrowser' in apps:
      <% from jobbrowser.conf import ENABLE_V2 %>
      % if not ENABLE_V2.get():
        <li class="hide1380"><a title="${_('Manage jobs')}" data-rel="navigator-tooltip" href="/${apps['jobbrowser'].display_name}"><i class="fa fa-list-alt"></i>&nbsp;${_('Job Browser')}&nbsp;<span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a></li>
        <li class="hideMoreThan1380"><a title="${_('Job Browser')}" data-rel="navigator-tooltip" href="/${apps['jobbrowser'].display_name}"><i class="fa fa-list-alt"></i></a></li>
      % else:
        <li class="hide1380"><a title="${_('Manage jobs')}" data-rel="navigator-tooltip" href="/jobbrowser/apps">
          <i class="fa fa-list-alt"></i>&nbsp;${_('Job Browser')}&nbsp;<span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a>
        </li>
        <li class="hideMoreThan1380"><a title="${_('Job Browser')}" data-rel="navigator-tooltip" href="/jobbrowser/apps"><i class="fa fa-list-alt"></i></a></li>
      % endif
    % endif
    <%
      view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or is_admin(user)
    %>
    % if view_profile:
    <li class="dropdown">
      <a title="${'Administration' if view_profile else ''}" href="#" data-rel="navigator-tooltip" data-toggle="dropdown" class="dropdown-toggle">
        <i class="fa fa-cogs"></i>&nbsp;${user.username}&nbsp;
        <b class="caret"></b>
      </a>
      <ul class="dropdown-menu pull-right">
      % if view_profile:
      <li>
        <a href="${ url('useradmin.views.edit_user', username=user.username) }"><i class="fa fa-fw fa-key"></i>
          % if is_ldap_setup:
            ${_('View Profile')}
          % else:
            ${_('Edit Profile')}
          % endif
        </a>
      </li>
        % if is_admin(user):
          <li><a href="${ url('useradmin.views.list_users') }"><i class="fa fa-fw fa-group"></i> ${_('Manage Users')}</a></li>
        % endif
      % endif
      </ul>
    </li>
    % else:
      <li><a title="" data-rel="navigator-tooltip" href="#"><i class="fa fa-fw fa-user"></i>&nbsp;${user.username}</a></li>
    % endif
    % if 'help' in apps:
    <li><a title="${_('Documentation')}" data-rel="navigator-tooltip" data-bind="hueLink: '/help'" href="javascript: void(0);"><i class="fa fa-question-circle"></i></a></li>
    % endif
    <li><a title="${_('Sign out')}" data-rel="navigator-tooltip" data-bind="hueLink: '/accounts/logout/'" href="javascript: void(0);" ><i class="fa fa-sign-out"></i></a></li>
  </ul>
  % endif

  </div>
    <a class="brand nav-tooltip pull-left" title="${_('About Hue')}" data-rel="navigator-tooltip" data-bind="hueLink: '/about'" href="javascript: void(0);">
      <svg style="margin-top: 2px; margin-left:8px;width: 60px;height: 16px;display: inline-block;">
        <use xlink:href="#hi-logo"></use>
      </svg>
    </a>
    % if user.is_authenticated() and section != 'login':
     <ul class="nav nav-pills pull-left">
       <li><a title="${_('My documents')}" data-rel="navigator-tooltip" data-bind="hueLink: '${ home_url }'" style="padding-bottom:2px!important"><i class="fa fa-home" style="font-size: 19px"></i></a></li>
       <%
         query_apps = count_apps(apps, ['beeswax', 'impala', 'rdbms', 'pig', 'jobsub', 'spark']);
       %>
       % if query_apps[1] > 1:
       <li class="dropdown oozie">
         <a title="${_('Query data')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-terminal inline-block hideMoreThan950"></i><span class="hide950">Query Editors</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'beeswax' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="${ url('notebook:editor') }?type=hive"><svg class="svg-app-icon"><use xlink:href="#hi-hive"></use></svg> ${_('Hive')}</a></li>
             % else:
             <li><a href="/${apps['beeswax'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-hive"></use></svg> ${_('Hive')}</a></li>
             % endif
           % endif
           % if 'impala' in apps:
             % if USE_NEW_EDITOR.get(): ## impala requires beeswax anyway
             <li><a href="${ url('notebook:editor') }?type=impala"><svg class="svg-app-icon"><use xlink:href="#hi-impala"></use></svg> ${_('Impala')}</a></li>
             % else:
             <li><a href="/${apps['impala'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-impala"></use></svg> ${_('Impala')}</a></li>
             % endif
           % endif
           % if 'rdbms' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="/${apps['rdbms'].display_name}"><img src="${ static(apps['rdbms'].icon_path) }" class="app-icon" alt="${ _('DBQuery icon') }"/> ${_('DB Query')}</a></li>
             % else:
             <li><a href="/${apps['rdbms'].display_name}"><img src="${ static(apps['rdbms'].icon_path) }" class="app-icon" alt="${ _('DBQuery icon') }"/> ${_('DB Query')}</a></li>
             % endif
           % endif
           % if 'pig' in apps:
             % if USE_NEW_EDITOR.get() and False:
             <li><a href="${ url('notebook:editor') }?type=pig"><svg class="svg-app-icon"><use xlink:href="#hi-pig"></use></svg> ${_('Pig')}</a></li>
             % else:
             <li><a href="/${apps['pig'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-pig"></use></svg> ${_('Pig')}</a></li>
             % endif
           % endif
           % if 'jobsub' in apps:
             <li><a href="/${apps['jobsub'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-job-designer"></use></svg> ${_('Job Designer')}</a></li>
           % endif
         </ul>
       </li>
       % elif query_apps[1] == 1:
           % if 'beeswax' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="${ url('notebook:editor') }?type=hive"><svg class="svg-app-icon"><use xlink:href="#hi-hive"></use></svg> ${_('Hive')}</a></li>
             % else:
             <li><a href="/${apps['beeswax'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-hive"></use></svg> ${_('Hive')}</a></li>
             % endif
           % elif 'impala' in apps:
             % if USE_NEW_EDITOR.get(): ## impala requires beeswax anyway
             <li><a href="${ url('notebook:editor') }?type=impala"><svg class="svg-app-icon"><use xlink:href="#hi-impala"></use></svg> ${_('Impala')}</a></li>
             % else:
             <li><a href="/${apps['impala'].display_name}"><svg class="svg-app-icon"><use xlink:href="#hi-impala"></use></svg> ${_('Impala')}</a></li>
             % endif
           % else:
           <li><a href="/${apps[query_apps[0]].display_name}"><i class="fa fa-terminal hideMoreThan950"></i><span class="hide950">${apps[query_apps[0]].nice_name}</span></a></li>
           % endif
       % endif
       % if 'beeswax' in apps:
        <%
          from notebook.conf import SHOW_NOTEBOOKS
        %>
        % if SHOW_NOTEBOOKS.get():
         <% from desktop.models import Document2, Document %>
         <% notebooks = [d.content_object.to_dict() for d in Document.objects.get_docs(user, Document2, extra='notebook') if not d.content_object.is_history] %>
         % if not notebooks:
           <li>
             <a title="${_('Notebook')}" data-rel="navigator-tooltip" href="${ url('notebook:new') }"><i class="fa fa-files-o hideMoreThan950"></i><span class="hide950">${_('Notebooks')}</span></a>
           </li>
         % else:
           <li class="dropdown">
             <a title="${_('Notebook')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
               <i class="fa fa-files-o inline-block hideMoreThan950"></i><span class="hide950">${_('Notebooks')}</span> <b class="caret"></b>
             </a>
             <ul role="menu" class="dropdown-menu">
               <li><a href="${ url('notebook:new') }"><i class="fa fa-fw fa-plus" style="vertical-align: middle"></i>${_('Notebook')}</a></li>
               <li><a href="${ url('notebook:notebooks') }"><i class="fa fa-fw fa-list" style="vertical-align: middle"></i>${_('Notebooks')}</a></li>
               <li class="divider"></li>
               % for notebook in notebooks:
                 <li>
                   <a href="${ url('notebook:notebook') }?notebook=${ notebook['id'] }">
                     <i class="fa fa-fw fa-file-text-o" style="vertical-align: middle"></i> ${ notebook['name'] |n }
                   </a>
                 </li>
               % endfor
             </ul>
           </li>
          % endif
        % endif
      % endif
       <%
         data_apps = count_apps(apps, ['metastore', 'hbase', 'sqoop', 'zookeeper']);
       %>
       % if data_apps[1] > 1:
       <li class="dropdown">
         <a title="${_('Manage data')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-database inline-block hideMoreThan950"></i><span class="hide950">Data Browsers</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'metastore' in apps:
             <li><a href="/${apps['metastore'].display_name}"><img src="${ static(apps['metastore'].icon_path) }" class="app-icon" alt="${ _('Metastore icon') }"/> ${_('Metastore Tables')}</a></li>
           % endif
           % if 'hbase' in apps:
             <li><a href="/${apps['hbase'].display_name}"><img src="${ static(apps['hbase'].icon_path) }" class="app-icon" alt="${ _('HBase icon') }"/> ${_('HBase')}</a></li>
           % endif
           % if 'sqoop' in apps:
             <li><a href="/${apps['sqoop'].display_name}"><img src="${ static(apps['sqoop'].icon_path) }" class="app-icon" alt="${ _('Sqoop icon') }"/> ${_('Sqoop Transfer')}</a></li>
           % endif
           % if 'zookeeper' in apps:
             <li><a href="/${apps['zookeeper'].display_name}"><img src="${ static(apps['zookeeper'].icon_path) }" class="app-icon" alt="${ _('ZooKeeper icon') }"/> ${_('ZooKeeper')}</a></li>
           % endif
         </ul>
       </li>
       % elif data_apps[1] == 1:
         <li><a href="/${apps[data_apps[0]].display_name}">${apps[data_apps[0]].nice_name}</a></li>
       % endif
       % if 'oozie' in apps:
       <li class="dropdown oozie">
         <a title="${_('Schedule with Oozie')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-random inline-block hideMoreThan950"></i><span class="hide950">Workflows</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           <li class="dropdown-submenu">
             <a href="${ url('oozie:index') }"><img src="${ static('oozie/art/icon_oozie_dashboard_48.png') }" class="app-icon"  alt="${ _('Oozie dashboard icon') }"/> ${_('Dashboards')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_oozie_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_oozie_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }"/> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_oozie_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundles icon') }" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % if not user.has_hue_permission(action="disable_editor_access", app="oozie") or is_admin(user):
           <% from oozie.conf import ENABLE_V2 %>
           % if not ENABLE_V2.get():
           <li class="dropdown-submenu">
             <a href="${ url('oozie:list_workflows') }"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" alt="${ _('Oozie editor icon') }" /> ${_('Editors')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % else:
           <li class="dropdown-submenu">
             <a href="${ url('oozie:list_editor_workflows') }"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" alt="${ _('Oozie editor icon') }" /> ${_('Editors')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_editor_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_editor_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_editor_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % endif
           % endif
         </ul>
       </li>
       % endif
       % if 'search' in apps:
         <% from dashboard.controller import DashboardController %>
         <% controller = DashboardController(user) %>
         <% collections = controller.get_shared_search_collections() %>
         % if not collections:
           <li>
             <a title="${_('Solr Search')}" data-rel="navigator-tooltip" href="${ url('search:index') }">${_('Search')}</a>
           </li>
         % else:
           <li class="dropdown">
             <a title="${_('Solr Search')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
               <i class="fa fa-search inline-block hideMoreThan950"></i><span class="hide950">${_('Search')}</span> <b class="caret"></b>
             </a>
             <ul role="menu" class="dropdown-menu">
               <li><a href="${ url('search:new_search') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-plus" style="vertical-align: middle"></i> ${ _('Dashboard') }</a></li>
               <li><a href="${ url('search:admin_collections') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-list" style="vertical-align: middle"></i>${ _('Dashboards') }</a></li>
               <%!
                 from indexer.conf import ENABLE_NEW_INDEXER
               %>
               % if ENABLE_NEW_INDEXER.get():
                 <li><a href="${ url('indexer:indexes') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-database" style="vertical-align: middle"></i> ${ _('Indexes') }</a></li>
                 <li><a href="${ url('indexer:indexes') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-plus" style="vertical-align: middle"></i> ${ _('Index') }</a></li>
               % else:
                 <li><a href="${ url('indexer:collections') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-database" style="vertical-align: middle"></i> ${ _('Indexes') }</a></li>
               % endif
               <li class="divider"></li>
               % for collection in collections:
                 <li>
                   <a href="${ url('search:index') }?collection=${ collection.id }">
                     <img src="${ static(controller.get_icon(collection.name)) }" class="app-icon" alt="${ _('Collection icon') }"/> ${ collection.name }
                   </a>
                 </li>
               % endfor
             </ul>
           </li>
         % endif
       % endif
       % if 'security' in apps:
         <% from security.conf import HIVE_V1, HIVE_V2, SOLR_V2 %>
         <li class="dropdown">
           <a title="${_('Hadoop Security')}" data-rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-unlock inline-block hideMoreThan950"></i><span class="hide950">Security</span> <b class="caret"></b></a>
           <ul role="menu" class="dropdown-menu">
             % if HIVE_V1.get():
             <li><a href="${ url('security:hive') }">&nbsp;<img src="/static/metastore/art/icon_metastore_48.png" class="app-icon" alt="${ _('Metastore icon') }"> ${_('Hive Tables')}</a></li>
             % endif
             % if HIVE_V2.get():
             <li><a href="${ url('security:hive2') }">&nbsp;<img src="/static/metastore/art/icon_metastore_48.png" class="app-icon" alt="${ _('Metastore icon') }"> ${_('Hive Tables v2')}</a></li>
             % endif
             % if SOLR_V2.get():
             <li><a href="${ url('security:solr') }">&nbsp;<i class="fa fa-database"></i>&nbsp;${_('Solr Collections')}</a></li>
             % endif
             <li><a href="${ url('security:hdfs') }">&nbsp;<i class="fa fa-file"></i>&nbsp;${_('File ACLs')}</a></li>
           </ul>
         </li>
       % endif
       % if other_apps:
       <li class="dropdown">
         <a href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-tasks inline-block hideMoreThan950"></i><span class="hide950">${_('Other apps')}</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % for other in other_apps:
             <li><a href="/${ other.display_name }"><img src="${ static(other.icon_path) }" class="app-icon" alt="${ _('App icon') }"/> ${ other.nice_name }</a></li>
           % endfor
         </ul>
       </li>
       % endif
     </ul>
   % endif

</div>
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

<div id="jHueNotify" class="alert alert-dismissible alert-warning hide">
  <button type="button" class="close" data-dismiss="alert">
    <span aria-hidden="true">&times;</span>
    <span class="sr-only">${ _('Close') }</span>
  </button>
  <p class="message"></p>
</div>
