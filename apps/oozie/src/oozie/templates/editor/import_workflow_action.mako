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

<form id="actionForm" action="${ form_url }" method="POST">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_("Select Job Design to Import")}</h3>
  </div>
  <div class="modal-content">
    <div class="container-fluid">
      <table id="jobdesignerActionsTable" class="table datatables">
        <thead>
          <tr>
            <th></th>
            <th>${ _('Name') }</th>
            <th>${ _('Description') }</th>
          </tr>
        </thead>
        <tbody>
          %for action in available_actions:
            <tr class="action-row">
              <td class=".btn-large action-column" data-row-selector-exclude="true" style="background-color: white;">
                <input type="radio" name="action_id" value="${ action.id }" />
              </td>
              <td>
                ${ action.name }
              </td>
              <td>${ action.description }</td>
            </tr>
          %endfor
          % if not available_actions:
            <tr class="action-row">
              <td>${ _('N/A') }</td><td></td><td></td>
            </tr>
          % endif
        </tbody>
      </table>
    </div>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn secondary" data-dismiss="modal">${_('Cancel')}</a>
    <input type="submit" class="btn primary" value="${_('Import')}"/>
  </div>
</form>


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function() {
    $(".action-row").click(function(e){
      var select_btn = $(this).find('input');
      select_btn.prop("checked", true);

      $(".action-row").css("background-color", "");
      $(this).css("background-color", "#ECF4F8");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>
