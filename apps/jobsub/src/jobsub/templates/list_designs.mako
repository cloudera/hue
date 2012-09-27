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
import cgi
import urllib
import time as py_time
from django.template.defaultfilters import date, time
from desktop.lib.django_util import extract_field_data
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${commonheader(_('Job Designer'), "jobsub", user, "100px")}
${layout.menubar(section='designs')}

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
    <h1>${_('Job Designs')}</h1>

    <%actionbar:render>
        <%def name="creation()">
            <a href="${ url('jobsub.views.new_design', action_type='mapreduce') }" class="btn">${_('Create Mapreduce Design')}</a>
            <a href="${ url('jobsub.views.new_design', action_type='streaming') }" class="btn">${_('Create Streaming Design')}</a>
            <a href="${ url('jobsub.views.new_design', action_type='java') }" class="btn">${_('Create Java Design')}</a>
            %if show_install_examples:
            <a id="installSamplesLink" href="javascript:void(0)" data-confirmation-url="${url('jobsub.views.setup')}" class="btn" >${_('Install Samples')}</a>
            %endif
        </%def>
    </%actionbar:render>

    <table id="designTable" class="table table-condensed datatables">
        <thead>
        <tr>
            <th>${_('Owner')}</th>
            <th>${_('Name')}</th>
            <th>${_('Type')}</th>
            <th>${_('Description')}</th>
            <th>${_('Last Modified')}</th>
            <th nowrap="nowrap">&nbsp;</th>
        </tr>
        </thead>
        <tbody>
                %for design in designs:
                <tr>
                    <td>${design.owner.username}</td>
                    <td>${design.name}</td>
                    <td>${design.root_action.action_type}</td>
                    <td>${design.description}</td>
                    <td nowrap="nowrap" data-sort-value="${py_time.mktime(design.last_modified.timetuple())}">${date(design.last_modified)} ${time(design.last_modified).replace("p.m.","PM").replace("a.m.","AM")}</td>
                <td nowrap="nowrap" class="right">
                %if currentuser.username == design.owner.username:
                    <a title="${_('Submit %(name)s to the cluster') % dict(name=design.name)}" class="btn small submitConfirmation"
                       alt="${_('Submit %(name)s to the cluster') % dict(name=design.name)}"
                       href="javascript:void(0)"
                       data-param-url="${ url('jobsub.views.get_design_params', design_id=design.id) }"
                       data-submit-url="${ url('jobsub.views.submit_design', design_id=design.id) }">${_('Submit')}</a>
                    <a title="${_('Edit %(name)s') % dict(name=design.name)}" class="btn small"
                       href="${ url('jobsub.views.edit_design', design_id=design.id) }" data-row-selector="true">${_('Edit')}</a>
                %endif
                %if currentuser.is_superuser or currentuser.username == design.owner.username:
                    <a title="${_('Delete %(name)s') % dict(name=design.name)}" class="btn small deleteConfirmation"
                       alt="${_('Are you sure you want to delete %(name)s?') % dict(name=design.name)}"
                       href="javascript:void(0)"
                       data-confirmation-url="${ url('jobsub.views.delete_design', design_id=design.id) }">${_('Delete')}</a>
                %endif
                    <a title="${_('Clone %(name)s') % dict(name=design.name)}" class="btn small" href="${ url('jobsub.views.clone_design', design_id=design.id) }">${_('Clone')}</a>
                </td>
                </tr>
                %endfor
        </tbody>
    </table>

</div>


<div id="submitWf" class="modal hide fade">
    <form id="submitWfForm" action="" method="POST">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3 id="submitWfMessage">${_('Submit this design?')}</h3>
        </div>
        <div class="modal-body">
            <fieldset>
                <div id="param-container">
                </div>
            </fieldset>
        </div>
        <div class="modal-footer">
            <input id="submitBtn" type="submit" class="btn primary" value="${_('Submit')}"/>
            <a href="#" class="btn secondary hideModal">${_('Cancel')}</a>
        </div>
    </form>
</div>

<div id="deleteWf" class="modal hide fade">
    <form id="deleteWfForm" action="" method="POST">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3 id="deleteWfMessage">${_('Delete this design?')}</h3>
        </div>
        <div class="modal-footer">
            <input type="submit" class="btn primary" value="${_('Yes')}"/>
            <a href="#" class="btn secondary hideModal">${_('No')}</a>
        </div>
    </form>
</div>

<div id="installSamples" class="modal hide fade">
    <form id="installSamplesForm" action="${url('jobsub.views.setup')}" method="POST">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Install sample job designs?')}</h3>
        </div>
        <div class="modal-body">
            ${_('It will take a few seconds to install.')}
        </div>
        <div class="modal-footer">
            <input type="submit" class="btn primary" value="${_('Yes')}"/>
            <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
        </div>
    </form>
</div>


<script type="text/javascript" charset="utf-8">
    $(document).ready(function() {

        $(".deleteConfirmation").click(function(){
            var _this = $(this);
            var _action = _this.attr("data-confirmation-url");
            $("#deleteWfForm").attr("action", _action);
            $("#deleteWfMessage").text(_this.attr("alt"));
            $("#deleteWf").modal("show");
        });
        $("#deleteWf .hideModal").click(function(){
            $("#deleteWf").modal("hide");
        });

        $(".submitConfirmation").click(function(){
            var _this = $(this);
            var _action = _this.attr("data-submit-url");
            $("#submitWfForm").attr("action", _action);
            $("#submitWfMessage").text(_this.attr("alt"));
            // We will show the model form, but disable the submit button
            // until we've finish loading the parameters via ajax.
            $("#submitBtn").attr("disabled", "disabled");
            $("#submitWf").modal("show");

            $.get(_this.attr("data-param-url"), function(data) {
                var params = data["params"]
                var container = $("#param-container");
                container.empty();
                for (key in params) {
                    if (!params.hasOwnProperty(key)) {
                        continue;
                    }
                    container.append(
                            $("<div/>").addClass("clearfix")
                                    .append($("<label/>").text(params[key]))
                                    .append(
                                    $("<div/>").addClass("input")
                                            .append($("<input/>").attr("name", key).attr("type", "text"))
                            )
                    )
                }
                // Good. We can submit now.
                $("#submitBtn").removeAttr("disabled");
            }, "json");
        });
        $("#submitWf .hideModal").click(function(){
            $("#submitWf").modal("hide");
        });

        var oTable = $('#designTable').dataTable( {
            "sPaginationType": "bootstrap",
            "bLengthChange": false,
            "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
            "aoColumns": [
                null,
                null,
                null,
                null,
                { "sSortDataType": "dom-sort-value", "sType": "numeric" },
                { "bSortable": false }
            ],
            "aaSorting": [[ 4, "desc" ]],
            "oLanguage": {
                "sEmptyTable":     "${_('No data available in table')}",
                "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
                "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
                "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
                "sZeroRecords":    "${_('No matching records found')}",
                "oPaginate": {
                    "sFirst":    "${_('First')}",
                    "sLast":     "${_('Last')}",
                    "sNext":     "${_('Next')}",
                    "sPrevious": "${_('Previous')}"
                }
            }
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val());
        });

        $("#installSamplesLink").click(function(){
            $("#installSamples").modal("show");
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>
${commonfooter(messages)}
