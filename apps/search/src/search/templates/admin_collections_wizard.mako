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
  from django.utils.translation import ugettext as _
%>

<%namespace name="macros" file="macros.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }

<link rel="stylesheet" href="/search/static/css/admin.css">

<div class="container-fluid">
  % if collections:
  <h1>${_('Import a new collection')}</h1>

  <div class="row-fluid">
    <div class="span12">
      <ul id="collections">
      % for collection in collections:
        <li>
          <a class="addCollection" data-name="${ collection }">
            <h4><i class="icon-list"></i> ${ collection }</h4>
          </a>
        </li>
      % endfor
      </ul>
    </div>
  </div>
  % endif

  % if cores:
  <h1>${_('Import a new core')}</h1>

  <div class="row-fluid">
    <div class="span12">
      <ul id="collections">
      % for core in cores:
        <li>
          <h4><i class="icon-list"></i> ${ core }</h4>
        </li>
      % endfor
      </ul>
    </div>
  </div>
  % endif

  % if not collections and not cores:
  <h1>${_('No available indexes')}</h1>

  <div class="row-fluid">
    ${ _('Already installed all the collections. You can change the indexes URL in hue.ini.') }
  </div>
  % endif

</div>

<style type="text/css">
  #collections {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  #collections li {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #E3E3E3;
    height: 40px;
  }

  .placeholder {
    height: 40px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }
</style>

<script type="text/javascript">
  $(document).ready(function () {
    $(".addCollection").click(function() {
      var collectionName = $(this).data('name');
      $.post('${ url("search:admin_collections_wizard") }', {type: 'collection', name: collectionName},
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Problem: ') }" + response['message']);
          } else {
            window.location = "/search/admin/collection/" + collectionName;
          }
	  });
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
