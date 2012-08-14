## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.	See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##	   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from desktop import conf
from django.utils.translation import ugettext as _
%>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>Hue Login</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta name="description" content="">
	<meta name="author" content="">

	<link href="/static/ext/css/bootstrap.min.css" rel="stylesheet">
	<link href="/static/css/hue2.css" rel="stylesheet">

	<!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
	<!--[if lt IE 9]>
	<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	<style type="text/css">
		body {
			padding-top: 100px;
		}
	</style>
</head>

<body>
	<div class="navbar navbar-fixed-top">
		% if conf.CUSTOM.BANNER_TOP_HTML.get():
		<div id="banner-top" class="banner">
			${conf.CUSTOM.BANNER_TOP_HTML.get()}
		</div>
		% endif
		<div class="navbar-inner">
			<div class="container-fluid">
				<a class="brand" href="#">Hue</a>
			</div>
		</div>
	</div>

	<div class="container">
		<div class="row">
			<div class="span4 offset4">
				<form method="POST" action="${action}" class="well">
					<label>${_('Username')}
						<input name="username" class="input-large" type="text" maxlength="30">
					</label>
					<label>${_('Password')}
						<input name="password" class="input-large" type="password" maxlength="30">
					</label>

					%if first_login_ever==True:
						<input type="submit" class="btn primary" value="${_('Sign up')}" />
					%else:
						<input type="submit" class="btn primary" value="${_('Sign in')}" />
					%endif
					<input type="hidden" name="next" value="${next}" />

					%if login_errors==True:
						<br/>
						<br/>
						<div class="alert alert-error">
							<p><strong>${_('Error!')}</strong> ${_('Invalid username or password.')}</p>
						</div>
					%endif
				</form>
			</div>
		</div>

		%if first_login_ever==True:
		<div class="row">
			<div class="span6 offset3">
				<div class="alert alert-block">
					<p>${_('Since this is your first time logging in, please pick any username and password. Be sure to remember these, as')}
					 <strong>${_('they will become your superuser credentials for Hue')}</strong>.</p>
				</div>
			</div>
		</div>
		%endif
	</div>
</body>
</html>
