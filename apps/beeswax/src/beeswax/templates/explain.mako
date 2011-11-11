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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
<%namespace name="util" file="util.mako" />
${wrappers.head('Query Explanation', section='saved queries')}


	<h1>Query Explanation: ${util.render_query_context(query_context)}</h1>

	<ul class="tabs">
		<li class="active"><a href="#explanation">Explanation</a></li>
      	<li><a href="#query">Query</a></li>
	</ul>
    
	<div class="tab-content">
		<div class="active tab-pane" id="explanation">
			<pre>${explanation}</pre>
		</div>
		<div class="tab-pane" id="query">
			<pre>${query}</pre>
		</div>
	</div>
	
	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$(".tabs").tabs();
		});
	</script>

${wrappers.foot()}
