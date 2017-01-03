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
  from desktop.views import commonheader, commonfooter
  from useradmin.password_policy import is_password_policy_enabled, get_password_hint
%>

<%namespace name="hueIcons" file="/hue_icons.mako" />

${ commonheader(_("Welcome to Hue"), "login", user, request, "50px", True, True) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/css/login.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<style type="text/css">
  body {
    background-color: #FAFAFA;
    padding-top: 150px;
  }

  .footer {
    position: fixed;
    bottom: 0;
    background-color: #338BB8;
    height: 6px;
    width: 100%;
  }
</style>

${ hueIcons.symbols() }

<div class="navbar">
  <div class="navbar-inner">
    <a class="brand" href="/">
      <svg style="margin-top: 2px; margin-left:8px;width: 60px;height: 16px;display: inline-block;">
        <use xlink:href="#hue-logo"></use>
      </svg>
    </a>
    <ul class="nav pull-right">
      <li><a href="http://gethue.com" target="_blank" title="${_('Go to gethue.com')}" rel="navigator-tooltip" data-placement="left"><i class="fa fa-globe"></i></a></li>
    </ul>
  </div>
</div>


<div class="login-container">

  <form method="POST" action="${action}" autocomplete="off">
    ${ csrf_token(request) | n,unicode }

    % if conf.CUSTOM.LOGO_SVG.get():
    <div class="empty-logo">
    </div>
    % else:
    <div class="logo">
      <img src="${ static('desktop/art/hue-login-logo-ellie@2x.png') }" width="70" height="70">
    </div>
    % endif

    %if first_login_ever:
      <div class="alert alert-info center">
        ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
        <strong>${_('they will become your Hue superuser credentials.')}</strong>
        %if is_password_policy_enabled():
        <p>${get_password_hint()}</p>
        %endif
      </div>
    %endif

    <div class="text-input
      %if backend_names == ['OAuthBackend']:
        hide
      %endif
      %if form['username'].errors or (not form['username'].errors and not form['password'].errors and login_errors):
        error
      %endif
    ">
      ${ form['username'] | n,unicode }
    </div>

    ${ form['username'].errors | n,unicode }

    <div class="text-input
      %if 'AllowAllBackend' in backend_names or backend_names == ['OAuthBackend']:
        hide
      %endif
      %if form['password'].errors or (not form['username'].errors and not form['password'].errors and login_errors):
        error
      %endif
    ">
      ${ form['password'] | n,unicode }
    </div>

    ${ form['password'].errors | n,unicode }

    %if active_directory:
    <div>
      ${ form['server'] | n,unicode }
    </div>
    %endif

    %if login_errors and not form['username'].errors and not form['password'].errors:
      %if form.errors:
        % for error in form.errors:
         ${ form.errors[error]|unicode,n }
        % endfor
      %endif
    %endif

    %if first_login_ever:
      <input type="submit" class="btn btn-primary" value="${_('Create Account')}"/>
    %else:
      <input type="submit" class="btn btn-primary" value="${_('Sign In')}"/>
    %endif
    <input type="hidden" name="next" value="${next}"/>

  </form>

  %if conf.CUSTOM.LOGIN_SPLASH_HTML.get():
  <div class="alert alert-info" id="login-splash">
    ${ conf.CUSTOM.LOGIN_SPLASH_HTML.get() | n,unicode }
  </div>
  %endif
</div>


<div class="trademark center muted">
  % if conf.CUSTOM.LOGO_SVG.get():
    ${ _('Powered by') } <img src="${ static('desktop/art/hue-login-logo.png') }" width="40" style="vertical-align: text-top;"> -
  % endif
  ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
</div>


<div class="footer"></div>


<script>
  $(document).ready(function () {
    $("form").on("submit", function () {
      window.setTimeout(function () {
        $(".logo").find("img").addClass("waiting");
      }, 1000);
    });

    %if 'AllowAllBackend' in backend_names:
      $('#id_password').val('password');
    %endif

    %if backend_names == ['OAuthBackend']:
      $("input").css({"display": "block", "margin-left": "auto", "margin-right": "auto"});
      $("input").bind('click', function () {
        window.location.replace('/login/oauth/');
        return false;
      });
    %endif
  });
</script>

${ commonfooter(None, messages) | n,unicode }
