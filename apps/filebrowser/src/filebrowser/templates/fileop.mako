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
import datetime
from django import forms
from django.template.defaultfilters import urlencode, escape, stringformat, date, filesizeformat, time
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>



${ commonheader(_('File Operation'), 'filebrowser', user, request) | n,unicode }

## Not sure if enctype breaks anything if used for things other than file upload.

<div class="container-fluid">
<div class="well">
<form action="" method="POST" enctype="multipart/form-data" class="form-stacked">
${ csrf_token(request) | n,unicode }
<h1>${form.op}</h1>
% if isinstance(form, forms.Form):
	${form.as_p()|n}
% else:
	% for _form in form.forms:
		${_form.as_p()|n}
	% endfor
	${form.management_form}
% endif
<div>
<input type="submit" value="${('Submit')}" class="btn btn-primary" />
<a href="${urlencode(next)}" class="btn">${('Cancel')}</a>
</div>
</form>
</div>

${ commonfooter(request, messages) | n,unicode }
