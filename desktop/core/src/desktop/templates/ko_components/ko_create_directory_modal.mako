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
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%def name="createDirectory()">
  <script type="text/html" id="create-directory-template">
      <!-- ko with: activeEntry -->
      <form class="form-horizontal">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title">${_('Create Directory')}</h2>
        </div>
        <div class="modal-body ">
          <input id="newDirectoryName" class="input large-as-modal" type="text" placeholder="${ _('Directory name') }" />
        </div>
        <div class="modal-footer">
          <input type="button" class="btn" data-dismiss="modal" data-bind="click: function () { $('#newDirectoryName').val(null) }" value="${ _('Cancel') }">
          <input type="submit" class="btn btn-primary disable-feedback" value="${ _('Create') }" data-bind="click: function () { if ($('#newDirectoryName').val()) { $data.createDirectory($('#newDirectoryName').val()); $('#createDirectoryModal').modal('hide'); } }"/>
        </div>
      </form>
      <!-- /ko -->
</script>

  <script type="text/javascript">
    (function () {
      ko.components.register('create-directory', {
        template: {element: 'create-directory-template'}
      });

      huePubSub.subscribe('show.create.directory.modal', function (docViewModel) {
        if ($('#createDirectoryModal').length > 0) {
          ko.cleanNode($('#createDirectoryModal')[0]);
          $('#createDirectoryModal').remove();
        }
        var $createDirectoryModal = $('<div id="createDirectoryModal" data-bind="component: { name: \'create-directory\', params: $data }" data-keyboard="true" class="modal hide fade" tabindex="-1"/>');
        $(HUE_CONTAINER).append($createDirectoryModal);
        ko.applyBindings(docViewModel, $createDirectoryModal[0]);
      });

    })();
  </script>
</%def>
