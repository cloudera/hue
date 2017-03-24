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
from django.utils.translation import ugettext as _
from desktop.views import commonheader, commonfooter
%>
${ commonheader(_('403 - CSRF error'), "", user, request) | n,unicode }

<link rel="stylesheet" href="${ static('desktop/css/httperrors.css') }">

<div id="httperror" class="container-fluid">
  <div class="row-fluid">
    <div class="span12 center">
      <div class="error-code">403</div>
    </div>
  </div>
  <div class="row-fluid">
    <div class="span6 offset3 center error-box">
      <h1>${_('CSRF error.')}</h1>

      <p>${_("Sorry, your session is invalid or has expired. Please go back, refresh the page, and try your submission again.")}</p>
      <br/>
      <a class="pointer" onclick="history.back()">${ _('Go back') }</a>
    </div>
  </div>
</div>


${ commonfooter(None, messages) | n,unicode }
