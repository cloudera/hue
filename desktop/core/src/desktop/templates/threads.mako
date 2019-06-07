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

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Threads'), "about", user, request) | n,unicode }
%endif


<script type="text/javascript">
  (function () {
    var ThreadsViewModel = function () {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.threads = ko.observable();
      self.fetchThreads = function () {
        self.apiHelper.simpleGet('/desktop/debug/threads', {}, {successCallback: self.threads});
      };
    }
    $(document).ready(function () {
      var viewModel = new ThreadsViewModel();
      ko.applyBindings(viewModel, $('#threadsComponents')[0]);
    });
  })();
</script>

${layout.menubar(section='threads')}

<div id="threadsComponents" class="container-fluid">
  <div class="card card-small" style="padding-top: 10px">
    <pre data-bind="text: $root.threads"></pre>
  </div>
</div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
