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

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Beeswax'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    % if not examples_installed:
                    <li class="nav-header">${_('Examples')}</li>
                    <li><a href="#installSamples" data-toggle="modal">${_('Install Samples')}</a></li>
                    % endif
                    <li class="nav-header">${_('Tables')}</li>
                    <li><a href="${ url(app_name + ':show_tables') }">${_('Show Tables')}</a></li>
                    <li><a href="${ url(app_name + ':create_table') }">${_('Create Table')}</a></li>
                    <li class="nav-header">${_('Queries')}</li>
                    <li><a href="${ url(app_name + ':list_designs') }">${_('Saved Queries')}</a></li>
                    <li><a href="${ url(app_name + ':execute_query') }">${_('Execute Query')}</a></li>
                    <li><a href="${ url(app_name + ':list_query_history') }">${_('Query History')}</a></li>
                    <li class="nav-header">${_('Configuration')}</li>
                    <li><a href="${ url(app_name + ':configuration') }">${_('Configuration')}</a></li>
                    <li><a href="${ url(app_name + ':configuration') }?include_hadoop=1">${_('Extended Configuration')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <h1>${_('Welcome to Beeswax for Hive')}</h1>
            ${_("To get started with Beeswax you'll first need set up some data:")}
            <a href="${ url(app_name + ':create_table') }" class='btn'>${_('Import Data')}</a>
            ${_("or")} <a href="#installSamples" data-toggle="modal" class='btn'>${_('Install Samples')}</a>
        </div>
    </div>
</div>

<div id="installSamples" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Install samples')}</h3>
    </div>
    <div class="modal-body">
      <div id="installSamplesMessage"></div>
    </div>
    <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <a href="#" id="installSamplesBtn" class="btn btn-primary">${_('Yes, install samples')}</a>
    </div>
</div>


<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $.getJSON("${ url(app_name + ':install_examples') }",function(data){
            $("#installSamplesMessage").text(data.title);
        });

        $("#installSamplesBtn").click(function(){
            $.post(
                "${ url(app_name + ':install_examples') }",
                { submit:"Submit" },
                function(result){
                    if (result.creationSucceeded){
                        window.location.href = "/beeswax/tables";
                    }
                    else {
                        var message = "${_('There was an error processing your request:')} " + result.message;
                        $("#installSamplesMessage").addClass("alert").addClass("alert-error").text(message);
                    }
                }
            );
        });
    });
</script>

${ commonfooter(messages) | n,unicode }
