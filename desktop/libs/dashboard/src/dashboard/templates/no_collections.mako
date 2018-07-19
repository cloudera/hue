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
from indexer.conf import ENABLE_NEW_INDEXER
from desktop.auth.backend import is_admin
%>

<%namespace name="macros" file="macros.mako" />

% if not is_embeddable:
${ commonheader(_('Dashboard'), "dashboard", user, request, "120px") | n,unicode }
% endif

<style type="text/css">
  .waiting {
    font-size: 196px;
    color: #DDD;
  }

  h1 {
    margin-top: 50px;
    color: #BBB;
    line-height: 60px;
  }
</style>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span10 offset1 center">

      <i class="fa fa-search waiting"></i>
      <h1>${ _('It seems there is nothing to search on ...') }</h1>
      % if is_admin(user):
      <h1>
        ${ _('What about creating a') }
        % if ENABLE_NEW_INDEXER.get():
          <a href="${ url('indexer:indexes') }">${ _('new index') }</a> ?
        % else:
          <a href="${ url('indexer:collections')  }">${ _('new index') }</a> ?
        % endif
      </h1>
      % endif
    </div>
  </div>
</div>

% if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
% endif
