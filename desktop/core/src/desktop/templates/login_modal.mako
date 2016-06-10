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
  from useradmin.password_policy import is_password_policy_enabled, get_password_hint
%>


<link rel="stylesheet" href="${ static('desktop/css/login.css') }">

<div id="login-modal" class="modal fade hide" data-backdrop="static" data-keyboard="false" style="padding: 0px!important;box-shadow: none;background: transparent;">
  <div class="login-container">
    <form method="POST" action="${action}" autocomplete="off">
      <input type="hidden" name="csrfmiddlewaretoken" value="">

      <div class="logo"><img src="${ static('desktop/art/hue-login-logo-ellie@2x.png') }" width="70" height="70"></div>

      <h4 class="muted">${ _('You have been logged out, please sign in again') }</h4>

      <div class="text-input
        %if backend_names == ['OAuthBackend']:
          hide
        %endif
        %if form['username'].errors or login_errors:
          error
        %endif
      ">
        ${ form['username'] | n,unicode }
      </div>

      <div class="text-input
        %if 'AllowAllBackend' in backend_names or backend_names == ['OAuthBackend']:
          hide
        %endif
        %if form['password'].errors or login_errors:
          error
        %endif
      ">
        ${ form['password'] | n,unicode }
      </div>

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

      <div class="login-error alert alert-error hide" style="text-align: center">
        <strong><i class="fa fa-exclamation-triangle"></i> ${_('Sign in failed. Please try again.')}</strong>
      </div>

      <input type="submit" class="btn btn-primary" value="${_('Sign In')}"/>
      <input type="hidden" name="next" value="${next}"/>
      <input type="hidden" name="fromModal" value="true"/>

    </form>

    %if conf.CUSTOM.LOGIN_SPLASH_HTML.get():
    <div class="alert alert-info" id="login-splash">
      ${ conf.CUSTOM.LOGIN_SPLASH_HTML.get() | n,unicode }
    </div>
    %endif
  </div>
</div>

<script>
  $(document).ready(function () {

    $('#login-modal form').on('submit', function () {
      $('input[name="csrfmiddlewaretoken"]').val($.cookie('csrftoken'));
      $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function (response) {
          $('#login-modal .logo').find('img').removeClass('waiting');
          huePubSub.publish('hue.login.result', response);
        }
      });
      $('#login-modal .logo').find('img').addClass('waiting');
      return false;
    });

    %if 'AllowAllBackend' in backend_names:
      $('#id_password').val('password');
    %endif

    %if backend_names == ['OAuthBackend']:
      $('#login-modal input').css({'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'});
      $('#login-modal input').bind('click', function () {
        window.location.replace('/login/oauth/');
        return false;
      });
    %endif
  });
</script>

