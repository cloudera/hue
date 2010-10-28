{% comment %}
Licensed to Cloudera, Inc. under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  Cloudera, Inc. licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
{% endcomment %}
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
	<head>
		<title>Refresh with params</title>
	</head>
	<body>
		<div class="jframe_padded">
			<p>clicking the two links below will update the view to have their corresponding get parameters added. This is cumulative, so clicking each one only updates the relevant param (not deleting others)</p>
			<a class="ccs-refresh_with_params" data-refresh-params="iLike=cookies">I refresh this view with "iLike=cookies"</a><br/>
			<a class="ccs-refresh_with_params" data-refresh-params="iLike=cake">I refresh this view with "iLike=cake"</a><br/>
			<a class="ccs-refresh_with_params" data-refresh-params="youLike=cookies">I refresh this view with "youLike=cookies"</a><br/>
			<a class="ccs-refresh_with_params" data-refresh-params="youLike=cake">I refresh this view with "youLike=cake"</a><br/>
			<hr/>
			the current values: <br/>
			iLike: ${ get_var("iLike", "~")}<br/>
			youLike: ${ get_var("youLike", "~")}<br/>
		</div>
	</body>
</html>
