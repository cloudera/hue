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
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
from desktop.auth.backend import is_admin
%>

%if not is_embeddable:
${ commonheader(_('500 - Server error'), "", user, request) | n,unicode }
%endif

<link rel="stylesheet" href="${ static('desktop/css/httperrors.css') }">

<div id="httperror" class="container-fluid">
  <div class="row-fluid">
    <div class="span12 center">
      <div class="error-code">500</div>
    </div>
  </div>
  <div class="row-fluid">
    <div class="
    % if traceback:
    span8 offset2
    % else:
    span6 offset3
    % endif
    center error-box">
      <h1>${_('Server error.')}</h1>

      <p>${_("Sorry, there's been an error. An email was sent to your administrators. Thank you for your patience.")}</p>
      <br/>

      % if traceback and is_admin(user):
        <a href="javascript:toggleDisplay('#traceback');" title="${ _('See the stacktrace') }">${_('More info...')}</a>
          &nbsp;|&nbsp;
        <a href="/logs" target="_new" title="${ _('View server logs') }">${_('View logs')}</a>
        <div id="traceback" class="hide">
          <table class="table table-condensed margin-top-30" style="background: white; border: 1px solid #DDDDDD;">
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
        % if is_admin(user):
          <a href="/logs" ${ not is_embeddable and 'target="_blank"'  or '' } title="${ _('View server logs') }">${_('View logs')}</a>
        % endif
      % endif

    </div>
  </div>
</div>

<script type="text/javascript">
  function toggleDisplay(selector) {
    $(selector).slideToggle(500);
  }
</script>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
