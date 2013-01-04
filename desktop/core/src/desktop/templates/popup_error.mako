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
from desktop.views import commonheader, commonfooter
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

${ commonheader(title, "", user) | n,unicode }

  <div class="container-fluid">
    <div class="alert">
      <p><strong>${smart_unicode(message)}</strong></p>

      % if detail:
      <p>${smart_unicode(detail) or "" }</p>
      % endif

    </div>

    <div class="details">
      % if traceback:
        <a href="javascript:toggleDisplay('#traceback');"><i class="icon-share-alt"></i> ${_('More Info')}</a>
        &nbsp;
        <a href="/logs" target="_new">${_('View Logs')}</a>
        <br />
        <br />
        <div id="traceback" class="hide">
          <table class="table table-striped" style="background: white; border: 1px solid #DDDDDD;">
            <thead>
              <tr>
                <td>${_("File Name")}</td>
                <td>${_("Line Number")}</td>
              <td>${_("Function Name")}</td>
              </tr>
            </thead>
            <tbody>
              % for (file_name, line_number, function_name, text) in traceback:
                <tr>
                  <td>${smart_unicode(file_name) or ""}</td>
                  <td>${smart_unicode(line_number) or ""}</td>
                  <td>${smart_unicode(function_name) or ""}</td>
                </tr>
              % endfor
            </tbody>
          </table>
        </div>
      % else:
        <a href="/logs" target="_new">${_('View Logs')}</a>
        <br />
        <br />
      % endif
    </div>

    <div class="alert-actions">
      <a class="btn small" href="javascript:window.history.back(-1)">${_('Go back')}</a>
    </div>
  </div>

  <script type="text/javascript">
    function toggleDisplay(selector) {
      $(selector).slideToggle(500);
    }
  </script>

${ commonfooter(messages) | n,unicode }
