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
from desktop.views import commonheader_iframe, commonfooter_iframe
import urllib
%>

${commonheader_iframe()}
<form id="editForm" class="form-horizontal" action="${urllib.quote(action)}" method="POST">
    <div class="alert alert-info">
        This will not import any users or groups that don't already exist in Hue.
        Only users and groups imported from LDAP can be synced.
        <br/>
        All user information and group memberships will be updated based on the LDAP
        server's current state.
    </div>
</form>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$("#id_groups").jHueSelector();
	});
</script>
${commonfooter_iframe()}
