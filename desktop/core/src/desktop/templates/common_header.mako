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
from desktop.conf import USE_NEW_EDITOR
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from metadata.conf import has_optimizer

home_url = url('desktop.views.home')
if USE_NEW_EDITOR.get():
  home_url = url('desktop.views.home2')
%>

<%namespace name="koComponents" file="/ko_components.mako" />

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
  <title>Hue ${get_nice_name(current_app, section)} ${get_title(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }" />
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="${ static('desktop/css/roboto.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/bootplus.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue3.css') }" rel="stylesheet">

  <style type="text/css">
    % if conf.CUSTOM.BANNER_TOP_HTML.get():
      body {
        display: none;
        visibility: hidden;
        padding-top: ${str(int(padding[:-2]) + 30) + 'px'};
      }
      .banner {
        height: 40px;
        width: 100%;
        padding: 0;
        position: fixed;
        top: 0;
        background-color: #F9F9F9;
        z-index: 1033;
      }
      .navigator {
        top: 30px!important;
      }
      .navbar-fixed-top {
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

  <script type="text/javascript" charset="utf-8">

    var LOGGED_USERNAME = '${ user.username }';
    var IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';
    var HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';

    // jHue plugins global configuration
    jHueFileChooserGlobals = {
      labels: {
        BACK: "${_('Back')}",
        SELECT_FOLDER: "${_('Select this folder')}",
        CREATE_FOLDER: "${_('Create folder')}",
        FOLDER_NAME: "${_('Folder name')}",
        CANCEL: "${_('Cancel')}",
        FILE_NOT_FOUND: "${_('The file has not been found')}",
        UPLOAD_FILE: "${_('Upload a file')}",
        FAILED: "${_('Failed')}"
      },
      user: "${ user.username }"
    };

    jHueHdfsTreeGlobals = {
      labels: {
        CREATE_FOLDER: "${_('Create folder')}",
        FOLDER_NAME: "${_('Folder name')}",
        CANCEL: "${_('Cancel')}"
      }
    };

    jHueTableExtenderGlobals = {
      labels: {
        GO_TO_COLUMN: "${_('Go to column:')}",
        PLACEHOLDER: "${_('column name...')}",
        LOCK: "${_('Click to lock this row')}",
        UNLOCK: "${_('Click to unlock this row')}"
      }
    };

    jHueTourGlobals = {
      labels: {
        AVAILABLE_TOURS: "${_('Available tours')}",
        NO_AVAILABLE_TOURS: "${_('None for this page.')}",
        MORE_INFO: "${_('Read more about it...')}",
        TOOLTIP_TITLE: "${_('Demo tutorials')}"
      }
    };

    LeafletGlobals = {
      layer: '${ leaflet['layer'] |n,unicode }',
      attribution: '${ leaflet['attribution'] |n,unicode }'
    };

    ApiHelperGlobals = {
      i18n: {
        errorLoadingDatabases: '${ _('There was a problem loading the databases') }',
        errorLoadingTablePreview: '${ _('There was a problem loading the preview') }'
      },
      user: '${ user.username }'
    }
  </script>

  <!--[if lt IE 9]>
  <script type="text/javascript">
    if (document.documentMode && document.documentMode < 9){
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>
  <![endif]-->

  <script type="text/javascript">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop.views.unsupported') }";
      }
    }

    // check for IE document modes
    if (document.documentMode && document.documentMode < 9){
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>

  <script src="${ static('desktop/js/hue.utils.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/jquery-2.1.1.min.js') }"></script>
  <script src="${ static('desktop/js/jquery.migration.js') }"></script>
  <script src="${ static('desktop/js/jquery.hdfsautocomplete.js') }" type="text/javascript" charset="utf-8"></script>
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
  <script src="${ static('desktop/js/jquery.scrollup.js') }"></script>
  <script src="${ static('desktop/js/jquery.tour.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.cookie.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.placeholder.min.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js') }"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.form.js') }"></script>
  <script src="${ static('desktop/js/jquery.nicescroll.js') }"></script>
  <script src="${ static('desktop/js/jquery.datatables.sorting.js') }"></script>
  <script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
  <script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>
  <script src="${ static('desktop/ext/js/fileuploader.js') }"></script>
  <script src="${ static('desktop/ext/js/filesize.min.js') }"></script>
  <script src="${ static('desktop/js/popover-extra-placements.js') }"></script>
  <script src="${ static('desktop/ext/js/moment-with-locales.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/knockout.min.js') }"></script>
  <script src="${ static('desktop/ext/js/knockout-mapping.min.js') }"></script>
  <script src="${ static('desktop/js/ko.hue-bindings.js') }"></script>

  ${ koComponents.all() }

  <script type="text/javascript" charset="utf-8">

    moment.locale(window.navigator.userLanguage || window.navigator.language);
    localeFormat = function (time) {
      var mTime = time;
      if (typeof ko !== 'undefined' && ko.isObservable(time)) {
        mTime = time();
      }
      try {
        mTime = new Date(mTime);
        if (moment(mTime).isValid()) {
          return moment.utc(mTime).format("L LT");
        }
      }
      catch (e) {
        return mTime;
      }
      return mTime;
    }

    //Add CSRF Token to all XHR Requests
    var xrhsend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function (data) {
    %if request and request.COOKIES and request.COOKIES.get('csrftoken','')!='':
      this.setRequestHeader('X-CSRFToken', "${request.COOKIES.get('csrftoken')}");
    %else:
      this.setRequestHeader('X-CSRFToken', "");
    %endif

      return xrhsend.apply(this, arguments);
    }

    $.fn.dataTableExt.sErrMode = "throw";

    // sets global apiHelper TTL
    $.totalStorage('hue.cacheable.ttl', ${conf.CUSTOM.CACHEABLE_TTL.get()});

    var IDLE_SESSION_TIMEOUT = -1;

    $(document).ready(function () {
      // forces IE's ajax calls not to cache
      if ($.browser.msie) {
        $.ajaxSetup({ cache: false });
      }

      // prevents framebusting and clickjacking
      if (self == top){
        $("body").css({
          'display': 'block',
          'visibility': 'visible'
        });
      }
      else {
        top.location = self.location;
      }

      %if conf.AUTH.IDLE_SESSION_TIMEOUT.get() > -1 and not skip_idle_timeout:
      IDLE_SESSION_TIMEOUT = ${conf.AUTH.IDLE_SESSION_TIMEOUT.get()};
      var idleTimer;
      function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(function () {
          // Check if logged out
          $.get('/desktop/debug/is_idle');
        }, (IDLE_SESSION_TIMEOUT * 1000) + 1000);
      }

      $(document).on('mousemove', resetIdleTimer);
      $(document).on('keydown', resetIdleTimer);
      $(document).on('click', resetIdleTimer);
      resetIdleTimer();
      %endif

      $("input, textarea").placeholder();
      $(".submitter").keydown(function (e) {
        if (e.keyCode == 13) {
          $(this).closest("form").submit();
        }
      }).change(function () {
          $(this).closest("form").submit();
      });

      $(".navbar .nav-tooltip").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[rel='tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[rel='navigator-tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      % if 'jobbrowser' in apps:
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
      var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

      function checkJobBrowserStatus(){
        $.post("/jobbrowser/jobs/", {
            "format": "json",
            "state": "running",
            "user": "${user.username}"
          },
          function(data) {
            if (data != null && data.jobs != null) {
              huePubSub.publish('jobbrowser.data', data.jobs);
              if (data.jobs.length > 0){
                $("#jobBrowserCount").removeClass("hide").text(data.jobs.length);
              }
              else {
                $("#jobBrowserCount").addClass("hide");
              }
            }
          checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
        }).fail(function () {
          window.clearTimeout(checkJobBrowserStatusIdx);
        });
      }
      huePubSub.subscribe('check.job.browser', checkJobBrowserStatus);
      % endif

      function openDropdown(which, timeout){
        var _this = which;
        var _timeout = timeout!=null?timeout:800;
        if ($(".navigator").find("ul.dropdown-menu:visible").length > 0) {
          _timeout = 10;
        }
        window.clearTimeout(closeTimeout);
        openTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator .nav-pills li.dropdown > ul.dropdown-menu").hide();
          $("[rel='navigator-tooltip']").tooltip("hide");
          _this.find("ul.dropdown-menu:eq(0)").show();
        }, _timeout);
      }

      var openTimeout, closeTimeout;
      $(".navigator ul.nav li.dropdown").on("click", function(){
        openDropdown($(this), 10);
      });
      $(".navigator ul.nav li.dropdown").hover(function () {
        openDropdown($(this));
      },
      function () {
        window.clearTimeout(openTimeout);
        closeTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator li a:focus").blur();
          $(".navigator").find("ul.dropdown-menu").hide();
        }, 1000);
      });

      function showSubmenu(menuElement) {
        $(".tooltip").remove();
        menuElement.data("lastShown", (new Date()).getTime())
        menuElement.show();
      }

      $(".navigator ul.nav li.dropdown-submenu a").on("mouseenter", function () {
        showSubmenu($(this).siblings(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu a img").on("mouseenter", function () {
        showSubmenu($(this).parent().siblings(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu").on("mouseenter", function () {
        $(this).siblings().find(".dropdown-menu").hide();
        showSubmenu($(this).find(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu").on("mouseleave", function () {
        var _lastShown = $(this).find(".dropdown-menu").data("lastShown");
        if (_lastShown == null || (new Date()).getTime() - _lastShown > 300) {
          var _el = $(this);
          _el.hideTimeout = window.setTimeout(function () {
            window.clearTimeout(_el.hideTimeout);
            _el.find(".dropdown-menu").hide();
          }, 50);
        }
      });

      var _skew = -1;
      $("[data-hover]").on("mouseover", function(){
        var _this = $(this);
        _skew = window.setTimeout(function(){
          _this.attr("src", _this.data("hover"));
        }, 3000);
      });

      $("[data-hover]").on("mouseout", function(){
        $(this).attr("src", $(this).data("orig"));
        window.clearTimeout(_skew);
      });

      window.hueDebug = {
        viewModel: function (element) {
          return ko.dataFor(element || document.body);
        }
      }
    });
  </script>
</head>
<body>

% if conf.CUSTOM.BANNER_TOP_HTML.get():
  <div id="banner-top" class="banner">
    ${ conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
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
      % if not is_s3_enabled:
      <li class="hide1380">
        <a title="${_('Manage HDFS')}" rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}">
          <i class="fa fa-file"></i>&nbsp;${_('File Browser')}&nbsp;
        </a>
      </li>
      % else:
        <li class="dropdown hide1380">
          <a title="${_('File Browsers')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
            <i class="fa fa-file"></i>&nbsp;${_('File Browsers')} <b class="caret"></b>
          </a>
          <ul role="menu" class="dropdown-menu">
            <li><a href="/${apps['filebrowser'].display_name}">
              <i class="fa fa-fw fa-file" style="vertical-align: middle"></i>${_('HDFS Browser')}</a>
            </li>
            <li><a href="/${apps['filebrowser'].display_name}/view=S3A://">
              <i class="fa fa-fw fa-cubes" style="vertical-align: middle"></i>${_('S3 Browser')}</a>
            </li>
          </ul>
        </li>
      % endif
      <li class="hideMoreThan1380">
        <a title="${_('HDFS Browser')}" rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}">
          <i class="fa fa-file"></i>
        </a>
      </li>
      <li class="hideMoreThan1380">
        % if is_s3_enabled:
          <a title="${_('S3 Browser')}" rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}/view=S3A://">
            <i class="fa fa-cubes"></i>
          </a>
        % endif
      </li>
    % endif
    % if 'jobbrowser' in apps:
      <li class="hide1380"><a title="${_('Manage jobs')}" rel="navigator-tooltip" href="/${apps['jobbrowser'].display_name}"><i class="fa fa-list-alt"></i>&nbsp;${_('Job Browser')}&nbsp;<span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a></li>
      <li class="hideMoreThan1380"><a title="${_('Job Browser')}" rel="navigator-tooltip" href="/${apps['jobbrowser'].display_name}"><i class="fa fa-list-alt"></i></a></li>
      <% from jobbrowser.conf import ENABLE_V2 %>
      % if ENABLE_V2.get():
        <li class="hide1380"><a title="${_('Manage jobs')}" rel="navigator-tooltip" href="/jobbrowser/apps">
          <i class="fa fa-list-alt"></i>&nbsp;${_('Job Browser 2')}&nbsp;<span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a>
        </li>
        <li class="hideMoreThan1380"><a title="${_('Job Browser 2')}" rel="navigator-tooltip" href="/jobbrowser/apps"><i class="fa fa-list-alt"></i></a></li>
      % endif
    % endif
    <%
      view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or user.is_superuser
    %>
    <li class="dropdown">
      <a title="${ _('Administration') if view_profile else '' }" href="#" rel="navigator-tooltip" data-toggle="dropdown" class="dropdown-toggle">
        <i class="fa fa-cogs"></i>&nbsp;${user.username}&nbsp;
        % if view_profile:
          <b class="caret"></b>
        % endif
      </a>
      % if view_profile:
      <ul class="dropdown-menu pull-right">
        <li>
          <a href="${ url('useradmin.views.edit_user', username=user.username) }"><i class="fa fa-key"></i>&nbsp;&nbsp;
            % if is_ldap_setup:
              ${_('View Profile')}
            % else:
              ${_('Edit Profile')}
            % endif
          </a>
        </li>
        % if user.is_superuser:
          <li><a href="${ url('useradmin.views.list_users') }"><i class="fa fa-group"></i>&nbsp;&nbsp;${_('Manage Users')}</a></li>
        % endif
      </ul>
    % endif
    </li>
    % if 'help' in apps:
    <li><a title="${_('Documentation')}" rel="navigator-tooltip" href="/help"><i class="fa fa-question-circle"></i></a></li>
    % endif
    <li id="jHueTourFlagPlaceholder"></li>
    <li><a title="${_('Sign out')}" rel="navigator-tooltip" href="/accounts/logout/"><i class="fa fa-sign-out"></i></a></li>
  </ul>
  % else:
  <ul class="nav nav-pills" style="margin-right: 40px">
    <li id="jHueTourFlagPlaceholder"></li>
  </ul>
  % endif

  </div>
    <a class="brand nav-tooltip pull-left" title="${_('About Hue')}" rel="navigator-tooltip" href="/about"><img src="${ static('desktop/art/hue-logo-mini-white.png') }" data-orig="${ static('desktop/art/hue-logo-mini-white.png') }" data-hover="${ static('desktop/art/hue-logo-mini-white-hover.png') }" /></a>
    % if user.is_authenticated() and section != 'login':
     <ul class="nav nav-pills pull-left">
       <li><a title="${_('My documents')}" rel="navigator-tooltip" href="${ home_url }" style="padding-bottom:2px!important"><i class="fa fa-home" style="font-size: 19px"></i></a></li>
       <%
         query_apps = count_apps(apps, ['beeswax', 'impala', 'rdbms', 'pig', 'jobsub', 'spark']);
       %>
       % if query_apps[1] > 1:
       <li class="dropdown oozie">
         <a title="${_('Query data')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-terminal inline-block hideMoreThan950"></i><span class="hide950">Query Editors</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'beeswax' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="${ url('notebook:editor') }?type=hive"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive')}</a></li>
             % else:
             <li><a href="/${apps['beeswax'].display_name}"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive')}</a></li>
             % endif
           % endif
           % if 'impala' in apps:
             % if USE_NEW_EDITOR.get(): ## impala requires beeswax anyway
             <li><a href="${ url('notebook:editor') }?type=impala"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala')}</a></li>
             % else:
             <li><a href="/${apps['impala'].display_name}"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala')}</a></li>
             % endif
           % endif
           % if 'rdbms' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="/${apps['rdbms'].display_name}"><img src="${ static(apps['rdbms'].icon_path) }" class="app-icon"/> ${_('DB Query')}</a></li>
             % else:
             <li><a href="/${apps['rdbms'].display_name}"><img src="${ static(apps['rdbms'].icon_path) }" class="app-icon"/> ${_('DB Query')}</a></li>
             % endif
           % endif
           % if 'pig' in apps:
             % if USE_NEW_EDITOR.get() and False:
             <li><a href="${ url('notebook:editor') }?type=pig"><img src="${ static(apps['pig'].icon_path) }" class="app-icon"/> ${_('Pig')}</a></li>
             % else:
             <li><a href="/${apps['pig'].display_name}"><img src="${ static(apps['pig'].icon_path) }" class="app-icon"/> ${_('Pig')}</a></li>
             % endif
           % endif
           % if 'jobsub' in apps:
             <li><a href="/${apps['jobsub'].display_name}"><img src="${ static(apps['jobsub'].icon_path) }" class="app-icon"/> ${_('Job Designer')}</a></li>
           % endif
         </ul>
       </li>
       % elif query_apps[1] == 1:
          <li><a href="/${apps[query_apps[0]].display_name}"><i class="fa fa-terminal hideMoreThan950"></i><span class="hide950">${apps[query_apps[0]].nice_name}</span></a></li>
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
             <a title="${_('Notebook')}" rel="navigator-tooltip" href="${ url('notebook:new') }"><i class="fa fa-files-o hideMoreThan950"></i><span class="hide950">${_('Notebooks')}</span></a>
           </li>
         % else:
           <li class="dropdown">
             <a title="${_('Notebook')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
               <i class="fa fa-files-o inline-block hideMoreThan950"></i><span class="hide950">${_('Notebooks')}</span> <b class="caret"></b>
             </a>
             <ul role="menu" class="dropdown-menu">
               <li><a href="${ url('notebook:new') }"><i class="fa fa-fw fa-plus" style="vertical-align: middle"></i>${_('Notebook')}</a></li>
               <li><a href="${ url('notebook:notebooks') }"><i class="fa fa-fw fa-tags" style="vertical-align: middle"></i>${_('Notebooks')}</a></li>
               <li class="divider"></li>
               % for notebook in notebooks:
                 <li>
                   <a href="${ url('notebook:notebook') }?notebook=${ notebook['id'] }">
                     <i class="fa fa-file-text-o" style="vertical-align: middle"></i> ${ notebook['name'] |n }
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
         <a title="${_('Manage data')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-database inline-block hideMoreThan950"></i><span class="hide950">Data Browsers</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'metastore' in apps:
             <li><a href="/${apps['metastore'].display_name}"><img src="${ static(apps['metastore'].icon_path) }" class="app-icon"/> ${_('Metastore Tables')}</a></li>
           % endif
           % if 'hbase' in apps:
             <li><a href="/${apps['hbase'].display_name}"><img src="${ static(apps['hbase'].icon_path) }" class="app-icon"/> ${_('HBase')}</a></li>
           % endif
           % if 'sqoop' in apps:
             <li><a href="/${apps['sqoop'].display_name}"><img src="${ static(apps['sqoop'].icon_path) }" class="app-icon"/> ${_('Sqoop Transfer')}</a></li>
           % endif
           % if 'zookeeper' in apps:
             <li><a href="/${apps['zookeeper'].display_name}"><img src="${ static(apps['zookeeper'].icon_path) }" class="app-icon"/> ${_('ZooKeeper')}</a></li>
           % endif
         </ul>
       </li>
       % elif data_apps[1] == 1:
         <li><a href="/${apps[data_apps[0]].display_name}">${apps[data_apps[0]].nice_name}</a></li>
       % endif
       % if 'oozie' in apps:
       <li class="dropdown oozie">
         <a title="${_('Schedule with Oozie')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-random inline-block hideMoreThan950"></i><span class="hide950">Workflows</span> <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           <li class="dropdown-submenu">
             <a href="${ url('oozie:index') }"><img src="${ static('oozie/art/icon_oozie_dashboard_48.png') }" class="app-icon" /> ${_('Dashboards')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_oozie_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_oozie_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_oozie_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % if not user.has_hue_permission(action="disable_editor_access", app="oozie") or user.is_superuser:
           <% from oozie.conf import ENABLE_V2 %>
           % if not ENABLE_V2.get():
           <li class="dropdown-submenu">
             <a href="${ url('oozie:list_workflows') }"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" /> ${_('Editors')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % else:
           <li class="dropdown-submenu">
             <a href="${ url('oozie:list_editor_workflows') }"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" /> ${_('Editors')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_editor_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_editor_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_editor_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           % endif
           % endif
         </ul>
       </li>
       % endif
       % if 'search' in apps:
         <% from search.search_controller import SearchController %>
         <% controller = SearchController(user) %>
         <% collections = controller.get_shared_search_collections() %>
         % if not collections:
           <li>
             <a title="${_('Solr Search')}" rel="navigator-tooltip" href="${ url('search:index') }">${_('Search')}</a>
           </li>
         % else:
           <li class="dropdown">
             <a title="${_('Solr Search')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">
               <i class="fa fa-search inline-block hideMoreThan950"></i><span class="hide950">${_('Search')}</span> <b class="caret"></b>
             </a>
             <ul role="menu" class="dropdown-menu">
               % if 'indexer' in apps or 'search' in apps:
                 % if 'search' in apps:
                 <li><a href="${ url('search:new_search') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-plus" style="vertical-align: middle"></i> ${ _('Dashboard') }</a></li>
                 <li><a href="${ url('search:admin_collections') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-tags" style="vertical-align: middle"></i>${ _('Dashboards') }</a></li>
                 % endif
                 % if 'indexer' in apps:
                 <li><a href="${ url('indexer:collections') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-database" style="vertical-align: middle"></i> ${ _('Indexes') }</a></li>
                 <%!
                 from indexer.conf import ENABLE_NEW_INDEXER
                 %>
                 % if hasattr(ENABLE_NEW_INDEXER, 'get') and ENABLE_NEW_INDEXER.get():
                 <li><a href="${ url('indexer:indexer') }" style="height: 24px; line-height: 24px!important;"><i class="fa fa-plus" style="vertical-align: middle"></i> ${ _('Index') }</a></li>
                 % endif
                 % endif
                 <li class="divider"></li>
               % endif
               % for collection in collections:
                 <li>
                   <a href="${ url('search:index') }?collection=${ collection.id }">
                     <img src="${ static(controller.get_icon(collection.name)) }" class="app-icon"/> ${ collection.name }
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
           <a title="${_('Hadoop Security')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-unlock inline-block hideMoreThan950"></i><span class="hide950">Security</span> <b class="caret"></b></a>
           <ul role="menu" class="dropdown-menu">
             % if HIVE_V1.get():
             <li><a href="${ url('security:hive') }">&nbsp;<img src="/static/metastore/art/icon_metastore_48.png" class="app-icon"> ${_('Hive Tables')}</a></li>
             % endif
             % if HIVE_V2.get():
             <li><a href="${ url('security:hive2') }">&nbsp;<img src="/static/metastore/art/icon_metastore_48.png" class="app-icon"> ${_('Hive Tables v2')}</a></li>
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
             <li><a href="/${ other.display_name }"><img src="${ static(other.icon_path) }" class="app-icon"/> ${ other.nice_name }</a></li>
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

<div id="jHueNotify" class="alert hide">
    <button class="close">&times;</button>
    <div class="message"></div>
</div>
