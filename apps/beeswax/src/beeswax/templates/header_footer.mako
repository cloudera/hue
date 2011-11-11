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
def is_selected(section, matcher):
  if section == matcher:
    return "selected"
  else:
    return ""
%>

<%def name="head(title='Beeswax for Hive', toolbar=True, section=False)">

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
	<script src="/static/js/Source/jHue/jquery.filechooser.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.simpleplaceholder.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.ocupload-1.1.2.packed.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/bootstrap-tabs.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-modal.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-twipsy.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-popover.js" type="text/javascript" charset="utf-8"></script>	

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
					<li class="active"><a href="/beeswax">Beeswax</a></li>
					<li><a href="/filebrowser/">File Browser</a></li>
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
					<li><a href="/beeswax/execute" class="${is_selected(section, 'query')}">Query Editor</a></li>
					<li><a href="/beeswax/my_queries" class="${is_selected(section, 'my queries')}">My Queries</a></li>
					<li><a href="/beeswax/list_designs" class="${is_selected(section, 'saved queries')}">Saved Queries</a></li>
					<li><a href="/beeswax/query_history" class="${is_selected(section, 'history')}">History</a></li>
					<li><a href="/beeswax/tables" class="${is_selected(section, 'tables')}">Tables</a></li>
					<li><a href="/beeswax/configuration" class="${is_selected(section, 'hive configuration')}">Settings</a></li>
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
  <div class="toolbar">
    <a href="${ url('beeswax.views.index') }"><img src="/beeswax/static/art/beeswax-logo.png" width="55" height="55" alt="Beeswax" class="beeswax_logo"></a>
    % if toolbar:
    <ul class="bw-nav" data-filters="ArtButtonBar">
      <li><a href="${ url('beeswax.views.execute_query') }" 
        class="bw-nav_icon bw-query_nav ${is_selected(section, 'query')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Query Editor</a></li>
      <li><a href="${ url('beeswax.views.my_queries') }"
        class="bw-nav_icon bw-my_queries_nav ${is_selected(section, 'my queries')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">My Queries</a></li>
      <li><a href="${ url('beeswax.views.list_designs') }" 
        class="bw-nav_icon bw-queries_nav ${is_selected(section, 'saved queries')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Saved Queries</a></li>
    ## <li><a href="${ url('beeswax.views.edit_report') }" class="bw-nav_icon bw-new_report_gen_nav ${is_selected(section, 'report generator')}" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Report Generator</a></li>
      <li><a href="${ url('beeswax.views.list_query_history') }" 
        class="bw-nav_icon bw-history_nav ${is_selected(section, 'history')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">History</a></li>
      <li><a href="${ url('beeswax.views.show_tables') }" 
        class="bw-nav_icon bw-tables_nav ${is_selected(section, 'tables')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Tables</a></li>
      <li><a href="${ url('beeswax.views.configuration') }" 
        class="bw-nav_icon bw-config_nav ${is_selected(section, 'hive configuration')}" data-filters="ArtButton"
        data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">Settings</a>
      </li>
      <li><a class="jframe-refresh large" data-filters="ArtButton">Refresh</a></li>
    </ul>
    % endif
  </div>
  <hr class="jframe-hidden"/>
</%def>

<%def name="footz()">
  </body>
</html>
</%def>


