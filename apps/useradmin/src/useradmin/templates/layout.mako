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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and
## multiple spaces and line breaks cause issues
<%!
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="render_field(field, show_label=True, extra_attrs={})">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}"
      rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
      % if show_label:
        <label class="control-label">${ field.label }</label>
      % endif
      <div class="controls">
        <% field.field.widget.attrs.update(extra_attrs) %>
        ${ field | n,unicode }
        % if field.errors:
          <span class="help-inline">${ field.errors | n,unicode }</span>
        % endif
      </div>
    </div>
  %endif
</%def>

<%def name="menubar(section='', _=None)">
	<div class="subnav subnav-fixed">
		<div class="container-fluid">
			<ul class="nav nav-pills">
				<li class="${is_selected(section, 'users')}"><a href="/useradmin/users">${_('Users')}</a></li>
				<li class="${is_selected(section, 'groups')}"><a href="/useradmin/groups">${_('Groups')}</a></li>
				<li class="${is_selected(section, 'permissions')}"><a href="/useradmin/permissions">${_('Permissions')}</a></li>
			</ul>
		</div>
	</div>
</%def>

<%def name="commons()">
    <style type="text/css">
        .fixed {
            position: fixed;
            top: 80px;
            filter: progid:dximagetransform.microsoft.gradient(startColorstr='#ffffffff', endColorstr='#fff2f2f2', GradientType=0);
            -webkit-box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
            -moz-box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.065);
        }
        .pull-right {
            margin: 4px;
        }
        .sortable {
            cursor: pointer;
        }
        .file-row {
            height:37px;
        }
    </style>
    <script type="text/javascript">
        $(document).ready(function(){
            $("#filterInput").keyup(function(){
                var shown = 0;
                $(".datatables tfoot").hide();
                $.each($(".tableRow"), function(index, value) {
                    if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
                        $(value).hide();
                    }
                    else{
                        $(value).show();
                        shown++;
                    }
                });
                if (shown == 0){
                    $(".datatables tfoot").show();
                }
            });
        });
    </script>
</%def>

