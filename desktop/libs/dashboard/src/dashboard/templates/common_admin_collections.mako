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
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport, _ko
  from django.utils.translation import ugettext as _
%>

<%namespace name="macros" file="macros.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

<%def name="page_structure(is_mobile=False)">

<link rel="stylesheet" href="${ static('dashboard/css/admin.css') }">
%if is_mobile:
<link rel="stylesheet" href="${ static('dashboard/css/admin_mobile.css') }">
<h3 style="text-align: center">${_('Dashboards')}</h3>
%endif

<div id="collectionsComponents">
%if not is_mobile:
<div class="search-bar" style="height: 30px">
  <div class="pull-right">
    % if user.has_hue_permission(action="access", app='indexer'):
    <a class="btn importBtn" href="${ is_embeddable and "javascript: huePubSub.publish('open.link', '" + url('indexer:collections') + "')" or url('indexer:collections') }" title="${ _('Indexes') }">
      <i class="fa fa-database"></i> ${ _('Indexes') }
    </a>
    % endif
  </div>
  <h4><i class="fa fa-list"></i> ${_('Dashboards')}</h4>
</div>
%endif

<div class="container-fluid">
  <div class="card card-home card-small" style="min-height: 400px">
    <%actionbar:render>
      <%def name="search()">
        <input type="text" placeholder="${_('Filter dashboards...')}" class="input-xlarge search-query" id="filterInput" data-bind="visible: collections().length > 0 && !isLoading()">
      </%def>

      <%def name="actions()">
        %if not is_mobile:
        <a data-bind="visible: collections().length > 0 && !isLoading(), click: $root.copyCollections, clickBubble: false, css: {'btn': true, 'disabled': selectedCollections().length == 0}">
          <i class="fa fa-files-o"></i> ${_('Copy')}
        </a>

        <a data-bind="visible: collections().length > 0 && !isLoading(), click: $root.markManyForDeletion, clickBubble: false, css: {'btn': true, 'disabled': ! atLeastOneSelected()}">
          <i class="fa fa-times"></i> ${_('Delete')}
        </a>

        <a class="share-link btn" rel="tooltip" data-placement="bottom" style="margin-left:20px" data-bind="visible: collections().length > 0 && !isLoading(), click: function(e){ $root.oneSelected() ? prepareShareModal(e) : void(0) },
          attr: {'data-original-title': '${ _ko("Share") } ' + name},
          css: {'disabled': ! $root.oneSelected(), 'btn': true}">
          <i class="fa fa-users"></i> ${ _('Share') }
        </a>

        <a data-bind="visible: collections().length > 0 && !isLoading(), click: function() { atLeastOneSelected() ? exportDocuments() : void(0) }, css: {'btn': true, 'disabled': ! atLeastOneSelected() }">
          <i class="fa fa-download"></i> ${ _('Export') }
        </a>
        %endif
      </%def>

      <%def name="creation()">
        %if not is_mobile:
        <a data-bind="visible: collections().length > 0 && !isLoading()" class="btn" href="${ is_embeddable and "javascript: huePubSub.publish('open.link', '" + url('dashboard:new_search') + "')" or url('dashboard:new_search') }" title="${ _('Create a new dashboard') }">
          <i class="fa fa-plus-circle"></i> ${ _('Create') }
        </a>
        <a data-bind="visible: !isLoading(), click: function() { $('#import-documents').modal('show'); }" class="btn">
          <i class="fa fa-upload"></i> ${ _('Import') }
        </a>
        %endif
      </%def>
    </%actionbar:render>

    <div class="row-fluid" data-bind="visible: collections().length == 0 && !isLoading()">
      <div class="span10 offset1 center importBtn pointer">
        <a href="${ url('dashboard:new_search') }">
          <i class="fa fa-plus-circle waiting"></i>
        </a>

        <h1 class="emptyMessage">
          ${ _('There are currently no dashboards defined.') }<br/>
          <a href="${ url('dashboard:new_search') }">${ _('Click here to add') }</a> ${ _('one or more.') }</h1>
        </h1>
      </div>
    </div>

    <div class="row-fluid" data-bind="visible: isLoading()">
      <div class="span10 offset1 center">
        <i class="fa fa-spinner fa-spin spinner"></i>
      </div>
    </div>

    <div class="row-fluid" data-bind="visible: collections().length > 0 && !isLoading()">
      <div class="span12">
        <table class="table table-condensed">
          <thead>
            <tr>
              <th style="width: 1%">
                <span data-bind="click: toggleSelectAll, css: {'fa-check': ! ko.utils.arrayFilter(filteredCollections(), function(collection) {return !collection.selected()}).length}" class="hue-checkbox fa"></span>
              </th>
              <th>${ _('Name') }</th>
              <th>${ _('Description') }</th>
              <th width="15%">${ _('Owner') }</th>
            </tr>
          </thead>
          <tbody data-bind="foreach: filteredCollections">
            <tr>
              <td data-bind="click: $root.toggleCollectionSelect.bind($root), clickBubble: false">
                <span data-bind="css: {'fa-check': $root.filteredCollections()[$index()].selected()}" class="hue-checkbox fa"></span>
              </td>
              <td><a data-bind="text: name, click: $root.editCollection" title="${ _('Click to edit') }" class="pointer"></a></td>
              <td><span data-bind="text: description"></span></td>
              <td><span data-bind="text: owner"></span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script id="importableTemplate" type="text/html">
  <tr>
    <td width="24">
      <div data-bind="click: handleSelect, css: { 'hue-checkbox': true, 'fa': true, 'fa-check': selected}"></div>
    </td>
    <td data-bind="text: name"></td>
  </tr>
</script>

<div id="deleteModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Confirm Delete')}</h2>
  </div>
  <div class="modal-body">
    <p>${_('Are you sure you want to delete the selected dashboards?')}</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${ _('Cancel') }</a>
    <a id="deleteModalBtn" class="btn btn-danger disable-feedback" data-bind="click: deleteCollections">${ _('Yes') }</a>
  </div>
</div>


</div>


${ commonshare() | n,unicode }
${ commonimportexport(request) | n,unicode }


<script src="${ static('dashboard/js/collections.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/share2.vm.js') }"></script>


<script>
  var appProperties = {
    labels: [],
    %if is_mobile:
    listCollectionsUrl: "${ url("dashboard:admin_collections") }?format=json&is_mobile=true",
    %else:
    listCollectionsUrl: "${ url("dashboard:admin_collections") }?format=json",
    %endif
    deleteUrl: "${ url("dashboard:admin_collection_delete") }",
    copyUrl: "${ url("dashboard:admin_collection_copy") }",
    indexerUrl: "/indexer/#link/"
  }

  var viewModel = new SearchCollectionsModel(appProperties);
  ko.applyBindings(viewModel, $("#collectionsComponents")[0]);

  if (!shareViewModel) {
    shareViewModel = initSharing("#documentShareModal");
    shareViewModel.setDocUuid('');
  }

  $(document).ready(function () {
    viewModel.updateCollections();

    var orderedCores;

    (function serializeList() {
      orderedCores = [];
      $("#collections li").each(function () {
        orderedCores.push($(this).data("collection"));
      });
    }());

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
      $(document).trigger("info", "${ _("Dashboard(s) deleted successfully.") }");
    });

    $(document).on("collectionCopied", function () {
      $(document).trigger("info", "${ _("Dashboard(s) copied successfully.") }");
    });

    $(document).on("confirmDelete", function () {
      $("#deleteModal").modal('show');
    });

    self.exportDocuments = function() {
      $('#export-documents').find('input[name=\'documents\']').val(ko.mapping.toJSON($.map(viewModel.selectedCollections(), function(doc) { return doc.id(); })));
      $('#export-documents').find('form').submit();
    };

    prepareShareModal = function() {
      shareViewModel.setDocUuid(viewModel.selectedCollections()[0].uuid());
      openShareModal();
    };
  });
</script>

</%def>

