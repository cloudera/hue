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
    <div class="well">
        <form class="form-search">
			Filter: <input id="filterInput" class="input-xlarge search-query" placeholder="Search for username, name, etc...">
		    <a href="#" id="clearFilterBtn" class="btn">Clear</a>
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
                <% wf = record.design %>
                <tr>
                    <td><a href="${url('jobsub.views.oozie_job', jobid=record.job_id)}">${record.job_id}</a></td>
                    <td>${record.owner.username}</td>
                    <td>${wf.name}</td>
                    <td>${wf.root_action.action_type}</td>
                    <td>${wf.description}</td>
                    <td>${record.submission_date.strftime('%c')}</td>
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
          "sDom": "<'row'r>t<'row'<'span8'i><''p>>"
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val());
        });

		$("#clearFilterBtn").click(function(){
	        $("#filterInput").val("");
	        oTable.fnFilter("");
	    });
    });
</script>

${commonfooter()}
