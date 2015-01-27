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
  from desktop.views import commonheader, commonfooter, commonshare
  from django.utils.translation import ugettext as _
%>

${ commonheader(_("Notebooks"), "oozie", user) | n,unicode }

<div id="editor">

<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Spark Editor') }</h1>


<div class="actionbar-actions">
                
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    
       &nbsp;&nbsp;&nbsp;&nbsp;
                
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
        <a data-bind="click: showSubmitPopup, css: {'btn': true, 'disabled': ! oneSelected()}">
          <i class="fa fa-play"></i> ${ _('Submit') }
        </a>

        <span style="padding-right:40px"></span>

        <a class="share-link btn" rel="tooltip" data-placement="bottom" data-bind="click: prepareShareModal,
          attr: {'data-original-title': '${ _("Share") } ' + name},
          css: {'disabled': ! oneSelected(), 'btn': true}">
          <i class="fa fa-users"></i> ${ _('Share') }
        </a>

        <a data-bind="click: copy, css: {'btn': true, 'disabled': ! atLeastOneSelected()}">
          <i class="fa fa-files-o"></i> ${ _('Copy') }
        </a>

        <a data-bind="click: function() { $('#deleteWf').modal('show'); }, css: {'btn': true, 'disabled': ! atLeastOneSelected() }">
          <i class="fa fa-times"></i> ${ _('Delete') }
        </a>

      </div>
    
      <a href="${ url('spark:new') }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Create') }</a>
</div>
       
  <table id="notebookTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Description') }</th>
        <th>${ _('Owner') }</th>
        <th>${ _('Last Modified') }</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: { data: jobs }">
      <tr>
        <td data-bind="click: $root.handleSelect" class="center" style="cursor: default" data-row-selector-exclude="true">
          <div data-bind="css: { 'hueCheckbox': true, 'fa': true, 'fa-check': isSelected }" data-row-selector-exclude="true"></div>          
          <a data-bind="attr: { 'href': '${ url('spark:editor') }?notebook=' + id() }" data-row-selector="true"></a>
        </td>
        <td data-bind="text: name"></td>
        <td data-bind="text: description"></td>
        <td data-bind="text: owner"></td>
        <td data-bind="text: last_modified, attr: { 'data-sort-value': last_modified_ts }" data-type="date"></td>
      </tr>
    </tbody>
  </table>

  </div>
</div>


<div class="hueOverlay" data-bind="visible: isLoading">
  <!--[if lte IE 9]>
    <img src="/static/art/spinner-big.gif" />
  <![endif]-->
  <!--[if !IE]> -->
    <i class="fa fa-spinner fa-spin"></i>
  <!-- <![endif]-->
</div>

<div id="submit-wf-modal" class="modal hide"></div>

<div id="deleteWf" class="modal hide fade">
  <form id="deleteWfForm" method="POST" data-bind="submit: delete2">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteWfMessage">${ _('Delete the selected notebook(s)?') }</h3>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
    </div>
  </form>
</div>


</div>


${ commonshare() | n,unicode }


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/share.vm.js"></script>


<script type="text/javascript" charset="utf-8">
  var Editor = function () {
    var self = this;

    self.jobs = ko.mapping.fromJS(${ notebooks_json | n });
    self.selectedJobs = ko.computed(function() {
      return $.grep(self.jobs(), function(job) { return job.isSelected(); });
    });
    self.isLoading = ko.observable(false);

    self.oneSelected = ko.computed(function() {
      return self.selectedJobs().length == 1;
    });
    self.atLeastOneSelected = ko.computed(function() {
      return self.selectedJobs().length >= 1;
    });
    self.allSelected = ko.observable(false);

    self.handleSelect = function(wf) {
      wf.isSelected(! wf.isSelected());
    }

    self.selectAll = function() {
      self.allSelected(! self.allSelected());
      ko.utils.arrayForEach(self.jobs(), function (job) {
        job.isSelected(self.allSelected());
      });
    }

    self.datatable = null;

    self.showSubmitPopup = function () {
      $.get("/oozie/editor/workflow/submit/" + self.selectedJobs()[0].id(), {
      }, function (data) {
        $(document).trigger("showSubmitPopup", data);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.delete2 = function() {
      $.post("${ url('oozie:delete_editor_workflow') }", {
        "selection": ko.mapping.toJSON(self.selectedJobs)
      }, function() {
        window.location.reload();
        $('#deleteWf').modal('hide');
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.copy = function() {
      $.post("${ url('oozie:copy_workflow') }", {
        "selection": ko.mapping.toJSON(self.selectedJobs)
      }, function(data) {
        window.location.reload();
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.prepareShareModal = function() {
     shareViewModel.setDocId(self.selectedJobs()[0].doc1_id());
      openShareModal();
    };
  }

  var viewModel;
  var shareViewModel;

  $(document).ready(function () {
    viewModel = new Editor();
    ko.applyBindings(viewModel, $("#editor")[0]);

    shareViewModel = initSharing("#documentShareModal");
    shareViewModel.setDocId(-1);

    $(document).on("showSubmitPopup", function(event, data){
      $('#submit-wf-modal').html(data);
      $('#submit-wf-modal').modal('show');
    });

    var oTable = $("#notebookTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "aoColumns":[
        { "bSortable":false },
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" }
      ],
      "aaSorting":[
        [4, 'desc'],
        [1, 'asc' ]
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords":"${_('No matching records')}",
        "oPaginate":{
          "sFirst":"${_('First')}",
          "sLast":"${_('Last')}",
          "sNext":"${_('Next')}",
          "sPrevious":"${_('Previous')}"
        },
        "bDestroy": true
      },
      "fnDrawCallback":function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    viewModel.datatable = oTable;

    $("#filterInput").keydown(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function () {
      oTable.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>


${commonfooter(messages) | n,unicode}
