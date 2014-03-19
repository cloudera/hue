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
% if tours_and_tutorials:

<style type="text/css">
  .steps {
    min-height: 150px;
  }
</style>

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
$(document).ready(function(){
  var currentStep = "tourStep1";

  routie({
    "tourStep1":function () {
      showStep("tourStep1");
    },
    "tourStep2":function () {
      showStep("tourStep2");
    },
    "tourStep3":function () {
      showStep("tourStep3");
    }
  });

  function showStep(step) {
    currentStep = step;

    $("a.tourStep").parent().removeClass("active");
    $("a.tourStep[href=#" + step + "]").parent().addClass("active");
    if (step == "tourStep3") {
      $("#tourLastStep").parent().addClass("active");
    }
    $(".tourStepDetails").hide();
    $("#" + step).show();
  }
});
</script>

  <%include file="tours.mako"/>

  <div id="jHueTourModal" class="modal fade" tabindex="-1">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
      <h3>${_('Did you know?')}</h3>
    </div>
    <div class="modal-body">
     <div class="row-fluid">
       <div id="properties" class="section">
      <ul class="nav nav-tabs" style="margin-bottom: 0">
        <li class="active"><a href="#tourStep1" class="tourStep">${ _('Step 1:') } ${ _('Add data') }</a></li>
        <li><a href="#tourStep2" class="tourStep">${ _('Step 2:') }  ${ _('Query data') }</a></li>
        <li><a id="tourLastStep" href="#tourStep3" class="tourStep">${ _('Step 3:') } ${_('Do more!') }</a></li>
      </ul>
    </div>

    <div class="tourSteps">
      <div id="tourStep1" class="tourStepDetails">
        <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-download"></i></div>
        <div style="margin: 40px">
          <p>
            ${ _('With') }  <span class="badge badge-info"><i class="fa fa-file"></i> File Browser</span>
            ${ _('and the apps in the') }  <span class="badge badge-info">Data Browsers <b class="caret"></b></span> ${ _('section, upload, view your data and create tables.') }
          </p>
          <p>
            ${ _('Pre-installed samples are also already there.') }
          </p>
        </div>
      </div>

      <div id="tourStep2" class="tourStepDetails hide">
          <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-search"></i></div>
          <div style="margin: 40px">
            <p>
              ${ _('Then query and visualize the data with the') } <span class="badge badge-info">Query Editors <b class="caret"></b></span>
               ${ _('and') }  <span class="badge badge-info">Search <b class="caret"></b></span>
            </p>
          </div>
      </div>

      <div id="tourStep3" class="tourStepDetails hide">
        <div class="pull-left" style="color: #DDDDDD;font-size: 116px;margin: 10px; margin-right: 20px"><i class="fa fa-flag-checkered"></i></div>
        <div style="margin: 40px">
          <p>
            ${ _('Tours were created to guide you around.') }
            ${ _('You can see the list of tours by clicking on the checkered flag icon') } <span class="badge badge-info"><i class="fa fa-flag-checkered"></i></span>
            ${ ('at the top right of this page.') }
          </p>
          <p>
            ${ _('More documentation is available at') } <a href="http://learn.gethue.com">learn.gethue.com</a>.
          </p>
        </div>
      </div>
     </div>
     </div>
     <div class="modal-footer">
       <label class="checkbox" style="float:left"><input id="jHueTourModalChk" type="checkbox" />${_('Do not show this dialog again')}</label>
       <a id="jHueTourModalClose" href="#" class="btn btn-primary disable-feedback">${_('Got it, prof!')}</a>
     </div>
   </div>
% endif
  </body>
</html>
