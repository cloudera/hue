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
${wrappers.head("Beeswax: Table List", section='tables')}
  <h1>Tables</h1>
<div class="sidebar">
	<div class="well">
		<h6>Actions</h6>
		% if not examples_installed:
        <a href="${ url('beeswax.views.install_examples') }">Install samples</a><br/>
      % endif
      	<a href="${ url('beeswax.create_table.index') }">Create a new table</a><br/><br/>
    </div>
</div>

<div class="content">


  <!--div class="toolbar">
    <div class="bw-input-filter">
      <input type="text" class="jframe-hidden" data-filters="OverText, ArtInput, FilterInput" data-art-input-type="search"
        title="Filter by Name"
        data-filter-elements="td.bw-tables_table" data-filter-parents="tr" value=""/>
    </div>
  </div-->

  <table class="datatables">
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Browse</th>
      </tr>
    </thead>
    <tbody>
      % for table in tables:
        <tr>
          <td>
            <a href="${ url("beeswax.views.describe_table", table=table) }">${ table }</a>
          </td>
          <td><a href="${ url("beeswax.views.read_table", table=table) }">Browse Data</a></td>
        </tr>
      % endfor
    </tbody>
  </table>
	<div class="row">
		<div class="span16">&nbsp;</div>
	</div>
</div>


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".tabs").tabs();
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false
		});

	});
</script>
${wrappers.foot()}
