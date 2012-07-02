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

<%namespace name="edit" file="editor_components.mako" />
<%! from desktop.lib.django_util import extract_field_data %>

<%
  is_superuser = extra_params['current_user'].username == extra_params['superuser']
  select_filter = is_superuser and 'SelectWithOther' or ''
%>

## Puts together a selection list with an "other" field as well.
<%def name="selection(name, choices, current_value, other_key=None)">
    <% seen = False %>
    % if len(choices) == 0:
      <select name="${name}" class="hide">
    % else:
      <select name="${name}">
    % endif
    % for choice in choices:
      % if choice == current_value:
        <% seen = True %>
        <option selected>${choice}</option>
      % else:
        <option>${choice}</option>
      % endif
    % endfor
    % if is_superuser:
      % if seen or not current_value:
        <option value="__other__">Other</option>
      % else:
        <option value="__other__" selected="true">Other</option>
      % endif
    % endif

    </select>
    % if is_superuser:
      % if seen or not current_value:
        <input name="${other_key}" class="hide">
      % else:
        <input name="${other_key}" value="${current_value}">
      % endif
    % endif
</%def>
<form id="chownForm" action="/filebrowser/chown?next=${next|u}" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Change Owner / Group:')} ${path}</h3>
    </div>
    <div class="modal-body change-owner-modal-body clearfix" >
        <div class="alert alert-message block-message info">${_('Note: Only the Hadoop superuser, on this FS "%(superuser)s", may change the owner of a file.') % dict(superuser=extra_params['superuser'])}"</div>
        <div style="padding-left: 15px; padding-bottom: 10px;">
            ${edit.render_field(form["path"], hidden=True)}

            <label>${_('User')}</label>

            % if is_superuser:
            ${ selection("user", form.all_users, extract_field_data(form["user"]), "user_other") }
            % else:
            ${ selection("user", [extract_field_data(form['user'])], extract_field_data(form["user"])) }
            % endif

            <label>${_('Group')}</label>

            % if is_superuser:
            ${ selection("group", form.all_groups, extract_field_data(form["group"]), "group_other") }
            % else:
            ${ selection("group", [group for group in form.all_groups if group in extra_params['current_user'].get_groups()], extract_field_data(form["group"])) }
            % endif
        </div>


    </div>
    <div class="modal-footer" style="padding-top: 10px;">
        <div id="chownRequired" class="hide" style="position: absolute; left: 10;">
            <span class="label label-important">${_('Sorry, name is required.')}</span>
        </div>
        <input class="btn primary" type="submit" value="${_('Submit')}" />
        <a class="btn" onclick="$('#changeOwnerModal').modal('hide');">${_('Cancel')}</a>
    </div>
</form>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $("select[name='user']").change(function(){
            if ($(this).val() == "__other__"){
                $("input[name='user_other']").show();
            }
            else {
                $("input[name='user_other']").hide();
            }
        });
        $("select[name='group']").change(function(){
            if ($(this).val() == "__other__"){
                $("input[name='group_other']").show();
            }
            else {
                $("input[name='group_other']").hide();
            }
        });

        $("#chownForm").submit(function(){
            if ($("select[name='user']").val() == null){
                $("#chownRequired").find(".label").text("${_('Sorry, user is required.')}");
                $("#chownRequired").show();
                return false;
            }
            else if ($("select[name='group']").val() == null){
                $("#chownRequired").find(".label").text("${_('Sorry, group is required.')}");
                $("#chownRequired").show();
                return false;
            }
            else {
                if ($("select[name='group']").val() == "__other__" && $("input[name='group_other']").val() == ""){
                    $("#chownRequired").find(".label").text("${_('Sorry, you need to specify another group.')}");
                    $("input[name='group_other']").addClass("fieldError");
                    $("#chownRequired").show();
                    return false;
                }
                if ($("select[name='user']").val() == "__other__" && $("input[name='user_other']").val() == ""){
                    $("#chownRequired").find(".label").text("${_('Sorry, you need to specify another user.')}");
                    $("input[name='user_other']").addClass("fieldError");
                    $("#chownRequired").show();
                    return false;
                }
                return true;
            }
        });
    });
</script>

