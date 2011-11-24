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

<%def name="header(title='Hue Shell', toolbar=True, shells=[], name='')">

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
	<link rel="stylesheet" href="/static/ext/css/fileuploader.css" type="text/css" media="screen" title="no title" charset="utf-8" />
	
	<style type="text/css">
      body {
		% if toolbar and shells:
			padding-top: 100px;
		% else:
			padding-top: 60px;
		% endif
      }
    </style>
	<script src="/static/ext/js/jquery/jquery-1.7.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/js/Source/jHue/jquery.showusername.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/js/Source/jHue/jquery.filechooser.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/js/Source/jHue/jquery.contextmenu.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.simpleplaceholder.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/bootstrap-dropdown.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-tabs.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-modal.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-twipsy.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/bootstrap-popover.js" type="text/javascript" charset="utf-8"></script>	
	<script src="/static/ext/js/fileuploader.js" type="text/javascript" charset="utf-8"></script>

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
			var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
			for (var i=0;i<hashes.length;i++){
				if (hashes[i].indexOf("keyName")>-1){
					$("."+hashes[i].split("=")[1]).addClass("selected");
				}
			}
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
					<li><a href="/filebrowser/">File Browser</a></li>
					<li><a href="/jobsub/">Job Designer</a></li>
					<li><a href="/jobbrowser/jobs/">Job Browser</a></li>
					<li><a href="/useradmin/">User Admin</a></li>
					<li class="active"><a href="/shell/">Shell</a></li>
					<li><a href="/help/">Help</a></li>
					<li><a href="/about/">About</a></li>
				</ul>
				<p class="pull-right">Logged in as <a id="username" href="/accounts/logout">xxx</a></p>
			</div>
		</div>
	</div>
	% if toolbar and shells:
	<div class="menubar">
		<div class="menubar-inner">
			<div class="container-fluid">
				<ul class="nav">
				% if len(shells) == 1:
					% if shells[0]["exists"]:
						<li><a href="${url('shell.views.create')}?keyName=${shells[0]["keyName"]}" class="${shells[0]["keyName"]}">${shells[0]["niceName"]}</a></li>
					% else: 
						<li><a href="#" class="disabled">${shells[0]["niceName"]}</a></li>
					% endif
				% else:
					% if shells[0]["exists"]:
						<li><a href="${url('shell.views.create')}?keyName=${shells[0]["keyName"]}" class="${shells[0]["keyName"]}">${shells[0]["niceName"]}</a></li>
					% else:
						<li><a href="#" class="disabled">${shells[0]["niceName"]}</a></li>
					% endif
					% for item in shells[1:-1]:
						% if item["exists"]:
							<li><a href="${url('shell.views.create')}?keyName=${item["keyName"]}" class="${item["keyName"]}">${item["niceName"]}</a></li>
						% else:
							<li><a href="#" class="disabled">${item["niceName"]}</a></li>
						% endif
					% endfor
					% if shells[-1]["exists"]:
						<li><a href="${url('shell.views.create')}?keyName=${shells[-1]["keyName"]}" class="${shells[-1]["keyName"]}">${shells[-1]["niceName"]}</a></li>
					% else:
						<li><a href="#" class="disabled">${shells[-1]["niceName"]}</a></li>
					% endif
				% endif
				</ul>
			</div>
		</div>
	</div>
	% endif
	<div class="container-fluid">

</%def>

<%def name="footer()">
	</div>
</body>
</html>
</%def>
