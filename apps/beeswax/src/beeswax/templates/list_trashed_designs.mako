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
  <div class="card">
    <h1 class="card-heading simple">${_('Trashed Queries')}</h1>

    <%actionbar:render>
      <%def name="search()">
        <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for query')}">
      </%def>

      <%def name="actions()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <button id="deleteQueryBtn" class="btn toolbarBtn" title="${_('Delete forever')}" disabled="disabled">
            <i class="icon-bolt"></i> ${_('Delete forever')}
          </button>
          <button id="restoreQueryBtn" class="btn toolbarBtn" title="${_('Restore from trash')}" disabled="disabled">
            <i class="icon-cloud-upload"></i> ${_('Restore')}
          </button>
        </div>
      </%def>

      <%def name="creation()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <button id="viewQueriesBtn" class="btn" title="${_('View queries')}">
            <i class="icon-home"></i> ${_('View queries')}
          </button>
          <button id="emptyTrashBtn" class="btn" title="${_('Empty trash')}" data-bind="enabled: availableSavedQueries().length > 0">
            <i class="icon-fire"></i> ${_('Empty trash')}
          </button>
        </div>
      </%def>
    </%actionbar:render>

    <table class="table table-condensed datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hueCheckbox selectAll" data-selectables="savedCheck"></div></th>
        <th>${_('Name')}</th>
        <th>${_('Description')}</th>
        <th>${_('Owner')}</th>
        <th>${_('Last Modified')}</th>
      </tr>
    </thead>
    <tbody>
      % for design in page.object_list:
        <%
          may_edit = user == design.owner
        %>
      <tr>
        <td data-row-selector-exclude="true">
          <div class="hueCheckbox savedCheck"
            % if may_edit:
              data-delete-id="${ design.id }"
            % endif
            data-row-selector-exclude="true">
         </div>
        </td>
        <td>
         ${ design.name }
        </td>
        <td>
        % if design.desc:
          ${ design.desc }
        % endif
        </td>
        <td>${ design.owner.username }</td>
        <td data-sort-value="${time.mktime(design.mtime.timetuple())}">${ timesince(design.mtime) } ${_('ago')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
    <div class="card-body">
      <p>
        ${comps.pagination(page)}
      </p>
    </div>
  </div>
</div>

<div id="deleteQuery" class="modal hide fade">
  <form id="deleteQueryForm" action="${ url(app_name + ':delete_design') }" method="POST">
    <input type="hidden" name="skipTrash" id="skipTrash" value="true"/>
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

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

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
      "bStateSave": true
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

      if (selector.length >= 1) {
        $(".toolbarBtn").removeAttr("disabled");
      }
    }

    function restoreQuery() {
      viewModel.chosenSavedQueries.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenSavedQueries.push($(this).data("delete-id"));
      });

      $("#deleteQuery").modal("show");
    }

    $("#restoreQueryBtn").click(function () {
      $("#deleteQueryForm").attr("action", "${ url(app_name + ':restore_design') }");
      $("#deleteQueryMessage").text("${ _('Restore the selected queries?') }");
      restoreQuery();
    });

    $("#deleteQueryBtn").click(function () {
      $("#deleteQueryForm").attr("action", "${ url(app_name + ':delete_design') }");
      $("#deleteQueryMessage").text("${ _('Delete the selected queries?') }");
      restoreQuery();
    });

    $("#emptyTrashBtn").click(function () {
      $("#deleteQueryForm").attr("action", "${ url(app_name + ':delete_design') }");
      $("#deleteQueryMessage").text("${ _('Empty the trash?') }");

      viewModel.chosenSavedQueries.removeAll();
      $.each(viewModel.availableSavedQueries(), function(index, query) {
        viewModel.chosenSavedQueries.push(query);
      });

      $("#deleteQuery").modal("show");
    });

    $("#viewQueriesBtn").click(function(){
      history.back();
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(messages) | n,unicode }
