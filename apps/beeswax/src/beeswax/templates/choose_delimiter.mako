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
<%namespace name="util" file="util.mako" />
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Create table from file'), 'metastore', user) | n,unicode }
${ layout.metastore_menubar() }

<link rel="stylesheet" href="/metastore/static/css/metastore.css">

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="sidebar-nav">
                <ul class="nav nav-list">
                  <li class="nav-header">${_('database')}</li>
                  <li class="white">
                      <select id="chooseDatabase" class="input-medium">
                    % for db in databases:
                      <option value="${db["url"]}"
                              %if database==db["name"]:
                                selected="selected"
                              %endif
                          >${db["name"]}</option>
                    % endfor
                      </select>
                  </li>
                  <li class="nav-header">${_('Actions')}</li>
                  <li><a href="${ url(app_name + ':import_wizard', database=database)}"><i class="fa fa-files-o"></i> ${_('Create a new table from a file')}</a></li>
                  <li><a href="${ url(app_name + ':create_table', database=database)}"><i class="fa fa-wrench"></i> ${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
          <div class="card card-small" style="margin-top: 0">
            <h1 class="card-heading simple">
              <ul id="breadcrumbs" class="nav nav-pills hueBreadcrumbBar">
                <li>
                  <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
                </li>
                <li>
                  <a href="${ url('metastore:show_tables', database=database) }">${database}</a><span class="divider">&gt;</span>
                </li>
                <li>
                    <span style="padding-left:12px">${_('Create a new table from a file')}</span>
                </li>
              </ul>
            </h1>
            <div class="card-body">
              <p>
                <ul class="nav nav-pills">
                <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
                <li class="active"><a href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li><a id="step3" href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
                <form id="delimiterForm" action="${action}" method="POST" class="form-horizontal">
                ${ csrf_token(request) | n,unicode }
                <div class="hide">
                    ${util.render_form(file_form)}
                    ${comps.field(delim_form['file_type'])}
                </div>
                <fieldset>
                    <div class="alert alert-info"><h3>${_('Choose a Delimiter')}</h3>
                        % if initial:
                            ${_('Beeswax has determined that this file is delimited by')} <strong>${delim_readable}</strong>.
                        % endif
                    </div>
                    <div class="control-group">
                        ${comps.bootstrapLabel(delim_form["delimiter"])}
                        <div class="controls">
                            ${comps.field(delim_form["delimiter"], render_default=True)}
                            <input id="submit_preview" class="btn btn-info" type="submit" value="${_('Preview')}" name="submit_preview"/>
                            <span class="help-block">
                            ${_('Enter the column delimiter which must be a single character. Use syntax like "\\001" or "\\t" for special characters.')}
                            </span>
                        </div>
                    </div>
                    <div class="control-group">
                        <label class="control-label">${_('Table preview')}</label>
                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped table-condensed">
                                    <thead>
                                    <tr>
                                      % for i in range(n_cols):
                                          <th>col_${i+1}</th>
                                      % endfor
                                    </tr>
                                    </thead>
                                    <tbody>
                                      % for row in fields_list:
                                      <tr>
                                        % for val in row:
                                          ${ comps.getEllipsifiedCell(val, "left")}
                                        % endfor
                                      </tr>
                                      % endfor
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </fieldset>

                <div class="form-actions" style="padding-left: 10px">
                    <input class="btn" type="submit" value="${_('Previous')}" name="cancel_delim"/>
                    <input class="btn btn-primary" type="submit" name="submit_delim" value="${_('Next')}" />
                </div>
            </form>
              </p>
            </div>
          </div>
        </div>
    </div>
</div>

<style type="text/css">
  .scrollable {
    width: 100%;
    overflow-x: auto;
  }
</style>

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("#chooseDatabase").chosen({
      disable_search_threshold: 5,
      width: "100%",
      no_results_text: "${_('Oops, no database found!')}"
    });

    $("#chooseDatabase").chosen().change(function () {
      window.location.href = $("#chooseDatabase").val();
    });

    $("[rel='tooltip']").tooltip();

    $(".scrollable").width($(".form-actions").width() - 170);

    $("#id_delimiter_1").css("margin-left", "4px").attr("placeholder", "${_('Type your delimiter here')}").hide();
    $("#id_delimiter_0").change(function () {
      if ($(this).val() == "__other__") {
        $("#id_delimiter_1").show();
      }
      else {
        $("#id_delimiter_1").hide();
        $("#id_delimiter_1").val('');
      }
    });

    $("#id_delimiter_0").change();

    $("#step1").click(function (e) {
      e.preventDefault();
      $("input[name='cancel_delim']").click();
    });
    $("#step3").click(function (e) {
      e.preventDefault();
      $("input[name='submit_delim']").click();
    });
    $("body").keypress(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        $("input[name='submit_delim']").click();
      }
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
