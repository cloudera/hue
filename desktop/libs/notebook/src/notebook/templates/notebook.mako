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
  from desktop import conf
  from django.utils.translation import ugettext as _
%>

<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="editorComponents" file="editor_components.mako" />
<%namespace name="notebookKoComponents" file="notebook_ko_components.mako" />

${ commonheader(_('Notebook'), app_name, user, "68px") | n,unicode }

${ editorComponents.includes() }
${ editorComponents.topBar(editor_type) }
<%editorComponents:commonHTML>
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

${ tableStats.tableStats() }
${ assist.assistPanel() }
${ configKoComponents.config() }
${ notebookKoComponents.addSnippetMenu() }
${ notebookKoComponents.downloadSnippetResults() }

${ editorComponents.commonJS() }

${ commonfooter(request, messages) | n,unicode }
