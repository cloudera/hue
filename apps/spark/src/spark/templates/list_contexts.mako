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

<%namespace name="common" file="common.mako" />

${ commonheader(_('Context'), app_name, user) | n,unicode }

${ common.navbar('contexts') }

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Contexts')}</h1>

    <a href="#" id="deleteContextBtn" title="${_('Delete forever')}" class="btn"><i class="fa fa-bolt"></i> ${_('Delete')}</a>

    <table class="table table-condensed datatables">
    <thead>
      <th width="1%"><div class="hueCheckbox selectAll fa" data-selectables="savedCheck"></div></th>
      <th>${ _('Name') }</th>
    </thead>
    <tbody>
      % for contextz in contexts:
      <tr>
        <td data-row-selector-exclude="true">
          <div class="hueCheckbox savedCheck fa" data-delete-name="${ contextz  }" data-row-selector-exclude="true"></div>
        </td>
        <td data-name="${ contextz }">${ contextz }</td>
      </tr>
      % endfor

    </tbody>
  </table>
    <div class="card-body">
      <p>
        ## ${ comps.pagination(page) }
      </p>
    </div>
  </div>
</div>

<div id="deleteContext" class="modal hide fade">
  <form id="deleteContextForm" action="${ url('spark:delete_contexts') }" method="POST">
    <input type="hidden" name="skipTrash" id="skipTrash" value="false"/>
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteContextMessage">${_('Confirm action')}</h3>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="contexts_selection" data-bind="options: availableSavedQueries, selectedOptions: chosenSavedQueries" multiple="true"></select>
    </div>
  </form>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableSavedQueries : ko.observableArray(${ contexts_json | n,unicode }),
        chosenSavedQueries : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    var savedQueries = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "aaSorting":[
        [2, 'desc']
      ],
      "aoColumns":[
        null,
        null
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sZeroRecords":"${_('No matching records')}",
      },
      "bStateSave": true
    });

    $("#filterInput").keyup(function () {
      savedQueries.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();

    $(".selectAll").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("fa-check");
        $("." + $(this).data("selectables")).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("fa-check");
        $("." + $(this).data("selectables")).addClass("fa-check").attr("checked", "checked");
      }
      toggleActions();
    });

    $(".savedCheck").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("fa-check").removeAttr("checked");
      }
      else {
        $(this).addClass("fa-check").attr("checked", "checked");
      }
      $(".selectAll").removeAttr("checked").removeClass("fa-check");
      toggleActions();
    });

    function toggleActions() {
      $(".toolbarBtn").attr("disabled", "disabled");

      var selector = $(".hueCheckbox[checked='checked']");
      if (selector.length == 1) {
        if (selector.data("edit-url")) {
          $("#editBtn").removeAttr("disabled").click(function () {
            location.href = selector.data("edit-url");
          });
        }
        if (selector.data("clone-url")) {
          $("#cloneBtn").removeAttr("disabled").click(function () {
            location.href = selector.data("clone-url")
          });
        }
        if (selector.data("history-url")) {
          $("#historyBtn").removeAttr("disabled").click(function () {
            location.href = selector.data("history-url")
          });
        }
      }
      if (selector.length >= 1) {
        $("#trashContextBtn").removeAttr("disabled");
        $("#trashContextCaretBtn").removeAttr("disabled");
      }
    }

    function deleteQueries() {
      viewModel.chosenSavedQueries.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenSavedQueries.push($(this).data("delete-name"));
      });

      $("#deleteContext").modal("show");
    }

    $("#deleteContextBtn").click(function () {
      $("#skipTrash").val(true);
      $("#deleteContextMessage").text("${ _('Delete the selected queries?') }");
      deleteQueries();
    });


    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
