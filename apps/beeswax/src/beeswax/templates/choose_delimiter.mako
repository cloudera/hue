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
                <li class="active"><a href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li><a id="step3" href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form id="delimiterForm" action="${action}" method="POST" class="form-horizontal">
                <div class="hide">
                    ${util.render_form(file_form)}
                    ${comps.field(delim_form['file_type'])}
                </div>
                <fieldset>
                    <div class="alert alert-info"><h3>${_('Choose a Delimiter')}</h3>
                        % if initial:
                            ${_('Beeswax has determined that this file is delimited by')} <strong>${delim_readable}</strong>.
                        % endif
                    </div>
                    <div class="control-group">
                        ${comps.bootstrapLabel(delim_form["delimiter"])}
                        <div class="controls">
                            ${comps.field(delim_form["delimiter"], render_default=True)}
                            <input id="submit_preview" class="btn btn-info" type="submit" value="${_('Preview')}" name="submit_preview"/>
                            <span class="help-block">
                            ${_('Enter the column delimiter. Must be a single character. Use syntax like "\\001" or "\\t" for special characters.')}
                            </span>
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label">${_('Table preview')}</label>
                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped table-condensed">
                                    <thead>
                                    <tr>
                                            % for i in range(n_cols):
                                                <th>col_${i+1}</th>
                                            % endfor
                                    </tr>
                                    </thead>
                                    <tbody>
                                            % for row in fields_list:
                                            <tr>
                                                % for val in row:
                                                    <td>${val}</td>
                                                % endfor
                                            </tr>
                                            % endfor
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </fieldset>

                <div class="form-actions">
                    <input class="btn" type="submit" value="${_('Previous')}" name="cancel_delim"/>
                    <input class="btn primary" type="submit" name="submit_delim" value="${_('Next')}" />
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

        $("#id_delimiter_1").css("margin-left","4px").attr("placeholder","${_('Please type your delimiter here')}").hide();
        $("#id_delimiter_0").change(function(){
            if ($(this).val() == "__other__"){
                $("#id_delimiter_1").show();
            }
            else {
                $("#id_delimiter_1").hide();
                $("#id_delimiter_1").val('');
            }
        });

        $("#id_delimiter_0").change();

        $("#step1").click(function(e){
            e.preventDefault();
            $("input[name='cancel_delim']").click();
        });
        $("#step3").click(function(e){
            e.preventDefault();
            $("input[name='submit_delim']").click();
        });
        $("body").keypress(function(e){
            if(e.which == 13){
                e.preventDefault();
                $("input[name='submit_delim']").click();
            }
        });
    });
</script>

${commonfooter(messages)}
