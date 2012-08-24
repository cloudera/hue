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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
<%!  from beeswax.views import collapse_whitespace %>
${commonheader(_('My Queries'), "beeswax", user, "100px")}
${layout.menubar(section='my queries')}
<style>
    .tab-content {
        overflow:visible!important;
    }
</style>
<div class="container-fluid">
    <h1>${_('My Queries')}</h1>

    <div class="well hueWell">
        <div class="btn-group pull-right">
            <a class="btn" href="/beeswax/">${_('Create New Query')}</a>
        </div>

        <form class="form-search">
            ${_('Filter:')} <input type="text" placeholder="${_('Search for name, description, etc...')}" class="input-xlarge search-query" id="filterInput">
        </form>
    </div>

    <ul class="nav nav-tabs">
        <li class="active"><a href="#recentSavedQueries" data-toggle="tab">${_('Recent Saved Queries')} &nbsp;<span id="recentSavedQueriesFilterCnt" class="badge badge-info hide"></span></a></li>
        <li><a href="#recentRunQueries" data-toggle="tab">${_('Recent Run Queries')}  &nbsp;<span id="recentRunQueriesFilterCnt" class="badge badge-info hide"></span></a></li>
    </ul>

    <div class="tab-content">
            <div class="active tab-pane" id="recentSavedQueries">

                 <table id="recentSavedQueriesTable" class="table table-striped table-condensed datatables">
                      <thead>
                        <tr>
                          <th>${_('Name')}</th>
                          <th>${_('Desc')}</th>
                          <th>${_('Type')}</th>
                          <th>${_('Last Modified')}</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                      <%!
                        from beeswax import models
                      %>
                      % for design in q_page.object_list:
                        <tr>
                          <td>
                            <a href="${ url('beeswax.views.execute_query', design_id=design.id) }" data-row-selector="true">${design.name}</a>
                          </td>
                          <td>
                            % if design.desc:
                             <p>${design.desc}</p>
                            % endif
                          </td>
                          <td>
                            ${_('Query')}
                          </td>
                          <td data-sort-value="${time.mktime(design.mtime.timetuple())}">${ timesince(design.mtime) } ${_('ago')}</td>
                          <td>
                            <div class="btn-group">
                                <a href="#" data-toggle="dropdown" class="btn dropdown-toggle">
                                  ${_('Options')}
                                  <span class="caret"></span>
                                </a>
                                <ul class="dropdown-menu">
                                  <li><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" title="${_('Edit this query.')}" class="contextItem">${_('Edit')}</a></li>
                                  <li><a href="javascript:void(0)" data-confirmation-url="${ url('beeswax.views.delete_design', design_id=design.id) }" title="${_('Delete this query.')}" class="contextItem confirmationModal">${_('Delete')}</a></li>
                                  <li><a href="${ url('beeswax.views.list_query_history') }?design_id=${design.id}" title="${_('View the usage history of this query.')}" class="contextItem">${_('Usage History')}</a></li>
                                  <li><a href="${ url('beeswax.views.clone_design', design_id=design.id) }" title="${_('Copy this query.')}" class="contextItem">${_('Clone')}</a></li>
                                </ul>
                            </div>
                          </td>
                        </tr>
                      % endfor
                      </tbody>
                    </table>
                    % if q_page.number != q_page.num_pages():
                      <a href="${ url('beeswax.views.list_designs') }?user=${request.user.username|u}" >${_('View all my queries')} &raquo;</a>
                    % endif
            </div>

            <div class="tab-pane" id="recentRunQueries">
                <table id="recentRunQueriesTable" class="table table-striped table-condensed datatables">
                  <thead>
                    <tr>
                      <th>${_('Time')}</th>
                      <th>${_('Name')}</th>
                      <th>${_('Query')}</th>
                      <th>${_('State')}</th>
                      <th>${_('Result')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  <%!
                    from beeswax import models, views
                  %>
                  % for query in h_page.object_list:
                    <%
                    qcontext = ""
                    try:
                      design = query.design
                      qcontext = views.make_query_context('design', design.id)
                    except:
                      pass
                    %>
                    <tr>
                      <td data-sort-value="${time.mktime(query.submission_date.timetuple())}">${query.submission_date.strftime("%x %X")}</td>
                      <td><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" data-row-selector="true">${design.name}</a></td>
                      <td>
                        <p>
                          % if len(query.query) > 100:
                            <code>${collapse_whitespace(query.query[:100])}...</code>
                          % else:
                            <code>${collapse_whitespace(query.query)}</code>
                          % endif
                        </p>
                      </td>
                      <td>${models.QueryHistory.STATE[query.last_state]}</td>
                      <td>
                        % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
                          <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}">${_('View')}</a>
                        % else:
                          ~
                        % endif
                      </td>
                    </tr>
                  % endfor
                  </tbody>
                </table>
                % if h_page.number != h_page.num_pages():
                  <a href="${ url('beeswax.views.list_query_history') }">${_('View my entire query history')} &raquo;</a>
                % endif
            </div>
    </div>
</div>

<div id="deleteQuery" class="modal hide fade">
    <form id="deleteQueryForm" action="" method="POST">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3 id="deleteQueryMessage">${_('Confirm action')}</h3>
    </div>
    <div class="modal-footer">
        <input type="submit" class="btn primary" value="${_('Yes')}"/>
        <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
    </div>
    </form>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        var recentSavedQueries = $("#recentSavedQueriesTable").dataTable({
            "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "aoColumns": [
                null,
                null,
                null,
                { "sSortDataType": "dom-sort-value", "sType": "numeric" },
                { "bSortable": false }
            ]
        });

        var recentRunQueries = $("#recentRunQueriesTable").dataTable({
            "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "aoColumns": [
                { "sSortDataType": "dom-sort-value", "sType": "numeric" },
                null,
                null,
                null,
                { "bSortable": false }
            ]
        });


        $("#filterInput").keyup(function() {
            recentSavedQueries.fnFilter($(this).val());
            recentRunQueries.fnFilter($(this).val());
            if ($.trim($(this).val()) != ""){
                var recentSavedQueriesCnt = $("#recentSavedQueriesTable tbody tr").length;
                var isRecentSavedQueriesEmpty = ($("#recentSavedQueries tbody tr td.dataTables_empty").length == 1)
                if (recentSavedQueriesCnt > 0 && !isRecentSavedQueriesEmpty){
                    $("#recentSavedQueriesFilterCnt").text(recentSavedQueriesCnt).show();
                }
                else {
                    $("#recentSavedQueriesFilterCnt").hide().text("");
                }

                var recentRunQueriesCnt = $("#recentRunQueriesTable tbody tr").length;
                var isRecentRunQueriesEmpty = ($("#recentRunQueriesTable tbody tr td.dataTables_empty").length == 1)
                if (recentRunQueriesCnt > 0 && !isRecentRunQueriesEmpty){
                    $("#recentRunQueriesFilterCnt").text(recentRunQueriesCnt).show();
                }
                else {
                    $("#recentRunQueriesFilterCnt").hide().text("");
                }
            }
            else {
                $("#recentSavedQueriesFilterCnt").hide().text("");
                $("#recentRunQueriesFilterCnt").hide().text("");
            }
        });

        $(".confirmationModal").live("click", function(){
            $.getJSON($(this).attr("data-confirmation-url"), function(data){
                $("#deleteQueryForm").attr("action", data.url);
                $("#deleteQueryMessage").text(data.title);
            });
            $("#deleteQuery").modal("show");
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>

${commonfooter(messages)}
