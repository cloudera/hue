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
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from django.template.defaultfilters import escape, escapejs
from desktop.lib.i18n import smart_unicode
from desktop.views import login_modal
%>

% if request is not None:
${ smart_unicode(login_modal(request).content) | n,unicode }
% endif

<script type="text/javascript">
  $(document).ready(function () {
    $(document).on("info", function (e, msg) {
      $.jHueNotify.info(msg);
    });
    $(document).on("warn", function (e, msg) {
      $.jHueNotify.warn(msg);
    });
    $(document).on("error", function (e, msg) {
      $.jHueNotify.error(msg);
    });

    %if messages:
      %for message in messages:
        %if message.tags == 'error':
          $(document).trigger('error', '${ escapejs(escape(message)) }');
        %elif message.tags == 'warning':
          $(document).trigger('warn', '${ escapejs(escape(message)) }');
        %else:
          $(document).trigger('info', '${ escapejs(escape(message)) }');
        %endif
      %endfor
    %endif

    // global catch for ajax calls after the user has logged out
    var isLoginRequired = false;
    $(document).ajaxComplete(function (event, xhr, settings) {
      var whiteListURLs = [
        'filebrowser/copy?next='
      ];
      var whiteListed = false;
      whiteListURLs.forEach(function(url){
        if (settings.url.indexOf(url) > -1){
          whiteListed = true;
        }
      });
      if ((xhr.responseText === '/* login required */' || (xhr.status === 403 && !whiteListed)) && !isLoginRequired) {
        isLoginRequired = true;
        $('.blurred').removeClass('blurred');
        if ($('#login-modal').length > 0 && $('#login-modal').is(':hidden')) {
          $('#login-modal .link-message').hide();
          if (xhr.status === 403) {
            $('#login-modal .wrong-token').show();
            $('#login-modal').modal('show');
          }
          else {
            $('body').children(':not(#login-modal)').addClass('blurred');
            $('#login-modal .logged-out').show();
            $('#login-modal').modal({
              backdrop: 'static',
              keyboard: false
            });
          }
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
        if ($('#login-modal #id_username').val() !== LOGGED_USERNAME) { //LOGGED_USERNAME is in common_header
          location.reload();
        }
        else {
          $('#login-modal').modal('hide');
          $.jHueNotify.info('${ _('You have signed in successfully!') }');
          $('#login-modal .login-error').addClass('hide');
        }
      }
      else {
        $('#login-modal .login-error').removeClass('hide');
      }
    });


    $("div.navigator ul.dropdown-menu").css("maxHeight", $(window).height() - 50);
    var scrollableDropdownTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(scrollableDropdownTimeout);
      scrollableDropdownTimeout = window.setTimeout(function () {
        $("div.navigator ul.dropdown-menu").css("maxHeight", $(window).height() - 50);
      }, 500);
    });

    $(".dataTables_wrapper").jHueTableScroller();
    var resetTimeout = -1;
    var pendingRequestsInterval = -1;

    // sets feedback on every primary and danger action across Hue
    // can be disabled adding the class "disable-feedback" to the button
    $(document).on("click", ".btn-primary:not(.disable-feedback), .btn-danger:not(.disable-feedback)", function () {
      if (!$(this).hasClass('disabled')) {
        var text = ($(this).text() != "") ? $(this).text() : $(this).val();
        $(this).attr("data-loading-text", text + " ...");
        $(this).button("loading");
        startPendingRequestsPolling();
        resetTimeout = window.setTimeout(function () {
          resetPrimaryButtonsStatus();
        }, 200);
      }
    });

    $(document).on("hidden", ".modal", function () {
      resetPrimaryButtonsStatus();
    });

    $(window).unload(function () {
      window.clearInterval(pendingRequestsInterval);
      window.clearTimeout(resetTimeout);
    });

    $(document).on("submit", "form", function () {
      hasAjaxBeenSent = false;
      window.setInterval(function () {
        window.clearTimeout(resetTimeout);
      }, 10);
    });

    var hasAjaxBeenSent = false;
    $(document).ajaxSend(function () {
      hasAjaxBeenSent = true;
    });

    function startPendingRequestsPolling() {
      pendingRequestsInterval = window.setInterval(function () {
        if (hasAjaxBeenSent) {
          var activeRequests = 0;
          if (jQuery.ajax.active) {
            activeRequests = jQuery.ajax.active;
          }
          else {
            activeRequests = jQuery.active;
          }
          if (activeRequests == 0) {
            resetPrimaryButtonsStatus();
            window.clearInterval(pendingRequestsInterval);
          }
        }
        else {
          window.clearInterval(pendingRequestsInterval);
        }
      }, 200);
    }
    %if tours_and_tutorials:
        $.jHueTour({});
        if ($.totalStorage("jHueTourExtras") != null) {
          $.jHueTour({tours: $.totalStorage("jHueTourExtras")});
        }
        var _qs = location.search;
        if (_qs !== undefined && _qs.indexOf("tour=") > -1) {
          $.jHueTour(getParameterByName("tour"), 1);
        }
        function getParameterByName(name) {
          name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
          var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"), results = regex.exec(_qs);
          return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
        }
    %endif
  });

  function resetPrimaryButtonsStatus() {
    $(".btn-primary:not(.disable-feedback), .btn-danger:not(.disable-feedback)").button("reset");
  }

  var _catchEnterKeyOnModals = false;

  $(document).on("shown", ".modal", function () {
    _catchEnterKeyOnModals = true;
    // safe ux enhancement: focus on the first editable input
    $(".modal:visible").find('input:not(.disable-autofocus):visible:first').not($('.jHueFilechooserActions input')).focus();
  });

  $(document).on("hidden", ".modal", function () {
    _catchEnterKeyOnModals = false;
  });

  $(document).on("keyup", function (e) {
    var _code = (e.keyCode ? e.keyCode : e.which);
    if (_catchEnterKeyOnModals && $(".modal").is(":visible") && _code == 13) {
      var _currentModal = $(".modal:visible");
      if (_currentModal.find(".btn-primary:not(.disable-enter)").length > 0) {
        _currentModal.find(".btn-primary:not(.disable-enter)").click();
      }
      else if (_currentModal.find(".btn-danger:not(.disable-enter)").length > 0) {
        _currentModal.find(".btn-danger:not(.disable-enter)").click();
      }
    }
  });

  if (typeof nv != "undefined"){
    // hides all the nvd3 logs
    nv.log = function() {};
  }


    %if collect_usage:

      (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
      (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
      m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
      })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

      ga('create', 'UA-40351920-1', 'auto');
      ga('set', 'referrer', 'http://gethue.com'); // we force the referrer to prevent leaking sensitive information

      // We collect only 2 path levels: not hostname, no IDs, no anchors...
      var _pathName = location.pathname;
      var _splits = _pathName.substr(1).split("/");
      _pathName = _splits[0] + (_splits.length > 1 && $.trim(_splits[1]) != "" ? "/" + _splits[1] : "");

      ga('send', 'pageview', {
        'page': '/remote/${ version }/' + _pathName
      });

      function trackOnGA(path) {
        if (typeof ga != "undefined" && ga != null) {
          ga('set', 'referrer', 'http://gethue.com'); // we force the referrer to prevent leaking sensitive information
          ga('send', 'pageview', {
            'page': '/remote/${ version }/' + path
          });
        }
      }

    %endif

</script>

% if tours_and_tutorials:
  <%include file="tours.mako"/>
% endif

  </body>
</html>
