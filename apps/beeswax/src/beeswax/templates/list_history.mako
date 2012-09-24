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
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%!  from beeswax.views import collapse_whitespace %>

${commonheader(_('Query History'), "beeswax", user, "100px")}
${layout.menubar(section='history')}

<%def name="show_saved_query(design, history)">
  % if design:
    % if request.user == design.owner:
      <a href="${ url('beeswax.views.execute_query', design_id=design.id) }">
    % endif
    % if design.is_auto:
      [ ${_('Unsaved')} ]
    % else:
      ${design.name}
    % endif
    % if request.user == design.owner:
    </a>
    % else:
    ## TODO (bc/nutron): Shouldn't be able to edit someone else's design. Let user clone instead.
    <a href="${ url('beeswax.views.clone_design', design_id=design.id) }" title="${_('Copy this query.')}">${_('Clone')}</a>
    % endif
  % else:
    [ ${_('Auto generated action')} ]
  % endif
</%def>

<div class="container-fluid">
    <h1>${_('Query History')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    % if share_queries:
                        % if filter_params.get('user') == ':all':
                          <%
                            my_querydict = filter_params.copy()
                            my_querydict['user'] = request.user.username
                          %>
                        <li><a href="?${my_querydict.urlencode()}">${_('Show my queries')}</a></li>
                        % else:
                          <%
                            my_querydict = filter_params.copy()
                            my_querydict['user'] = ':all'
                          %>
                          <li><a href="?${my_querydict.urlencode()}">${_("Show everyone's queries")}</a></li>
                        % endif
                    % endif

                     % if filter_params.get('auto_query', None):
                      <%
                        my_querydict = filter_params.copy()
                        my_querydict['auto_query'] = ''
                      %>
                      <li><a href="?${my_querydict.urlencode()}">${_('Show user queries')}</a></li>
                    % else:
                      <%
                        my_querydict = filter_params.copy()
                        my_querydict['auto_query'] = 'on'
                      %>
                      <li><a href="?${my_querydict.urlencode()}">${_('Show auto actions')}</a></li>
                    % endif
                </ul>
            </div>
        </div>
        <div class="span9">

        <table class="table table-striped table-condensed datatables">
            <thead>
              <tr>
                <th width="10%">${_('Time')}</th>
                <th width="10%">${_('Query Server')}</th>
                <th width="15%">${_('Name')}</th>
                <th width="45%">${_('Query')}</th>
                <th width="10%">${_('User')}</th>
                <th width="5%">${_('State')}</th>
                <th width="5%">${_('Result')}</th>
              </tr>
            </thead>
            <tbody>
            <%!
              from beeswax import models, views
            %>
            % for query in page.object_list:
              <%
                qcontext = ""
                try:
                  design = query.design
                  qcontext = views.make_query_context('design', design.id)
                except:
                  pass
              %>
              <tr class="histRow">
                <td data-sort-value="${time.mktime(query.submission_date.timetuple())}">${query.submission_date.strftime("%x %X")}</td>
                <td>${query.server_name}</td>
                <td>${show_saved_query(design, query)}</td>
                <td>
                  <p>
                    % if len(query.query) > 100:
                      <code>${collapse_whitespace(query.query[:100])}...</code>
                    % else:
                      <code>${collapse_whitespace(query.query)}</code>
                    % endif
                  </p>
                </td>
                <td>${query.owner}</td>
                <td>${models.QueryHistory.STATE[query.last_state]}</td>
                <td>
                  % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
                    <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}" data-row-selector="true">${_('Results')}</a>
                  % else:
                    ~
                  % endif
                </td>
              </tr>
            % endfor
            </tbody>
          </table>
         ${comps.pagination(page)}
        </div>
    </div>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
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
                null,
                { "bSortable": false }
            ],
            "oLanguage": {
                "sEmptyTable":     "${_('No data available in table')}",
                "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
                "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
                "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
                "sZeroRecords":    "${_('No matching records found')}",
                "oPaginate": {
                    "sFirst":    "${_('First')}",
                    "sLast":     "${_('Last')}",
                    "sNext":     "${_('Next')}",
                    "sPrevious": "${_('Previous')}"
                }
            }
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>
${commonfooter(messages)}
