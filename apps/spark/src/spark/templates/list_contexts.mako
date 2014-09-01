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
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="common" file="common.mako" />

${ commonheader(_('Context'), app_name, user) | n,unicode }

${ common.navbar('contexts') }

<div class="container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Contexts')}</h1>

    <%actionbar:render>
      <%def name="search()">
          <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name')}">
      </%def>
      <%def name="actions()">
        <button type="button" id="deleteContextBtn" title="${_('Delete forever')}" class="btn" disabled="disabled">
          <i class="fa fa-bolt"></i> ${ _('Delete selected') }
        </button>
      </%def>
      <%def name="creation()">
         <button type="button" class="btn createContextModalBtn"><i class="fa fa-plus-circle"></i> ${ _('Create context') }</button>
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables" id="contextTable">
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
    <tfoot>
      <tr class="hide">
        <td colspan="2" style="text-align: center">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #DDD"></i><!--<![endif]-->
          <!--[if IE]><img src="/static/art/spinner.gif"/><![endif]-->
        </td>
      </tr>
    </tfoot>
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
    ${ csrf_token(request) | n,unicode }
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
      <select name="contexts_selection" data-bind="options: availableSavedContexts, selectedOptions: chosenSavedContexts" multiple="true"></select>
    </div>
  </form>
</div>


${ common.createContextModal() }


<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>

<script src="/spark/static/js/spark.vm.js"></script>

<script type="text/javascript" charset="utf-8">

  $(document).ready(function() {
    var viewModel = {
        availableSavedContexts : ko.observableArray(${ contexts_json | n,unicode }),
        chosenSavedContexts : ko.observableArray([])
    };

    ko.applyBindings(viewModel, $('#deleteContext')[0]);

    var sViewModel = new sparkViewModel();
    ko.applyBindings(sViewModel, $('#createContextModal')[0]);

    var savedContexts;
    function createDataTable () {
      savedContexts = $(".datatables").dataTable({
        "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
        "bPaginate":false,
        "bLengthChange":false,
        "bInfo":false,
        "aaSorting":[
          [1, "desc"]
        ],
        "aoColumns":[
          {"bSortable": false},
          null
        ],
        "oLanguage":{
          "sEmptyTable":"${_('No data available')}",
          "sZeroRecords":"${_('No matching records')}",
        },
        "bDestroy": true
      });
    }

    createDataTable();

    $("#filterInput").on("keyup", function () {
      savedContexts.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();

    $(".selectAll").on("click", function () {
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

    $(document).on("click", ".savedCheck", function () {
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
        $("#deleteContextBtn").removeAttr("disabled");
      }
    }

    function deleteContexts() {
      viewModel.chosenSavedContexts.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenSavedContexts.push($(this).data("delete-name"));
      });

      $("#deleteContext").modal("show");
    }

    $("#deleteContextBtn").on("click", function () {
      $("#skipTrash").val(true);
      $("#deleteContextMessage").text("${ _('Delete the selected contexts?') }");
      deleteContexts();
    });

    $(".createContextModalBtn").on("click", function(){
      $("#createContextModal").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();

    $(document).on("created.context", function() {
      $(".datatables tfoot tr").removeClass("hide");
      $(".datatables tbody").empty();
      savedContexts.fnClearTable();
      $.getJSON("${ url('spark:list_contexts')}", function(data){
        viewModel.availableSavedContexts(data.contexts);
        var _h  = "";
        $(data.contexts).each(function(cnt, ctx){
          _h += getContextRow(ctx);
        });
        $(".datatables").find("tbody").html(_h);
        createDataTable();
      });
      $("#createContextModal").modal("hide");
      $("#createContextBtn").button("reset");
      $("input[data-default]").each(function(){
        $(this).val($(this).data("default"));
      });
      $(".datatables tfoot tr").addClass("hide");
    });

    function getContextRow(context) {
      return '<tr>' +
        '<td data-row-selector-exclude="true">' +
        '<div class="hueCheckbox savedCheck fa" data-delete-name="'+context+'" data-row-selector-exclude="true"></div>' +
        '</td>' +
        '<td data-name="'+context+'">'+context+'</td>' +
      '</tr>';
    }

  });
</script>

${ commonfooter(messages) | n,unicode }
