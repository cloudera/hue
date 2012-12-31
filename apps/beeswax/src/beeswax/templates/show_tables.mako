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

${commonheader(_('Table List'), app_name, user, '100px')}
${layout.menubar(section='tables')}


<div class="container-fluid">
    <h1>${_('Table List')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('database')}</li>
                    <li>
                       <form action="${ url(app_name + ':show_tables') }" id="db_form" method="POST">
                         ${ db_form }
                       </form>
                    </li>
                    <li class="nav-header">${_('Actions')}</li>
                    % if not examples_installed:
                    <li><a href="#installSamples" data-toggle="modal">${_('Install samples')}</a></li>
                      % endif
                      <li><a href="${ url(app_name + ':import_wizard', database=database) }">${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url(app_name + ':create_table', database=database) }">${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <table class="table table-condensed table-striped datatables">
                <thead>
                    <tr>
                        <th>${_('Table Name')}</th>
                        <th>&nbsp;</th>
                    </tr>
                </thead>
                <tbody>
                % for table in tables:
                    <tr>
                        <td>
                            <a href="${ url(app_name + ':describe_table', database=database, table=table) }" data-row-selector="true">${ table }</a>
                        </td>
                        <td><a href="${ url(app_name + ':read_table', database=database, table=table) }" class="btn">${_('Browse Data')}</a></td>
                    </tr>
                % endfor
                </tbody>
            </table>
        </div>
    </div>
</div>



% if not examples_installed:
<div id="installSamples" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Install samples')}</h3>
    </div>
    <div class="modal-body">
      <div id="installSamplesMessage">

      </div>
    </div>
    <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <a href="#" id="installSamplesBtn" class="btn btn-primary">${_('Yes, install samples')}</a>
    </div>
</div>
% endif

<script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".datatables").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bFilter": false,
            "aoColumns": [
                null,
                { "sWidth": "130px", "bSortable" : false }
             ],
            "oLanguage": {
                "sEmptyTable": "${_('No data available')}",
                "sZeroRecords": "${_('No matching records')}",
            }
        });

        $("a[data-row-selector='true']").jHueRowSelector();

        $("#id_database").change(function(){
             $.cookie("hueBeeswaxLastDatabase", $(this).val(), {expires: 90});
             $('#db_form').submit();
        });

        % if not examples_installed:
        $.getJSON("${ url(app_name + ':install_examples') }", function(data){
            $("#installSamplesMessage").text(data.title);
        });

        $("#installSamplesBtn").click(function(){
            $.post(
                "${ url(app_name + ':install_examples') }",
                { submit: "Submit" },
                function(result){
                    if (result.creationSucceeded){
                        window.location.href = "${ url(app_name + ':show_tables') }";
                    }
                    else {
                        var message = "${_('There was an error processing your request:')} " + result.message;
                        $("#installSamplesMessage").addClass("alert").addClass("alert-error").text(message);
                    }
                }
            );
        });
        % endif
    });
</script>

${commonfooter(messages)}
