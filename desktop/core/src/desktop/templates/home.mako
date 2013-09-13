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

${ commonheader(_('Welcome Home'), "home", user) | n,unicode }

<style type="text/css">
  .sidebar-nav img {
    margin-right: 6px;
  }

  .sidebar-nav .dropdown-menu a {
    padding-left: 6px;
  }

  .tag {
    float: left;
    margin-right: 6px;
    margin-bottom: 4px;
  }

  #trashCounter {
    margin-top: 3px;
  }

  .hueCheckbox {
    margin-right: 6px !important;
    line-height: 15px !important;
  }

  .toggleTag {
    cursor: pointer;
  }
</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="/home">
              <img src="/static/art/home.png" />
              ${ _('Home') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
         <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
           <li class="dropdown">
              <a href="#" data-toggle="dropdown"><i class="icon-plus-sign"></i> ${_('New document')}</a>
              <ul class="dropdown-menu" role="menu">
                <li><a href="#"><img src="/beeswax/static/art/icon_beeswax_24.png"/> ${_('Hive Query')}</a></li>
                <li><a href="#"><img src="/impala/static/art/icon_impala_24.png"/> ${_('Impala Query')}</a></li>
                <li><a href="#"><img src="/pig/static/art/icon_pig_24.png"/> ${_('Pig Script')}</a></li>
                <li class="dropdown-submenu">
                  <a href="#"><img src="/oozie/static/art/icon_oozie_24.png"/> ${_('Oozie')}</a>
                  <ul class="dropdown-menu">
                    <li><a href="#"><img src="/oozie/static/art/icon_oozie_24_workflow.png"/> ${_('Workflow')}</a></li>
                    <li><a href="#"><img src="/oozie/static/art/icon_oozie_24_coordinator.png"/> ${_('Coordinator')}</a></li>
                    <li><a href="#"><img src="/oozie/static/art/icon_oozie_24_bundle.png"/> ${_('Bundle')}</a></li>
                  </ul>
                </li>
              </ul>
           </li>
           <li class="viewTrash"><a href="javascript:void(0)"><i class="icon-trash"></i> ${_('View Trash')} <span id="trashCounter" class="badge pull-right">0</span></a></li>
          <li class="nav-header">${_('Tags')}</li>
          % for tag in tags:
            %if tag.tag != "trash":
            <li class="toggleTag white" data-tag="${ tag.tag }"><div class="hueCheckbox pull-left"></div>${ tag.tag }</li>
            %endif
          % endfor

        </ul>
      </div>

    </div>

    <div class="span10">
      <div class="card card-home" style="margin-top: 0">
        <input type="text" placeholder="Search for name, description, etc..." class="input-xlarge search-query pull-right" style="margin-right: 10px;margin-top: 3px" id="filterInput">
        <h2 class="card-heading simple">${_('My Documents')}</h2>

        <div class="card-body">
          <p>
          <table class="table table-striped table-condensed datatables" data-tablescroller-disable="true">
            <thead>
              <tr>
                <th>&nbsp;</th>
                <th>${_('Name')}</th>
                <th>${_('Description')}</th>
                <th>${_('Tags')}</th>
                <th>${_('Owner')}</th>
                <th>${_('Last Modified')}</th>
              </tr>
            </thead>
          </table>
          </p>
        </div>
      </div>
    </div>

  </div>
</div>

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">

  var JSON_DOCS = ${json_documents|n};
  var documentsTable;

  $(document).ready(function () {
    documentsTable = $(".datatables").dataTable({
      "sPaginationType": "bootstrap",
      "iDisplayLength": 50,
      "bLengthChange": false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "aoColumns": [
        { "bSortable": false, "sWidth": "26px" },
        null,
        null,
        null,
        null,
        { "sSortDataType": "dom-sort-value", "sType": "numeric", "sWidth": "100px" }
      ],
      "aaSorting": [
        [ 1, "desc" ]
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sInfo": "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty": "${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered": "${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords": "${_('No matching records')}",
        "oPaginate": {
          "sFirst": "${_('First')}",
          "sLast": "${_('Last')}",
          "sNext": "${_('Next')}",
          "sPrevious": "${_('Previous')}"
        }
      },
      "fnDrawCallback": function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    $("#filterInput").keydown(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function () {
      documentsTable.fnFilter($(this).val());
      documentsTable.fnDraw();
    });

    populateTable();

    $(".viewTrash").on("click", function () {
      $(".hueCheckbox").removeClass("icon-ok");
      var _this = $(this);
      if (_this.hasClass("active")) {
        populateTable();
        _this.removeClass("active");
      }
      else {
        populateTable("trash");
        _this.addClass("active");
      }
    });

    $(".toggleTag").on("click", function (e) {
      $(".viewTrash").removeClass("active");
      var _this = $(this);
      _this.blur();
      if (_this.find(".hueCheckbox").hasClass("icon-ok")) {
        _this.find(".hueCheckbox").removeClass("icon-ok");
      }
      else {
        _this.find(".hueCheckbox").addClass("icon-ok");
      }
      var _tags = [];
      $(".hueCheckbox.icon-ok").each(function () {
        _tags.push($(this).parent().data("tag"));
      });
      populateTable(_tags.join(","));
    });

    var _trashCounter = 0;
    $(JSON_DOCS).each(function (cnt, doc) {
      if (doc.tags.indexOf("trash") > -1) {
        _trashCounter++;
      }
    });
    $("#trashCounter").text(_trashCounter);
  });

  function populateTable(tags) {
    documentsTable.fnClearTable();
    documentsTable.fnDraw();
    if (tags == null || tags == "") {
      $(JSON_DOCS).each(function (cnt, doc) {
        if (doc.tags.indexOf("trash") == -1) {
          addRow(doc);
        }
      });
    }
    else {
      var _tags = tags.split(",");
      $(JSON_DOCS).each(function (cnt, doc) {
        var _add = false;
        $(_tags).each(function (cnt, tag) {
          console.log(tag);
          if (doc.tags.indexOf(tag) > -1) {
            _add = true;
          }
        });
        if (_add) {
          addRow(doc);
        }
      });
    }
    documentsTable.fnDraw();
  }

  function addRow(doc) {
    try {
      documentsTable.fnAddData([
        getIcon(doc.contentType),
        '<a href="' + doc.url + '" data-row-selector="true">' + doc.name + '</a>',
        emptyStringIfNull(doc.description),
        emptyStringIfNull(doc.tags.join("-")),
        emptyStringIfNull(doc.owner),
        emptyStringIfNull(doc.lastModified)
      ], false);
    }
    catch (error) {
      $(document).trigger("error", error);
    }
  }

  function getIcon(contentType) {
    var _code = '<img src="';
    switch (contentType) {
      case "workflow":
        _code += '/oozie/static/art/icon_oozie_24_workflow.png';
        break;
      case "coordinator":
        _code += '/oozie/static/art/icon_oozie_24_coordinator.png';
        break;
      case "bundle":
        _code += '/oozie/static/art/icon_oozie_24_bundle.png';
        break;
    }
    _code += '" />';
    return _code;
  }

  function emptyStringIfNull(obj) {
    if (obj != null && typeof obj != "undefined") {
      return obj;
    }
    return "";
  }
</script>

${ commonfooter(messages) | n,unicode }
