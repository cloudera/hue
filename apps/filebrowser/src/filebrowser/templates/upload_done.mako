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
from django.template.defaultfilters import urlencode
%>
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head('${path} - Upload Complete', 'upload', show_new_directory=False)}
<% path_enc = urlencode(path) %>
View uploaded file: <a href="${url('filebrowser.views.view', path=path_enc)}">${path}</a>.<br>
Go back to where you were: <a href="${next|urlencode}">${next}</a>.
${wrappers.foot()}
