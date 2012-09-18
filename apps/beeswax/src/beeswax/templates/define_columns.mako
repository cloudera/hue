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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="util" file="util.mako" />
${commonheader(_('Create table from file'), "beeswax", user, "100px")}
${layout.menubar(section='tables')}

<div class="container-fluid">
    <h1>${_('Create a new table from a file')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="${ url('beeswax.create_table.import_wizard')}">${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url('beeswax.create_table.create_table')}">${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <ul class="nav nav-pills">
                <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
                <li><a id="step2" href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li class="active"><a href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form action="${action}" method="POST" class="form-stacked">
                <div class="hide">
                    ${util.render_form(file_form)}
                ${util.render_form(delim_form)}
                ${unicode(column_formset.management_form) | n}
                </div>
                <%
                    n_rows = len(fields_list)
                    if n_rows > 2: n_rows = 2
                %>
                <fieldset>
                    <div class="alert alert-info"><h3>${_('Define your columns')}</h3></div>
                    <div class="control-group">
                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped">
                                    <tr>
                                        <td>&nbsp;</td>
                                        % for form in column_formset.forms:
                                                <td>
                                                ${comps.label(form["column_name"])}
                                                ${comps.field(form["column_name"],
                                                render_default=False,
                                                placeholder=_("Column name")
                                                )}
                                                    <br/><br/>
                                                ${comps.label(form["column_type"])}
                                                ${comps.field(form["column_type"],
                                                render_default=True
                                                )}
                                                ${unicode(form["_exists"]) | n}
                                                </td>
                                        %endfor
                                    </tr>
                                    % for i, row in enumerate(fields_list[:n_rows]):
                                        <tr>
                                            <td><em>${_('Row')} #${i + 1}</em></td>
                                        % for val in row:
                                                <td>${val}</td>
                                        % endfor
                                        </tr>
                                    % endfor
                                </table>
                            </div>
                        </div>
                    </div>
                </fieldset>
                <div class="form-actions">
                    <input class="btn" type="submit" name="cancel_create" value="${_('Previous')}" />
                    <input class="btn primary" type="submit" name="submit_create" value="${_('Create Table')}" />
                </div>
            </form>
        </div>
    </div>
</div>

<style>
    .scrollable {
        width: 100%;
        overflow-x: auto;
    }
</style>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".scrollable").width($(".form-actions").width());
        $("#step1").click(function(e){
            e.preventDefault();
            $("input[name='cancel_create']").attr("name","cancel_delim").click();
        });
        $("#step2").click(function(e){
            e.preventDefault();
            $("input[name='cancel_create']").click();
        });
        $("body").keypress(function(e){
            if(e.which == 13){
                e.preventDefault();
                $("input[name='submit_create']").click();
            }
        });
    });
</script>
${commonfooter(messages)}
