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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from metadata.conf import has_optimizer, OPTIMIZER

home_url = url('desktop_views_home')
from desktop.conf import USE_NEW_EDITOR

from webpack_loader.templatetags.webpack_loader import render_bundle

if USE_NEW_EDITOR.get():
  home_url = url('desktop_views_home2')
%>
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
    ${smart_unicode(title).upper()}
  % endif
</%def>
<html lang="en">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue ${get_nice_name(current_app, section)} - ${get_title(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }" />
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">

  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue-mobile.css') }" rel="stylesheet">

  <style type="text/css">
    body {
      display: none;
      visibility: hidden;
    }
  </style>

  <script type="text/javascript">

    var LOGGED_USERNAME = '${ user.username }';
    var IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';
    var HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';

    var CACHEABLE_TTL = {
      default: ${ conf.CUSTOM.CACHEABLE_TTL.get() },
      optimizer: ${ OPTIMIZER.CACHEABLE_TTL.get() }
    };

    var AUTOCOMPLETE_TIMEOUT = ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() };

    window.LEAFLET_DEFAULTS = {
      layer: '${ leaflet['layer'] |n,unicode }',
      attribution: '${ leaflet['attribution'] |n,unicode }'
    };
  </script>

  <!--[if lt IE 9]>
  <script type="text/javascript">
    if (document.documentMode && document.documentMode < 9){
      location.href = "${ url('desktop_views_unsupported') }";
    }
  </script>
  <![endif]-->

  <script type="text/javascript">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop_views_unsupported') }";
      }
    }

    // check for IE document modes
    if (document.documentMode && document.documentMode < 9) {
      location.href = "${ url('desktop_views_unsupported') }";
    }
  </script>

  ${ render_bundle('hue') | n,unicode }

  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.touchSwipe.min.js') }"></script>
  <script src="${ static('desktop/js/bootstrap-typeahead-touchscreen.js') }"></script>
  <script src="${ static('desktop/ext/js/bootstrap-better-typeahead.min.js') }"></script>
  <script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
  <script src="${ static('desktop/ext/js/moment-timezone-with-data.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/tzdetect.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/ace/ace.js') }"></script>
  <script src="${ static('desktop/js/ace/mode-impala.js') }"></script>
  <script src="${ static('desktop/js/ace/mode-hive.js') }"></script>
  <script src="${ static('desktop/js/ace/ext-language_tools.js') }"></script>
  <script src="${ static('desktop/js/ace.extended.js') }"></script>
  <script>
    ace.config.set("basePath", "${ static('desktop/js/ace') }");
  </script>

  <script type="text/javascript">

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

      % if 'jobbrowser' in apps:
      var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);
      var lastJobBrowserRequest = null;

      function checkJobBrowserStatus(){
        if (lastJobBrowserRequest !== null && lastJobBrowserRequest.readyState < 4) {
          return;
        }
        window.clearTimeout(checkJobBrowserStatusIdx);
        lastJobBrowserRequest = $.post("/jobbrowser/jobs/", {
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
          checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, window.JB_HEADER_CHECK_INTERVAL_IN_MILLIS);
        }).fail(function () {
          window.clearTimeout(checkJobBrowserStatusIdx);
        });
      }
      huePubSub.subscribe('check.job.browser', checkJobBrowserStatus);
      % endif

      window.hueDebug = {
        viewModel: function () {
          return ko.dataFor(document.body);
        }
      }
    });
  </script>
</head>
<body>

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
<div class="navbar hue-title-bar">
  <div class="navbar-inner">
    <div class="container">
      <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="brand" href="#">
        <img src="${ static('desktop/art/hue-logo-mini-white.png') }" alt="${ _('Hue logo') }" />
        ${get_title(title)}
      </a>
      <div class="nav-collapse collapse">
        <ul class="nav">
          <li><a title="${_('Assist')}" data-rel="navigator-tooltip" href="${ url('desktop.views.assist_m') }">${_('Assist')}</a></li>
          % if 'beeswax' in apps:
             % if USE_NEW_EDITOR.get():
             <li><a href="${ url('notebook:editor_m') }?type=hive">${_('Hive')}</a></li>
             % endif
           % endif
           % if 'impala' in apps:
             % if USE_NEW_EDITOR.get(): ## impala requires beeswax anyway
             <li><a href="${ url('notebook:editor_m') }?type=impala">${_('Impala')}</a></li>
             % endif
           % endif
           % if 'search' in apps:
             <li><a href="${ url('search:index_m') }">${_('Search')}</a></li>
           % endif
          <li><a title="${_('Sign out')}" href="/accounts/logout/">${_('Sign out')}</a></li>
        </ul>
      </div>
    </div>
  </div>
</div>

