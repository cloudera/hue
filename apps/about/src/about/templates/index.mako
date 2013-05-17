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
${ commonheader(_('About Oozie UI'), "about", user, "100px") | n,unicode }

	<div class="subnav subnav-fixed" style="margin-top:4px">
		<div class="container-fluid">
		<ul class="nav nav-pills">
			##<li><a href="${url("desktop.views.dump_config")}">${_('Configuration')}</a></li>
			##<li><a href="${url("desktop.views.check_config")}">${_('Check for misconfiguration')}</a></li>
			<li><a href="${url("desktop.views.log_view")}">${_('Server Logs')}</a></li>
		</ul>
		</div>
	</div>

	<div class="container-fluid" style="margin-top: 30px">

    <div class="row-fluid">
      <div class="span2 center">
        <img src="/static/art/oozie_200x.png" />
      </div>
      <div class="span2 center">
        <img src="/static/art/hue-login-logo.png" />
      </div>
    </div>
    <div class="row-fluid" style="margin-top: 15px">
      <div class="span2 center">
        tested on <a href="http://oozie.apache.org" target="_blank">Oozie 3.3.x</a>
      </div>
      <div class="span2 center">
        based on <a href="http://gethue.com" target="_blank">Hue 2.3</a>
      </div>
    </div>

	</div>

${ commonfooter(messages) | n,unicode }
