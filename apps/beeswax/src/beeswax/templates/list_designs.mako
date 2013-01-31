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
    from desktop.views import commonheader, commonfooter
    from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Saved Queries'), app_name, user, '100px') | n,unicode }

${layout.menubar(section='saved queries')}

<div class="container-fluid">
  <h1>${_('Saved Queries')}</h1>

  <%actionbar:render>
    <%def name="actions()">
      <button id="editBtn" class="btn toolbarBtn" title="${_('Edit the selected query')}" disabled="disabled"><i class="icon-edit"></i> ${_('Edit')}</button>
      <button id="cloneBtn" class="btn toolbarBtn" title="${_('Clone the selected query')}" disabled="disabled"><i class="icon-retweet"></i> ${_('Clone')}</button>
      <button id="historyBtn" class="btn toolbarBtn" title="${_('View the usage history of the selected query')}" disabled="disabled"><i class="icon-tasks"></i> ${_('Usage history')}</button>
      <button id="deleteBtn" class="btn toolbarBtn" title="${_('Delete the selected queries')}" disabled="disabled"><i class="icon-trash"></i>  ${_('Delete')}</button>
    </%def>

    <%def name="creation()">
      <a class="btn" href="${ url(app_name + ':execute_query') }"><i class="icon-plus-sign"></i> ${_('Create New Query')}</a>
    </%def>
  </%actionbar:render>

  <table class="table table-striped table-condensed datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hueCheckbox selectAll" data-selectables="savedCheck"></div></th>
        <th>${_('Name')}</th>
        <th>${_('Description')}</th>
        <th>${_('Owner')}</th>
        <th>${_('Type')}</th>
        <th>${_('Last Modified')}</th>
      </tr>
    </thead>
    <tbody>
      <%!
        from beeswax import models
      %>
      % for design in page.object_list:
        <%
          may_edit = user == design.owner
        %>
      <tr>
        <td data-row-selector-exclude="true">
          <div class="hueCheckbox savedCheck"
            % if may_edit:
              data-edit-url="${ url(app_name + ':execute_query', design_id=design.id) }"
              data-delete-name="${ design.id }"
              data-history-url="${ url(app_name + ':list_query_history') }?design_id=${design.id}"
            % endif
            data-clone-url="${ url(app_name + ':clone_design', design_id=design.id) }" data-row-selector-exclude="true"></div>
        </td>
        <td>
        % if may_edit:
          <a href="${ url(app_name + ':execute_query', design_id=design.id) }" data-row-selector="true">${design.name}</a>
        % else:
          ${design.name}
        % endif
        </td>
        <td>
        % if design.desc:
          ${design.desc}
        % endif
        </td>
        <td>${design.owner.username}</td>
        <td>
          ${_('Query')}
        </td>
        <td data-sort-value="${time.mktime(design.mtime.timetuple())}">${ timesince(design.mtime) } ${_('ago')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
  ${comps.pagination(page)}
</div>

<div id="deleteQuery" class="modal hide fade">
  <form id="deleteQueryForm" action="${ url(app_name + ':delete_design') }" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteQueryMessage">${_('Confirm action')}</h3>
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

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableSavedQueries : ko.observableArray(${ designs_json | n }),
        chosenSavedQueries : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    var savedQueries = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "aaSorting":[
        [1, 'asc']
      ],
      "aoColumns":[
        {"bSortable":false, "sWidth":"1%" },
        null,
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" }
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sZeroRecords":"${_('No matching records')}",
      }
    });

    $("#filterInput").keyup(function () {
      savedQueries.fnFilter($(this).val());
    });

    $(".selectAll").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("icon-ok");
        $("." + $(this).data("selectables")).removeClass("icon-ok").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("icon-ok");
        $("." + $(this).data("selectables")).addClass("icon-ok").attr("checked", "checked");
      }
      toggleActions();
    });

    $(".savedCheck").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("icon-ok").removeAttr("checked");
      }
      else {
        $(this).addClass("icon-ok").attr("checked", "checked");
      }
      $(".selectAll").removeAttr("checked").removeClass("icon-ok");
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
        $("#deleteBtn").removeAttr("disabled");
      }
    }

    $("#deleteBtn").click(function () {
      $.getJSON("${ url(app_name + ':delete_design') }", function(data) {
        $("#deleteQueryMessage").text(data.title);
      });
      viewModel.chosenSavedQueries.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenSavedQueries.push($(this).data("delete-name"));
      });
      $("#deleteQuery").modal("show");
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
