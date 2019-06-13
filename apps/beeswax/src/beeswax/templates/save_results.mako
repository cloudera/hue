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
from desktop.lib.django_util import extract_field_data

from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="util" file="util.mako" />

${ commonheader(_('Create table from file'), app_name, user, request) | n,unicode }
${layout.menubar(section='query')}

<div class="container-fluid">
% if error_msg:
  <h4>${error_msg}</h4>
% endif
  <div class="card card-small">
    <h1 class="card-heading simple">${_('Save Query Results')}</h1>
    <div class="card-body">
      <p>
        <form id="saveForm" action="${action}" method="POST" class="form form-inline">
          ${ csrf_token(request) | n,unicode }
          <fieldset>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input id="id_save_target_0" type="radio" name="save_target" value="${ form.SAVE_TYPE_TBL }" data-bind="checked: toWhere"/>
                  &nbsp;${ _('In a new table') }
                </label>
                <span data-bind="visible: toWhere() == 'to a new table'">
                  ${ comps.field(form['target_table'], notitle=True, placeholder='Table Name') }
                </span>
              </div>
            </div>
            <div class="control-group">
              <div class="controls">
                <label class="radio">
                  <input id="id_save_target_1" type="radio" name="save_target" value="${ form.SAVE_TYPE_DIR }" data-bind="checked: toWhere">
                  &nbsp;${ _('In an HDFS directory') }
                </label>
                <span data-bind="visible: toWhere() == 'to HDFS directory'">
                  ${ comps.field(form['target_dir'], notitle=True, placeholder=_('Results location'), klass='pathChooser') }
                </span>
              </div>
            </div>
            <div id="fileChooserModal" class="smallModal well hide">
              <a href="#" class="close" data-dismiss="modal">&times;</a>
            </div>
          </fieldset>
          <div class="form-actions" style="padding-left:10px">
            <input type="submit" name="save" value="${_('Save')}" class="btn btn-primary"/>
            <input type="submit" name="cancel" value="${_('Cancel')}" class="btn"/>
          </div>
        </form>
      </p>
    </div>
  </div>
</div>

<script type="text/javascript">
  $(document).ready(function () {
    $("input[name='target_dir']").after(hueUtils.getFileBrowseButton($("input[name='target_dir']")));

    var viewModel = {
      toWhere: ko.observable("${ extract_field_data(form['save_target']) }")
    };

    ko.applyBindings(viewModel);
  });
</script>

${ commonfooter(request, messages) | n,unicode }
