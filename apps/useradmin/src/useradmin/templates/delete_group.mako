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
%>
<form id="deleteGroupForm" action="${ url('useradmin.views.delete_group') }" method="POST">
  <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteGroupMessage">${_("Are you sure you want to delete the selected group(s)?")}</h3>
  </div>
  <div class="modal-footer">
      <a href="javascript:void(0);" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
  </div>
  <div class="hide">
    <select name="group_ids" data-bind="options: availableUsers, selectedOptions: chosenUsers"
            multiple="true"></select>
  </div>
</form>