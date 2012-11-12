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
  if is_view:
    view_or_table_noun = _("View")
  else:
    view_or_table_noun = _("Table")
%>
${commonheader(_("%s Metadata: %s") % (view_or_table_noun, table.tableName), "beeswax", user, "100px")}
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
	<h1>${_('Table Metadata:')} ${table.tableName}</h1>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">${_('Actions')}</li>
					<li><a href="#importData" data-toggle="modal">${_('Import Data')}</a></li>
					<li><a href="${ url("beeswax.views.read_table", table=table_name) }">${_('Browse Data')}</a></li>
			    <li><a href="#dropTable" data-toggle="modal">${_('Drop')} ${view_or_table_noun}</a></li>
			    <li><a href="${hdfs_link}" rel="${ table.sd.location }">${_('View File Location')}</a></li>
				</ul>
			</div>
      <div id="jumpToColumnAlert" class="alert hide">
        <button type="button" class="close" data-dismiss="alert">&times;</button>
        <strong>${_('Did you know?')}</strong> ${_('You can click on a row to select a column you want to jump to.')}
      </div>
		</div>
		<div class="span9">
			% if table.parameters.get("comment", False):
		    <h5>${ table.parameters.get("comment") }</h5>
			% endif

			<ul class="nav nav-tabs">
				<li class="active"><a href="#columns" data-toggle="tab">${_('Columns')}</a></li>
		        % if len(table.partitionKeys) > 0:
					<li><a href="#partitionColumns" data-toggle="tab">${_('Partition Columns')}</a></li>
		        % endif
				% if top_rows is not None:
					<li><a href="#sample" data-toggle="tab">${_('Sample')}</a></li>
				% endif
			</ul>

			<div class="tab-content">
				<div class="active tab-pane" id="columns">
					${column_table(table.sd.cols)}
				</div>
		        % if len(table.partitionKeys) > 0:
		          <div class="tab-pane" id="partitionColumns">
		            ${column_table(table.partitionKeys)}
		            <a href="${ url("beeswax.views.describe_partitions", table=table_name) }">${_('Show Partitions')}</a>
		          </div>
		        % endif
				% if top_rows is not None:
					<div class="tab-pane" id="sample">
						<table class="table table-striped table-condensed sampleTable">
			              <thead>
			                <tr>
			                  % for col in table.sd.cols:
			                    <th style="white-space: nowrap">${col.name}</th>
			                  % endfor
			                </tr>
			              </thead>
			              <tbody>
			                % for i, row in enumerate(top_rows):
			                  <tr>
			                    % for item in row:
			                      <td style="white-space: nowrap">${ item }</td>
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
	<form id="dropTableForm" method="POST" action="${ url("beeswax.views.drop_table", table=table_name) }">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>${_('Drop Table')}</h3>
	</div>
	<div class="modal-body">
	  <div id="dropTableMessage" class="alert">

	  </div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="${_('Yes')}"/>
		<a href="#" class="btn secondary hideModal">${_('No')}</a>
	</div>
	</form>
</div>



<div id="importData" class="modal hide fade">
	<form method="POST" action="${ url("beeswax.views.load_table", table=table_name) }" class="form-stacked">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>${_('Import data')}</h3>
	</div>
	<div class="modal-body">
	  <div class="alert">
	        <p>${_("Note that loading data will move data from its location into the table's storage location.")}</p>
	  </div>



	  <div class="clearfix">
	  ${comps.label(load_form["path"], title_klass='loadPath', attrs=dict(
        ))}
    	<div class="input">
		     ${comps.field(load_form["path"], title_klass='loadPath', attrs=dict(
		       klass='loadPath input-xlarge'
		       ))}
		</div>
		</div>

      % for pf in load_form.partition_columns:
		<div class="clearfix">
			${comps.label(load_form[pf], render_default=True)}
	    	<div class="input">
	        	${comps.field(load_form[pf], render_default=True, attrs=dict(
			       klass='input-xlarge'
			       ))}
			</div>
		</div>

      % endfor

		<div class="clearfix">
			<div class="input">
				<input type="checkbox" name="overwrite"/> ${_('Overwrite existing data')}
			</div>
		</div>


	<div id="filechooser">
	</div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="${_('Submit')}"/>
		<a href="#" class="btn secondary" data-dismiss="modal">${_('Cancel')}</a>
	</div>
	</form>
</div>
</div>
<style>
    #filechooser {
        display:none;
        min-height:100px;
        overflow-y:scroll;
        margin-top:10px;
    }

    .sampleTable td, .sampleTable th {
      white-space: nowrap;
    }
</style>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $("#filechooser").jHueFileChooser({
            initialPath: $(".loadPath").val(),
            onFileChoose: function(filePath){
                $(".loadPath").val(filePath);
                $("#filechooser").slideUp();
            },
            createFolder: false
        });
        $(".datatables").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bFilter": false
        });

        $.getJSON("${ url("beeswax.views.drop_table", table=table_name) }",function(data){
            $("#dropTableMessage").text(data.title);
        });
        $(".hideModal").click(function(){
            $(this).closest(".modal").modal("hide");
        });
        $(".loadPath").click(function(){
            $("#filechooser").slideDown();
        });

      $('a[data-toggle="tab"]').on('shown', function () {
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
          }
        });
      })


    });
</script>

${commonfooter(messages)}
