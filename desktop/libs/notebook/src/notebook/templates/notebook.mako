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
  from desktop.auth.backend import is_admin
  from desktop.conf import ENABLE_CONNECTORS
  from desktop.views import commonfooter, commonshare

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="editorComponents" file="editor_components.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />


<div id="notebookComponents" class="notebook">
  ${ editorComponents.includes(is_embeddable=is_embeddable, suffix='notebook') }
  ${ editorComponents.topBar(suffix='notebook') }
  <%editorComponents:commonHTML is_embeddable="${is_embeddable}" suffix="notebook">
    <%def name="addSnippetHTML()">
      <h1 class="empty" data-bind="visible: $root.availableSnippets().length == 0">${ _('There are no snippets configured.') }</h1>

      <!-- ko if: $root.availableSnippets().length > 0 -->
    <h1 class="empty" data-bind="visible: snippets().length == 0">${ _('Add a snippet to start your new notebook') }</h1>

    <div class="add-snippet" data-bind="component: {
      name: 'add-snippet-menu',
      params: {
        notebook: $data,
        availableSnippets: $root.availableSnippets
      }
    }">
    </div>
      <!-- /ko -->
    </%def>
  </%editorComponents:commonHTML>

  ${ notebookKoComponents.addSnippetMenu() }

  ${ editorComponents.commonJS(is_embeddable=is_embeddable, bindableElement='notebookComponents', suffix='notebook') }
</div>
