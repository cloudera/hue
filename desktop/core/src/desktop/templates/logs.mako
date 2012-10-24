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
${commonheader(_('About'), "about", user, "100px")}
${layout.menubar(section='log_view')}

<style>
  pre {
    margin: 0;
    padding: 2px;
    border: 0;
  }

  pre.highlighted {
    background-color: #FFFF88;
  }

  #logs {
    overflow: auto;
  }

  #logs pre:first-child {
    padding-top: 10px;
  }

  #logs pre:last-child {
    padding-bottom: 10px;
  }

  .notFound {
    background-color: #f09999 !important;
  }
</style>

<div class="container-fluid">
  <h1>${_('Log entries (most recent first)')}</h1>

  <%actionbar:render>
    <%def name="search()">
        <input type="text" class="input-xxlarge search-query" placeholder="${_('Search...')}" value="${query}">
    </%def>
    <%def name="creation()">
        <span class="btn-group">
          <a href="/download_logs" class="btn"><i class="icon-download-alt"></i> ${_('Download entire log as zip')}</a>
        </span>
    </%def>
  </%actionbar:render>

  <% log.reverse() %>

  <div id="logs">
      % for l in log:
        <pre>${smart_unicode(l, errors='ignore') | h}</pre>
      % endfor
  </div>

</div>

<script>
  $(document).ready(function () {

    resizeScrollingLogs();

    var resizeTimeout = -1;
    $(window).resize(function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        resizeScrollingLogs();
      }, 200);
    });

    var filterTimeout = -1;
    $(".search-query").keyup(function () {
      window.clearTimeout(filterTimeout);
      filterTimeout = window.setTimeout(function () {
        filterLogs($(".search-query").val());
      }, 500);
    });

    if ("${query}" != "") {
      filterLogs("${query}");
    }

    function resizeScrollingLogs() {
      var _el = $("#logs");
      if (!$.browser.msie) {
        _el.css("overflow-y", "").css("height", "");
      }
      var heightAfter = 0;
      _el.nextAll(":visible").each(function () {
        heightAfter += $(this).outerHeight(true);
      });
      if (_el.height() > ($(window).height() - _el.offset().top - heightAfter)) {
        _el.css("overflow-y", "auto").height($(window).height() - _el.offset().top - heightAfter);
      }
    }

    function filterLogs(query) {
      $(".search-query").removeClass("notFound");
      if ($.trim(query) == "") {
        $("#logs").scrollTop(0);
        return false;
      }
      $("pre.highlighted").removeClass("highlighted");
      var found = false;
      $("#logs pre").each(function () {
        var _el = $(this);
        if (_el.text().toLowerCase().replace(/\s/g, "").indexOf(query.toLowerCase().replace(/\s/g, "")) > -1) {
          _el.addClass("highlighted");
          $("#logs").scrollTop(_el.offset().top - $("#logs").position().top - 4);
          found = true;
          return false;
        }
      });
      if (!found) {
        $(".search-query").addClass("notFound");
        $("#logs").scrollTop(0);
      }
    }
  });
</script>

${commonfooter(messages)}
