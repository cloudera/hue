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
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="components" file="components.mako" />

<%
  if table.is_view:
    view_or_table_noun = _("View")
  else:
    view_or_table_noun = _("Table")
%>
${ commonheader(_("%s : %s") % (view_or_table_noun, table.name), app_name, user) | n,unicode }

<%def name="column_table(cols)">
    <table class="table table-striped table-condensed datatables">
      <thead>
        <tr>
          <th>${_('Name')}</th>
          <th>${_('Type')}</th>
          <th>${_('Comment')}</th>
        </tr>
      </thead>
      <tbody>
        % for column in cols:
          <tr>
            <td>${ column.name }</td>
            <td>${ column.type }</td>
            <td>${ column.comment or "" }</td>
          </tr>
        % endfor
      </tbody>
    </table>

</%def>

<div class="container-fluid">
    <h1>${_('Table')} ${table.name}</h1>

    ${ components.breadcrumbs(breadcrumbs) }

    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    % if has_write_access:
                    <li><a href="#" id="import-data-btn">${_('Import Data')}</a></li>
                    % endif
                    <li><a href="${ url('metastore:read_table', database=database, table=table.name) }">${_('Browse Data')}</a></li>
                    % if has_write_access:
                    <li><a href="#dropTable" data-toggle="modal">${_('Drop')} ${view_or_table_noun}</a></li>
                    % endif
                    <li><a href="${ table.hdfs_link }" rel="${ table.path_location }">${_('View File Location')}</a></li>
                    % if table.partition_keys:
                      <li><a href="${ url('metastore:describe_partitions', database=database, table=table.name) }">${_('Show Partitions')} (${ len(partitions) })</a></li>
                    % endif
                </ul>
            </div>
        </div>
        <div class="span10">
            % if table.comment:
                <div class="alert alert-info">${ _('Comment:') } ${ table.comment }</div>
            % endif

            <ul class="nav nav-tabs">
                <li class="active"><a href="#columns" data-toggle="tab">${_('Columns')}</a></li>
                % if table.partition_keys:
                    <li><a href="#partitionColumns" data-toggle="tab">${_('Partition Columns')}</a></li>
                % endif
                % if sample is not None:
                    <li><a href="#sample" data-toggle="tab">${_('Sample')}</a></li>
                % endif
            </ul>

            <div class="tab-content">
                <div class="active tab-pane" id="columns">
                    ${column_table(table.cols)}
                </div>

                % if table.partition_keys:
                  <div class="tab-pane" id="partitionColumns">
                    ${column_table(table.partition_keys)}
                  </div>
                % endif

                % if sample is not None:
                    <div class="tab-pane" id="sample">
                      % if error_message:
                        <div class="alert alert-error">
                          <h3>${_('Error!')}</h3>
                          <pre>${error_message | h}</pre>
                        </div>
                      % else:
                        <table class="table table-striped table-condensed sampleTable">
                          <thead>
                            <tr>
                              % for col in table.cols:
                                <th>${col.name}</th>
                              % endfor
                            </tr>
                          </thead>
                          <tbody>
                            % for i, row in enumerate(sample):
                              <tr>
                                % for item in row:
                                  <td>${ smart_unicode(item, errors='ignore') }</td>
                                % endfor
                              </tr>
                            % endfor
                          </tbody>
                        </table>
                      % endif
                    </div>
                % endif
            </div>
        </div>
    </div>
</div>




<div id="dropTable" class="modal hide fade">
    <form id="dropTableForm" method="POST" action="${ url('metastore:drop_table', database=database) }">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Drop Table')}</h3>
    </div>
    <div class="modal-body">
      <div id="dropTableMessage">
      </div>
    </div>
    <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
        <input type="submit" class="btn btn-danger" value="${_('Yes, drop this table')}"/>
    </div>
    <div class="hide">
      <select name="table_selection">
        <option value="${ table.name }" selected>${ table.name }</option>
      </select>
    </div>
    </form>
</div>


<div id="import-data-modal" class="modal hide fade"></div>

</div>

<style>
   .sampleTable td, .sampleTable th {
     white-space: nowrap;
   }
</style>

<link rel="stylesheet" href="/metastore/static/css/metastore.css" type="text/css">

<script type="text/javascript" charset="utf-8">
   $(document).ready(function () {
     $(".datatables").dataTable({
       "bPaginate": false,
       "bLengthChange": false,
       "bInfo": false,
       "bFilter": false,
       "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
           "sZeroRecords": "${_('No matching records')}",
       }
     });

     % if has_write_access:
     $.getJSON("${ url('metastore:drop_table', database=database) }", function(data) {
       $("#dropTableMessage").text(data.title);
     });
     % endif

     $('a[data-toggle="tab"]').on('shown', function() {
       $(".sampleTable").not('.initialized').addClass('initialized').dataTable({
         "bPaginate": false,
         "bLengthChange": false,
         "bInfo": false,
         "bFilter": false,
         "fnInitComplete": function () {
           $(".sampleTable").parent().jHueTableScroller();
           $(".sampleTable").jHueTableExtender({
             hintElement: "#jumpToColumnAlert",
             fixedHeader: true
           });
         },
         "oLanguage": {
            "sEmptyTable": "${_('No data available')}",
            "sZeroRecords": "${_('No matching records')}",
         }
       });
     })

    $("#import-data-btn").click(function () {
      $.get("${ url('metastore:load_table', database=database, table=table.name) }", function (response) {
          $("#import-data-modal").html(response['data']);
          $("#import-data-modal").modal("show");
        }
      );
    });

   });
</script>

${ commonfooter(messages) | n,unicode }
