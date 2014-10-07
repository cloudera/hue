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
import urllib
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

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

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Hue ${get_nice_name(current_app, section)} ${get_title(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/x-icon" href="/static/art/favicon.ico" />
  <meta name="description" content="">
  <meta name="author" content="">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">

  <link href="/static/ext/css/bootplus.css" rel="stylesheet">
  <link href="/static/ext/css/font-awesome.min.css" rel="stylesheet">
  <link href="/static/css/hue3.css" rel="stylesheet">
  <link href="/static/ext/css/fileuploader.css" rel="stylesheet">

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
    % else:
      body {
        display: none;
        visibility: hidden;
        padding-top: ${padding};
      }
    % endif
  </style>

  <script type="text/javascript" charset="utf-8">

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
        PLACEHOLDER: "${_('column name...')}"
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

  </script>

  <!--[if lt IE 9]>
  <script type="text/javascript">
    location.href = "${ url('desktop.views.unsupported') }";
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
  </script>

  <script src="/static/js/hue.utils.js"></script>
  <script src="/static/ext/js/jquery/jquery-2.1.1.min.js"></script>
  <script src="/static/js/jquery.migration.js"></script>
  <script src="/static/js/jquery.filechooser.js"></script>
  <script src="/static/js/jquery.selector.js"></script>
  <script src="/static/js/jquery.delayedinput.js"></script>
  <script src="/static/js/jquery.rowselector.js"></script>
  <script src="/static/js/jquery.notify.js"></script>
  <script src="/static/js/jquery.titleupdater.js"></script>
  <script src="/static/js/jquery.tablescroller.js"></script>
  <script src="/static/js/jquery.tableextender.js"></script>
  <script src="/static/js/jquery.scrollup.js"></script>
  <script src="/static/js/jquery.tour.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.total-storage.min.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.placeholder.min.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js"></script>
  <script src="/static/js/jquery.datatables.sorting.js"></script>
  <script src="/static/ext/js/bootstrap.min.js"></script>
  <script src="/static/ext/js/bootstrap-better-typeahead.min.js"></script>
  <script src="/static/ext/js/fileuploader.js"></script>
  <script src="/static/js/popover-extra-placements.js"></script>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function () {
      // forces IE's ajax calls not to cache
      if ($.browser.msie) {
        $.ajaxSetup({ cache: false });
      }

      //Add CSRF Token to all XHR Requests
      var csrftoken = $.cookie('csrftoken');
      function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      }

      var xrhsend = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.send = function(data) {
        this.setRequestHeader('X-CSRFToken', csrftoken);
        return xrhsend.apply(this, arguments);
      }
      /////

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
      window.setTimeout(checkJobBrowserStatus, 10);

      function checkJobBrowserStatus(){
        $.getJSON("/${apps['jobbrowser'].display_name}/?format=json&state=running&user=${user.username}", function(data){
          if (data != null){
            if (data.length > 0){
              $("#jobBrowserCount").removeClass("hide").text(data.length);
            }
            else {
              $("#jobBrowserCount").addClass("hide");
            }
          }
          window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
        }).fail(function () {
          window.clearTimeout(checkJobBrowserStatus);
        });
      }
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
          $(".navigator ul.dropdown-menu").hide();
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
        var _this = $(this);
        window.clearTimeout(openTimeout);
        closeTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator li a:focus").blur();
          $(".navigator").find("ul.dropdown-menu").hide();
        }, 1000);
      });
      $(".navigator ul.nav li.dropdown-submenu").hover(function () {
        $(this).find(".dropdown-menu").show();
      },
      function () {
        $(this).find(".dropdown-menu").hide();
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

<div class="navigator">
  <div class="pull-right">

  % if user.is_authenticated() and section != 'login':
  <ul class="nav nav-pills">
    <li class="divider-vertical"></li>
    % if 'filebrowser' in apps:
    <li><a title="${_('Manage HDFS')}" rel="navigator-tooltip" href="/${apps['filebrowser'].display_name}"><i class="fa fa-file"></i><span class="hideable">&nbsp;${_('File Browser')}&nbsp;</span></a></li>
    % endif
    % if 'jobbrowser' in apps:
    <li><a title="${_('Manage jobs')}" rel="navigator-tooltip" href="/${apps['jobbrowser'].display_name}"><i class="fa fa-list-alt"></i><span class="hideable">&nbsp;${_('Job Browser')}&nbsp;</span><span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a></li>
    % endif
    <li class="dropdown">
      <a title="${ _('Administration') }" rel="navigator-tooltip" href="index.html#" data-toggle="dropdown" class="dropdown-toggle"><i class="fa fa-cogs"></i>&nbsp;<span class="hideable">${user.username}&nbsp;</span><b class="caret"></b></a>
      <ul class="dropdown-menu">
        <li><a href="${ url('useradmin.views.edit_user', username=urllib.quote(user.username)) }"><i class="fa fa-key"></i>&nbsp;&nbsp;${_('Edit Profile')}</a></li>
        % if user.is_superuser:
          <li><a href="${ url('useradmin.views.list_users') }"><i class="fa fa-group"></i>&nbsp;&nbsp;${_('Manage Users')}</a></li>
        % endif
      </ul>
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
    <a class="brand nav-tooltip pull-left" title="${_('About Hue')}" rel="navigator-tooltip" href="/about"><img src="/static/art/hue-logo-mini-white.png" data-orig="/static/art/hue-logo-mini-white.png" data-hover="/static/art/hue-logo-mini-white-hover.png" /></a>
    % if user.is_authenticated() and section != 'login':
     <ul class="nav nav-pills pull-left">
       <li><a title="${_('My documents')}" rel="navigator-tooltip" href="${ url('desktop.views.home') }" style="padding-bottom:2px!important"><i class="fa fa-home" style="font-size: 19px"></i></a></li>        
       <%
         query_apps = count_apps(apps, ['beeswax', 'impala', 'rdbms', 'pig', 'jobsub', 'spark']);
       %>
       % if query_apps[1] > 1:
       <li class="dropdown">
         <a title="${_('Query data')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Query Editors')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'beeswax' in apps:
           <li><a href="/${apps['beeswax'].display_name}"><img src="${ apps['beeswax'].icon_path }" class="app-icon"/> ${_('Hive')}</a></li>
           % endif
           % if 'impala' in apps:
           <li><a href="/${apps['impala'].display_name}"><img src="${ apps['impala'].icon_path }" class="app-icon"/> ${_('Impala')}</a></li>
           % endif
           % if 'rdbms' in apps:
           <li><a href="/${apps['rdbms'].display_name}"><img src="${ apps['rdbms'].icon_path }" class="app-icon"/> ${_('DB Query')}</a></li>
           % endif
           % if 'pig' in apps:
           <li><a href="/${apps['pig'].display_name}"><img src="${ apps['pig'].icon_path }" class="app-icon"/> ${_('Pig')}</a></li>
           % endif
           % if 'jobsub' in apps:
           <li><a href="/${apps['jobsub'].display_name}"><img src="${ apps['jobsub'].icon_path }" class="app-icon"/> ${_('Job Designer')}</a></li>
           % endif
           % if 'spark' in apps:
           <li><a href="/${apps['spark'].display_name}"><img src="${ apps['spark'].icon_path }" class="app-icon"/> ${_('Spark')}</a></li>
           % endif
         </ul>
       </li>
       % elif query_apps[1] == 1:
          <li><a href="/${apps[query_apps[0]].display_name}">${apps[query_apps[0]].nice_name}</a></li>
       % endif
       <%
         data_apps = count_apps(apps, ['metastore', 'hbase', 'sqoop', 'zookeeper']);
       %>
       % if data_apps[1] > 1:
       <li class="dropdown">
         <a title="${_('Manage data')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Data Browsers')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'metastore' in apps:
           <li><a href="/${apps['metastore'].display_name}"><img src="${ apps['metastore'].icon_path }" class="app-icon"/> ${_('Metastore Tables')}</a></li>
           % endif
           % if 'hbase' in apps:
           <li><a href="/${apps['hbase'].display_name}"><img src="${ apps['hbase'].icon_path }" class="app-icon"/> ${_('HBase')}</a></li>
           % endif
           % if 'sqoop' in apps:
           <li><a href="/${apps['sqoop'].display_name}"><img src="${ apps['sqoop'].icon_path }" class="app-icon"/> ${_('Sqoop Transfer')}</a></li>
           % endif
           % if 'zookeeper' in apps:
           <li><a href="/${apps['zookeeper'].display_name}"><img src="${ apps['zookeeper'].icon_path }" class="app-icon"/> ${_('ZooKeeper')}</a></li>
           % endif
         </ul>
       </li>
       % elif data_apps[1] == 1:
         <li><a href="/${apps[data_apps[0]].display_name}">${apps[data_apps[0]].nice_name}</a></li>
       % endif
       % if 'oozie' in apps:
       <li class="dropdown">
         <a title="${_('Schedule with Oozie')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Workflows')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           <li class="dropdown-submenu">
             <a href="${ url('oozie:index') }"><img src="/oozie/static/art/icon_oozie_dashboard_48.png" class="app-icon" /> ${_('Dashboards')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_oozie_workflows')}"><img src="/oozie/static/art/icon_oozie_workflow_48.png" class="app-icon"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_oozie_coordinators')}"><img src="/oozie/static/art/icon_oozie_coordinator_48.png" class="app-icon" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_oozie_bundles')}"><img src="/oozie/static/art/icon_oozie_bundle_48.png" class="app-icon" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
           <li class="dropdown-submenu">
             <a href="${ url('oozie:list_workflows') }"><img src="/oozie/static/art/icon_oozie_editor_48.png" class="app-icon" /> ${_('Editors')}</a>
             <ul class="dropdown-menu">
               <li><a href="${url('oozie:list_workflows')}"><img src="/oozie/static/art/icon_oozie_workflow_48.png" class="app-icon"/> ${_('Workflows')}</a></li>
               <li><a href="${url('oozie:list_coordinators')}"><img src="/oozie/static/art/icon_oozie_coordinator_48.png" class="app-icon" /> ${_('Coordinators')}</a></li>
               <li><a href="${url('oozie:list_bundles')}"><img src="/oozie/static/art/icon_oozie_bundle_48.png" class="app-icon" /> ${_('Bundles')}</a></li>
             </ul>
           </li>
         </ul>
       </li>
       % endif
       % if 'search' in apps:
         <% from search.search_controller import SearchController %>
         <% collections = SearchController(user).get_search_collections() %>
         % if not collections:
           <li>
             <a title="${_('Solr Search')}" rel="navigator-tooltip" href="${ url('search:index') }">Search</a>
           </li>
         % else:
           <li class="dropdown">
             <a title="${_('Solr Search')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Search')} <b class="caret"></b></a>
             <ul role="menu" class="dropdown-menu">
               % for collection in collections:
               <li><a href="${ url('search:index') }?collection=${ collection.id }"><img src="${ collection.icon }" class="app-icon"/> ${ collection.label }</a></li>
               % endfor
               % if 'indexer' in apps:
                 <li class="divider"></li>
                 <li><a href="${ url('indexer:collections') }"><i class="fa fa-database"></i> ${ _('Indexes') }</a></li>
               % endif
             </ul>
           </li>
         % endif
       % endif
       % if 'security' in apps:
         <li class="dropdown">
           <a title="${_('Hadoop Security')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Security')} <b class="caret"></b></a>
           <ul role="menu" class="dropdown-menu">
             <li><a href="${ url('security:hive') }">&nbsp;<i class="fa fa-database"></i>&nbsp;&nbsp;${_('Sentry Tables')}</a></li>
             <li><a href="${ url('security:hdfs') }">&nbsp;<i class="fa fa-file"></i>&nbsp;&nbsp;${_('File ACLs')}</a></li>
           </ul>
         </li>
       % endif
       % if other_apps:
       <li class="dropdown">
         <a href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Other apps')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % for other in other_apps:
             <li><a href="/${ other.display_name }"><img src="${ other.icon_path }" class="app-icon"/> ${ other.nice_name }</a></li>
           % endfor
         </ul>
       </li>
       % endif
     </ul>
   % endif

</div>

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
    <span class="message"></span>
</div>

