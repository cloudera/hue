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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop import conf
from desktop.auth.backend import is_admin
%>

%if not is_embeddable:
${ commonheader(_('Error'), app_name, user, request, "40px") | n,unicode }
%endif

  <div class="container-fluid">
    <div class="row-fluid">
      <div class="span12">
        <div class="card card-small">
          <h1 class="card-heading simple">${ _('Error!') }</h1>
          <div class="card-body">
            <p>
              <pre>${ smart_unicode(error) }</pre>

              %if traceback and is_admin(user):
                <textarea style="width: 100%;" rows=80 readonly="readonly">
                ${ smart_unicode(traceback) }
                </textarea>
              %endif

              <a class="btn" onclick="history.back()">${ _('Back') }</a>

              %if conf.REDIRECT_WHITELIST.get():
                <a class="btn btn-primary" href="/">${ _('Home') }</a>
              % endif
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
