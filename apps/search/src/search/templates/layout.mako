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
  <link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
  <script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

  <div class="search-bar" style="height: 30px">
    % if not hasattr(caller, "no_navigation"):
      <div class="pull-right" style="margin-top: 4px; margin-right: 20px">
        <a href="${ url('search:index') }?collection=${ hue_collection.id }"><i class="fa fa-share"></i> ${ _('Search page') }</a> &nbsp; &nbsp;
        <a href="${ url('search:admin_collections') }"><i class="fa fa-sitemap"></i> ${ _('Collection manager') }</a>
      </div>
    % endif

    % if hasattr(caller, "title"):
      ${ caller.title() }
    % else:
        <h4>${ _('Search Admin') }</h4>
    % endif
  </div>

  <div class="container-fluid">

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

<%def name="sidebar(hue_collection, section='')">
  <div class="sidebar-nav" style="min-height: 250px">
    <ul class="nav nav-list">

    <li class="nav-header">${_('Collection')}</li>
      <li class="${ utils.is_selected(section, 'properties') }">
        <a href="${ url('search:admin_collection_properties', collection_id=hue_collection.id) }"><i class="fa fa-list"></i> ${_('Properties')}</a>
      </li>
      <li>
        <a href="${ url('search:index') }?collection=${ hue_collection.id }"><i class="fa fa-search"></i> ${ _('Search it') }</a>
      </li>

      <li class="nav-header">${_('Template')}</li>
      <li class="${ utils.is_selected(section, 'template') }">
        <a href="${ url('search:admin_collection_template', collection_id=hue_collection.id) }">${_('1. Snippet')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'facets') }">
        <a href="${ url('search:admin_collection_facets', collection_id=hue_collection.id) }">${_('2. Facets')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'sorting') }">
        <a href="${ url('search:admin_collection_sorting', collection_id=hue_collection.id) }">${_('3. Sorting')}</a>
      </li>
      <li class="${ utils.is_selected(section, 'highlighting') }">
        <a href="${ url('search:admin_collection_highlighting', collection_id=hue_collection.id) }">${_('4. Highlighting')}</a>
      </li>

    </ul>
  </div>
</%def>
