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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head('Create a Table', toolbar=has_tables, section='new table')}
<div class="toolbar">
  <ul class="ccs-bc-form ccs-breadcrumb clearfix" data-bc-sections=".ccs-bc-section" data-bc-form="form">
    <li><a href="#step1">Name</a></li>
    <li><a href="#step2">Record Format</a></li>
    <li><a href="#step3">Serialization</a></li>
    <li><a href="#step4">File Format</a></li>
    <li><a href="#step5">Location</a></li>
    <li><a href="#step6">Columns</a></li>
  </ul>
</div>
<div id="table-setup" class="view">
  <form action="#" method="POST" class="jframe_padded form-validator">
    <dl class="bw-table-setup">

  <div class="ccs-bc-section">
        <a name="step1"></a>
        <dt>Step 1: Create Your Table</dt>
        <dd>
          <p>Let's start with a name and description for where we'll store your data.</p>
          <dl class="clearfix">
            ${comps.field(table_form["name"], attrs=dict(
                klass='required bw-validate-name',
                data_filters="OverText",
                alt='table_name',
              ),
              help="Name of the new table.  Table names must be globally unique.  Table names tend to correspond as well to the directory where the data will be stored.",
              help_attrs=dict(
                data_help_direction='1'
              )
            )}
            ${comps.field(table_form["comment"], attrs=dict(
                klass='bw-table-comment',
                data_filters="OverText",
                alt='Optional'
              ),
              help="Use a table comment to describe your table.  For example, you might mention the data's provenance, and any caveats users of this table should expect.")}
          </dl>
          <a href="#step2" class="ccs-multipart-next">Step 2: Choose Your Record Format &raquo;</a>
        </dd>
      </div>

      <div class="ccs-bc-section">
        <a name="step2"></a>
        <dt>Step 2: Choose Your Record Format</dt>
        <dd>
          <p>Individual records are broken up into columns
          either with delimiters (e.g., CSV or TSV) or using
          a specific serialization / deserialization (SerDe) implementation.
          (One common specialized SerDe is for parsing out columns with a regular
          expression.)
          </p>
          <dl class="bw-format">
            <% 
              selected = table_form["row_format"].data or table_form["row_format"].field.initial
            %>
            <dt class="bw-format-delimited relays" data-group-toggle="{'group': '.bw-config-data li', 'show':'.bw-delim-options'}">
              <label>
                Delimited
                <input type="radio" name="table-row_format" value="Delimited" class="validate-one-required:'.bw-format'" title="Please choose one of these record formats." data-error-container=''
                  % if selected == "Delimited":
                    checked
                  % endif
                >
              </label>
              <div class="ccs-errors"></div>
            </dt>
            <dd>Data files use delimiters, like commas (CSV) or tabs.</dd>
            <dt class="bw-format-SerDe relays" data-group-toggle="{'group': '.bw-config-data li', 'show':'.bw-serde-options'}">
              <label>
                SerDe
                <input type="radio" name="table-row_format" value="SerDe"
                  % if selected == "SerDe":
                    checked
                  % endif
                >
              </label>
            </dt>
            <dd>Enter a specialized serialization implementation.</dd>
          </dl>
          <a href="#step3" class="ccs-multipart-next">Step 3: Configure Record Serialization &raquo;</a>
        </dd>
      </div>

      <div class="ccs-bc-section">
        <a name="step3"></a>
        <dt>Step 3: Configure Record Serialization</dt>
        <dd>
          <ul class="bw-config-data">
            <li class="bw-delim-options">
              <p class="ccs-hidden">If your records are delimited, please configure these fields:</p>
              Hive only supports single-character delimiters.
              <dl>
                ${comps.field(table_form["field_terminator"], render_default=True, help=r'Enter the column delimiter.  Must be a single character.  Use syntax like "\001" or "\t" for special characters.', klass="ccs-select-with-other")}
                ${comps.field(table_form["collection_terminator"], render_default=True, help="Use for array types.", klass="ccs-select-with-other")}
                ${comps.field(table_form["map_key_terminator"], render_default=True, help="Use for map types.", klass="ccs-select-with-other")}
              </dl>
            </li>
            <li class="bw-serde-options">
              <p class="ccs-hidden">If you're using SerDe data, please configure these fields:</p>
              <dl>
                ${comps.field(table_form["serde_name"],
                  help="Enter the Java Classname of your SerDe. <em>e.g.</em>, org.apache.hadoop.hive.contrib.serde2.RegexSerDe",
                  attrs=dict(
                    klass='required',
                    data_filters="OverText",
                    alt='com.acme.hive.SerDe',
                  )
                )}
                <%!
                  help=r'Properties to pass to the (de)serialization mechanism. <em>e.g.,</em>, "input.regex" = "([^ ]*) ([^ ]*) ([^ ]*) (-|\\[[^\\]]*\\]) ([^ \"]*|\"[^\"]*\") (-|[0-9]*) (-|[0-9]*)(?: ([^ \"]*|\"[^\"]*\") ([^ \"]*|\"[^\"]*\"))?", "output.format.string" = "%1$s %2$s %3$s %4$s %5$s %6$s %7$s %8$s %9$s"'
                %>

                ${comps.field(table_form["serde_properties"],
                  help=help,
                  attrs=dict(
                    data_filters="OverText",
                    alt=r'"prop" = "value", "prop2" = "value2"'
                  )
                )}
              </dl>
            </li>
          </ul>
          <a href="#step4" class="ccs-multipart-next">Step 4: Choose a File Format &raquo;</a>
        </dd>
      </div>

      <div class="ccs-bc-section">
        <a name="step4"></a>
        <dt>Step 4: Choose a File Format</dt>
        <dd>
          <ul>
            <li>Use TextFile for newline-delimited text files.</li>
            <li>Use SequenceFile for Hadoop's binary serialization format.</li>
            <li>Use InputFormat to choose a custom implementation.</li>
          </ul>
          <dl>
            ${comps.field(table_form["file_format"],
              render_default=True, 
              klass="bw-file_formats",
              notitle=True
            )}
            <div class="ccs-hidden bw-io_formats">
              ${comps.field(table_form["input_format_class"],
                help="Java Class to read data",
                attrs=dict(
                  data_filters="OverText",
                  alt='com.acme.data.MyInputFormat'
                )
              )}
              ${comps.field(table_form["output_format_class"],
                help="Java Class used to write data",
                attrs=dict(
                  data_filters="OverText",
                  alt='com.acme.data.MyOutputFormat'
                )
              )}
            </div>
          </dl>
          <a href="#step5" class="ccs-multipart-next">Step 5: Choose Where To Save Your Table &raquo;</a>
        </dd>
      </div>

      <div class="ccs-bc-section">
        <a name="step5"></a>
        <dt>Step 5: Choose Where Your Table's Data is Stored</dt>
        <dd class="bw-file_location">
          <dl>
            <div class="bw-default_location">
              ${comps.field(table_form["use_default_location"],
                render_default=True, 
                help="Store your table in the default location (controlled by Hive, and typically <code>/user/hive/warehouse/table_name</code>)."
              )}
            </div>
            <div class="bw-external_loc ccs-hidden">
              ${comps.field(table_form["external_location"],
                help="Enter the path (on HDFS) to your table's data location",
                attrs=dict(
                  klass='required',
                  data_filters="OverText",
                  alt='/user/user_name/data_dir'
                )
              )}<a class="ccs-choose_file ccs-art_button" data-icon-styles="{'width': 16, 'height': 16, 'top': 3, 'left': 6 }" data-chooseFor="table-external_location">Choose File</a>
            </div>
          </dl>
          <a href="#step6" class="ccs-multipart-next">Final Step: Configure Table Columns &raquo;</a>
        </dd>
      </div>

      <div class="ccs-bc-section">
        <a name="step6"></a>
        <dt>Final Step: Configure Table Columns</dt>
        <dd>
          <dl class="bw-columns">
            <%def name="render_column(form, is_partition_form=False)">
              <div class="bw-column">
                <dt class="bw-column_header bw-inactive">
                  <input name="${form["column_name"].html_name | n}" value="${form["column_name"].data or ''}" class="required bw-column_name" alt="Column Name" data-filters="OverText"/>
                  <p class="ccs-help_text" data-help-direction="1">
                    Column name must be single words that start
                    with a letter or a digit.
                  </p>
                  <div class="bw-remove_column">
                    ${str(form["_deleted"]) | n}
                  </div>
                </dt>
                <dd class="bw-column">
                  <dl>
                    <div class="bw-col_type ccs-inline">
                      ${comps.field(form["column_type"],
                        render_default=True,
                        help="Type for this column.  Certain advanced types (namely, structs) are not exposed in this interface.",
                        help_attrs=dict(
                          data_help_direction='12'
                        )
                      )}
                    </div>
                    % if is_partition_form == False: 
                      <div class="bw-array_type ccs-inline">
                        ${comps.field(
                            form["array_type"],
                            render_default=True,
                            help="Type of the array values.",
                          )}
                      </div>
                      <div class="bw-map_data">
                        <div class="bw-map_key_type ccs-inline">
                          ${comps.field(form["map_key_type"], render_default=True, help="Type of the map keys.")}
                        </div>
                        <div class="bw-map_value_type ccs-inline">
                          ${comps.field(form["map_value_type"], render_default=True, help="Type of the map values.")}
                        </div>
                      </div>
                    % endif
                    ${str(form["_exists"]) | n}
                    
                  </dl>
                </dd>
              </div>
            </%def>
            <div class="bw-column-forms">
              <p>Configure the columns of your table.</p>
              % for form in columns_form.forms:
                ${render_column(form)}
              %endfor
            </div>
            <div class="bw-add_column">
              ${str(columns_form.management_form) | n}
            </div>
            <h2>Partitions</h2>
              ## See http://wiki.apache.org/hadoop/Hive/Tutorial
              <p>
              If your data is naturally partitioned (by, say, date),
              partitions are a way to tell Hive that data
              for a specific partition value are stored together.
              Hive establishes a mapping between directories on disk
              (<em>e.g.,</em> <code>/user/hive/warehouse/logs/dt=20100101/</code>)
              and the data for that day.  Partitions are virtual
              columns; they are not represented in the data themselves,
              but are determined by the data location.  Hive implements
              query optimizations such that queries that are specific
              to a single partition need not read the data in other partitions.
              </p>
              <div class="bw-partition-forms">
                % for form in partitions_form.forms:
                  ${render_column(form, True)}
                % endfor
              </div>
              <div class="bw-add_partition bw-add_column">
                ${str(partitions_form.management_form) | n}
              </div>
          </dl>
          <input type="submit" class="bw-create_table_submit">
        </dd>
      </div>
    </dl>
  </dd>

</dl>

  <div style="display:none">
    <div class="beeswax_column_form_template ccs-hidden" style="display: none">
      ${render_column(columns_form.empty_form())}
    </div>
    <div class="beeswax_partition_form_template ccs-hidden" style="display: none">
      ${render_column(partitions_form.empty_form(), true)}
    </div>
  </div>
</form>
${wrappers.foot()}
