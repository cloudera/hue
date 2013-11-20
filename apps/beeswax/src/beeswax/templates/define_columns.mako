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

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Actions')}</li>
                    <li><a href="${ url(app_name + ':import_wizard', database=database)}"><i class="fa fa-files-o"></i> ${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url(app_name + ':create_table', database=database)}"><i class="fa fa-wrench"></i> ${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
          <div class="card" style="margin-top: 0">
            <h1 class="card-heading simple">${_('Create a new table from a file')}</h1>
            <div class="card-body">
              <p>
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

                    <div class="control-group" id="use-header">
                        <div class="controls">
                            ${_('Use first line as column names')}
                            <input id="use_header" type="checkbox" name="use_header"/>
                        </div>
                        <div class="controls">
                            ${_('Bulk edit column names')}
                            <i id="editColumns" class="fa fa-edit" rel="tooltip" data-placement="right" title="${ _('Bulk edit names') }"></i>
                        </div>
                    </div>

                        <div class="controls">
                            <div class="scrollable">
                                <table class="table table-striped">
                                    <thead>
                                      <th id="column_names">${ _('Column name') }</th>
                                      <th>${ _('Column Type') }</th>
                                      % for i in range(0, n_rows):
                                        <th><em>${_('Sample Row')} #${i + 1}</em></th>
                                      % endfor
                                    </thead>
                                    <tbody>
                                      % for col, form in zip(range(len(column_formset.forms)), column_formset.forms):
                                      <tr>
                                        <td class="cols">
                                          ${ comps.field(form["column_name"], render_default=False, placeholder=_("Column name")) }
                                        </td>
                                        <td>
                                          ${ comps.field(form["column_type"], render_default=True) }
                                          ${unicode(form["_exists"]) | n}
                                        </td>
                                        % for row in fields_list[:n_rows]:
                                          ${ comps.getEllipsifiedCell(row[col], "bottom", "dataSample cols-%s" % (loop.index + 1)) }
                                        % endfor
                                      </tr>
                                      %endfor
                                    </tbody>
                                </table>

                            </div>
                        </div>
                    </div>
                </fieldset>
                <div class="form-actions" style="padding-left: 10px">
                    <input class="btn" type="submit" name="cancel_create" value="${_('Previous')}" />
                    <input class="btn btn-primary" type="submit" name="submit_create" value="${_('Create Table')}" />
                </div>
            </form>
              </p>
            </div>
          </div>
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
                  <button type="button" class="btn btn-primary editable-submit"><i class="fa fa-check"></i></button>
                  <button type="button" class="btn editable-cancel"><i class="fa fa-times"></i></button>
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

<style type="text/css">
  .scrollable {
    width: 100%;
    overflow-x: auto;
  }

  #editColumns {
    cursor: pointer;
  }
</style>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    $("[rel='tooltip']").tooltip();

    $(".scrollable").width($(".form-actions").width() - 10);

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
      $("#columnNamesPopover").show().css("left", $("#column_names").position().left + 16).css("top", $("#column_names").position().top - ($("#columnNamesPopover").height() / 2));
      $(".editable-input input").val(_newVal).focus();
    });

    $("#columnNamesPopover .editable-submit").click(function () {
      parseEditable();
    });

    $(".editable-input input").keypress(function (e) {
      if (e.keyCode == 13) {
        parseEditable();
        return false;
      }
    });

    function parseEditable() {
      parseJSON($(".editable-input input").val());
      $("#columnNamesPopover").hide();
      $(".editable-input input").val("");
    }

    $("#columnNamesPopover .editable-cancel").click(function () {
      $("#columnNamesPopover").hide();
    });

    function guessColumnTypes() {
      // Pick from 2nd column only
      $(".dataSample").each(function () {
        var _val = $.trim($(this).text());
        var _field = $(this).siblings().find("select[id^=id_cols-]");
        var _foundType = "string";

        if ($.isNumeric(_val)) {
          if (isInt(_val)) {
            // it's an int
            _foundType = "int";
          }
          else {
            // it's possibly a float
            _foundType = "float";
          }
        }
        else {
          if (_val.toLowerCase().indexOf("true") > -1 || _val.toLowerCase().indexOf("false") > -1) {
            // it's a boolean
            _foundType = "boolean";
          }
          else {
            // it's most probably a string
            _foundType = "string";
          }
        }

        _field.data("possibleType", _foundType);
        $(this).data("possibleType", _foundType);
      });

      $("select[id^=id_cols-]").each(function () {
        $(this).val($(this).data("possibleType"));
      });
    }

    guessColumnTypes();

    $("#use_header").change(function (e) {
      var input = this;

      $(".cols input[type='text']").each(function (cnt, item) {
        if (input.checked) {
          $(item).data('previous', $(item).val());
          $(item).val($.trim(${ fields_list_json | n,unicode }[0][cnt]));
        } else {
          $(item).val($(item).data('previous'));
        }
      });

      $(".cols-1").each(function (cnt, item) {
        if (input.checked) {
          $(item).data('previous', $(item).text());
          $(item).text($.trim(${ fields_list_json | n,unicode }[1][cnt]));
        } else {
          $(item).text($(item).data('previous'));
        }
      });

      $(".cols-2").each(function (cnt, item) {
        if (input.checked) {
          $(item).data('previous', $(item).text());
          $(item).text($.trim(${ fields_list_json | n,unicode }[2][cnt]));
        } else {
          $(item).text($(item).data('previous'));
        }
      });

      guessColumnTypes();
    });

    // Really basic heuristic to detect if first row is a header.
    var isString = 0;
    $(".cols-1").each(function (cnt, item) {
      if ($(".cols-1").data("possibleType") == 'string') {
        isString += 1;
      }
    });

    if (isString > $(".cols-1").length - 1) {
      $("#use_header").prop('checked', true);
      $("#use_header").change();
    }


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

    function isInt(n) {
      return typeof n === 'number' && parseFloat(n) == parseInt(n, 10) && !isNaN(n);
    }
  });
</script>

${ commonfooter(messages) | n,unicode }
