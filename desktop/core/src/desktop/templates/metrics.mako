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
import sys

from desktop.views import commonheader, commonfooter
from desktop import conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%
MAIN_SCROLLABLE = is_embeddable and "'.page-content'" or "window"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = is_embeddable and "78px" or "106px"
else:
  TOP_SNAP = is_embeddable and "50px" or "106px"
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Metrics'), "about", user, request) | n,unicode }
%endif

${layout.menubar(section='metrics')}

<script src="${ static('desktop/js/metrics-inline.js') }" type="text/javascript"></script>

<div id="Metrics">
<Metrics data-reactcomponent='Metrics'></Metrics>
</div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
