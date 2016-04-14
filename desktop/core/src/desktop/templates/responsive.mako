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
  from desktop.views import _ko
  from django.utils.translation import ugettext as _
  from desktop.lib.i18n import smart_unicode
  from desktop.views import login_modal
%>

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

  <link href="${ static('desktop/ext/css/bootplus.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/responsive.css') }" rel="stylesheet">

  <!--[if lt IE 9]>
  <script type="text/javascript">
    if (document.documentMode && document.documentMode < 9) {
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>
  <![endif]-->

  <script type="text/javascript" charset="utf-8">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop.views.unsupported') }";
      }
    }

    // check for IE document modes
    if (document.documentMode && document.documentMode < 9) {
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>
</head>

<body>

<div class="main-page">
  <div class="top-nav">
    <a class="hamburger hamburger--squeeze pull-left" type="button">
      <span class="hamburger-box">
        <span class="hamburger-inner"></span>
      </span>
    </a>
    <a class="brand nav-tooltip pull-left" title="${_('About Hue')}" rel="navigator-tooltip" href="/about"><img
        src="${ static('desktop/art/hue-logo-mini-white.png') }"
        data-orig="${ static('desktop/art/hue-logo-mini-white.png') }"
        data-hover="${ static('desktop/art/hue-logo-mini-white-hover.png') }"/></a>
  </div>

  <div class="content-wrapper">
    <div class="left-nav">

    </div>
    <div class="page-content">
      <h1>responsive</h1>
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/jquery/jquery-2.2.3.min.js') }"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>

<script type="text/javascript" charset="utf-8">

  $(".hamburger").click(function () {
    $(this).toggleClass("is-active");
    $(".left-nav").toggleClass("left-nav-visible");
  })

  moment.locale(window.navigator.userLanguage || window.navigator.language);
  localeFormat = function (time) {
    if (typeof ko !== 'undefined' && ko.isObservable(time)) {
      return moment(time()).format("L LT");
    }
    return moment(time).format("L LT");
  }

  //Add CSRF Token to all XHR Requests
  var xrhsend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function (data) {
    this.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
    return xrhsend.apply(this, arguments);
  }

  // sets global assistHelper TTL
  $.totalStorage('hue.cacheable.ttl', ${conf.CUSTOM.CACHEABLE_TTL.get()});

  $(document).ready(function () {
##       // forces IE's ajax calls not to cache
##       if ($.browser.msie) {
##         $.ajaxSetup({ cache: false });
##       }

    // prevents framebusting and clickjacking
    if (self == top) {
      $("body").css({
        'display': 'block',
        'visibility': 'visible'
      });
    } else {
      top.location = self.location;
    }

    %if conf.AUTH.IDLE_SESSION_TIMEOUT.get() > -1 and not skip_idle_timeout:
      var idleTimer;

      function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(function () {
              // Check if logged out
              $.get('/desktop/debug/is_idle');
            }, ${conf.AUTH.IDLE_SESSION_TIMEOUT.get()} * 1000 + 1000
      )
        ;
      }

      $(document).on('mousemove', resetIdleTimer);
      $(document).on('keydown', resetIdleTimer);
      $(document).on('click', resetIdleTimer);
      resetIdleTimer();
    %endif

    % if 'jobbrowser' in apps:
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
      var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

      function checkJobBrowserStatus() {
        $.getJSON("/${apps['jobbrowser'].display_name}/?format=json&state=running&user=${user.username}", function (data) {
          if (data != null && data.jobs != null) {
            if (data.jobs.length > 0) {
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
    % endif
  });
</script>

<script type="text/javascript">

  $(document).ready(function () {
    // global catch for ajax calls after the user has logged out
    var isLoginRequired = false;
    $(document).ajaxComplete(function (event, xhr, settings) {
      if (xhr.responseText === '/* login required */' && !isLoginRequired) {
        isLoginRequired = true;
        $('body').children(':not(#login-modal)').addClass('blurred');
        if ($('#login-modal').length > 0) {
          $('#login-modal').modal('show');
          window.setTimeout(function () {
            $('.jHueNotify').remove();
          }, 200);
        }
        else {
          location.reload();
        }
      }
    });

    $('#login-modal').on('hidden', function () {
      isLoginRequired = false;
      $('.blurred').removeClass('blurred');
    });

    huePubSub.subscribe('hue.login.result', function (response) {
      if (response.auth) {
        $('#login-modal').modal('hide');
        $.jHueNotify.info('${ _('You have signed in successfully!') }');
        $('#login-modal .login-error').addClass('hide');
      } else {
        $('#login-modal .login-error').removeClass('hide');
      }
    });
  });

  $(".modal").on("shown", function () {
    // safe ux enhancement: focus on the first editable input
    $(".modal:visible").find("input:not(.disable-autofocus):visible:first").focus();
  });

    %if collect_usage:
      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-40351920-1']);

      // We collect only 2 path levels: not hostname, no IDs, no anchors...
      var _pathName = location.pathname;
      var _splits = _pathName.substr(1).split("/");
      _pathName = _splits[0] + (_splits.length > 1 && $.trim(_splits[1]) != "" ? "/" + _splits[1] : "");

      _gaq.push(['_trackPageview', '/remote/${ version }/' + _pathName]);

      (function () {
        var ga = document.createElement('script');
        ga.type = 'text/javascript';
        ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(ga, s);
      })();

      function trackOnGA(path) {
        if (typeof _gaq != "undefined" && _gaq != null) {
          _gaq.push(['_trackPageview', '/remote/${ version }/' + path]);
        }
      }
    %endif
</script>
</body>
</html>