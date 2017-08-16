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

<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Hue Users'), "useradmin", user, request) | n,unicode }
${ layout.menubar(section='users') }

<div class="useradmin container-fluid">
  <div class="card card-small">
    <h1 class="card-heading simple">${ _('User: %(username)s') % {'username': instance.username} }</h1>

    <div class="steps">
      <div id="step1" class="stepDetails">
        ${ _('Username') } ${ instance.username }
        <br/>
        ${ _('First name') } ${ instance.first_name }
        <br/>
        ${ _('Last name') } ${ instance.last_name }
        <br/>
        ${ _('Email') } ${ instance.email }
      </div>
  </div>
</div>


${layout.commons()}

${ commonfooter(request, messages) | n,unicode }
