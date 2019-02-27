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
  from useradmin.hue_password_policy import is_password_policy_enabled, get_password_hint
%>

<%namespace name="hueIcons" file="/hue_icons.mako" />

${ commonheader(_("Welcome to Hue"), "login", user, request, "50px", True, True) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/css/login.css') }">
<link rel="stylesheet" href="${ static('desktop/css/login4.css') }">

<style type="text/css">
  body {
    background-color: #F8F8F8;
    padding-top: 150px;
  }

  .footer {
    position: fixed;
    bottom: 0;
    background-color: #0B7FAD;
    height: 6px;
    width: 100%;
  }

  select {
    width: 100%;
  }
</style>

<div class="login-container">

  <form method="POST" action="${action}" autocomplete="off">
    ${ csrf_token(request) | n,unicode }

    <div class="logo">
      <svg style="height: 80px; width: 200px;"><use xlink:href="#hi-logo"></use></svg>
    </div>
    <h3>Query. Explore. Repeat.</h3>

    %if 'OIDCBackend' in backend_names:
      <button title="${ _('Single Sign-on') }" class="btn btn-primary" onclick="location.href='/oidc/authenticate/'">${ _('Single Sign-on') }</button>

      <hr class="separator-line"/>
    %endif

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
    <div
      %if 'server' in form.fields and len(form.fields['server'].choices) == 1:
        class="hide"
      %endif
      >
      %if 'server' in form.fields:
        ${ form['server'] | n,unicode }
      %endif
    </div>
    %endif

    %if 'ImpersonationBackend' in backend_names:
    <div class="text-input">
      ${ form['login_as'] | n,unicode }
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
    ${ _('Powered by') } <img src="${ static('desktop/art/hue-login-logo.png') }" width="40" style="vertical-align: middle"  alt="${ _('Hue logo') }"> -
  % endif
  ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
</div>

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

    % if next:
      var $redirect = $('input[name="next"]');
      $redirect.val($redirect.val() + window.location.hash);
    % endif
  });
</script>

${ commonfooter(None, messages) | n,unicode }
