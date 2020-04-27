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
import logging
import sys

from desktop.views import commonheader, commonfooter


LOG = logging.getLogger(__name__)
%>

<%namespace name="layout" file="about_layout.mako" />

${ layout.menubar(section='dump_config') }

<style type="text/css">
  .card-heading .pull-right {
    font-size: 12px;
    font-weight: normal;
  }
</style>

<div id="aboutConfiguration">
  <!-- ko component: { name: 'hue-config-tree' } --><!-- /ko -->
</div>

<script type="text/javascript">
  $(document).ready(function () {
    ko.applyBindings({}, $('#aboutConfiguration')[0]);
  });
</script>
