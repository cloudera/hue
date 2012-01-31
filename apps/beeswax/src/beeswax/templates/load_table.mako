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
%>
<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />
${commonheader("Beeswax: Load Data into " + table, "beeswax", "100px")}
${layout.menubar()}
<div class="container-fluid">
  <h1>Load Data into <tt>${table}</tt></h1>
  <div class="prompt_popup">
    <form action="${action}" method="POST">
      <dl>
        ${util.render_field(form["path"])}
        <a class="hue-chooseFile" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16, 'top': 6, 'left': 6 }" data-chooseFor="path">Open File Chooser </a>
        ## Path (on HDFS) of files to load.
        ${util.render_field(form["overwrite"])}
        ## Any existing data will be erased!
        % for pf in form.partition_columns:
          ${util.render_field(form[pf])}
        % endfor
        ## This table is partitioned.  Therefore,
        ## you must specify what partition
        ## this data corresponds to.
      </dl>
      <p>
      Note that loading data will move data from its location
      into the table's storage location.
      </p>
      <input type="submit">
    </form>
  </div>
</div>
${commonfooter()}
