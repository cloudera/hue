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
from desktop import conf
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_("Create table manually"), 'metastore', user, request) | n,unicode }

<span class="notebook">
${ layout.metastore_menubar() }

<script src="${ static('metastore/js/metastore.ko.js') }"></script>

${ assist.assistJSModels() }

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<link rel="stylesheet" href="${ static('notebook/css/notebook-layout.css') }">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>

${ assist.assistPanel() }

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>

<div class="main-content">
  <div class="vertical-full container-fluid" data-bind="style: { 'padding-left' : $root.isLeftPanelVisible() ? '0' : '20px' }">
    <div class="vertical-full">
      <div class="vertical-full row-fluid panel-container">

        <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
          <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                user: '${user.username}',
                sql: {
                  navigationSettings: {
                    openItem: false,
                    showStats: true
                  }
                },
                visibleAssistPanels: ['sql']
              }
            }"></div>
        </div>
        <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>

        <div class="content-panel">

          <div class="metastore-main">

            <h3>
              <div class="inline-block pull-right" style="margin-top: -8px">
                <a href="${ url('beeswax:import_wizard', database=database) }" title="${_('Create a new table from a file')}" class="inactive-action"><span class="fa-stack fa-fw" style="width: 1.28571429em"><i class="fa fa-file-o fa-stack-1x"></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 5px; margin-top: 6px;"></i></span></a>
              </div>
              <ul id="breadcrumbs" class="nav nav-pills hue-breadcrumbs-bar">
                <li>
                  <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
                </li>
                <li>
                  <a href="${ url('metastore:show_tables', database=database) }">${database}</a><span class="divider">&gt;</span>
                </li>
                <li>
                    <span style="padding-left:12px">${_('Create a new table manually')}</span>
                </li>
              </ul>
            </h3>

            <ul class="nav nav-pills">
              <li class="active"><a href="#step1" class="step">${_('Step 1: Name')}</a></li>
              <li><a href="#step2" class="step">${_('Step 2: Record Format')}</a></li>
              <li><a href="#step3" class="step">${_('Step 3: Serialization')}</a></li>
              <li><a href="#step4" class="step">${_('Step 4: File Format')}</a></li>
              <li><a href="#step5" class="step">${_('Step 5: Location')}</a></li>
              <li><a href="#step6" class="step">${_('Step 6: Columns')}</a></li>
            </ul>

            <form action="#" method="POST" id="mainForm" class="form-horizontal">
              ${ csrf_token(request) | n,unicode }
              <div class="steps">

                <div id="step1" class="stepDetails">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Create a table')}</h3>${_("Let's start with a name and description for where we'll store your data.")}</div>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["name"])}
                            <div class="controls">
                                ${comps.field(table_form["name"], attrs=dict(
                                    placeholder=_('table_name'),
                                  )
                                )}
                                <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                <p class="help-block muted">
                                    ${_('Name of the new table. Table names must be globally unique. Table names tend to correspond to the directory where the data will be stored.')}
                                </p>
                            </div>
                        </div>
                        <div class="control-group">
                            ${comps.bootstrapLabel(table_form["comment"])}
                            <div class="controls">
                                ${comps.field(table_form["comment"], attrs=dict(
                                  placeholder=_('Optional'),
                                  )
                                )}
                                <p class="help-block muted">
                                    ${_("Use a table comment to describe your table.  For example, note the data's provenance and any caveats users need to know.")}
                                </p>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step2" class="stepDetails hide">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Choose Your Record Format')}</h3>
                            ${_("Individual records are broken up into columns either with delimiters (e.g., CSV or TSV) or using a specific serialization/deserialization (SerDe) implementation. (One common specialized SerDe is for parsing out columns with a regular expression.)")}
                        </div>
                        <%
                            selected = table_form["row_format"].data or table_form["row_format"].field.initial
                        %>
                        <div class="control-group">
                            <label class="control-label" id="formatRadio">${_('Record format')}</label>
                            <div class="controls">
                                <label class="radio">
                                    <input type="radio" name="table-row_format" value="Delimited"
                                        % if selected == "Delimited":
                                           checked
                                        % endif
                                            >
                                    ${_('Delimited')}
                                    <span class="help-block muted">
                                    ${_('(Data files use delimiters, like commas (CSV) or tabs.)')}
                                    </span>
                                </label>
                                <label class="radio">
                                    <input type="radio" name="table-row_format" value="SerDe"
                                        % if selected == "SerDe":
                                           checked
                                        % endif
                                            >
                                    ${_('SerDe')}
                                    <span class="help-block muted">
                                    ${_('(Enter a specialized serialization implementation.)')}
                                    </span>
                                </label>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step3" class="stepDetails hide">
                    <fieldset>
                        <div id="step3Delimited" class="stepDetailsInner">
                            <div class="alert alert-info"><h3>${_('Configure Record Serialization')}</h3>
                                ${_('Only supports single-character delimiters.')}
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["field_terminator"])}
                                <div class="controls">
                                    ${comps.field(table_form["field_terminator"], render_default=True)}
                                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                    <span class="help-block muted">
                                        ${_('Enter the column delimiter. Must be a single character. Use syntax like "\\001" or "\\t" for special characters.')}
                                    </span>
                                </div>
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["collection_terminator"])}
                                <div class="controls">
                                    ${comps.field(table_form["collection_terminator"], render_default=True)}
                                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                    <span class="help-block muted">
                                        ${_('Use for array types.')}
                                    </span>
                                </div>
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["map_key_terminator"])}
                                <div class="controls">
                                    ${comps.field(table_form["map_key_terminator"], render_default=True)}
                                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                    <span class="help-block muted">
                                        ${_('Use for map types.')}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div id="step3SerDe" class="hide stepDetailsInner">
                            <div class="alert alert-info"><h3>${_('Configure Record Serialization')}</h3>
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["serde_name"])}
                                <div class="controls">
                                    ${comps.field(table_form["serde_name"], attrs=dict(
                                    placeholder='com.acme.hive.SerDe',
                                    )
                                    )}
                                    <span class="help-block muted">
                                        ${_('The Java class name of your SerDe.')} <em>${_('e.g.')}</em>, org.apache.hadoop.hive.contrib.serde2.RegexSerDe
                                    </span>
                                </div>
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["serde_properties"])}
                                <div class="controls">
                                    ${comps.field(table_form["serde_properties"], attrs=dict(
                                    placeholder='"prop" = "value", "prop2" = "value2"',
                                    )
                                    )}
                                    <span class="help-block muted">
                                        ${_('Properties to pass to the (de)serialization mechanism.')} <em>${_('e.g.')},</em>, "input.regex" = "([^ ]*) ([^ ]*) ([^ ]*) (-|\\[[^\\]]*\\]) ([^ \"]*|\"[^\"]*\") (-|[0-9]*) (-|[0-9]*)(?: ([^ \"]*|\"[^\"]*\") ([^ \"]*|\"[^\"]*\"))?", "output.format.string" = "%1$s %2$s %3$s %4$s %5$s %6$s %7$s %8$s %9$s"
                                    </span>
                                </div>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step4" class="stepDetails hide">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Choose a File Format')}</h3>
                            ${_('Use')} <strong>TextFile</strong> ${_('for newline-delimited text files.')}
                            ${_('Use')} <strong>SequenceFile</strong> ${_("for Hadoop's binary serialization format.")}
                            ${_('Use')} <strong>InputFormat</strong> ${_('to choose a custom implementation.')}
                            <br/>
                        </div>

                        <div class="control-group">
                            <label id="fileFormatRadio" class="control-label">${_('File format')}</label>
                            <div class="controls">
                                ${comps.field(table_form["file_format"],
                                render_default=True,
                                klass="bw-file_formats",
                                notitle=True
                                )}
                            </div>
                        </div>
                        <div id="inputFormatDetails" class="hide">
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["input_format_class"])}
                                <div class="controls">
                                    ${comps.field(table_form["input_format_class"], attrs=dict(
                                    placeholder='com.acme.data.MyInputFormat',
                                    )
                                    )}
                                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                    <span class="help-block muted">
                                        ${_('Java class used to read data.')}
                                    </span>
                                </div>
                            </div>
                            <div class="control-group">
                                ${comps.bootstrapLabel(table_form["output_format_class"])}
                                <div class="controls">
                                    ${comps.field(table_form["output_format_class"], attrs=dict(
                                    placeholder='com.acme.data.MyOutputFormat',
                                    )
                                    )}
                                    <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                                    <span class="help-block muted">
                                        ${_('Java class used to write data.')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step5" class="stepDetails hide">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_("Choose Where Your Table's Data is Stored")}</h3>
                        </div>
                        <div class="control-group">
                            <label class="control-label">${_('Location')}</label>
                            <div class="controls">
                                <label class="checkbox">
                                    ${comps.field(table_form["use_default_location"],
                                    render_default=True
                                    )}
                                    ${_('Use default location')}
                                </label>
                                <span class="help-block muted">
                                    ${_('Store your table in the default location (controlled by Hive, and typically')} <em>/user/hive/warehouse/table_name</em>).
                                </span>
                            </div>
                        </div>

                        <div id="location" class="control-group hide">
                            ${comps.bootstrapLabel(table_form["external_location"])}
                            <div class="controls">
                                ${comps.field(table_form["external_location"],
                                placeholder="/user/user_name/data_dir",
                                klass="pathChooser input-xxlarge",
                                file_chooser=True,
                                show_errors=False
                                )}
                                <span class="help-block muted">
                                ${_("Enter the path (on HDFS) to your table's data location")}
                                </span>
                            </div>
                        </div>
                    </fieldset>
                </div>

                <div id="step6" class="stepDetails hide">
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Configure Table Columns')}</h3>
                        </div>
                        <div class="control-group">
                            <label class="control-label">${_('Table Properties')}</label>
                            <div class="controls">
                                <label class="checkbox">
                                    ${comps.field(table_form["skip_header"],
                                    render_default=True
                                    )}
                                    ${_('Skip Header Row?')}
                                </label>
                            </div>
                        </div>
                        % for form in columns_form.forms:
                            ${render_column(form)}
                        %endfor
                        <div class="hide">
                            ${unicode(columns_form.management_form) | n}
                        </div>
                        <button class="btn addColumnBtn" value="True" name="columns-add" type="submit">${_('Add a column')}</button>
                    </fieldset>
                    <br/><br/>
                    <fieldset>
                        <div class="alert alert-info"><h3>${_('Configure Partitions')}</h3>
                            ${_('If your data is naturally partitioned (by date, for example), partitions are a way to tell the query server that data for a specific partition value are stored together.')}
                            ${_('The query server establishes a mapping between directories on disk')}
                            (<em>${_('e.g.')},</em> <code>/user/hive/warehouse/logs/dt=20100101/</code>)
                            ${_('and the data for that day.  Partitions are virtual columns; they are not represented in the data itself, but are determined by the data location. The query server implements query optimizations such that queries that are specific to a single partition need not read the data in other partitions.')}
                        </div>
                        % for form in partitions_form.forms:
                            ${render_column(form, True)}
                        % endfor
                        <div class="hide">
                            ${unicode(partitions_form.management_form) | n}
                        </div>
                        <button class="btn addPartitionBtn" value="True" name="partitions-add" type="submit">${_('Add a partition')}</button>
                    </fieldset>
                </div>
              </div>
              <div class="form-actions" style="padding-left: 0">
                  <button type="button" id="backBtn" class="btn hide">${_('Back')}</button>
                  <button type="button" id="nextBtn" class="btn btn-primary">${_('Next')}</button>
                  <input id="submit" type="submit" name="create" class="btn btn-primary hide" value="${_('Create table')}" />
              </div>
            </form>


          </div>

        </div>
      </div>
    </div>
  </div>
</div>


<%def name="render_column(form, is_partition_form=False)">
    <div class="cnt well">
        <div class="remove">
        ${comps.field(form['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
        type="submit",
        title=_("Delete this column"),
        klass="btn btn-small removeBtn"
        ), value=True)}
        </div>
        <div class="control-group">
            <label class="control-label">${_('Column name')}</label>
            <div class="controls">
                <input class="column input input-large" name="${form["column_name"].html_name | n}" value="${form["column_name"].data or ''}" placeholder="${_('Column Name')}"/>
                % if form["column_name"].errors:
                  <span class="help-inline error-inline">${ form["column_name"].errors.as_text() }</span>
                % endif
                <span  class="help-inline error-inline hide">${_('This field is required. Spaces are not allowed.')}</span>
                <span  class="help-inline error-inline error-inline-bis hide">${_('There is another field with the same name.')}</span>
                <span class="help-block muted">
                ${_('Column name must be single words that start with a letter or a digit.')}
                </span>
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">${_('Column type')}</label>
            <div class="controls columnType">
            ${comps.field(form["column_type"],
            render_default=True
            )}
            <span class="help-block muted">
            ${_('Type for this column. Certain advanced types (namely, structs) are not exposed in this interface.')}
            </span>
            </div>
        </div>
        % if is_partition_form == False:
                <div class="arraySpec hide">
                    <div class="control-group">
                        <label class="control-label">${_('Array value type')}</label>
                        <div class="controls">
                        ${comps.field(form["array_type"], render_default=True)}
                            <span class="help-block muted">
                            ${_('Type of the array values.')}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="mapSpec hide">
                    <div class="control-group">
                        <label class="control-label">${_('Map Key type')}</label>
                        <div class="controls">
                        ${comps.field(form["map_key_type"], render_default=True)}
                            <span class="help-block muted">
                            ${_('Type of the map keys.')}
                            </span>
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label">${_('Map Value type')}</label>
                        <div class="controls">
                        ${comps.field(form["map_value_type"], render_default=True)}
                            <span class="help-block muted">
                            ${_('Type of the map values.')}
                            </span>
                        </div>
                    </div>
                </div>
        % endif
        <div class="charSpec hide">
            <div class="control-group">
                <label class="control-label">${_('Size')}</label>
                <div class="controls">
                ${comps.field(form["char_length"], render_default=True)}
                    <span class="help-block muted">
                    ${_("Length of char value (1~255)")}
                    </span>
                </div>
            </div>
        </div>
        <div class="varcharSpec hide">
            <div class="control-group">
                <label class="control-label">${_('Size')}</label>
                <div class="controls">
                ${comps.field(form["varchar_length"], render_default=True)}
                    <span class="help-block muted">
                    ${_("Length of varchar value (1~65355)")}
                    </span>
                </div>
            </div>
        </div>

    ${unicode(form["_exists"]) | n}

    </div>

</%def>




<style type="text/css">
  #filechooser {
    min-height: 100px;
    overflow-y: auto;
    margin-top: 10px;
    height: 250px;
  }

  .inputs-list {
    list-style: none outside none;
    margin-left: 0;
  }

  .remove {
    float: right;
  }

  .error-inline {
    color: #B94A48;
    font-weight: bold;
  }

  .steps {
    min-height: 350px;
    margin-top: 10px;
  }

  div .alert {
    margin-bottom: 30px;
  }

  .cnt.well {
    border: none;
  }

  .cnt.well:hover {
    background-color: #F0F0F0;
  }

  .help-block.muted, .help-inline.muted  {
    color: #999;
  }
</style>

</div>


<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function CreateTableViewModel() {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name  + '?source=' + tableDef.sourceType + '&namespace=' + tableDef.namespace.id;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name + '?source=' + databaseDef.sourceType + '&namespace=' + databaseDef.namespace.id;
      });
    }

    $(document).ready(function () {

      var viewModel = new CreateTableViewModel();

      ko.applyBindings(viewModel);

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }

      if ($(".removeBtn").length == 1) {
        $(".removeBtn").first().hide();
      }

      $(".fileChooserBtn").click(function (e) {
        e.preventDefault();
        var _destination = $(this).attr("data-filechooser-destination");
        $("#filechooser").jHueFileChooser({
          initialPath: $("input[name='" + _destination + "']").val(),
          onFolderChoose: function (filePath) {
            $("input[name='" + _destination + "']").val(filePath);
            $("#chooseFile").modal("hide");
          },
          createFolder: false,
          selectFolder: true,
          uploadFile: false
        });
        $("#chooseFile").modal("show");
      });

      $(".step").click(function (event) {
        event.preventDefault();
        if (validateForm()) {
          $(".stepDetails").hide();
          var _step = $(this).attr("href");
          $(_step).css("visibility", "visible").show();
          $("#backBtn").hide();
          if (_step != "#step1") {
            $("#backBtn").css("visibility", "visible").show();
          }
          if (_step != "#step6") {
            $("#nextBtn").show();
            $("#submit").hide();
          }
          else {
            $("#nextBtn").hide();
            $("#submit").css("visibility", "visible").show();
          }
          $(".step").parent().removeClass("active");
          $(this).parent().addClass("active");
        }
      });

      $("#nextBtn").click(function () {
        $("ul.nav-pills li.active").next().find("a").click();
      });

      $("#backBtn").click(function () {
        $("ul.nav-pills li.active").prev().find("a").click();
      });

      $("#submit").click(function (event) {
        // validate step 6
        if (!validateStep6()) {
          event.preventDefault();
        }
      });

      var _url = location.href;
      if (_url.indexOf("#") > -1) {
        $(".step[href='" + _url.substring(_url.indexOf("#"), _url.length) + "']").click();
      }

      $("#id_table-field_terminator_1").css("margin-left", "4px").attr("placeholder", "${_('Type your field terminator here')}").hide();
      $("#id_table-field_terminator_0").change(function () {
        if ($(this).val() == "__other__") {
          $("#id_table-field_terminator_1").show();
        }
        else {
          $("#id_table-field_terminator_1").hide().nextAll(".error-inline").addClass("hide");
        }
      });
      $("#id_table-collection_terminator_1").css("margin-left", "4px").attr("placeholder", "${_('Type your collection terminator here')}").hide();
      $("#id_table-collection_terminator_0").change(function () {
        if ($(this).val() == "__other__") {
          $("#id_table-collection_terminator_1").show();
        }
        else {
          $("#id_table-collection_terminator_1").hide().nextAll(".error-inline").addClass("hide");
        }
      });
      $("#id_table-map_key_terminator_1").css("margin-left", "4px").attr("placeholder", "${_('Type your map key terminator here')}").hide();
      $("#id_table-map_key_terminator_0").change(function () {
        if ($(this).val() == "__other__") {
          $("#id_table-map_key_terminator_1").show();
        }
        else {
          $("#id_table-map_key_terminator_1").hide().nextAll(".error-inline").addClass("hide");
        }
      });

      // fire the event on page load
      $("#id_table-field_terminator_0").change();
      $("#id_table-collection_terminator_0").change();
      $("#id_table-map_key_terminator_0").change();

      // show the first validation error if any
      if ($(".errorlist").length > 0) {
        $(".step[href='#" + $(".errorlist").eq(0).closest(".stepDetails").attr("id") + "']").click();
      }

      $("input[name='table-row_format']").change(function () {
        $(".stepDetailsInner").hide();
        $("#step3" + $(this).val()).show();
      });

      $("input[name='table-file_format']").change(function () {
        $("#inputFormatDetails").hide();
        if ($(this).val() == "InputFormat") {
          $("#inputFormatDetails").slideDown();
        }
      });

      $("#id_table-use_default_location").change(function () {
        if (!$(this).is(":checked")) {
          $("#location").slideDown();
        }
        else {
          $("#location").slideUp();
        }
      });


      $("#step6").find("button").click(function () {
        $("#mainForm").attr("action", "#step6");
      });

      $(".columnType").find("select").change(function () {
        $(this).parents(".cnt").find(".arraySpec").hide();
        $(this).parents(".cnt").find(".mapSpec").hide();
        $(this).parents(".cnt").find(".charSpec").hide();
        $(this).parents(".cnt").find(".varcharSpec").hide();

        if ($(this).val() == "array") {
          $(this).parents(".cnt").find(".arraySpec").show();
        }
        if ($(this).val() == "map") {
          $(this).parents(".cnt").find(".mapSpec").show();
        }
        if ($(this).val() == "char") {
          $(this).parents(".cnt").find(".charSpec").show();
        }
        if ($(this).val() == "varchar") {
          $(this).parents(".cnt").find(".varcharSpec").show();
        }
      });
      // to show spec forms after clicking "Add a column" button
      $(".columnType").find("select").trigger("change");

      $("#step4").find("ul").addClass("inputs-list");

      $(".addColumnBtn, .addPartitionBtn").click(function (e) {
        if (!validateStep6()) {
          e.preventDefault();
        }
      });

      function validateStep6() {
        var scrollTo = 0;
        // step 6
        var step6Valid = true;
        $(".column").each(function () {
          var _field = $(this);
          if (!isValid($.trim(_field.val()))) {
            showFieldError(_field);
            if (scrollTo == 0) {
              scrollTo = $(this).offset().top + $('.content-panel').scrollTop() - 150;
            }
            step6Valid = false;
          }
          else {
            hideFieldError(_field);
          }
          var _lastSecondErrorField = null;
          $(".column").not("[name='" + _field.attr("name") + "']").each(function () {
            if ($.trim($(this).val()) != "" && $.trim($(this).val()) == $.trim(_field.val())) {
              _lastSecondErrorField = $(this);
              if (scrollTo == 0) {
                scrollTo = _field.offset().top + $('.content-panel').scrollTop() - 150;
              }
              step6Valid = false;
            }
          });
          if (_lastSecondErrorField != null) {
            showSecondFieldError(_lastSecondErrorField);
          }
          else {
            hideSecondFieldError(_field);
          }
        });
        if (!step6Valid && scrollTo > 0) {
          $('.content-panel').animate({
            'scrollTop' : scrollTo
          }, 500);
        }
        return step6Valid;
      }

      function validateForm() {
        // step 1
        var tableNameFld = $("input[name='table-name']");
        if (!isValid($.trim(tableNameFld.val())) || !withoutSpaces($.trim(tableNameFld.val()))) {
          showFieldError(tableNameFld);
          return false;
        }
        else {
          hideFieldError(tableNameFld);
        }

        // step 3
        var step3Valid = true;
        var fieldTerminatorFld = $("#id_table-field_terminator_1");
        if ($("#id_table-field_terminator_0").val() == "__other__" && !isValid($.trim(fieldTerminatorFld.val()))) {
          showFieldError(fieldTerminatorFld);
          step3Valid = false;
        }
        else {
          hideFieldError(fieldTerminatorFld);
        }

        var collectionTerminatorFld = $("#id_table-collection_terminator_1");
        if ($("#id_table-collection_terminator_0").val() == "__other__" && !isValid($.trim(collectionTerminatorFld.val()))) {
          showFieldError(collectionTerminatorFld);
          step3Valid = false;
        }
        else {
          hideFieldError(collectionTerminatorFld);
        }

        var mapKeyTerminatorFld = $("#id_table-map_key_terminator_1");
        if ($("#id_table-map_key_terminator_0").val() == "__other__" && !isValid($.trim(mapKeyTerminatorFld.val()))) {
          showFieldError(mapKeyTerminatorFld);
          step3Valid = false;
        }
        else {
          hideFieldError(mapKeyTerminatorFld);
        }
        if (!step3Valid) {
          return false;
        }

        // step 4
        var step4Valid = true;
        if ($("input[name='table-file_format']:checked").val() == "InputFormat") {
          var inputFormatFld = $("input[name='table-input_format_class']");
          if (!isValid($.trim(inputFormatFld.val()))) {
            showFieldError(inputFormatFld);
            step4Valid = false;
          }
          else {
            hideFieldError(inputFormatFld);
          }

          var outputFormatFld = $("input[name='table-output_format_class']");
          if (!isValid($.trim(outputFormatFld.val()))) {
            showFieldError(outputFormatFld);
            step4Valid = false;
          }
          else {
            hideFieldError(outputFormatFld);
          }
        }
        if (!step4Valid) {
          return false;
        }

        // step 5
        var tableExternalLocationFld = $("input[name='table-external_location']");
        if (!($("#id_table-use_default_location").is(":checked"))) {
          if (!isValid($.trim(tableExternalLocationFld.val()))) {
            showFieldError(tableExternalLocationFld);
            return false;
          }
          else {
            hideFieldError(tableExternalLocationFld);
          }
        }

        return true;
      }

      function isValid(str) {
        // validates against empty string
        return (str != "");
      }

      function withoutSpaces(str) {
        return (str.indexOf(" ") == -1);
      }

      function showFieldError(field) {
        field.nextAll(".error-inline").not(".error-inline-bis").removeClass("hide");
      }

      function showSecondFieldError(field) {
        field.nextAll(".error-inline-bis").removeClass("hide");
      }

      function hideFieldError(field) {
        if (!(field.nextAll(".error-inline").hasClass("hide"))) {
          field.nextAll(".error-inline").addClass("hide");
        }
      }

      function hideSecondFieldError(field) {
        if (!(field.nextAll(".error-inline-bis").hasClass("hide"))) {
          field.nextAll(".error-inline-bis").addClass("hide");
        }
      }
    });
  })();
</script>

</span>
${ commonfooter(request, messages) | n,unicode }
