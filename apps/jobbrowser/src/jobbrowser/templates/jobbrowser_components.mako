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

<%def name="header(title, toolbar=True)">
  <html>
    <head>
      <title>${title}</title>
    </head>
    <body>
      % if toolbar: 
      <div class="toolbar">
        <a href="/jobbrowser/jobs/"><img src="/jobbrowser/static/art/icon_large.png" class="jt_icon"/></a>
      </div>
      % endif
</%def>

<%def name="footer()">
    </body>
  </html>
</%def>


<%def name="task_counters(counters)">
<%
  from jobbrowser.views import format_counter_name
%>
    <table data-filters="HtmlTable" class="jt_counter_table">
      <thead>
         <tr>
           <th class="jt_counter_display_name">Counter Name</th>
           <th class="jt_counter_total">Value</th>   
        </tr>
      </thead>
      <tbody>
      % for group in counters.groups:
        <tr>
          <td colspan="4" class="jt_counter_group_name">${format_counter_name(group.displayName)}</td>
        </tr>
      % for name, counter in sorted(group.counters.iteritems()):
       <tr>
          <td class="jt_counter_display_name">${format_counter_name(counter.displayName)}</td>
          <td class="jt_counter_total">${counter.value}</td>
        </tr>
      % endfor
      % endfor
      </tbody>
     </table>
</%def>

<%def name="job_counters(counters)">
<%
  from jobbrowser.views import format_counter_name
%>

    <table data-filters="HtmlTable" class="jt_counter_table">
      <thead>
         <tr>
           <th class="jt_counter_display_name">Name</th>
           <th class="jt_counter_maps_total">Maps Total</th>
           <th class="jt_counter_reduces_total">Reduces Total</th>
           <th class="jt_counter_total">Total</th>   
        </tr>
      </thead>
      <tbody>
      % for group in counters.itervalues():
        <tr>
          <td colspan="4" class="jt_counter_group_name">${format_counter_name(group['displayName'])}</td>
        </tr>
      % for name, counter in sorted(group['counters'].iteritems()):
      <%
        map_count = counter.get('map', 0)
        reduce_count = counter.get('reduce', 0)
        job_count = counter.get('job', 0)
      %>
       <tr>
          <td class="jt_counter_display_name">${format_counter_name(counter.get('displayName', 'n/a'))}</td>
          <td class="jt_counter_maps_total">${map_count}</td>
          <td class="jt_counter_reduces_total">${reduce_count}</td>
          <td class="jt_counter_total">${map_count + reduce_count + job_count}</td>
        </tr>
      % endfor
      % endfor
      </tbody>
     </table>
</%def>

<%def name="mr_graph(job)">
  <div class="jt_mr_display">
    ${mr_graph_maps(job)}
    ${mr_graph_reduces(job)}
  </div>
</%def>

<%def name="mr_graph_maps(job)">
  <div class="jt_maps">
    <span class="jt_maps_complete" style="width: ${job.maps_percent_complete}%;">${job.finishedMaps} / ${job.desiredMaps}</span>
    <span class="jt_white_border"></span>
  </div>
</%def>
<%def name="mr_graph_reduces(job, right_border=False)">
  <div class="jt_reduces">
    <span class="jt_reduces_complete" style="width: ${job.reduces_percent_complete}%;">${job.finishedReduces} / ${job.desiredReduces}</span>
    % if right_border:
      <span class="jt_white_border"></span>
    % endif
  </div>
</%def>
