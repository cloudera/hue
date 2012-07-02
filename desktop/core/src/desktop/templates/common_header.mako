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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${smart_unicode(title) | h}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="/static/ext/css/bootstrap.min.css" rel="stylesheet">
  <link href="/static/css/hue2.css" rel="stylesheet">
  <link href="/static/ext/css/fileuploader.css" rel="stylesheet">

  <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
  <!--[if lt IE 9]>
  <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
  <![endif]-->

  <style type="text/css">
    body {
      padding-top: ${padding};
    }
  </style>

  <script src="/static/ext/js/jquery/jquery-1.7.1.min.js"></script>
  <script src="/static/js/Source/jHue/jquery.showusername.js"></script>
  <script src="/static/js/Source/jHue/jquery.filechooser.js"></script>
  <script src="/static/js/Source/jHue/jquery.selector.js"></script>
  <script src="/static/js/Source/jHue/jquery.alert.js"></script>
  <script src="/static/js/Source/jHue/jquery.rowselector.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.simpleplaceholder.js"></script>
  <script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js"></script>
  <script src="/static/js/Source/jHue/jquery.datatables.sorting.js"></script>
  <script src="/static/ext/js/bootstrap.min.js"></script>
  <script src="/static/ext/js/fileuploader.js"></script>

  <script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
      $("#username").jHueUsername({
        onLoad: function(user){
            $(".userProfile").attr("href","/useradmin/users/edit/"+user.username);
            $("#usernameDropdown").show();
        }
      });
      $("input:text[placeholder]").simplePlaceholder();
      $(".submitter").keydown(function(e){
        if (e.keyCode==13){
          $(this).closest("form").submit();
        }
      }).change(function(){
        $(this).closest("form").submit();
      });
      $("#checkConfig").load("/debug/check_config_ajax");
      $(".navbar .nav-tooltip").tooltip({
        delay:0,
        placement:'bottom'});
    });
  </script>
</head>
<body>

<%def name="is_selected(section, matcher)">
  %if section == matcher:
    class="active"
  %endif
</%def>

<div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container-fluid">
        <a class="brand nav-tooltip" title="${_('About Hue')}" href="/about">Hue</a>
        <div id="usernameDropdown" class="btn-group pull-right hide">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            <i class="icon-user"></i> <span id="username"></span>
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <li><a class="userProfile" href="#">${_('Profile')}</a></li>
            <li class="divider"></li>
            <li><a href="/accounts/logout/">${_('Sign Out')}</a></li>
          </ul>
        </div>

        <div class="nav-collapse">
          <ul class="nav">
            %for app in apps:
              %if app.icon_path:
              <li id="${app.display_name}Icon" ${is_selected(section, app.display_name)}>
                <a class="nav-tooltip" title="${app.nice_name}"
                  href="/${app.display_name}"><img width="25" height="25"
                  src="${app.icon_path}"/></a></li>
              %endif
            %endfor
            <li class="divider-vertical"></li>
            <li id="checkConfig"></li>
          </ul>
        </div>
      </div>
    </div>
  </div>


