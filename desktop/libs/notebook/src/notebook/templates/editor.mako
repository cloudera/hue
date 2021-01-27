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

  from desktop.views import commonfooter, commonshare
  from desktop import conf
%>

<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="editorComponents" file="editor_components.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />

<div id="editorComponents" class="editorComponents notebook">
  ${ editorComponents.includes(is_embeddable=is_embeddable, suffix='editor') }
  ${ editorComponents.topBar(suffix='editor') }
  ${ editorComponents.commonHTML(is_embeddable=is_embeddable, suffix='editor') }
  ${ editorComponents.commonJS(is_embeddable=is_embeddable, suffix='editor') }
</div>

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif
