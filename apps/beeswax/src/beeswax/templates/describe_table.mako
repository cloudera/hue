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

<%
  if table.is_view:
    view_or_table_noun = _("View")
  else:
    view_or_table_noun = _("Table")
%>
${commonheader(_("%s Metadata: %s") % (view_or_table_noun, table.name), "beeswax", user, "100px")}
${layout.menubar(section='tables')}

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
    <h1>${_('Table Metadata:')} ${table.name}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="#importData" data-toggle="modal">${_('Import Data')}</a></li>
                    <li><a href="${ url("beeswax.views.read_table", table=table.name) }">${_('Browse Data')}</a></li>
                    <li><a href="#dropTable" data-toggle="modal">${_('Drop')} ${view_or_table_noun}</a></li>
                    <li><a href="${ table.hdfs_link }" rel="${ table.path_location }">${_('View File Location')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            % if table.comment is not None:
                <h5>${ table.comment }</h5>
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
                    <a href="${ url("beeswax.views.describe_partitions", table=table.name) }">${_('Show Partitions')}</a>
                  </div>
                % endif

                % if sample is not None:
                    <div class="tab-pane" id="sample">
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
                                  <td>${ item }</td>
                                % endfor
                              </tr>
                            % endfor
                          </tbody>
                        </table>
                    </div>
                % endif
            </div>
        </div>
    </div>
</div>




<div id="dropTable" class="modal hide fade">
    <form id="dropTableForm" method="POST" action="${ url("beeswax.views.drop_table", table=table.name) }">
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
    </form>
</div>



<div id="importData" class="modal hide fade">
    <form method="POST" action="${ url("beeswax.views.load_table", table=table.name) }" class="form-horizontal">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal">&times;</a>
            <h3>${_('Import data')}</h3>
        </div>
        <div class="modal-body">

            <div class="control-group">
                ${comps.bootstrapLabel(load_form["path"])}
                <div class="controls">
                    ${comps.field(load_form["path"],
                    placeholder="/user/user_name/data_dir/file",
                    klass="pathChooser input-xlarge",
                    file_chooser=True,
                    show_errors=False
                    )}
                </div>
            </div>

            <div id="filechooser"></div>

            % for pf in load_form.partition_columns:
                <div class="control-group">
                     ${comps.bootstrapLabel(load_form[pf])}
                     <div class="controls">
                       ${comps.field(load_form[pf], render_default=True, attrs={'klass': 'input-xlarge'})}
                    </div>
                </div>
            % endfor

            <div class="control-group">
              <div class="controls">
                <label class="checkbox">
                    <input type="checkbox" name="overwrite"/> ${_('Overwrite existing data')}
                  </label>
                </div>
            </div>

            <p class="muted"><em>${_("Note that loading data will move data from its location into the table's storage location.")}</em></p>
        </div>

        <div class="modal-footer">
            <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
            <input type="submit" class="btn btn-primary" value="${_('Submit')}"/>
        </div>
    </form>
</div>
</div>

 <style>
   #filechooser {
     display: none;
     min-height: 100px;
     height: 250px;
     overflow-y: scroll;
     margin-top: 10px;
   }

   .sampleTable td, .sampleTable th {
     white-space: nowrap;
   }

   .form-horizontal .controls {
     margin-left: 0;
   }

   .form-horizontal .control-label {
     width: auto;
     padding-right: 10px;
   }
 </style>

 <script type="text/javascript" charset="utf-8">
   $(document).ready(function () {

     $(".fileChooserBtn").click(function(e){
       e.preventDefault();
       var _destination = $(this).attr("data-filechooser-destination");
       $("#filechooser").jHueFileChooser({
         initialPath: $("input[name='"+_destination+"']").val(),
         onFileChoose: function(filePath){
           $("input[name='"+_destination+"']").val(filePath);
           $("#filechooser").slideUp();
         },
         createFolder: false
       });
       $("#filechooser").slideDown();
     });

     $(".datatables").dataTable({
       "bPaginate":false,
       "bLengthChange":false,
       "bInfo":false,
       "bFilter":false
     });

     $.getJSON("${ url("beeswax.views.drop_table", table=table.name) }", function (data) {
       $("#dropTableMessage").text(data.title);
     });

     $('a[data-toggle="tab"]').on('shown', function () {
       $(".sampleTable").not('.initialized').addClass('initialized').dataTable({
         "bPaginate":false,
         "bLengthChange":false,
         "bInfo":false,
         "bFilter":false,
         "fnInitComplete":function () {
           $(".sampleTable").parent().jHueTableScroller();
           $(".sampleTable").jHueTableExtender({
             hintElement:"#jumpToColumnAlert",
             fixedHeader:true
           });
         }
       });
     })

   });
 </script>

 ${commonfooter(messages)}
