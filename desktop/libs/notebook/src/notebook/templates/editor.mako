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

  from notebook.conf import ENABLE_NOTEBOOK_2
%>

<%namespace name="configKoComponents" file="/config_ko_components.mako" />
<%namespace name="editorComponents" file="editor_components.mako" />
<%namespace name="editorComponents2" file="editor_components2.mako" />
<%namespace name="notebookKoComponents" file="/common_notebook_ko_components.mako" />
<%namespace name="hueAceAutocompleter" file="/hue_ace_autocompleter.mako" />

<div id="editorComponents" class="editorComponents notebook">
% if ENABLE_NOTEBOOK_2.get():
<div style="display: flex; flex-direction:column; height: 100%; width: 100%">
  <div style="flex: 0 0 auto;">
  ${ editorComponents2.includes(is_embeddable=is_embeddable, suffix='editor') }
  ${ editorComponents2.topBar(suffix='editor') }
  </div>
  <div style="flex: 1;">
  ${ editorComponents2.commonHTML(is_embeddable=is_embeddable, suffix='editor') }
  </div>
  ${ editorComponents2.commonJS(is_embeddable=is_embeddable, suffix='editor') }
</div>
% else:
  ${ editorComponents.includes(is_embeddable=is_embeddable, suffix='editor') }
  ${ editorComponents.topBar(suffix='editor') }
  ${ editorComponents.commonHTML(is_embeddable=is_embeddable, suffix='editor') }
  ${ editorComponents.commonJS(is_embeddable=is_embeddable, suffix='editor') }
% endif
</div>

% if not is_embeddable:
  ${ commonfooter(request, messages) | n,unicode }
% endif
