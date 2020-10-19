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

  <link href="${ static('desktop/ext/css/cui/cui.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap2.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/cui/bootstrap-responsive2.css') }" rel="stylesheet">

  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue3.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/hue3-extra.css') }" rel="stylesheet">

  <style type="text/css">
    body {
      padding-top: 80px;
    }

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
      background-color: #0B7FAD;
      height: 4px;
      width: 100%;
    }

	.btn.btn-large {
			min-width: 38%;
			margin: 8px 0 0 0;
			text-align: left;

			/*......added from here......*/
			min-height: 0;
			height: auto;
	}

	.icons-only {
			text-align: center;
	}

	.icons-only .btn.btn-large img {
			margin-right: 0;
	}

	.icons-only .btn.btn-large span {
			display: none;
			text-align: center;
	}

	.icons-only .btn.btn-large {
			min-width: 32px;
			text-align: center;
	}

	.login-content h3 {
			text-align: center;
			margin: 0 0 -25px;
			font-size: 18px;
			color: silver;
	}

  </style>
</head>

<body>

<div class="footer"></div>

<div class="navigator">
  <a class="brand nav-tooltip pull-left" href="#">
    <img src="${ static('desktop/art/hue-logo-mini-white.png') }" alt="${ _('Hue logo') }"
       data-orig="${ static('desktop/art/hue-logo-mini-white.png') }"
       data-hover="${ static('desktop/art/hue-logo-mini-white-hover.png') }"/>
  </a>
  <ul class="nav nav-pills pull-left hide" id="visit">
    <li><a title="${_('Visit gethue.com')}" href="http://gethue.com">${_('Fell asleep? Visit us on gethue.com instead!')} <i class="fa fa-external-link-circle"></i></a></li>
  </ul>
</div>


<div class="container">
  <div class="row">
    <div class="login-content">
      <form method="POST" action="${action}" class="well">
        ${ csrf_token(request) | n,unicode }
        <img id="logo" src="${ static('desktop/art/hue-login-logo.png') }" data-orig="${ static('desktop/art/hue-login-logo.png') }"
             data-hover="${ static('desktop/art/hue-login-logo-skew.png') }" alt="${ _('Hue logo') }"/>

        %if login_errors:
            <div class="alert alert-error" style="text-align: center">
              <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong> ${_('Invalid username or password.')}
            </div>
        %endif

        %if first_login_ever:
            <div class="alert alert-block">
              <i class="fa fa-exclamation-triangle"></i>
            ${_('This is your first time logging in.')}
              <strong>${_('You will become Hue superuser.')}</strong>.
            </div>
            <h3>${_('Sign Up via')}</h3>
            <hr/>
        %else:
            <h3>${_('Sign In via')}</h3>
            <hr/>
        %endif
            <div id="buttons_group" class="buttons-group">
                %if socialGoogle:
                    <span class="btn btn-large btn-primary google">
                      <img src="${ static('liboauth/art/icon-gplus.png') }" alt="${ _('Google icon') }">
                      <span>Google</span>
                    </span>
                %endif
                %if socialFacebook:
                    <span class="btn btn-large btn-primary facebook">
                      <img src="${ static('liboauth/art/icon-fb.png') }" alt="${ _('Facebook icon') }">
                      <span>Facebook</span>
                    </span>
                %endif
                %if socialLinkedin:
                    <span class="btn btn-large btn-primary linkedin">
                      <img src="${ static('liboauth/art/icon-linkedin.png') }" alt="${ _('Linkedin icon') }">
                      <span>Linkedin</span>
                    </span>
                %endif
                %if socialTwitter:
                    <span class="btn btn-large btn-primary twitter">
                      <img src="${ static('liboauth/art/icon-twitter.png') }" alt="${ _('Twitter icon') }">
                      <span>Twitter</span>
                    </span>
                %endif
                %if not socialGoogle and not socialFacebook and not socialLinkedin and not socialTwitter:
                  ${ _('The oauth app is not configured with any provider.') }
                % endif
            </div>
        <input type="hidden" name="next" value="${next}"/>
      </form>
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/jquery/jquery-3.5.1.min.js') }"></script>
<script>
  var $buttonsGroup = $("#buttons_group");
  if($buttonsGroup.children().length > 2) {
     $buttonsGroup.addClass("icons-only");
  }

  $(document).ready(function () {
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

        $("input").css({"display": "block", "margin-left": "auto", "margin-right": "auto"});
        $("span.google").on('click', function () {
          window.location.replace('/oauth/social_login/oauth?social=google');
          return false;
        });
        $("span.facebook").on('click', function () {
          window.location.replace('/oauth/social_login/oauth?social=facebook');
          return false;
        });

        $("span.linkedin").on('click', function () {
          window.location.replace('/oauth/social_login/oauth?social=linkedin');
          return false;
        });
        $("span.twitter").on('click', function () {
          window.location.replace('/oauth/social_login/oauth?social=twitter');
          return false;
        });

    $("ul.errorlist").each(function () {
      $(this).prev().addClass("error");
    });
  });
</script>
</body>
</html>
