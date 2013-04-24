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
%>

<%namespace name="utils" file="utils.inc.mako" />

<%def name="skeleton()">
  <link rel="stylesheet" href="/search/static/css/admin.css">
  <link rel="stylesheet" href="/static/ext/chosen/chosen.css">
  <script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

  <div class="container-fluid">
    %if hasattr(caller, "title"):
      ${caller.title()}
    %else:
        <h1>${_('Search Admin')}</h1>
    %endif
    <div class="row-fluid">
      %if hasattr(caller, "navigation"):
          <div class="span2">
            ${caller.navigation()}
          </div>

          <div class="span10">
            %if hasattr(caller, "content"):
              ${caller.content()}
            %endif
          </div>
      %else:
        <div class="span12">
          %if hasattr(caller, "content"):
              ${caller.content()}
          %endif
        </div>
      %endif
    </div>
  </div>
  <script type="text/javascript">
    $(document).ready(function () {
      $("#change-core").change(function(){
        location.href = $("#change-core").val();
      });
    });
  </script>
</%def>

<%def name="sidebar(core, section='')">
  <div class="well sidebar-nav" style="min-height: 250px">
    <ul class="nav nav-list">

    <li class="nav-header">${_('Core')}</li>
      <li class="${ utils.is_selected(section, 'properties') }">
        <a href="${ url('search:admin_core_properties', core=core) }"><i class="icon-reorder"></i> ${_('Properties')}</a>
      </li>

      <li class="nav-header">${_('Template')}</li>
      <li class="${ utils.is_selected(section, 'template') }">
        <a href="${ url('search:admin_core_template', core=core) }">${_('1. Snippet')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'facets') }">
        <a href="${ url('search:admin_core_facets', core=core) }">${_('2. Facets')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'sorting') }">
        <a href="${ url('search:admin_core_sorting', core=core) }">${_('3. Sorting')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'highlighting') }">
        <a href="${ url('search:admin_core_highlighting', core=core) }">${_('4. Highlighting')}</a>
      </li>

      <li class="nav-header">${_('Search')}</li>
      <li>
        <a href="${ url('search:index') }?collection=${ core }"><i class="icon-share-alt"></i> ${ _('Query') }</a>
      </li>
    </ul>
  </div>
</%def>