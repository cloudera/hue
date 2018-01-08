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
    import time
    from django.template.defaultfilters import timesince
    from django.utils.encoding import force_unicode
    from django.utils.translation import ugettext as _

    from desktop.views import commonheader, commonfooter
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Saved Queries'), app_name, user, request) | n,unicode }

${ layout.menubar(section='saved queries') }

<div class="container-fluid">
  <div class="card card-small">
    % if app_name == 'spark':
      <h1 class="card-heading simple">${_('App Configurations')}</h1>
    % else:
      <h1 class="card-heading simple">${_('Saved Queries')}</h1>
    % endif

    <%
      noun = "query"
      pluralnoun = "queries"
      if app_name == 'spark':
        noun = "app"
        pluralnoun = "apps"
    %>
    <%actionbar:render>
      <%def name="search()">
        <form id="searchQueryForm" action="${ url(app_name + ':list_designs') }" method="GET" class="inline">
          <input id="filterInput" type="text" name="text" class="input-xlarge search-query" value="${ filter_params.get(prefix + 'text', '') }" placeholder="${_('Search for %s') % noun }" />
        </form>
      </%def>

      <%def name="actions()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <button id="editBtn" class="btn toolbarBtn" title="${_('Edit the selected %s' % noun)}" disabled="disabled"><i class="fa fa-edit"></i> ${_('Edit')}</button>
          <button id="cloneBtn" class="btn toolbarBtn" title="${_('Copy the selected %s' % noun)}" disabled="disabled"><i class="fa fa-files-o"></i> ${_('Copy')}</button>
          <button id="historyBtn" class="btn toolbarBtn" title="${_('View the usage history of the selected %s' % noun)}" disabled="disabled"><i class="fa fa-tasks"></i> ${_('Usage history')}</button>

          <div id="delete-dropdown" class="btn-group" style="vertical-align: middle">
            <button id="trashQueryBtn" class="btn toolbarBtn" disabled="disabled"><i class="fa fa-times"></i> ${_('Move to trash')}</button>
            <button id="trashQueryCaretBtn" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown" disabled="disabled">
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu">
              <li><a href="#" id="deleteQueryBtn" title="${_('Delete forever')}"><i class="fa fa-bolt"></i> ${_('Delete forever')}</a></li>
            </ul>
          </div>
        </div>
      </%def>

      <%def name="creation()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <a class="btn" href="${ url(app_name + ':execute_query') }" title="${_('Create new %s' % noun)}"><i class="fa fa-plus-circle"></i> ${_('New %s' % noun)}</a>
          <a class="btn" href="${ url(app_name + ':list_trashed_designs') }" title="${_('Go to the trash')}"><i class="fa fa-trash-o"></i> ${_('View trash')}</a>
        </div>
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hueCheckbox selectAll fa" data-selectables="savedCheck"></div></th>
        <th>${_('Name')}</th>
        <th>${_('Description')}</th>
        <th>${_('Owner')}</th>
        <th>${_('Last Modified')}</th>
      </tr>
    </thead>
    <tbody>
      % if page:
        % for design in page.object_list:
          <%
            may_edit = design.doc.get().can_write(user)
          %>
        <tr>
          <td data-row-selector-exclude="true">
            <div class="hueCheckbox savedCheck fa"
                data-edit-url="${ url(app_name + ':execute_design', design_id=design.id) }"
                data-history-url="${ url(app_name + ':list_query_history') }?q-design_id=${design.id}"
              % if may_edit:
                data-delete-name="${ design.id }"
              % endif
              data-clone-url="${ url(app_name + ':clone_design', design_id=design.id) }" data-row-selector-exclude="true"></div>
          </td>
          <td>
            <a href="${ url(app_name + ':execute_design', design_id=design.id) }" data-row-selector="true">${ force_unicode(design.name) }</a>
          </td>
          <td>
          % if design.desc:
            ${ force_unicode(design.desc) }
          % endif
          </td>
          <td>${ design.owner.username }</td>
          <td data-sort-value="${time.mktime(design.mtime.timetuple())}"></td>
        </tr>
        % endfor
      % endif
    </tbody>
  </table>
    <div class="card-body">
      <p>
        ${ comps.pagination(page) }
      </p>
    </div>
  </div>
</div>

<div id="deleteQuery" class="modal hide fade">
  <form id="deleteQueryForm" action="${ url(app_name + ':delete_design') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <input type="hidden" name="skipTrash" id="skipTrash" value="false"/>
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="deleteQueryMessage" class="modal-title">${ _('Confirm action') }</h2>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="designs_selection" data-bind="options: availableSavedQueries, selectedOptions: chosenSavedQueries" multiple="true"></select>
    </div>
  </form>
</div>

<script type="text/javascript">
  $(document).ready(function () {
    var viewModel = {
        availableSavedQueries : ko.observableArray(${ designs_json | n }),
        chosenSavedQueries : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    $("[data-sort-value]").each(function(){
      $(this).text(moment($(this).attr("data-sort-value")*1000).format("L LTS"));
    });

    var savedQueries = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "aaSorting":[
        [4, 'desc']
      ],
      "aoColumns":[
        {"bSortable":false, "sWidth":"1%" },
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" }
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sZeroRecords":"${_('No matching records')}",
      },
      "bStateSave": false
    });

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

      var selector = $(".hueCheckbox[checked='checked']:not(.selectAll)");
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

      var can_delete = $(".hueCheckbox[checked='checked'][data-delete-name]");
      if (can_delete.length > 0 && can_delete.length == selector.length) {
        $("#trashQueryBtn").removeAttr("disabled");
        $("#trashQueryCaretBtn").removeAttr("disabled");
      }
    }

    function deleteQueries() {
      viewModel.chosenSavedQueries.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenSavedQueries.push($(this).data("delete-name"));
      });

      $("#deleteQuery").modal("show");
    }

    $("#trashQueryBtn").click(function () {
      $("#skipTrash").val(false);
      $("#deleteQueryMessage").text("${ _('Move the selected %s to the trash?' % pluralnoun) }");
      deleteQueries();
    });

    $("#deleteQueryBtn").click(function () {
      $("#skipTrash").val(true);
      $("#deleteQueryMessage").text("${ _('Delete the selected %s?' % pluralnoun) }");
      deleteQueries();
    });

    $("a[data-row-selector='true']").jHueRowSelector();

    var _searchInputValue = $("#filterInput").val();

    $("#filterInput").jHueDelayedInput(function(){
      if ($("#filterInput").val() != _searchInputValue){
        $("#searchQueryForm").submit();
      }
    });

    $("#filterInput").focus();
    $("#filterInput").val(_searchInputValue); // set caret at the end of the field
  });
</script>

${ commonfooter(request, messages) | n,unicode }
