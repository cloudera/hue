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
  import sys 

  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
  from desktop.auth.backend import is_admin

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="docBrowser" file="/document_browser.mako" />

<%def name="homeJSModels(is_embeddable=False)">
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.mousewheel.min.js') }"></script>
  <script src="${ static('desktop/js/home2.vm.js') }"></script>

  ${ docBrowser.docBrowser(is_embeddable) }
</%def>


<%def name="navbar()">
<div class="navbar hue-title-bar nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="app-header">
            <a href="${ url('desktop_views_home2') }">
              <img src="${ static('desktop/art/home.png') }" class="app-icon" alt="${ _('Home icon') }" />
              ${ _('My documents') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="vm(is_embeddable=False)">
<script type="text/html" id="document-template">
  <tr>
    <td style="width: 26px"></td>
    <td><a data-bind="attr: { href: absoluteUrl }, html: name"></a></td>
    <td data-bind="text: ko.mapping.toJSON($data)"></td>
  </tr>
</script>

</%def>
