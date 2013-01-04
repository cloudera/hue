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
${ commonheader(_('Not Found'), "", user) | n,unicode }

  <div class="container-fluid">
    <h1>${_('Page not found')}</h1>
    <p>${_("We're sorry, but the requested page could not be found:")}</p>
    <br/>
    <code>${uri}</code>
  </div>

${ commonfooter(messages) | n,unicode }
