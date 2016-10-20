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

<%namespace name="common" file="common.mako" />

${ commonheader(_('Query'), app_name, user, request) | n,unicode }

<%common:navbar></%common:navbar>

<div class="container-fluid">
  <div class="card">
    <div class="row-fluid">
      <div class="span10 offset1 center error-wrapper">
        <i class="fa fa-cogs"></i>
        <br />
        <br />
        <h1>${_('There are currently no databases configured.')}</h1>
        <h1>${_('Please go to your Hue configuration and add a database under the "rdbms" section.')}</h1>
        <br />
      </div>
    </div>
  </div>

</div>

<style type="text/css">
.error-wrapper {
  margin-top: 50px;
  color: #BBB;
  line-height: 60px;
}

.error-wrapper i {
  font-size: 196px;
}
</style>

${ commonfooter(request, messages) | n,unicode }
