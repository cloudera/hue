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
%>

${ commonheader("Welcome to Hue", "login", user, "50px") | n,unicode }

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<style type="text/css">
  body {
    background-color: #FFF;
  }

  @-webkit-keyframes spinner {
    from {
      -webkit-transform: rotateY(0deg);
    }
    to {
      -webkit-transform: rotateY(-360deg);
    }
  }

  #logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 10px;
    background: #FFF url("/static/art/hue-login-logo-ellie.png") 50% 2px no-repeat;
    width: 130px;
    height: 130px;
    -webkit-border-radius: 65px;
    -moz-border-radius: 65px;
    border-radius: 65px;
    border: 1px solid #EEE;
  }

  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    #logo {
      background: #FFF url("/static/art/hue-login-logo-ellie@2x.png") 50% 2px no-repeat;
      background-size: 114px 114px;
    }
  }

  #logo.waiting {
    -webkit-animation-name: spinner;
    -webkit-animation-timing-function: linear;
    -webkit-animation-iteration-count: infinite;
    -webkit-animation-duration: 2s;
    -webkit-transform-style: preserve-3d;
  }

  .login-content {
    width: 360px;
    display: block;
    margin-left: auto;
    margin-right: auto;
  }

  .input-prepend {
    width: 100%;
  }

  .input-prepend .add-on {
    min-height: 38px;
    line-height: 38px;
    color: #999;
  }

  .login-content input {
    width: 85%;
    min-height: 38px;
    font-size: 18px;
  }

  .login-content .input-prepend.error input, .login-content .input-prepend.error .add-on {
    border-top-color: #dd4b39;
    border-bottom-color: #dd4b39;
  }

  .login-content .input-prepend.error input {
    border-right-color: #dd4b39;
  }

  .login-content .input-prepend.error .add-on {
    border-left-color: #dd4b39;
  }

  .login-content input[type='submit'] {
    height: 44px;
    min-height: 44px;
    font-weight: normal;
    text-shadow: none;
  }

  hr {
    border-top-color: #DEDEDE;
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

  input.error {
    border-color: #b94a48;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
  }

  .well {
    border: 1px solid #D8D8D8;
    border-radius: 3px 3px 3px 3px;
    background-color: #F7F7F7;
  }

  .footer {
    position: fixed;
    bottom: 0;
    background-color: #338BB8;
    height: 6px;
    width: 100%;
  }

  h3 {
    color: #666;
    font-size: 24px;
    font-weight: 400;
    margin-bottom: 20px;
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


<div class="footer"></div>

<div class="container">
  <div class="row">
    <div class="login-content center">
      <div id="logo"></div>

      <form method="POST" action="${action}" class="well">
        ${ csrf_token(request) | n,unicode }
        %if first_login_ever:
          <h3>${_('Create your Hue account')}</h3>
        %else:
          <h3>${_('Sign in to continue to Hue')}</h3>
        %endif

        %if first_login_ever:
          <div class="alert alert-block">
            ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
            <strong>${_('they will become your Hue superuser credentials.')}</strong>.
          </div>
        %endif

        <div class="input-prepend
          % if backend_name == 'OAuthBackend':
            hide
          % endif
        ">
          <span class="add-on"><i class="fa fa-user"></i></span>
          ${ form['username'] | n,unicode }
        </div>

        ${ form['username'].errors | n,unicode }

        <div class="input-prepend
          % if backend_name in ('AllowAllBackend', 'OAuthBackend'):
            hide
          % endif
        ">
          <span class="add-on"><i class="fa fa-lock"></i></span>
          ${ form['password'] | n,unicode }
        </div>
        ${ form['password'].errors | n,unicode }

        %if active_directory:
        <div class="input-prepend">
          <span class="add-on"><i class="fa fa-globe"></i></span>
          ${ form['server'] | n,unicode }
        </div>
        %endif

        %if login_errors and not form['username'].errors and not form['password'].errors:
          <div class="alert alert-error" style="text-align: center">
            <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong>
            % if form.errors:
              % for error in form.errors:
               ${ form.errors[error]|unicode,n }
              % endfor
            % endif
          </div>
        %endif
        <hr/>
        %if first_login_ever:
          <input type="submit" class="btn btn-large btn-primary" value="${_('Create account')}"/>
        %else:
          <input type="submit" class="btn btn-large btn-primary" value="${_('Sign in')}"/>
        %endif
        <input type="hidden" name="next" value="${next}"/>
      </form>
    </div>
  </div>
</div>

<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script>
  $(document).ready(function () {
    $("#id_server").chosen({
      disable_search_threshold: 5,
      width: "90%",
      no_results_text: "${_('Oops, no database found!')}"
    });

    $("form").on("submit", function () {
      window.setTimeout(function () {
        $("#logo").addClass("waiting");
      }, 1000);
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

${ commonfooter(messages) | n,unicode }
