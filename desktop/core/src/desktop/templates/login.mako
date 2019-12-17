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
  from django.utils.translation import ugettext as _

  from useradmin.hue_password_policy import is_password_policy_enabled, get_password_hint

  from desktop.conf import CUSTOM, ENABLE_ORGANIZATIONS, SSO_GOOGLE_API_KEY
  from desktop.views import commonheader, commonfooter
%>

<%namespace name="hueIcons" file="/hue_icons.mako" />

${ commonheader(_("Welcome to Hue"), "login", user, request, "50px", True, True) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/css/login.css') }">
<link rel="stylesheet" href="${ static('desktop/css/login4.css') }">

% if 'GoogleSignInBackend' in backend_names:
  <script src="https://apis.google.com/js/platform.js" async defer></script>
  <meta name="google-signin-client_id" content="${ SSO_GOOGLE_API_KEY.get() }">
% endif

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

    % if 'OIDCBackend' in backend_names:
      <button title="${ _('Single Sign-on') }" class="btn btn-primary" onclick="location.href='/oidc/authenticate/'">
        ${ _('Single Sign-on') }
      </button>
      <hr class="separator-line"/>
    % endif

    % if first_login_ever:
      <div class="alert alert-info center">
        ${ _('Since this is your first time logging in, pick any username and password. Be sure to remember these, as') }
        <strong>${ _('they will become your Hue superuser credentials.') }</strong>
        % if is_password_policy_enabled():
        <p>${ get_password_hint() }</p>
        % endif
      </div>
    % endif

    % if ENABLE_ORGANIZATIONS.get():
      <div class="text-input
        % if form['email'].errors or (not form['email'].errors and not form['email'].errors and login_errors):
          error
        % endif
      ">
        ${ form['email'] | n,unicode }
      </div>

      ${ form['email'].errors | n,unicode }
    % else:
      % if 'username' in form.fields:
        <div class="text-input
          % if backend_names == ['OAuthBackend']:
            hide
          % endif
          % if form['username'].errors or (login_errors and not form['username'].errors and not form['password'].errors):
            error
          % endif
        ">
          ${ form['username'] | n,unicode }
        </div>

        ${ form['username'].errors | n,unicode }
      % endif
    % endif

    % if 'password' in form.fields:
      <div class="text-input
        % if 'AllowAllBackend' in backend_names or backend_names == ['OAuthBackend']:
          hide
        % endif
        % if form['password'].errors or (login_errors and 'username' in form.fields and not form['username'].errors and not form['password'].errors):
          error
        % endif
      ">
        ${ form['password'] | n,unicode }
      </div>

      ${ form['password'].errors | n,unicode }
    % endif

    % if active_directory:
    <div
      % if 'server' in form.fields and len(form.fields['server'].choices) == 1:
      % endif
      >
      % if 'server' in form.fields:
        ${ form['server'] | n,unicode }
      % endif
    </div>
    % endif

    % if 'ImpersonationBackend' in backend_names:
    <div class="text-input">
      ${ form['login_as'] | n,unicode }
    </div>
    % endif

    % if login_errors and ('username' in form.fields and not form['username'].errors) and ('password' in form.fields and not form['password'].errors):
      % if form.errors:
        % for error in form.errors:
         ${ form.errors[error] | unicode,n }
        % endfor
      % endif
    % endif

    % if 'username' in form.fields or 'email' in form.fields:
      % if first_login_ever:
        <input type="submit" class="btn btn-primary" value="${ _('Create Account') }"/>
      % else:
        <input type="submit" class="btn btn-primary" value="${ _('Sign In') }"/>
      % endif
      % if ENABLE_ORGANIZATIONS.get():
        <input type="submit" class="btn btn-primary" value="${ _('Create Account') }"/>
      % endif
    % endif

    % if 'GoogleSignInBackend' in backend_names:
      % if login_errors:
        ${ _('Authentication failed') }
      % endif

      <div class="g-signin2" data-onsuccess="onSignIn"></div>
      <input type="hidden" name="id_token"/>
    % endif

    <input type="hidden" name="next" value="${next}"/>
  </form>

  % if CUSTOM.LOGIN_SPLASH_HTML.get():
  <div class="alert alert-info" id="login-splash">
    ${ CUSTOM.LOGIN_SPLASH_HTML.get() | n,unicode }
  </div>
  % endif
</div>

<div id="trademark" class="trademark center muted">
  <trademark-banner>
  % if CUSTOM.LOGO_SVG.get():
    ${ _('Powered by') } <img src="${ static('desktop/art/hue-login-logo.png') }" width="40" style="vertical-align: middle" alt="${ _('Hue logo') }"> -
  % endif
  ${ _('Hue and the Hue logo are trademarks of Cloudera, Inc.') }
  </trademark-banner>
</div>

% if 'JwtBackend' in backend_names:
  <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/0.18.1/axios.min.js"></script>
% endif


<script>
   % if 'GoogleSignInBackend' in backend_names:
    function onSignIn(googleUser) {
      ## var profile = googleUser.getBasicProfile();
      ## console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
      ## console.log('Name: ' + profile.getName());
      ## console.log('Image URL: ' + profile.getImageUrl());
      ## console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.

      var id_token = googleUser.getAuthResponse().id_token;
      $('input[name="id_token"]').val(id_token);
      % if not user.is_authenticated():
        console.log('is not auth');
        $("form").submit();
      % else:
        console.log('is auth');
      % endif
    }
    % endif

  $(document).ready(function () {

    $("form").on("submit", function () {
      window.setTimeout(function () {
        $(".logo").find("img").addClass("waiting");
      }, 1000);
    });

    % if 'AllowAllBackend' in backend_names:
      $('#id_password').val('password');
    % endif

    % if backend_names == ['OAuthBackend']:
      $("input").css({"display": "block", "margin-left": "auto", "margin-right": "auto"});
      $("input").bind('click', function () {
        window.location.replace('/login/oauth/');
        return false;
      });
    % endif

    % if 'GoogleSignInBackend' in backend_names:
      $("#gsso").bind('click', function () {
        onSignIn()
      });
    % endif

    % if 'JwtBackend' in backend_names:
      const baseURL = 'http://127.0.0.1:8005';
      var HTTP = axios.create({
        baseURL: baseURL
      });

      function verifyAuthToken(token) {
        return HTTP.post('/auth/verify-token/', {token: token});
      }
      function login(credentials) {
        return HTTP.post('/auth/', credentials);
      }

      $("input").bind('click', function () {
        var credentials = {
          email: 'romain@iquery.io',
          password: 'romain',
        };
        // window.JwtAuth. // to clean-up
        login(credentials).then(
          res => {
            loginCallback(res.data.token, credentials.email)
          },
          err => {
            alert(err)
          }
        ).catch(e => {
          alert(e);
        });

        //return false;
      });

      function loginCallback(token, email) {
        console.log('JWT logged in')
        ## Total storage token
        ## JwtBackend calls get_profile with token to login into Hue

        HTTP.defaults.headers.common['Authorization'] = 'JWT ' + token;
        HTTP.get('/datagen/');

        ## _this.$session.start();
        ## _this.$session.set('token', token);
        ## _this.$session.set('email', email);
        ## _this.$store.state.HTTP.defaults.headers.common['Authorization'] = 'JWT ' + token;
        ## _this.$store.commit('setIsAuthenticated', true)
      }
    % endif

    % if next:
      var $redirect = $('input[name="next"]');
      $redirect.val($redirect.val() + window.location.hash);
    % endif
  });
</script>

${ commonfooter(None, messages) | n,unicode }
