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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and
## multiple spaces and line breaks cause issues
<%!
import datetime
from django.template.defaultfilters import urlencode, escape
%>
<%!
def is_selected(section, matcher):
  if section == matcher:
    return "selected"
  else:
    return ""
%>

<%!
def is_home(path):
    if path == "/":
        return "selected"
    else:
        return ""
%>

<%def name="head(title='Beeswax for Hive', section='', path='', current_request_path=False, toolbar=True, cwd_set=True, show_upload=False, show_new_directory=False)">

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<meta name="viewport" content="width=device-width user-scalable=no initial-scale=1" />
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<title>${title}</title>
	<link rel="stylesheet" href="/static/ext/css/bootstrap.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />
	<link rel="stylesheet" href="/static/css/jhue.css" type="text/css" media="screen" title="no title" charset="utf-8" />

	<style type="text/css">
      body {
        padding-top: 100px;
      }
    </style>
	<script src="/static/ext/js/jquery/jquery-1.7.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/js/Source/jHue/jquery.showusername.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.simpleplaceholder.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/bootstrap-tabs.js" type="text/javascript" charset="utf-8"></script>

	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$("#username").showUsername();
			$("input:text[placeholder]").simplePlaceholder();
			$(".submitter").keydown(function(e){
				if (e.keyCode==13){
					$(this).closest("form").submit();
				}
			}).change(function(){
				$(this).closest("form").submit();
			});
		});
	</script>

</head>
<body>
	<div class="topbar">
		<div class="topbar-inner">
			<div class="container-fluid">
				<a class="brand" href="#">jHue</a>
				<ul class="nav">
					<li><a href="/beeswax">Beeswax</a></li>
					<li class="active"><a href="/filebrowser/">File Browser</a></li>
					<li><a href="/jobsub/">Job Designer</a></li>
					<li><a href="/jobbrowser/jobs/">Job Browser</a></li>
					<li><a href="/useradmin/">User Admin</a></li>
					<li><a href="/help/">Help</a></li>
				</ul>
				<p class="pull-right">Logged in as <a id="username" href="/accounts/logout">xxx</a></p>
			</div>
		</div>
	</div>
	<div class="menubar">
		<div class="menubar-inner">
			<div class="container-fluid">
				<ul class="nav">
                     % if toolbar:
                        % if home_directory:
                          <% my_home_disabled = "" %>
                        % else:
                          <% my_home_disabled = "disabled" %>
                        % endif
                        <li><a class="${is_home(path)}" href="${url('filebrowser.views.view', path=(home_directory or "/"))}">My Home</a></li>
                        % if cwd_set:
                          % if show_upload:
                            <li><a class="${is_selected(section, 'upload')}" href="${url('filebrowser.views.upload')}?dest=${path|urlencode}&next=${current_request_path|urlencode}">Upload Files</a></li>
                          % endif
                          % if show_new_directory:
                            <li><a class="${is_selected(section, 'new directory')}" href="${url('filebrowser.views.mkdir')}?path=${path|urlencode}&next=${current_request_path|urlencode}">New Directory</a></li>
                          %endif
                        % endif
                     % endif
				</ul>
			</div>
		</div>
	</div>

	<div class="container-fluid">

</%def>

<%def name="foot()">
	</div>
</body>
</html>
</%def>





<%def name="headz(title='Beeswax for Hive', toolbar=True, section=False)">
<html>
  <head>
    <title>${title}</title>
  </head>
  <body class="hue-shared">
  
</%def>

<%def name="footz()">
  </body>
</html>
</%def>


