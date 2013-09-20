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
        padding-top: ${str(int(padding[:-2]) + 40) + 'px'};
      }
      .banner {
        height: 40px;
        padding: 0;
      }
      .subnav-fixed {
        top: 80px;
      }
    % else:
      body {
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
        MORE_INFO: "${_('Read more about it...')}"
      }
    };

  </script>

  <script src="/static/ext/js/jquery/jquery-2.0.2.min.js"></script>
  <script src="/static/js/jquery.migration.js"></script>
  <script src="/static/js/jquery.filechooser.js"></script>
  <script src="/static/js/jquery.selector.js"></script>
  <script src="/static/js/jquery.alert.js"></script>
  <script src="/static/js/jquery.rowselector.js"></script>
  <script src="/static/js/jquery.notify.js"></script>
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
  <script src="/static/ext/js/fileuploader.js"></script>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function () {
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

      % if 'jobbrowser' in apps:
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
      window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);

      function checkJobBrowserStatus(){
        $.getJSON("/${apps['jobbrowser'].display_name}/?format=json&state=running&user=${user.username}&rnd="+Math.random(), function(data){
          if (data != null){
            if (data.length > 0){
              $("#jobBrowserCount").removeClass("hide").text(data.length);
            }
            else {
              $("#jobBrowserCount").addClass("hide");
            }
          }
          window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
        });
      }
      % endif

      var openTimeout, closeTimeout;
      $(".navigator ul.nav li.dropdown").hover(function () {
        var _this = $(this);
        var _timeout = 500;
        if ($(".navigator").find("ul.dropdown-menu:visible").length > 0) {
          _timeout = 10;
        }
        window.clearTimeout(closeTimeout);
        openTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator ul.dropdown-menu").hide();
          _this.find("ul.dropdown-menu").show();
        }, _timeout);
      },
      function () {
        var _this = $(this);
        window.clearTimeout(openTimeout);
        closeTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator").find("ul.dropdown-menu").hide();
        }, 500);
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
    ${ conf.CUSTOM.BANNER_TOP_HTML.get() }
  </div>
% endif

<div class="navigator">
  <div class="pull-right">
  % if user.is_authenticated():
  <ul class="nav nav-pills">
    <li class="divider-vertical"></li>
    % if 'filebrowser' in apps:
    <li><a title="${_('Manage HDFS')}" href="/${apps['filebrowser'].display_name}"><i class="icon-file"></i>&nbsp;${_('File Browser')} &nbsp;</a></li>
    % endif
    % if 'jobbrowser' in apps:
    <li><a title="${_('Manage jobs')}" href="/${apps['jobbrowser'].display_name}"><i class="icon-list-alt"></i>&nbsp;${_('Job Browser')} &nbsp;<span id="jobBrowserCount" class="badge badge-warning hide" style="padding-top:0;padding-bottom: 0"></span></a></li>
    % endif
    <li class="dropdown">
      <a title="${ _('Administration') }" href="index.html#" data-toggle="dropdown" class="dropdown-toggle"><i class="icon-cogs"></i>&nbsp;&nbsp;<b class="caret"></b></a>
      <ul class="dropdown-menu">
        <li><a href="${ url('useradmin.views.edit_user', username=urllib.quote(user.username)) }"><i class="icon-key"></i>&nbsp;&nbsp;${_('Change Password')}</a></li>
        %if user.is_superuser:
        <li><a href="${ url('useradmin.views.list_users') }"><i class="icon-group"></i>&nbsp;&nbsp;${_('Manage users')}</a></li>
        %endif
      </ul>
    </li>
    <li><a title="${_('Sign out')}" data-placement="left" href="/accounts/logout/"><i class="icon-signout"></i>&nbsp;&nbsp;${user.username}</a></li>
    <li><a title="${_('Documentation')}" data-placement="left" href="/help"><i class="icon-question-sign"></i></a></li>
    <li id="jHueTourFlagPlaceholder"></li>
  </ul>
  % endif
  </div>
    <a class="brand nav-tooltip pull-left" title="${_('About Hue')}" href="/about"><img src="/static/art/hue-logo-mini-white.png" data-orig="/static/art/hue-logo-mini-white.png" data-hover="/static/art/hue-logo-mini-white-hover.png"/></a>
     <ul class="nav nav-pills pull-left">
       <li><a title="${_('My documents')}" href="/home"><i class="icon-home" style="font-size: 19px"></i></a></li>
       <li class="dropdown">
         <a title="${_('Query data')}" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Query Editors')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'beeswax' in apps:
           <li><a href="/${apps['beeswax'].display_name}"><img src="${ apps['beeswax'].icon_path }"/> ${_('Hive')}</a></li>
           % endif
           % if 'impala' in apps:
           <li><a href="/${apps['impala'].display_name}"><img src="${ apps['impala'].icon_path }"/> ${_('Impala')}</a></li>
           % endif
           % if 'pig' in apps:
           <li><a href="/${apps['pig'].display_name}"><img src="${ apps['pig'].icon_path }"/> ${_('Pig')}</a></li>
           % endif
           % if 'jobsub' in apps:
           <li><a href="/${apps['jobsub'].display_name}"><img src="${ apps['jobsub'].icon_path }"/> ${_('Job Designer')}</a></li>
           % endif
         </ul>
       </li>
       <li class="dropdown">
         <a title="${_('Manage data')}" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Data Browsers')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % if 'metastore' in apps:
           <li><a href="/${apps['metastore'].display_name}"><img src="${ apps['metastore'].icon_path }"/> ${_('Metastore Tables')}</a></li>
           % endif
           % if 'hbase' in apps:
           <li><a href="/${apps['hbase'].display_name}"><img src="${ apps['hbase'].icon_path }"/> ${_('HBase')}</a></li>
           % endif
           % if 'sqoop' in apps:
           <li><a href="/${apps['sqoop'].display_name}"><img src="${ apps['sqoop'].icon_path }"/> ${_('Sqoop Transfer')}</a></li>
           % endif
           % if 'zookeeper' in apps:
           <li><a href="/${apps['zookeeper'].display_name}"><img src="${ apps['zookeeper'].icon_path }"/> ${_('ZooKeeper')}</a></li>
           % endif
         </ul>
       </li>
       % if 'oozie' in apps:
       <li class="dropdown">
         <a title="${_('Schedule with Oozie')}" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Workflows')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           <li><a href="${ url('oozie:index') }"><img src="${ apps['oozie'].icon_path }"/> ${_('Dashboard')}</a></li>
           <li><a href="${ url('oozie:list_workflows') }"><img src="${ apps['oozie'].icon_path }"/> ${_('Editor')}</a></li>
         </ul>
       </li>
       % endif
       % if 'search' in apps:
       <li>
         <a title="${_('Solr Search')}" href="${ url('search:index') }">${_('Search')}</a>
       </li>
       % endif
       % if other_apps:
       <li class="dropdown">
         <a title="${_('Other apps')}" href="#" data-toggle="dropdown" class="dropdown-toggle">${_('Other apps')} <b class="caret"></b></a>
         <ul role="menu" class="dropdown-menu">
           % for other in other_apps:
             <li><a href="/${ other.display_name }"><img src="${ other.icon_path }"/> ${ other.nice_name }</a></li>
           % endfor
         </ul>
       </li>
       % endif
     </ul>

</div>

<div id="jHueNotify" class="alert hide">
    <button class="close">&times;</button>
    <span class="message"></span>
</div>

