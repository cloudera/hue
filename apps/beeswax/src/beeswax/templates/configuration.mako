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
<%namespace name="wrappers" file="header_footer.mako" />
<%namespace name="util" file="util.mako" />
${wrappers.head('Hive Configuration Variables', section='hive configuration')}
<h1>Hive Configuration Variables</h1>
<div class="toolbar">
  <div class="bw-input-filter">
    <!--input type="text" class="jframe-hidden" data-filters="OverText, ArtInput, FilterInput" data-art-input-type="search"
      title="Filter by Name"
      data-filter-elements="tbody tr" value=""/-->
  </div>
</div>
<table class="datatables">
  <thead>
    <tr>
      <th>Key</th>
      <th>Value</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    % for config_value in config_values:
    <tr>
      <td>${config_value.key or ""}</td><td>${config_value.value or ""}</td><td>${config_value.description or ""}</td>
    </tr>
    % endfor
  </tbody>
</table>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
		    "bFilter": false,
			"bInfo": false,
		});
	});
</script>
${wrappers.foot()}
