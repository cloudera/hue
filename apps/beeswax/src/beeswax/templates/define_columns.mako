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
<%namespace name="util" file="util.mako" />

${ commonheader(_('Create table from file'), app_name, user, '100px') | n,unicode }
${layout.menubar(section='tables')}

<div class="container-fluid">
    <h1>${_('Create a new table from a file')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="${ url(app_name + ':import_wizard', database=database)}">${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url(app_name + ':create_table', database=database)}">${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
            <ul class="nav nav-pills">
                <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
                <li><a id="step2" href="#">${_('Step 2: Choose Delimiter')}</a></li>
                <li class="active"><a href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form action="${action}" method="POST" class="form-stacked">
                <div class="hide">
                    ${util.render_form(file_form)}
                ${util.render_form(delim_form)}
                ${unicode(column_formset.management_form) | n}
                </div>
                <%
                    n_rows = len(fields_list)
                    if n_rows > 2: n_rows = 2
                %>
                <fieldset>
                    <div class="alert alert-info"><h3>${_('Define your columns')}</h3></div>
                    <div class="control-group">
                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped">
                                    <tr>
                                        <td id="editColumns"><i class="icon-edit" rel="tooltip" data-placement="left" title="${ _('Bulk edit names') }"></i></td>
                                        % for form in column_formset.forms:
                                                <td class="cols">
                                                ${comps.label(form["column_name"])}
                                                ${comps.field(form["column_name"],
                                                render_default=False,
                                                placeholder=_("Column name")
                                                )}
                                                    <br/><br/>
                                                ${comps.label(form["column_type"])}
                                                ${comps.field(form["column_type"],
                                                render_default=True
                                                )}
                                                ${unicode(form["_exists"]) | n}
                                                </td>
                                        %endfor
                                    </tr>
                                    % for i, row in enumerate(fields_list[:n_rows]):
                                        <tr>
                                            <td><em>${_('Row')} #${i + 1}</em></td>
                                        % for val in row:
                                                <td>${val}</td>
                                        % endfor
                                        </tr>
                                    % endfor
                                </table>
                            </div>
                        </div>
                    </div>
                </fieldset>
                <div class="form-actions">
                    <input class="btn" type="submit" name="cancel_create" value="${_('Previous')}" />
                    <input class="btn btn-primary" type="submit" name="submit_create" value="${_('Create Table')}" />
                </div>
            </form>
        </div>
    </div>
</div>

<div id="columnNamesPopover" class="popover editable-container hide right">
  <div class="arrow"></div>
  <div class="popover-inner">
    <h3 class="popover-title left">${ _('Write or paste comma separated column names') }</h3>
    <div class="popover-content">
      <p>
        <div>
          <form style="display: block;" class="form-inline editableform">
            <div class="control-group">
              <div>
                <div style="position: relative;" class="editable-input">
                  <input type="text" class="span8" style="padding-right: 24px;" placeholder="${ _('e.g. id, name, salary') }">
                </div>
                <div class="editable-buttons">
                  <button type="button" class="btn btn-primary editable-submit"><i class="icon-ok icon-white"></i></button>
                  <button type="button" class="btn editable-cancel"><i class="icon-remove"></i></button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </p>
    </div>
  </div>
</div>

<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
<style>
  .scrollable {
    width: 100%;
    overflow-x: auto;
  }

  #editColumns {
    cursor: pointer;
    text-align: right;
    padding-top: 36px;
  }
</style>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("[rel='tooltip']").tooltip();

    $(".scrollable").width($(".form-actions").width());
    $("#step1").click(function (e) {
      e.preventDefault();
      $("input[name='cancel_create']").attr("name", "cancel_delim").click();
    });
    $("#step2").click(function (e) {
      e.preventDefault();
      $("input[name='cancel_create']").click();
    });
    $("body").keypress(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        $("input[name='submit_create']").click();
      }
    });

    $("body").click(function () {
      if ($("#columnNamesPopover").is(":visible")) {
        $("#columnNamesPopover").hide();
      }
    });

    $(".editable-container").click(function (e) {
      e.stopImmediatePropagation();
    });

    $("#editColumns").click(function (e) {
      e.stopImmediatePropagation();
      $("[rel='tooltip']").tooltip("hide");
      var _newVal = "";
      $(".cols input[type='text']").each(function (cnt, item) {
        _newVal += $(item).val() + (cnt < $(".cols input[type='text']").length - 1 ? ", " : "");
      });
      $("#columnNamesPopover").show().css("left", $("#editColumns i").position().left + 16).css("top", $("#editColumns i").position().top - ($("#columnNamesPopover").height() / 2));
      $(".editable-input input").val(_newVal).focus();
    });

    $("#columnNamesPopover .editable-submit").click(function () {
      parseJSON($(".editable-input input").val());
      $("#columnNamesPopover").hide();
      $(".editable-input input").val("");
    });

    $("#columnNamesPopover .editable-cancel").click(function () {
      $("#columnNamesPopover").hide();
    });

    function parseJSON(val) {
      try {
        if (val.indexOf("\"") == -1 && val.indexOf("'") == -1) {
          val = '"' + val.replace(/,/gi, '","') + '"';
        }
        if (val.indexOf("[") == -1) {
          val = "[" + val + "]";
        }
        var _parsed = JSON.parse(val);
        $(".cols input[type='text']").each(function (cnt, item) {
          try {
            $(item).val($.trim(_parsed[cnt]));
          }
          catch (i_err) {
          }
        });
      }
      catch (err) {
      }
    }
  });
</script>
${ commonfooter(messages) | n,unicode }
