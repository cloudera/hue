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

<link rel="stylesheet" href="${ static('desktop/css/httperrors.css') }">

<div id="httperror" class="container-fluid">
  <div class="row-fluid">
    <div class="span12 center">
      <div class="error-code"><i class="fa fa-exclamation"></i></div>
    </div>
  </div>
  <div class="row-fluid">
    <div class="span6 offset3 center error-box">
      <h1>${_('Job Designer is not available on Hue 4')}</h1>

      <p>${_("We're sorry, but the requested page is deprecated and could not be shown.")}</p>
      <br/>
      <a id="openInHue3" href="javascript:void(0)" target="_blank">${_('Open it in Hue 3 instead')}</a>
    </div>
  </div>
</div>

<script>
  $(document).ready(function(){
    $('#openInHue3').attr('href', window.location.pathname.substr(4) + window.location.hash);
  });
</script>
