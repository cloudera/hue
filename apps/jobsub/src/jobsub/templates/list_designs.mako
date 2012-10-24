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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="commonlayout" file="layout.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${commonheader(_('Job Designer'), "jobsub", user, "100px")}
${commonlayout.menubar(section='designs')}

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/jobsub.ko.js" type="text/javascript" charset="utf-8"></script>


<%def name="layout()">
  <div class="container-fluid">
    <h1>${_('Job Designs')}</h1>

  <%actionbar:render>
    <%def name="actions()">
        <button class="btn" title="${_('Submit')}" data-bind="click: submitDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canSubmit"><i class="icon-play"></i> ${_('Submit')}</button>
        <button class="btn" title="${_('Edit')}" data-bind="click: editDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canSubmit"><i class="icon-pencil"></i> ${_('Edit')}</button>
        <button class="btn" title="${_('Delete')}" data-bind="click: deleteDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canDelete"><i class="icon-trash"></i> ${_('Delete')}</button>
        <button class="btn" title="${_('Clone')}" data-bind="click: cloneDesign, enable: selectedDesigns().length == 1"><i class="icon-share"></i> ${_('Clone')}</button>
    </%def>
    <%def name="creation()">
        <span class="btn-group">
                <a href="${ url('jobsub.views.new_design', action_type='mapreduce') }" class="btn" title="${_('Create Mapreduce Design')}" rel="tooltip"><i class="icon-plus-sign"></i> ${_('Mapreduce')}</a>
                <a href="${ url('jobsub.views.new_design', action_type='streaming') }" class="btn" title="${_('Create Streaming Design')}" rel="tooltip"><i class="icon-plus-sign"></i> ${_('Streaming')}</a>
                <a href="${ url('jobsub.views.new_design', action_type='java') }" class="btn"title="${_('Create Java Design')}" rel="tooltip"><i class="icon-plus-sign"></i> ${_('Java')}</a>
            </span>
      %if show_install_examples:
          &nbsp; <a id="installSamplesLink" href="javascript:void(0)" data-confirmation-url="${url('jobsub.views.setup')}" class="btn"><i class="icon-download-alt"></i> ${_('Install Samples')}</a>
      %endif
    </%def>
  </%actionbar:render>

    <table id="designTable" class="table table-condensed datatables">
      <thead>
      <tr>
        <th width="1%"><div id="selectAll" data-bind="click: selectAll, css: {hueCheckbox: true, 'icon-ok': allSelected}"></div></th>
        <th>${_('Owner')}</th>
        <th>${_('Name')}</th>
        <th>${_('Type')}</th>
        <th>${_('Description')}</th>
        <th>${_('Last Modified')}</th>
      </tr>
      </thead>
      <tbody id="designs" data-bind="template: {name: 'designTemplate', foreach: designs}">

      </tbody>
    </table>

  </div>

  <script id="designTemplate" type="text/html">
    <tr style="cursor: pointer">
      <td class="center" data-bind="click: handleSelect" style="cursor: default">
        <div data-bind="visible: name != '..', css: {hueCheckbox: name != '..', 'icon-ok': selected}"></div>
      </td>
      <td data-bind="click: $root.editDesign, text: owner"></td>
      <td data-bind="click: $root.editDesign, text: name"></td>
      <td data-bind="click: $root.editDesign, text: type"></td>
      <td data-bind="click: $root.editDesign, text: description"></td>
      <td data-bind="click: $root.editDesign, text: lastModified, attr: { 'data-sort-value': lastModifiedMillis }" style="white-space: nowrap;"></td>
    </tr>
  </script>
</%def>

${layout()}

<div id="submitWf" class="modal hide fade">
    <form id="submitWfForm" action="" method="POST" style="margin:0">
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
            <a href="#" class="btn secondary" data-dismiss="modal">${_('Cancel')}</a>
        </div>
    </form>
</div>

<div id="deleteWf" class="modal hide fade">
    <form id="deleteWfForm" action="" method="POST" style="margin:0">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3 id="deleteWfMessage">${_('Delete this design?')}</h3>
        </div>
        <div class="modal-footer">
            <input type="submit" class="btn primary" value="${_('Yes')}"/>
            <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
        </div>
    </form>
</div>

<div id="installSamples" class="modal hide fade">
    <form id="installSamplesForm" action="${url('jobsub.views.setup')}" method="POST" style="margin:0">
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

    var deleteMessage = "${_('Are you sure you want to delete %(name)s?') % dict(name='##PLACEHOLDER##')}";
    var submitMessage = "${_('Submit %(name)s to the cluster') % dict(name='##PLACEHOLDER##')}";

    $(document).ready(function() {

        var designTable, viewModel;

        $("#filterInput").keyup(function() {
            if (designTable != null){
                designTable.fnFilter($(this).val());
            }
        });

        $("#installSamplesLink").click(function(){
            $("#installSamples").modal("show");
        });

        viewModel = new JobSubModel(${designs});
        ko.applyBindings(viewModel);
        designTable = $('#designTable').dataTable( {
            "sPaginationType": "bootstrap",
            "bLengthChange": false,
            "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
            "aoColumns": [
                { "bSortable": false },
                null,
                null,
                null,
                null,
                { "sSortDataType": "dom-sort-value", "sType": "numeric" }
            ],
            "aaSorting": [[ 5, "desc" ]],
            "fnPreDrawCallback": function( oSettings ) {
                if (viewModel.allSelected()){
                    viewModel.selectAll();
                }
            },
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

        $(".btn[rel='tooltip']").tooltip({placement:'bottom'});
        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>
${commonfooter(messages)}
