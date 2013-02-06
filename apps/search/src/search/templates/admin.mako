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

<%namespace name="macros" file="macros.mako" />
<%namespace name="navigation" file="navigation_bar_admin.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }


<div class="container-fluid">
  ${ navigation.menubar('cores') }

  % for core in hue_cores:
    <p><a href="${ core.get_absolute_url() }">${ core.name }</a></p>
  % endfor


  ${ cores }
  ${ hue_cores }

</div>

${ commonfooter(messages) | n,unicode }
