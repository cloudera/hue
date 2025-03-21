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
from django.http import HttpRequest

from desktop.lib.i18n import smart_str
from desktop.views import login_modal
from desktop.lib.django_util import nonce_attribute

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="commonHeaderFooterComponents" file="/common_header_footer_components.mako" />

% if request is not None:
${ smart_str(login_modal(request).content) | n,unicode }
% endif

<iframe id="zoomDetectFrame" style="width: 250px; display: none" ></iframe>

${ commonHeaderFooterComponents.footer(messages, nonce_attribute(request) ) }

  </body>
</html>
