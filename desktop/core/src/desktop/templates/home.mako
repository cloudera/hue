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

  .toggleTag, .documentTagsModalCheckbox, .tagsModalCheckbox {
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
                % if 'beeswax' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['beeswax'].icon_path }"/> ${_('Hive Query')}</a></li>
                % endif
                % if 'impala' in apps:
                <li><a href="${ url('impala:index') }"><img src="${ apps['impala'].icon_path }"/> ${_('Impala Query')}</a></li>
                % endif
                % if 'pig' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ apps['pig'].icon_path }"/> ${_('Pig Script')}</a></li>
                % endif
                % if 'sqoop' in apps:
                <li><a href="#"><img src="${ apps['sqoop'].icon_path }"/> ${_('Sqoop Transfer')}</a></li>
                % endif                
                % if 'oozie' in apps:
                <li class="dropdown-submenu">
                  <a href="#"><img src="${ apps['oozie'].icon_path }"/> ${_('Oozie Scheduler')}</a>
                  <ul class="dropdown-menu">
                    <li><a href="${ url('oozie:create_workflow') }"><img src="/oozie/static/art/icon_oozie_24_workflow.png"/> ${_('Workflow')}</a></li>
                    <li><a href="${ url('oozie:create_coordinator') }"><img src="/oozie/static/art/icon_oozie_24_coordinator.png"/> ${_('Coordinator')}</a></li>
                    <li><a href="${ url('oozie:create_bundle') }"><img src="/oozie/static/art/icon_oozie_24_bundle.png"/> ${_('Bundle')}</a></li>
                  </ul>
                </li>
                % endif
              </ul>
           </li>
           <li class="viewTrash"><a href="javascript:void(0)"><i class="icon-trash"></i> ${_('View Trash')} <span id="trashCounter" class="badge pull-right">0</span></a></li>
          <li class="nav-header tag-header">${_('Tags')} <div id="editTags" style="display: inline;cursor: pointer;margin-left: 6px"><i class="icon-edit"></i></div> </li>
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

<div id="documentTagsModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Tags for ')}<span id="documentTagsModalName"></span></h3>
  </div>
  <div class="modal-body">
    <p>
      <div id="documentTagsModalList"></div>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="documentTagsNew" type="text">
          <button id="documentTagsNewBtn" class="btn" type="button"><i class="icon-plus-sign"></i> ${_('Add')}</button>
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="saveDocumentTags" href="#" class="btn btn-primary disable-feedback">${_('Save tags')}</a>
  </div>
</div>

<div id="tagsModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Manage tags')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div id="tagsModalList"></div>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="tagsNew" type="text">
          <button id="tagsNewBtn" class="btn" type="button"><i class="icon-plus-sign"></i> ${_('Add')}</button>
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="removeTags" href="#" class="btn btn-danger disable-feedback">${_('Remove selected')}</a>
  </div>
</div>


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">

var JSON_DOCS = ${json_documents|n};
var JSON_TAGS = ${json_tags|n};
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
      { "sClass": "row-selector-exclude"},
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

  $(document).on("click", ".toggleTag", function (e) {
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
    if (isInTags(doc, "trash")) {
      _trashCounter++;
    }
  });
  $("#trashCounter").text(_trashCounter);

  $(document).on("click", ".documentTags", function () {
    $("#documentTagsModal").data("document-id", $(this).data("document-id"));
    renderDocumentTagsModal();
  });

  function renderTags() {
    $(".toggleTag").remove();
    for (var i = JSON_TAGS.length - 1; i >= 0; i--) {
      if (!JSON_TAGS[i].isTrash) {
        var _t = $("<li>").addClass("toggleTag").addClass("white");
        _t.data("tag", JSON_TAGS[i].name);
        _t.html('<div class="hueCheckbox pull-left"></div>' + JSON_TAGS[i].name);
        _t.insertAfter(".tag-header");
      }
    }
  }

  function renderTagsModal() {
    var _tags = "";
    for (var i = 0; i < JSON_TAGS.length; i++) {
      if (!JSON_TAGS[i].isTrash) {
        _tags += '<div style="margin-right:10px;margin-bottom: 6px;float:left;"><span class="tagsModalCheckbox badge" data-value="' + JSON_TAGS[i].id + '"><i class="icon-trash hide"></i> ' + JSON_TAGS[i].name + '</span></div>';
      }
    }
    $("#tagsModalList").html(_tags);
  }

  function renderDocumentTagsModal() {
    var _doc = getDocById($("#documentTagsModal").data("document-id"));
    if (_doc != null) {
      $("#documentTagsModalList").empty();
      $("#documentTagsModalName").text(_doc.name);
      var _tags = "";
      for (var i = 0; i < JSON_TAGS.length; i++) {
        if (!JSON_TAGS[i].isTrash) {
          var _inTags = isInTags(_doc, JSON_TAGS[i].name);
          _tags += '<div style="margin-right:10px;margin-bottom: 6px;float:left;"><span class="documentTagsModalCheckbox badge' + (_inTags ? ' badge-info selected' : '') + '" data-value="' + JSON_TAGS[i].id + '"><i class="icon-ok-sign' + (_inTags ? '' : ' hide') + '"></i> ' + JSON_TAGS[i].name + '</span></div>';
        }
      }
      $("#documentTagsModalList").html(_tags);
      $("#documentTagsModal").modal("show");
    }
  }

  $("#documentTagsModal").modal({
    show: false
  });

  $("#tagsModal").modal({
    show: false
  });

  $("#documentTagsNewBtn").on("click", function () {
    addTag($("#documentTagsNew").val(), function () {
      $("#documentTagsNew").val("");
      renderDocumentTagsModal();
    });
  });

  $("#tagsNewBtn").on("click", function () {
    addTag($("#tagsNew").val(), function () {
      $("#tagsNew").val("");
      renderTagsModal();
    });
  });


  function addTag(value, callback) {
    $.post("/tag/add_tag", {
      name: value
    }, function (data) {
      $("#documentTagsNew").val("");
      $.getJSON("/tag/list_tags", function (data) {
        JSON_TAGS = data;
        renderTags();
        callback();
      })
    });
  }

  $(document).on("click", ".documentTagsModalCheckbox", function () {
    var _this = $(this);
    if (_this.hasClass("selected")) {
      _this.removeClass("selected").removeClass("badge-info");
      _this.find(".icon-ok-sign").addClass("hide");
    }
    else {
      _this.addClass("selected").addClass("badge-info");
      _this.find(".icon-ok-sign").removeClass("hide");
    }
  });


  $("#editTags").on("click", function () {
    renderTagsModal();
    $("#tagsModal").modal("show");
  });

  $(document).on("click", ".tagsModalCheckbox", function () {
    var _this = $(this);
    if (_this.hasClass("selected")) {
      _this.removeClass("selected").removeClass("badge-important");
      _this.find(".icon-trash").addClass("hide");
    }
    else {
      _this.addClass("selected").addClass("badge-important");
      _this.find(".icon-trash").removeClass("hide");
    }
  });

  $("#saveDocumentTags").on("click", function () {
    $(this).attr("data-loading-text", $(this).text() + " ...");
    $(this).button("loading");
    var _tags = [];
    $(".documentTagsModalCheckbox.selected").each(function () {
      var _this = $(this);
      _tags.push(_this.data("value"));
    });
    $.post("/doc/update_tags", {
      data: JSON.stringify({
        doc_id: $("#documentTagsModal").data("document-id"),
        tag_ids: _tags
      })
    }, function (response) {
      if (response.doc != null) {
        var _doc = response.doc;
        var _dtNodes = documentsTable.fnGetNodes();
        $(_dtNodes).each(function (iNode, node) {
          if ($(node).children("td").eq(3).find(".documentTags").data("document-id") == _doc.id) {
            var _tags = "";
            for (var i = 0; i < _doc.tags.length; i++) {
              _tags += '<span class="badge">' + _doc.tags[i].name + '</span> ';
            }
            documentsTable.fnUpdate('<div class="documentTags" data-document-id="' + _doc.id + '">' + _tags + '</div>', node, 3, false);
            updateDoc(_doc);
            $("#saveDocumentTags").button("loading");
          }
        });
      }
      $("#documentTagsModal").modal("hide");
    })
  });

  $("#removeTags").on("click", function () {
    $(this).attr("data-loading-text", $(this).text() + " ...");
    $(this).button("loading");
    var _tags = [];
    $(".tagsModalCheckbox.selected").each(function () {
      var _this = $(this);
      _tags.push(_this.data("value"));
    });
    $.post("/tag/remove_tags", {
      data: JSON.stringify({
        tag_ids: _tags
      })
    }, function (response) {
      $.getJSON("/tag/list_tags", function (data) {
        JSON_TAGS = data;
        renderTags();
        renderTagsModal();
        renderDocs(function () {
          $("#removeTags").button("reset");
          $("#tagsModal").modal("hide");
        });
      });
    });
  });

});

function renderDocs(callback) {
  $.getJSON("/doc/list_docs", function (data) {
    JSON_DOCS = data;
    populateTable();
    if (callback != null) {
      callback();
    }
  });
}

function isInTags(doc, tag) {
  if (doc.tags == null) {
    return false;
  }
  var _inTags = false;
  for (var i = 0; i < doc.tags.length; i++) {
    if (doc.tags[i].name == tag) {
      _inTags = true;
    }
  }
  return _inTags;
}

function populateTable(tags) {
  documentsTable.fnClearTable();
  documentsTable.fnDraw();
  if (tags == null || tags == "") {
    $(JSON_DOCS).each(function (cnt, doc) {
      if (!isInTags(doc, "trash")) {
        addRow(doc);
      }
    });
  }
  else {
    var _tags = tags.split(",");
    $(JSON_DOCS).each(function (cnt, doc) {
      var _add = false;
      $(_tags).each(function (cnt, tag) {
        if (isInTags(doc, tag)) {
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
    var _tags = "";
    for (var i = 0; i < doc.tags.length; i++) {
      _tags += '<span class="badge">' + doc.tags[i].name + '</span> ';
    }
    documentsTable.fnAddData([
      '<img src="' + doc.icon + '" width="80%"/>',
      '<a href="' + doc.url + '" data-row-selector="true">' + doc.name + '</a>',
      emptyStringIfNull(doc.description),
      '<div class="documentTags" data-document-id="' + doc.id + '">' + _tags + '</div>',
      emptyStringIfNull(doc.owner),
      emptyStringIfNull(doc.lastModified)
    ], false);
  }
  catch (error) {
    $(document).trigger("error", error);
  }
}

function getDocById(id) {
  var _doc = null;
  $(JSON_DOCS).each(function (cnt, doc) {
    if (doc.id == id) {
      _doc = doc;
    }
  });
  return _doc;
}

function updateDoc(updatedDoc) {
  $(JSON_DOCS).each(function (cnt, doc) {
    if (doc.id == updatedDoc.id) {
      JSON_DOCS[cnt] = updatedDoc;
    }
  });
}

function emptyStringIfNull(obj) {
  if (obj != null && typeof obj != "undefined") {
    return obj;
  }
  return "";
}
</script>

${ commonfooter(messages) | n,unicode }
