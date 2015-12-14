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

${ commonheader("Welcome to Hue", "login", user, "50px", True) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/ext/chosen/chosen.min.css') }">
<style type="text/css">
  body {
    background-color: #EEE;
    padding-top: 150px;
  }

  @-webkit-keyframes spinner {
    from {
      -webkit-transform: rotateY(0deg);
    }
    to {
      -webkit-transform: rotateY(-360deg);
    }
  }

  .logo {
    background-color: #338BB8;
    width: 60px;
    height: 60px;
    text-align: center;
    -webkit-border-radius: 30px;
    -moz-border-radius: 30px;
    border-radius: 30px;
    margin-left: 400px;
    margin-top: -30px;
  }

  .logo img {
    margin-top: 2px;
  }

  .logo img.waiting {
    -webkit-animation-name: spinner;
    -webkit-animation-timing-function: linear;
    -webkit-animation-iteration-count: infinite;
    -webkit-animation-duration: 2s;
    -webkit-transform-style: preserve-3d;
  }

  .login-box {
    width: 500px;
    display: block;
    margin: auto;
    margin-bottom: 50px;
    background: #fff;
    box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 1px 5px 0 rgba(0, 0, 0, 0.12);
  }

  .login-box .input-prepend.error input, .login-box .input-prepend.error .add-on {
    border-top-color: #dd4b39;
    border-bottom-color: #dd4b39;
  }

  .login-box .input-prepend.error input {
    border-right-color: #dd4b39;
  }

  .login-box .input-prepend.error .add-on {
    border-left-color: #dd4b39;
  }

  .login-box input[type='submit'] {
    height: 44px;
    min-height: 44px;
    font-weight: normal;
    text-shadow: none;
  }

  .login-header {
    background-color: #fafafa !important;
    padding: 35px;
  }

  .login-header h1 {
    margin: 0;
    font-size: 18px;
    line-height: 18px;
  }

  .login-header h2 {
    margin: 5px 0 0 0;
    color: #757575;
    font-weight: normal;
    font-size: 14px;
    line-height: 14px;
  }

  .login-content {
    padding: 35px;
  }

  ul.errorlist {
    text-align: left;
    margin-bottom: 4px;
    margin-top: -4px;
  }

  .alert-error ul.errorlist {
    text-align: center;
    margin-top: 0;
  }

  ul.errorlist li {
    font-size: 13px;
    font-weight: normal;
    font-style: normal;
  }

  .login-content input[type='text'], .login-content input[type='password'], .login-content input[type='text']:hover, .login-content input[type='password']:hover {
    padding: 0 10px 2px 0;
    height: auto;
    border: none;
    border-bottom: 2px solid #eeeeee;
    border-radius: 0;
    background: none;
    box-shadow: none;
    color: #9e9e9e;
    font-weight: 400;
    resize: none;
    width: 100%;
  }

  input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0px 1000px white inset!important;
  }

  .login-content input.error {
    border-color: #b94a48;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
  }

  .btn-large.btn-primary {
    width: 100%;
    margin-top: 20px;
  }

  .chosen-single {
    min-height: 38px;
    text-align: left;
    font-size: 18px;
  }

  .chosen-single span {
    display: inline;
    line-height: 38px;
    vertical-align: middle;
  }

  .chosen-container-active.chosen-with-drop .chosen-single div b,
  .chosen-container-single .chosen-single div b {
    background-position-x: 1px;
    background-position-y: 10px;
  }

  .chosen-container-active.chosen-with-drop .chosen-single div b {
    background-position-x: -17px;
    background-position-y: 10px;
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

    $("ul.errorlist").each(function () {
      $(this).prev().addClass("error");
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
