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
<%namespace name="util" file="util.mako" />

${ commonheader(_('Create table from file'), 'metastore', user, request) | n,unicode }
<span class="notebook">
${ layout.metastore_menubar() }

<script src="${ static('metastore/js/metastore.ko.js') }"></script>

${ assist.assistJSModels() }

<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">
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
                <a href="${ url('beeswax:import_wizard', database=database) }" title="${_('Create a new table from a file')}" class="inactive-action"><i class="fa fa-files-o"></i></a>
                <a href="${ url('beeswax:create_table', database=database) }" title="${_('Create a new table manually')}" class="inactive-action margin-left-10"><i class="fa fa-wrench"></i></a>
              </div>

              <ul id="breadcrumbs" class="nav nav-pills hue-breadcrumbs-bar">
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
            </h3>
            <ul class="nav nav-pills">
              <li><a id="step1" href="#">${_('Step 1: Choose File')}</a></li>
              <li><a id="step2" href="#">${_('Step 2: Choose Delimiter')}</a></li>
              <li class="active"><a href="#">${_('Step 3: Define Columns')}</a></li>
            </ul>
            <form action="${action}" method="POST" class="form-stacked">
              ${ csrf_token(request) | n,unicode }
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
                <div class="alert alert-info margin-top-10">
                  <h3>${_('Define your columns')}</h3>
                </div>
                <div class="row" style="margin-left: 8px">
                  <div class="span3">
                    <input id="removeHeader" type="checkbox" class="hide" name="removeHeader">
                    ${_('Use first row as column names')} &nbsp;<a id="useHeader" class="btn disable-feedback"><i class="fa fa-outdent"></i></a>
                  </div>
                  <div class="span3">
                    ${ _('Bulk edit column names') } &nbsp;<a id="editColumns" class="btn"><i class="fa fa-edit"></i></a>
                  </div>
                </div>
                <div class="control-group" style="margin-top: 10px">
                  <div class="controls">
                    <div class="scrollable">
                      <table class="table table-condensed">
                        <thead>
                          <th id="column_names" style="width:210px">${ _('Column name') }</th>
                          <th style="width:210px">${ _('Column Type') }</th>
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

          </div>

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

<link href="${ static('desktop/ext/css/bootstrap-editable.css') }" rel="stylesheet">

<style type="text/css">
  .scrollable {
    width: 100%;
    overflow-x: auto;
  }

  #editColumns {
    cursor: pointer;
  }
</style>

<script type="text/javascript">
  (function () {
    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    function ImportWizardDefineColumnsViewModel() {
      var self = this;
      self.apiHelper = window.apiHelper;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);


      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name + '?source=' + tableDef.sourceType + '&namespace=' + tableDef.namespace.id;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name + '?source=' + databaseDef.sourceType + '&namespace=' + databaseDef.namespace.id;
      });
    }

    $(document).ready(function () {

      var viewModel = new ImportWizardDefineColumnsViewModel();

      ko.applyBindings(viewModel);

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }

      $("[rel='tooltip']").tooltip();

      $("#useHeader").on("click", function () {
        var _isChecked = false;
        var _klass = "btn-info";
        if ($(this).hasClass(_klass)) {
          $(this).removeClass(_klass);
        }
        else {
          $(this).addClass(_klass);
          _isChecked = true;
        }
        $("#removeHeader").prop('checked', _isChecked);

        $(".cols input[type='text']").each(function (cnt, item) {
          if (_isChecked) {
            $(item).data('previous', $(item).val());
            $(item).val($.trim(${ fields_list_json | n,unicode }[0][cnt]));
          } else {
            $(item).val($(item).data('previous'));
          }
        });

        $(".cols-1").each(function (cnt, item) {
          if (_isChecked) {
            $(item).data('previous', $(item).text());
            $(item).text($.trim(${ fields_list_json | n,unicode }[1][cnt]));
          } else {
            $(item).text($(item).data('previous'));
          }
        });

        $(".cols-2").each(function (cnt, item) {
          if (_isChecked) {
            $(item).data('previous', $(item).text());
            $(item).text($.trim(${ fields_list_json | n,unicode }[2][cnt]));
          } else {
            $(item).text($(item).data('previous'));
          }
        });

        guessColumnTypes();
      });

      guessColumnTypes();

      // Really basic heuristic to detect if first row is a header.
      var isString = 0;
      $(".cols-1").each(function (cnt, item) {
        if ($(item).data("possibleType") == 'string') {
          isString += 1;
        }
      });
      // First row is just strings
      if (isString == $(".cols-1").length) {
        $("#useHeader").click();
      }

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
              try {
                // try to detect the size of the int
                var _bytes = Math.ceil((Math.log(_val) / Math.log(2)) / 8);
                switch (_bytes) {
                  case 1:
                  case 2:
                  case 3:
                  case 4:
                    _foundType = "int";
                    break;
                  default:
                    _foundType = "bigint";
                    break;
                }
              }
              catch (e) {
                _foundType = "int";
              }
            }
            else {
              // it's possibly a float
              try {
                _foundType = "float";
                // try to detect the size of the int
                var _bytes = Math.ceil((Math.log(_val) / Math.log(2)) / 8);
                if (_bytes > 4) {
                  _foundType = "double";
                }
              }
              catch (e) {
                _foundType = "float";
              }
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
        return Math.floor(n) == n && n.toString().indexOf(".") == -1;
      }
    });
  })();
</script>
</span>
${ commonfooter(request, messages) | n,unicode }
