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

${ commonheader(_("Welcome to Hue"), "login", user, "50px", True) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/css/login.css') }">
<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<style type="text/css">
  body {
    background-color: #EEE;
    padding-top: 150px;
  }
</style>


<div class="container">
  <div class="row">
    <div class="login-box">
      <form method="POST" action="${action}">
      ${ csrf_token(request) | n,unicode }

      <div class="login-header">
        <h1>${ _('Welcome to Hue') }</h1>
        %if first_login_ever:
          <h2>${_('Create your Hue account')}</h2>
        %else:
          <h2>${_('Sign in to continue to your dashboard')}</h2>
        %endif
      </div>

      <div class="logo"><img src="${ static('desktop/art/hue-login-white.png') }" width="50" height="50" /> </div>

      <div class="login-content">

        %if first_login_ever:
          <div class="alert alert-block">
            ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
            <strong>${_('they will become your Hue superuser credentials.')}</strong>
            %if is_password_policy_enabled():
	          <p>${get_password_hint()}</p>
            %endif
          </div>
        %endif

        <div class="
          %if backend_names == ['OAuthBackend']:
            hide
          %endif
        ">
          ${ form['username'] | n,unicode }
        </div>

        ${ form['username'].errors | n,unicode }

        <div class="
          %if 'AllowAllBackend' in backend_names or backend_names == ['OAuthBackend']:
            hide
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
          <div class="alert alert-error" style="text-align: center">
            <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong>
            %if form.errors:
              % for error in form.errors:
               ${ form.errors[error]|unicode,n }
              % endfor
            %endif
          </div>
        %endif

        %if first_login_ever:
          <input type="submit" class="btn btn-large btn-primary" value="${_('Create account')}"/>
        %else:
          <input type="submit" class="btn btn-large btn-primary" value="${_('Sign in')}"/>
        %endif
        <input type="hidden" name="next" value="${next}"/>
        </div>

      </form>

      %if conf.CUSTOM.LOGIN_SPLASH_HTML.get():
      <div class="alert alert-info" id="login-splash">
        ${ conf.CUSTOM.LOGIN_SPLASH_HTML.get() | n,unicode }
      </div>
      %endif
    </div>
  </div>
  <div class="row">
    <div class="center muted">
      ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/chosen/chosen.jquery.min.js') }" type="text/javascript" charset="utf-8"></script>
<script>
  $(document).ready(function () {
    $("#id_server").chosen({
      disable_search_threshold: 5,
      width: "90%",
      no_results_text: "${_('Oops, no database found!')}"
    });

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

${ commonfooter(messages) | n,unicode }
