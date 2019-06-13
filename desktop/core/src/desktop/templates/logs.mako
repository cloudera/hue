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
from desktop.lib.conf import BoundConfig
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
import re
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />
%if not is_embeddable:
${ commonheader(_('Server Logs'), "about", user, request) | n,unicode }
%endif
${layout.menubar(section='log_view')}

<style type="text/css">
  pre {
    margin: 0;
    padding: 2px;
    border: 0;
    white-space: pre-wrap;
  }

  pre.nowrap {
    white-space: nowrap;
  }

  pre.highlighted {
    background-color: #FFFF88;
  }

  #hue-logs {
    overflow: auto;
    background-color: #F5F5F5;
    width: 100%;
  }

  #hue-logs pre:first-child {
    padding-top: 10px;
  }

  #hue-logs pre:last-child {
    padding-bottom: 10px;
  }

  .notFound {
    background-color: #f09999 !important;
  }
</style>

<div id="logsComponents" class="container-fluid">
  <div class="card card-small">
    <%actionbar:render>
      <%def name="search()">
        <input type="text" class="input-xlarge" id="hue-logs-search-query" placeholder="${_('Search in the logs')}" value="${query}">
      </%def>
      <%def name="creation()">
        <form class="form-inline">
            <label class="checkbox margin-right-10">
              ${ _('Host') }: ${ hostname }
            </label>
            <label class="checkbox margin-right-10">
              <input type="checkbox" id="forcedDebug" data-bind="checked: forcedDebug">
              ${_('Force DEBUG level')}
            </label>
            <label class="checkbox margin-right-10">
              <input id="wrapLogs" id="wrap" type="checkbox" checked="checked">
              ${_('Wrap logs')}
            </label>
            <a href="javascript:void(0)" onclick="huePubSub.publish('open.link', '/desktop/download_logs');" class="btn"><i class="fa fa-download"></i> ${_('Download entire log as zip')}</a>
        </form>
      </%def>
    </%actionbar:render>

    <% log.reverse() %>

    <div id="hue-logs">
        % for l in log:
          <pre>${smart_unicode(l, errors='ignore')}</pre>
        % endfor
    </div>

  </div>

</div>

<script>
  var LiveDebugging = function () {
    var self = this;

    self.forcedDebug = ko.observable();
    self.forcedDebug.subscribe(function(oldValue) {
      if (oldValue != null) {
        self.setLogLevel(! oldValue);
      }
    }, this, "beforeChange");

    self.getDebugLevel = function() {
      $.get("/desktop/get_debug_level", function(data) { self.forcedDebug(data.debug_all); });
    };

    self.setLogLevel = function(set_debug) {
      var _url = "";
      if (set_debug) {
        _url = "/desktop/set_all_debug";
      } else {
        _url = "/desktop/reset_all_debug";
      }

      $.post(_url, {}, function(data) {
        if (data,status != 0) {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  }

  $(document).ready(function () {
    var viewModel = new LiveDebugging();
    ko.applyBindings(viewModel, $("#logsComponents")[0]);

    viewModel.getDebugLevel();

    resizeScrollingLogs();

    var resizeTimeout = -1;
    $(window).resize(function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        resizeScrollingLogs();
      }, 200);
    });

    $("#hue-logs-search-query").jHueDelayedInput(function(){
      filterLogs($("#hue-logs-search-query").val());
    }, 500);

    if ("${query}" != "") {
      filterLogs("${query}");
    }

    function resizeScrollingLogs() {
      var _el = $("#hue-logs");
      if (_el.length > 0) {
        if (!$.browser.msie) {
          _el.css("overflow-y", "").css("height", "");
        }
        var heightAfter = 0;
        _el.nextAll(":visible").each(function () {
          heightAfter += $(this).outerHeight(true);
        });
        if (_el.height() > ($(window).height() - _el.offset().top - heightAfter)) {
          _el.css("overflow-y", "auto").height($(window).height() - _el.offset().top - heightAfter - 30);
        }
      }
    }

    function filterLogs(query) {
      $("#hue-logs-search-query").removeClass("notFound");
      if ($.trim(query) == "") {
        $("#hue-logs").scrollTop(0);
        return false;
      }
      $("pre.highlighted").removeClass("highlighted");
      var found = false;
      $("#hue-logs pre").each(function () {
        var _el = $(this);
        if (_el.text().toLowerCase().replace(/\s/g, "").indexOf(query.toLowerCase().replace(/\s/g, "")) > -1) {
          _el.addClass("highlighted");
          $("#hue-logs").scrollTop(_el.offset().top - $("#hue-logs").position().top - 100);
          found = true;
          return false;
        }
      });
      if (!found) {
        $("#hue-logs-search-query").addClass("notFound");
        $("#hue-logs").scrollTop(0);
      }
    }

    $("#wrapLogs").on("change", function(){
      if ($(this).is(":checked")){
        $("pre").removeClass("nowrap");
      }
      else {
        $("pre").addClass("nowrap");
      }
    });
  });
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif