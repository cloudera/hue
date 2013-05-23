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
      $("#change-collection").change(function(){
        location.href = $("#change-collection").val();
      });
    });
  </script>
</%def>

<%def name="sidebar(collection, section='')">
  <div class="well sidebar-nav" style="min-height: 250px">
    <ul class="nav nav-list">

    <li class="nav-header">${_('Collection')}</li>
      <li class="${ utils.is_selected(section, 'properties') }">
        <a href="${ url('search:admin_collection_properties', collection=collection) }"><i class="icon-reorder"></i> ${_('Properties')}</a>
      </li>
      ## Yes or no????? No for now
      <li class="${ utils.is_selected(section, 'cores') }">
        <a href="${ url('search:admin_collection_properties', collection=collection) }"><i class="icon-reorder"></i> ${_('Cores')}</a>
      </li>

      <li class="nav-header">${_('Template')}</li>
      <li class="${ utils.is_selected(section, 'template') }">
        <a href="${ url('search:admin_collection_template', collection=collection) }">${_('1. Snippet')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'facets') }">
        <a href="${ url('search:admin_collection_facets', collection=collection) }">${_('2. Facets')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'sorting') }">
        <a href="${ url('search:admin_collection_sorting', collection=collection) }">${_('3. Sorting')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'highlighting') }">
        <a href="${ url('search:admin_collection_highlighting', collection=collection) }">${_('4. Highlighting')}</a>
      </li>

      <li class="nav-header">${_('Search')}</li>
      <li>
        <a href="${ url('search:index') }?collection=${ collection }"><i class="icon-share-alt"></i> ${ _('Query') }</a>
      </li>
    </ul>
  </div>
</%def>