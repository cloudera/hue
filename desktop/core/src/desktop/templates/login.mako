## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.    See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from desktop import conf
from django.utils.translation import ugettext as _
%>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  %if first_login_ever:
    <title>${_('Hue - Sign up')}</title>
  %else:
    <title>${_('Hue - Sign in')}</title>
  %endif

  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="/static/ext/css/bootplus.css" rel="stylesheet">
  <link href="/static/ext/css/font-awesome.min.css" rel="stylesheet">
  <link href="/static/css/hue3.css" rel="stylesheet">

  <style type="text/css">
    % if conf.CUSTOM.BANNER_TOP_HTML.get():
      body {
        display: none;
        padding-top: 120px;
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
    % else:
      body {
        display: none;
        padding-top: 80px;
      }
    % endif
  </style>

  <style type="text/css">
    #logo {
      display: block;
      margin-left: auto;
      margin-right: auto;
      margin-bottom: 30px
    }

    .login-content {
      width: 400px;
      display: block;
      margin-left: auto;
      margin-right: auto;
    }

    .login-content label {
      margin-bottom: 20px;
      font-size: 16px;
    }

    .login-content input[type='text'], .login-content input[type='password'] {
      width: 90%;
      margin-top: 10px;
      font-size: 18px;
    }

    .login-content input {
      width: 100%;
      padding: 10px 16px;
    }

    hr {
      border-top-color: #DEDEDE;
    }

    ul.errorlist li {
      font-size: 13px;
      font-weight: normal;
      font-style: normal;
    }

    input.error {
      border-color: #b94a48;
      -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
      -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
      box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    }

    .well {
      border: 1px solid #D8D8D8;
      border-radius: 3px 3px 3px 3px;
    }

    .footer {
      position: fixed;
      bottom: 0;
      background-color: #338BB8;
      height: 4px;
      width: 100%;
    }
  </style>
</head>

<body>

% if conf.CUSTOM.BANNER_TOP_HTML.get():
  <div id="banner-top" class="banner">
    ${ conf.CUSTOM.BANNER_TOP_HTML.get() | n,unicode }
  </div>
% endif


<div class="footer"></div>

<div class="navigator">
  <div class="pull-right">
    <ul class="nav nav-pills">
      <li id="jHueTourFlagPlaceholder"></li>
    </ul>
  </div>
  <a class="brand nav-tooltip pull-left" href="#"><img src="/static/art/hue-logo-mini-white.png"
                                                       data-orig="/static/art/hue-logo-mini-white.png"
                                                       data-hover="/static/art/hue-logo-mini-white-hover.png"/></a>
  <ul class="nav nav-pills pull-left hide" id="visit">
    <li><a title="${_('Visit gethue.com')}" href="http://gethue.com">${_('Fell asleep? Visit us on gethue.com instead!')} <i class="fa fa-external-link-circle"></i></a></li>
  </ul>
</div>


<div class="container">
  <div class="row">
    <div class="login-content">
      <form method="POST" action="${action}" class="well">
        <img id="logo" src="/static/art/hue-login-logo.png" data-orig="/static/art/hue-login-logo.png"
             data-hover="/static/art/hue-login-logo-skew.png"/>
        <label
          % if backend_name == 'OAuthBackend':
            class="hide"
          % endif
            ><i class="fa fa-user"></i> ${_('Username')}
          ${ form['username'] | n,unicode }
          ${ form['username'].errors | n,unicode }
        </label>
        <label
          % if backend_name in ('AllowAllBackend', 'OAuthBackend'):
            class="hide"
          % endif
            ><i class="fa fa-lock"></i> ${_('Password')}
          ${ form['password'] | n,unicode }
          ${ form['password'].errors | n,unicode }
        </label>

        %if login_errors:
            <div class="alert alert-error" style="text-align: center">
              <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong> ${_('Invalid username or password.')}
            </div>
        %endif

        %if first_login_ever:
            <div class="alert alert-block">
              <i class="fa fa-exclamation-triangle"></i>
            ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
              <strong>${_('they will become your Hue superuser credentials.')}</strong>.
            </div>
            <hr/>
            <input type="submit" class="btn btn-large btn-primary" value="${_('Sign up')}"/>
        %else:
            <hr/>
            <input type="submit" class="btn btn-large btn-primary" value="${_('Sign in')}"/>
        %endif
        <input type="hidden" name="next" value="${next}"/>
      </form>
    </div>
  </div>
</div>

<script src="/static/ext/js/jquery/jquery-2.0.2.min.js"></script>
<script>
  $(document).ready(function () {
    // prevents framebusting and clickjacking
    if (self == top){
      $("body").show();
    }
    else {
      top.location = self.location;
    }

    var _skew = -1;
    $("[data-hover]").on("mouseover", function () {
      var _this = $(this);
      _skew = window.setTimeout(function () {
        _this.attr("src", _this.data("hover"));
        $("#visit").removeClass("hide");
      }, 3000);
    });

    $("[data-hover]").on("mouseout", function () {
      $(this).attr("src", $(this).data("orig"));
      window.clearTimeout(_skew);
    });

    % if backend_name == 'AllowAllBackend':
        $('#id_password').val('password');
    % endif

    % if backend_name == 'OAuthBackend':
        $("input").css({"display": "block", "margin-left": "auto", "margin-right": "auto"});
        $("input").bind('click', function () {
          window.location.replace('/login/oauth/');
          return false;
        });
    % endif

    $("ul.errorlist").each(function () {
      $(this).prev().addClass("error");
    });
  });
</script>
</body>
</html>
