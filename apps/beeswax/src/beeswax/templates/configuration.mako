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

<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Settings'), app_name, user, request) | n,unicode }
${layout.menubar(section='configuration')}

<div class="container-fluid">
  <div class="card card-small">
	  <h1 class="card-heading simple">${_('Settings')}</h1>
    <div class="card-body">
      <p>
        <form class="form-search" method="POST">
          ${ csrf_token(request) | n,unicode }
          <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${_('Search for key or value.')}">
          <a href="#" id="clearFilterBtn" class="btn">${_('Clear')}</a>
        </form>
        <table class="table table-condensed datatables">
          <thead>
            <tr>
              <th>${_('Key')}</th>
              <th>${_('Value')}</th>
            </tr>
          </thead>
          <tbody>
            % for key, value in configuration.items():
              <tr class="confRow" data-search="${key or ""}${value or ""}">
                  <td>${key or ""}</td><td>${value or ""}</td>
              </tr>
            % endfor
          </tbody>
        </table>
      </p>
    </div>
  </div>
</div>

<script type="text/javascript">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
		    "bFilter": false,
			"bInfo": false,
            "oLanguage": {
                "sEmptyTable": "${_('No data available')}",
                "sZeroRecords": "${_('No matching records')}",
            }
		});

		var searchTimeoutId = 0;
		$("#filterInput").keyup(function(){
			window.clearTimeout(searchTimeoutId);
			searchTimeoutId = window.setTimeout(function(){
				$.each($(".confRow"), function(index, value) {
		          if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
		            $(value).hide();
		          }else{
		            $(value).show();
		          }
		        });
			}, 500);
	    });

		$("#clearFilterBtn").click(function(){
	        $("#filterInput").val("");
	        $.each($(".confRow"), function(index, value) {
	            $(value).show();
	        });
	    });
	});
</script>

${ commonfooter(request, messages) | n,unicode }
