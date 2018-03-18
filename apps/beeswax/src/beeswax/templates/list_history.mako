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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
from beeswax import models
from beeswax.views import collapse_whitespace
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />

${ commonheader(_('History'), app_name, user, request) | n,unicode }
${ layout.menubar(section='history') }

<%def name="show_saved_query(design, history)">
  % if design:
    % if request.user == design.owner:
      <a href="${ url(app_name + ':execute_design', design_id=design.id) }">
    % endif
    % if design.is_auto:
      [ ${_('Unsaved')} ]
    % else:
      ${design.name}
    % endif
    % if request.user == design.owner:
    </a>
    % else:
    <a href="${ url(app_name + ':clone_design', design_id=design.id) }" title="${_('Copy this query.')}">${_('Copy')}</a>
    % endif
  % else:
    [ ${_('Auto generated action')} ]
  % endif
</%def>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span2">
            <div class="sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    % if share_queries:
                        % if filter_params.get(prefix + 'user') == ':all':
                          <%
                            my_querydict = filter_params.copy()
                            my_querydict[prefix + 'user'] = request.user.username
                            if filter:
                              my_querydict[prefix + 'search'] = filter
                          %>
                        <li><a href="?${my_querydict.urlencode()}">${_('Show my queries')}</a></li>
                        % else:
                          <%
                            my_querydict = filter_params.copy()
                            my_querydict[prefix + 'user'] = ':all'
                            if filter:
                              my_querydict[prefix + 'search'] = filter
                          %>
                          <li><a href="?${my_querydict.urlencode()}">${_("Show everyone's queries")}</a></li>
                        % endif
                    % endif

                     % if filter_params.get(prefix + 'auto_query', 'on') == 'off':
                      <%
                        my_querydict = filter_params.copy()
                        my_querydict[prefix + 'auto_query'] = 'on'
                        if filter:
                          my_querydict[prefix + 'search'] = filter
                      %>
                      <li><a href="?${my_querydict.urlencode()}">${_('Show auto queries')}</a></li>
                    % else:
                      <%
                        my_querydict = filter_params.copy()
                        my_querydict[prefix + 'auto_query'] = 'off'
                        if filter:
                          my_querydict[prefix + 'search'] = filter
                      %>
                      <li><a href="?${my_querydict.urlencode()}">${_('Show only saved queries')}</a></li>
                    % endif
                </ul>
            </div>
        </div>
        <div class="span10">
          <div class="card card-small">
            <h1 class="card-heading simple">${_('History')}</h1>

            <%actionbar:render>
              <%def name="search()">
                <input id="filter" type="text" class="input-xxlarge search-query" placeholder="${_('Search for name, query, etc.')}" data-bind="textInput: searchQuery">
              </%def>
            </%actionbar:render>

            <div class="card-body">
              <p>

            <table class="table table-condensed datatables" style="padding-left: 0;">
            <thead>
              <tr>
                <th width="15%">${_('Time')}</th>
                <th width="15%">${_('Name')}</th>
                <th width="40%">${_('Query')}</th>
                <th width="10%">${_('User')}</th>
                <th width="5%">${_('State')}</th>
                <th width="5%">${_('Result')}</th>
              </tr>
            </thead>
            <tbody>
            % if page:
              % for query in page.object_list:
                <tr class="histRow">
                  <td data-sort-value="${time.mktime(query.submission_date.timetuple())}"></td>
                  <td>${show_saved_query(query.design, query)}</td>
                  <td>
                    % if len(query.query) > 100:
                      <code>${collapse_whitespace(query.query[:100])}...</code>
                    % else:
                      <code>${collapse_whitespace(query.query)}</code>
                    % endif
                  </td>
                  <td>${query.owner}</td>
                  <td>${query.last_state}</td>
                  <td>
                    % if query.last_state not in (models.QueryHistory.STATE.expired.value, models.QueryHistory.STATE.failed.value):
                      <a href="${ url(app_name + ':watch_query_history', query_history_id=query.id) }" data-row-selector="true">${_('Results')}</a>
                    % else:
                      ~
                    % endif
                  </td>
                </tr>
              % endfor
            % endif
            </tbody>
          </table>

                ${ comps.pagination(page) }
              </p>
            </div>
          </div>
        </div>
    </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {

    function HistoryViewModel() {
      this.searchQuery = ko.observable("${ filter }").extend({ throttle: 500 });
      this.searchQuery.subscribe(function (val) {
        $(".datatables").css("opacity", 0.5)
        $(".pagination").css("opacity", 0.5)
        location.href = '?${ filter_params.get(prefix + 'user') and (prefix + 'user=' + filter_params.get(prefix + 'user') + '&') or '' }${ prefix }search=' + val;
      });
    }

    ko.applyBindings(new HistoryViewModel());

    $("[data-sort-value]").each(function(){
      $(this).text(moment($(this).attr("data-sort-value")*1000).format("L LTS"));
    });

    $(".datatables").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "aoColumns": [
        { "sSortDataType": "dom-sort-value", "sType": "numeric" },
        null,
        null,
        null,
        null,
        { "bSortable": false }
      ],
      "aaSorting": [
        [0, 'desc']
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sInfo": "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty": "${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered": "${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords": "${_('No matching records')}",
        "oPaginate": {
          "sFirst": "${_('First')}",
          "sLast": "${_('Last')}",
          "sNext": "${_('Next')}",
          "sPrevious": "${_('Previous')}"
        }
      },
      "bStateSave": true
    });

    $(".search-query").focus().val($(".search-query").val());

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${ commonfooter(request, messages) | n,unicode }
