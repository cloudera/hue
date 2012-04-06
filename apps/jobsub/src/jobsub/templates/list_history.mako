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
  import urllib
  from django.template.defaultfilters import date, time
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext, ungettext, get_language, activate

  _ = ugettext
%>
<%namespace name="layout" file="layout.mako" />

${commonheader("Job Designer", "jobsub", "100px")}
${layout.menubar(section='history')}

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
    <h1>Job Submission History</h1>
    <div class="well hueWell">
        <form class="form-search">
			Filter: <input id="filterInput" class="input-xlarge search-query" placeholder="Search for username, name, etc...">
		</form>
    </div>


    <table class="table table-condensed datatables" id="jobTable">
        <thead>
            <tr>
                <th>Oozie Job ID</th>
                <th>Owner</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Submission Date</th>
            </tr>
        </thead>
        <tbody>
            %for record in history:
                <% design = record.design %>
                <tr>
                    <td><a href="${url('jobsub.views.oozie_job', jobid=record.job_id)}">${record.job_id}</a></td>
                    <td>${record.owner.username}</td>
                    <td>${design.name}</td>
                    <td>${design.root_action.action_type}</td>
                    <td>${design.description}</td>
                    <td>${date(record.submission_date)} ${time(record.submission_date).replace("p.m.","PM").replace("a.m.","AM")}</td>
                </tr>
            %endfor
        </tbody>
    </table>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function() {
        var oTable = $('#jobTable').dataTable( {
          'sPaginationType': 'bootstrap',
          "bLengthChange": false,
          "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
		  "aoColumns": [
				null,
				null,
				null,
				null,
				null,
				{ "sType": "date" }
			],
			"aaSorting": [[ 5, "desc" ]]
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val());
        });

    });
</script>

${commonfooter()}
