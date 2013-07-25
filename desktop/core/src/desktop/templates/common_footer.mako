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
from django.utils.translation import ugettext as _
from django.template.defaultfilters import escape, escapejs
%>


%if messages:
  <script>
    %for message in messages:
      %if message.tags == 'error':
        $.jHueNotify.error('${ escapejs(escape(message)) }');
      %else:
        $.jHueNotify.info('${ escapejs(escape(message)) }');
      %endif
    %endfor
  </script>
%endif

<script type="text/javascript">
  $(document).ready(function () {
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
          var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
                  results = regex.exec(_qs);
          return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
        }
    %endif
  });

  function resetPrimaryButtonsStatus() {
    $(".btn-primary:not(.disable-feedback), .btn-danger:not(.disable-feedback)").button("reset");
  }

  var _catchEnterKeyOnModals = false;

  $(".modal").on("shown", function () {
    _catchEnterKeyOnModals = true;
    // safe ux enhancement: focus on the first editable input
    $(".modal:visible").find("input:visible:first").focus();
  });

  $(".modal").on("hidden", function () {
    _catchEnterKeyOnModals = false;
  });

  $(document).on("keyup", function (e) {
    var _code = (e.keyCode ? e.keyCode : e.which);
    if (_catchEnterKeyOnModals && $(".modal").is(":visible") && _code == 13) {
      var _currentModal = $(".modal:visible");
      if (_currentModal.find(".btn-primary").length > 0) {
        _currentModal.find(".btn-primary").click();
      }
      else if (_currentModal.find(".btn-danger").length > 0) {
        _currentModal.find(".btn-danger").click();
      }
    }
  });

    %if collect_usage:

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-40351920-1']);

      // We collect only 2 path levels: not hostname, no IDs, no anchors...
      var _pathName = location.pathname;
      var _splits = _pathName.substr(1).split("/");
      _pathName = _splits[0] + (_splits.length > 1 && $.trim(_splits[1]) != "" ? "/" + _splits[1] : "");

      _gaq.push(['_trackPageview', '/remote/${ version }/' + _pathName]);

      (function () {
        var ga = document.createElement('script');
        ga.type = 'text/javascript';
        ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(ga, s);
      })();

      function trackOnGA(path) {
        if (typeof _gaq != "undefined" && _gaq != null) {
          _gaq.push(['_trackPageview', '/remote/${ version }/' + path]);
        }
      }

    %endif

</script>
%if tours_and_tutorials:
  <script src="/static/js/Source/jHue/available.tours.js"></script>
  <div id="jHueTourModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
      <h3>${_('Did you know?')}</h3>
    </div>
    <div class="modal-body">
      <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="icon-flag-checkered"></i></div>
      <div style="margin: 10px">
      <p>
        ${_('There is one or more tours available for this page. These tours were created to guide you around.')}
      </p>
      <p>
        ${_('You can see the list of the tours by clicking on the checkered flag badge on the side of this page.')}
      </p>
        </div>
    </div>
    <div class="modal-footer">
      <label class="checkbox" style="float:left"><input id="jHueTourModalChk" type="checkbox" />${_('Do not show this dialog again')}</label>
      <a href="#" class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Got it, prof!')}</a>
    </div>
  </div>
%endif
  </body>
</html>
