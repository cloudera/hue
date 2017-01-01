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

<script src="${ static('desktop/ext/js/bootstrap-fileupload.js') }" type="text/javascript" charset="utf-8"></script>
<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-fileupload.css') }">

<div id="export-documents" class="modal hide">
  <form method="POST" action="/desktop/api2/doc/export" style="display: inline">
    ${ csrf_token(request) | n,unicode }
    <input type="hidden" name="documents"/>
  </form>
</div>

<div id="import-documents" class="modal hide fade fileupload-modal">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal" data-clear="fileupload"></a>
    <h3 class="modal-title">${_('Import Hue documents')}</h3>
  </div>
  <div class="modal-body form-inline">
    <div class="pull-right">
      <input type="button" class="btn" data-dismiss="modal" data-clear="fileupload" value="${ _('Cancel') }" />
      <a class="btn btn-danger" data-bind="click: import_document"> ${ _('Import') } </a>
    </div>
    <div class="fileupload fileupload-new" data-provides="fileupload">
      <span class="btn btn-file" style="line-height: 29px">
        <span class="fileupload-new">${ _('Select json file') }</span>
        <span class="fileupload-exists">${ _('Change') }</span>
        <input type="file" accept=".json" id="fileData"/>
      </span>
      &nbsp;&nbsp;<span class="fileupload-preview"></span>
        <a href="#" class="fileupload-exists" data-clear="fileupload"><i class="fa fa-times"></i></a>
    </div>
    ${ csrf_token(request) | n,unicode }
    <input type="hidden" name="redirect" value="${ request.get_full_path() }"/>
  </div>
</div>

<div id="import-document-data" class="modal hide fade">
  <div class="modal-body">
    <div class="center animated" style="display: none;" data-bind="visible: importedDocumentCount() == 0">
      <i class="fa fa-spinner fa-spin fa-2x"></i>
    </div>
    <!-- ko if: importedDocumentCount() > 0 -->
      <h3> ${_('Document Summary')} </h3>
      <ul>
        <li> ${_('Imported: ')} <span data-bind="text: importedDocSummary()['count']"></span></li>
        <li> ${_('Created: ')} <span data-bind="text: importedDocSummary()['created_count']"></span></li>
        <li> ${_('Updated: ')} <span data-bind="text: importedDocSummary()['updated_count']"></span></li>
      </ul>

      ${_('Show Details')}
      <button id="show-details-caret" class="btn toolbarBtn" data-bind="click: $root.toggleShowTable"><span class="caret"></span></button>
      <!-- ko if: $root.showTable() -->
        <table class="table table-striped table-condensed">
          <thead>
            <tr>
              <th>${_('Name')}</th>
              <th>${_('Type')}</th>
              <th>${_('Owner')}</th>
            </tr>
          </thead>
          <tbody data-bind="foreach: importedDocSummary()['documents']">
            <tr>
              <td data-bind="text: $data.name"> </td>
              <td data-bind="text: $data.type"> </td>
              <td data-bind="text: $data.owner"> </td>
            </tr>
          </tbody>
        </table>
      <!-- /ko -->
    <!-- /ko -->
  </div>
  <div class="modal-footer">
    <input id="import-document-data-close" data-dismiss="modal" type="button" class="btn btn-primary" value="${ _('Close') }" data-bind="click: refreshPage"/>
  </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {
    $('#import-documents input[type="file"]').val('');
    $('#import-documents input[type="submit"]').attr('disabled', 'disabled');
    $('#import-documents input[type="file"]').on('change', function () {
      if ($(this).val() !== '') {
        $('#import-documents input[type="submit"]').removeAttr('disabled');
      }
      else {
        $('#import-documents input[type="submit"]').attr('disabled', 'disabled');
      }
    });
  });
</script>

<script type="text/javascript" charset="utf-8">
  var ImportDocument = function () {
    var self = this;
    self.fileData = new FormData();
    self.importedDocSummary = ko.observable();
    self.showTable = ko.observable();

    self.import_document = function() {
      self.importedDocSummary(null);
      self.showTable(false);
      $('#import-documents').modal('hide');
      $('#import-document-data').modal('show');

      self.fileData = new FormData();
      self.fileData.append("documents", $('#fileData')[0].files[0]);
      $.ajax({
        type: "POST",
        url: "/desktop/api2/doc/import",
        data: self.fileData,
        contentType: false,
        processData: false,
        success: function (data) {
          if (data.status == 0) {
            self.importedDocSummary(data);
          } else {
            $(document).trigger('error', data.message);
          }
        },
      });
    };

    self.importedDocumentCount = function() {
      if (self.importedDocSummary()) {
        return self.importedDocSummary()['documents'].length;
      }
      return 0;
    };

    self.toggleShowTable = function() {
      self.showTable(!self.showTable());
    };

    self.refreshPage = function() {
      window.location.reload();
    };

    $('#import-document-data-close').keyup(function(e) {
      if (e.keyCode == 27) {
        self.refreshPage();
      }
    });
  }

  var importDocumentModel;
  $(document).ready(function () {
    importDocumentModel = new ImportDocument();
    ko.applyBindings(importDocumentModel, $("#import-documents")[0]);
    ko.applyBindings(importDocumentModel, $("#import-document-data")[0]);
  });
</script>
