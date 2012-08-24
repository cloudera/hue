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

${commonheader(_('Configuration Variables'), "beeswax", user, "100px")}
${layout.menubar(section='configuration')}

<div class="container-fluid">
	<h1>${_('Configuration Variables')}</h1>
	<div class="well">
		<form class="form-search" method="POST">
		  <span>
		    ${server_form['server']}
		    <button type="submit" class="btn primary">${_('Look')}</button>
		   </span>
		   <span class="pull-right">
              ${_('Filter:')} <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${_('Search for key, value, etc...')}">
		      <a href="#" id="clearFilterBtn" class="btn">${_('Clear')}</a>
		   </span>
		</form>
	</div>
	<table class="table table-striped table-condensed datatables">
		<thead>
			<tr>
				<th>${_('Key')}</th>
				<th>${_('Value')}</th>
				<th>${_('Description')}</th>
			</tr>
		</thead>
		<tbody>
    	% for config_value in config_values:
	    	<tr class="confRow" data-search="${config_value.key or ""}${config_value.value or ""}${config_value.description or ""}">
	      		<td>${config_value.key or ""}</td><td>${config_value.value or ""}</td><td>${config_value.description or ""}</td>
	    	</tr>
	    % endfor
		</tbody>
	</table>
</div>


<script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
		    "bFilter": false,
			"bInfo": false,
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

        $("#id_server").change(function(){
            $.cookie("hueBeeswaxLastQueryServer", $(this).val(), {expires: 90});
        });

        if ($.cookie("hueBeeswaxLastQueryServer") != null) {
            $("#id_server").val($.cookie("hueBeeswaxLastQueryServer"));
        }
	});
</script>

${commonfooter(messages)}
