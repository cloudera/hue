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

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/admin.css">

<div class="search-bar" style="height: 30px">
    <div class="pull-right" style="margin-right: 20px">
    <a class="btn importBtn" href="${ url('indexer:collections') }">
      <i class="fa fa-database"></i> ${ _('Indexes') }
    </a>
    </div>
  <h4><a href="">${_('Dashboards')}</a></h4>
</div>


<div class="container-fluid">
  <div class="card">
  <%actionbar:render>
    <%def name="search()">
      <input type="text" placeholder="${_('Filter dashboards...')}" class="input-xlarge search-query" id="filterInput" data-bind="visible: collections().length > 0 && !isLoading()">
      &nbsp;
      &nbsp;
      <a data-bind="visible: collections().length > 0 && !isLoading()" class="btn" href="${ url('search:new_search') }" title="${ _('Create a new dashboard') }"><i class="fa fa-plus-circle"></i> ${ _('Dashboard') }</a>
    </%def>

    <%def name="creation()">
    </%def>
  </%actionbar:render>

  <div class="row-fluid" data-bind="visible: collections().length == 0 && !isLoading()">
    <div class="span10 offset1 center importBtn" style="cursor: pointer">
      <i class="fa fa-plus-circle waiting"></i>
      <h1 class="emptyMessage">
        ${ _('There are currently no dashboards defined.') }<br/>
        <a class="btn importBtn" href="${ url('search:new_search') }">
          <i class="fa fa-plus-circle"></i> ${ _('Dashboard') }
        </a>
      </h1>
    </div>
  </div>
  <div class="row-fluid" data-bind="visible: isLoading()">
    <div class="span10 offset1 center">
      <i class="fa fa-spinner fa-spin" style="font-size: 60px; color: #DDD"></i>
    </div>
  </div>
  <div class="row-fluid">
    <div class="span12">
      <p>
      <ul id="collections" data-bind="template: {name: 'collectionTemplate', foreach: filteredCollections}">
      </ul>
      </p>
    </div>
  </div>

  <script id="collectionTemplate" type="text/html">
    <li class="collectionRow" data-bind="click: $root.editCollection" title="${ _('Click to edit') }">
      <div class="pull-right" style="margin-top: 10px;margin-right: 10px; cursor: pointer">
        <a data-bind="click: $root.copyCollection, clickBubble: false"><i class="fa fa-files-o"></i> ${_('Copy')}</a> &nbsp;
        <a data-bind="click: $root.markForDeletion, clickBubble: false"><i class="fa fa-times"></i> ${_('Delete')}</a>
      </div>
      <h4><img src="/search/static/art/icon_search_48.png" class="app-icon"/> <span data-bind="text: label"></span></h4>
    </li>
  </script>
  </div>
</div>


<script id="importableTemplate" type="text/html">
  <tr>
    <td width="24">
      <div data-bind="click: handleSelect, css: {hueCheckbox: true, 'fa': true, 'fa-check': selected}"></div>
    </td>
    <td data-bind="text: name"></td>
  </tr>
</script>

<div id="deleteModal" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Confirm Delete')}</h3>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to delete this collection?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${_('No')}</a>
    <a id="deleteModalBtn" class="btn btn-danger disable-feedback" data-bind="click: deleteCollection">${_('Yes')}</a>
  </div>
</div>


<style type="text/css">
  #collections {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  .placeholder {
    height: 40px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }
</style>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/collections.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">

  var appProperties = {
    labels: [],
    listCollectionsUrl: "${ url("search:admin_collections") }?format=json",
    deleteUrl: "${ url("search:admin_collection_delete") }",
    copyUrl: "${ url("search:admin_collection_copy") }"
  }

  var viewModel = new SearchCollectionsModel(appProperties);
  ko.applyBindings(viewModel);

  $(document).ready(function () {
    viewModel.updateCollections();

    var orderedCores;
    serializeList();

    function serializeList() {
      orderedCores = [];
      $("#collections li").each(function () {
        orderedCores.push($(this).data("collection"));
      });
    }

    var filter = -1;
    $("#filterInput").on("keyup", function () {
      clearTimeout(filter);
      filter = window.setTimeout(function () {
        viewModel.filterCollections($("#filterInput").val());
      }, 300);
    });

    $("#deleteModal").modal({
      show: false
    });

    $(document).on("deleting", function () {
      var _btn = $("#deleteModalBtn");
      _btn.attr("data-loading-text", _btn.text() + " ...");
      _btn.button("loading");
    });

    $(document).on("collectionDeleted", function () {
      $("#deleteModal").modal("hide");
      $("#deleteModalBtn").button("reset");
      $(document).trigger("info", "${ _("Collection deleted successfully.") }");
    });

    $(document).on("collectionCopied", function () {
      $(document).trigger("info", "${ _("Collection copied successfully.") }");
    });

    $(document).on("confirmDelete", function () {
      $("#deleteModal").modal('show');
    });

  });
</script>

${ commonfooter(messages) | n,unicode }
