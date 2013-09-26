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

  #trashCounter, #historyCounter {
    margin-top: 3px;
  }

  .tagCounter {
    margin-top: 2px;
  }

  .toggleTag, .documentTagsModalCheckbox, .tagsModalCheckbox {
    cursor: pointer;
  }

  .badge-left {
    border-radius: 9px 0px 0px 9px;
    padding-right: 5px;
  }

  .badge-right {
    border-radius: 0px 9px 9px 0px;
    padding-left: 5px;
  }

  .airy li {
    margin-bottom: 6px;
  }

  .trashShare {
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
           <li class="viewTrash toggableSection">
             <a href="javascript:void(0)"><i class="icon-trash"></i> ${_('Trash')} <span id="trashCounter" class="badge pull-right">0</span></a>
           </li>
           <li class="viewHistory toggableSection">
             <a href="javascript:void(0)"><i class="icon-time"></i> ${_('History')} <span id="historyCounter" class="badge pull-right">0</span></a>
           </li>
          <li class="nav-header tag-header">${_('Projects')} <div id="editTags" style="display: inline;cursor: pointer;margin-left: 6px" title="${ _('Edit projects') }"><i class="icon-tags"></i></div> </li>
          % for tag in tags:
            % if tag.tag not in ('trash', 'history'):
            <li class="toggleTag" data-tag="${ tag.tag }"><a href="javascript:void(0)">${ tag.tag } <span class="tagCounter badge pull-right">0</span></a></li>
            % endif
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
                <th>${_('Projects')}</th>
                <th>${_('Owner')}</th>
                <th>${_('Last Modified')}</th>
                <th>${_('Sharing')}</th>
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
    <h3>${_('Projects for ')}<span id="documentTagsModalName"></span></h3>
  </div>
  <div class="modal-body">
    <p>
      <div id="documentTagsModalList"></div>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="documentTagsNew" type="text">
          <a id="documentTagsNewBtn" class="btn" type="button"><i class="icon-plus-sign"></i> ${_('Add')}</a>
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="saveDocumentTags" href="#" class="btn btn-primary disable-feedback">${_('Save projects')}</a>
  </div>
</div>

<div id="tagsModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Manage projects')}</h3>
  </div>
  <div class="modal-body">
    <p>
      <div id="tagsModalList"></div>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="tagsNew" type="text">
          <a id="tagsNewBtn" class="btn" type="button"><i class="icon-plus-sign"></i> ${_('Add')}</a>
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="removeTags" href="#" class="btn btn-danger disable-feedback">${_('Remove selected')}</a>
  </div>
</div>

<div id="documentShareModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Share ')}<span id="documentShareModalName"></span></h3>
  </div>
  <div class="modal-body">
    <p>
      <h4 id="documentShareNoShare" class="muted" style="margin-top:0px">${_('Not shared yet.')}</h4>
      <ul id="documentShareList" class="unstyled inline airy hide">
      </ul>
      <div class="clearfix"></div>
      <div style="margin-top: 20px">
        <div class="input-append">
          <input id="documentShareAdd" type="text" class="input-large" placeholder="${_('You can type a username or a group')}">
          <a id="documentShareAddBtn" class="btn" type="button"><i class="icon-plus-sign"></i> ${_('Add')}</a>
        </div>
      </div>
    </p>
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn">${_('Cancel')}</a>
    <a id="saveDocumentShare" href="#" class="btn btn-primary disable-feedback">${_('Update')}</a>
  </div>
</div>



<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script type="text/javascript" charset="utf-8">

var JSON_DOCS = ${json_documents | n};
var JSON_TAGS = ${json_tags | n};
var JSON_USERS_GROUPS;
var documentsTable;

$(document).ready(function () {
  var selectedUserOrGroup, map, dropdown = null;
  $.getJSON("${ url('useradmin.views.list_for_autocomplete') }", function (data) {
    JSON_USERS_GROUPS = data;
    dropdown = [];
    map = {};
    $.each(JSON_USERS_GROUPS.users, function (i, user) {
      map[user.username] = user;
      dropdown.push(user.username);
    });
    $.each(JSON_USERS_GROUPS.groups, function (i, group) {
      map[group.name] = group;
      dropdown.push(group.name);
    });
    $("#documentShareAdd").typeahead({
      source: function (query, process) {
        process(dropdown);
      },
      matcher: function (item) {
        if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
          return true;
        }
      },
      sorter: function (items) {
        return items.sort();
      },
      highlighter: function (item) {
        var _icon = map[item].username ? "icon-user" : "icon-group";
        var regex = new RegExp('(' + this.query + ')', 'gi');
        return "<i class='" + _icon + "'></i> " + item.replace(regex, "<strong>$1</strong>");
      },
      updater: function (item) {
        selectedUserOrGroup = map[item];
        return item;
      }
    });
  });

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
      { "sSortDataType": "dom-sort-value", "sType": "numeric", "sWidth": "100px" },
      { "bSortable": false, "sClass": "row-selector-exclude", "sWidth": "20px"}
    ],
    "aaSorting": [
      [ 5, "desc" ]
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

  $(".viewTrash").on("click", function () {
    $(".viewHistory").removeClass("active");
    toggleSpecificSection($(this), "trash");
  });

  $(".viewHistory").on("click", function () {
    $(".viewTrash").removeClass("active");
    toggleSpecificSection($(this), "history");
  });

  function toggleSpecificSection(section, filter){
    section.siblings().removeClass("active");
    if (section.hasClass("active")) {
      populateTable();
      section.removeClass("active");
      section.find("a").blur();
    }
    else {
      populateTable(filter);
      section.addClass("active");
    }
  }

  $(document).on("click", ".toggleTag", function (e) {
    var _this = $(this);
    _this.siblings().removeClass("active");
    _this.blur();
    if (_this.hasClass("active")) {
      _this.removeClass("active");
      _this.find("a").blur();
    }
    else {
      _this.addClass("active");
    }
    var _tags = [];
    $(".toggleTag.active").each(function () {
      _tags.push($(this).data("tag"));
    });
    populateTable(_tags.join(","));
  });

  // update tag counters
  var _tagCounters = {};
  $(JSON_DOCS).each(function (cnt, doc) {
    if (doc.tags != null) {
      for (var i = 0; i < doc.tags.length; i++) {
        if (_tagCounters[doc.tags[i].name] == null) {
          _tagCounters[doc.tags[i].name] = 1;
        }
        else {
          _tagCounters[doc.tags[i].name]++;
        }
      }
    }
  });
  $("#trashCounter").text(_tagCounters["trash"]);
  $("#historyCounter").text(_tagCounters["history"]);
  $("li[data-tag]").each(function () {
    if (_tagCounters[$(this).data("tag")] != null) {
      $(this).find(".badge").text(_tagCounters[$(this).data("tag")]);
    }
  });

  if ($.totalStorage("hueHomeTags") != null && $.totalStorage("hueHomeTags") != "") {
    if ($.totalStorage("hueHomeTags") == "history") {
      $(".viewHistory").click();
    }
    else if ($.totalStorage("hueHomeTags") == "trash") {
      $(".viewTrash").click();
    }
    else {
      $("li[data-tag='" + $.totalStorage("hueHomeTags") + "']").click();
    }
  }
  else {
    populateTable();
  }

  $(document).on("click", ".documentTags", function () {
    $("#documentTagsModal").data("document-id", $(this).data("document-id"));
    renderDocumentTagsModal();
  });

  function renderTags() {
    $(".toggleTag").remove();
    for (var i = JSON_TAGS.length - 1; i >= 0; i--) {
      if (!JSON_TAGS[i].isTrash && !JSON_TAGS[i].isHistory && !JSON_TAGS[i].isExample) {
        var _t = $("<li>").addClass("toggleTag");
        _t.attr("data-tag", JSON_TAGS[i].name);
        _t.html('<a href="javascript:void(0)">' + JSON_TAGS[i].name + '<span class="tagCounter badge pull-right">0</span></a>');
        _t.insertAfter(".tag-header");
      }
    }
    $("li[data-tag]").each(function () {
      if (_tagCounters[$(this).data("tag")] != null) {
        $(this).find(".badge").text(_tagCounters[$(this).data("tag")]);
      }
    });
  }

  function renderTagsModal() {
    var _tags = "";
    for (var i = 0; i < JSON_TAGS.length; i++) {
      if (!JSON_TAGS[i].isTrash && !JSON_TAGS[i].isHistory && !JSON_TAGS[i].isExample) {
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
        if (!JSON_TAGS[i].isTrash && !JSON_TAGS[i].isHistory && !JSON_TAGS[i].isExample) {
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

  $("#documentShareModal").modal({
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
        $(document).trigger("info", "${ _("Projects updated successfully.") }");
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
        if (response!=null){
          if (response.status == 0){
            $(document).trigger("info", response.message);
            $.getJSON("/tag/list_tags", function (data) {
              JSON_TAGS = data;
              renderTags();
              renderTagsModal();
              renderDocs(function () {
                $("#removeTags").button("reset");
                $("#tagsModal").modal("hide");
              });
            });
          }
          else {
            $(document).trigger("error", "${_("There was an error processing your action: ")}"+response.message);
          }
        }
    });
  });

  $(document).on("click", ".shareDocument", function () {
    var _doc = getDocById($(this).data("document-id"));
    if (_doc != null) {
      if (_doc.perms != null && _doc.perms.read != null){
        if (_doc.perms.read.users != null){
          for (var i=0; i<_doc.perms.read.users.length;i++){
            addToShareList(map[_doc.perms.read.users[i].username]);
          }
        }
        if (_doc.perms.read.groups != null){
          for (var i=0; i<_doc.perms.read.groups.length;i++){
            addToShareList(map[_doc.perms.read.groups[i].name]);
          }
        }
      }
      $("#documentShareModal").data("document-id", _doc.id);
      $("#documentShareAdd").val("");
      $("#documentShareModalName").text(_doc.name);
      renderShareList();
      $("#documentShareModal").modal("show");
    }
  });

  $("#documentShareAddBtn").on("click", function () {
    handleTypeaheadSelection();
  });

  function handleTypeaheadSelection() {
    if (selectedUserOrGroup != null) {
      addToShareList(selectedUserOrGroup);
      renderShareList();
    }
    selectedUserOrGroup = null;
    $("#documentShareAdd").val("");
  }

  var shareList = {};

  function addToShareList(item) {
    shareList[item.id] = item;
  }

  function renderShareList() {
    var _html = "";
    for (var id in shareList) {
      if (shareList.hasOwnProperty(id)) {
        var _obj = shareList[id];
        var _icon = _obj.username != null ? "icon-user" : "icon-group";
        var _label = _obj.username != null ? _obj.username : _obj.name;
        _html += '<li data-object-id="' + _obj.id + '"><span class="badge badge-left"><i class="' + _icon + '"></i> ' + _label + '</span><span class="badge badge-important badge-right trashShare"><i class="icon-trash"></i></span></li>';
      }
    }
    if (_html != "") {
      $("#documentShareList").removeClass("hide").empty();
      $("#documentShareList").html(_html);
      $("#documentShareNoShare").addClass("hide");
    }
    else {
      $("#documentShareList").addClass("hide");
      $("#documentShareNoShare").removeClass("hide");
    }
  }

  $(document).on("click", ".trashShare", function () {
    delete shareList[$(this).parent().data("object-id")];
    renderShareList();
  });

  $("#saveDocumentShare").on("click", function () {
    var _postPerms = {
      read: {
        user_ids: [],
        group_ids: []
      }
    }

    for (var id in shareList) {
      if (shareList.hasOwnProperty(id)) {
        var _obj = shareList[id];
        if (_obj.username != null) {
          _postPerms.read.user_ids.push(id);
        }
        else {
          _postPerms.read.group_ids.push(id);
        }
      }
    }

    $.post("/doc/update_permissions", {
      doc_id: $("#documentShareModal").data("document-id"),
      data: JSON.stringify(_postPerms)
    }, function (response) {
      $("#documentShareModal").modal("hide");
      if (response!=null){
        if (response.status == 0){
          $(document).trigger("info", response.message);
          updateDoc(response.doc);
        }
        else {
          $(document).trigger("error", "${_("There was an error processing your action: ")}"+response.message);
        }
      }
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
  $.totalStorage("hueHomeTags", tags);
  documentsTable.fnClearTable();
  documentsTable.fnDraw();
  if (tags == null || tags == "") {
    $(JSON_DOCS).each(function (cnt, doc) {
      if (!isInTags(doc, "trash") && !isInTags(doc, "history")) {
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
  $("a[rel='tooltip']").tooltip();
}

function addRow(doc) {
  try {
    var _tags = "";
    for (var i = 0; i < doc.tags.length; i++) {
      _tags += '<span class="badge">' + doc.tags[i].name + '</span> ';
    }
    var _addedRow = documentsTable.fnAddData([
      '<img src="' + doc.icon + '" width="80%"/>',
      '<a href="' + doc.url + '" data-row-selector="true">' + doc.name + '</a>',
      emptyStringIfNull(doc.description),
      '<div class="documentTags" data-document-id="' + doc.id + '">' + _tags + '</div>',
      emptyStringIfNull(doc.owner),
      emptyStringIfNull(doc.lastModified),
      '<a href="#" class="shareDocument" data-document-id="' + doc.id + '" rel="tooltip" title="${_('Share')} ' + doc.name + '" data-placement="left" style="padding-left:10px"><i class="icon-share-sign"></i></a>',
    ], false);
    $("td", documentsTable.fnGetNodes(_addedRow[0]))[5].setAttribute("data-sort-value", doc.lastModifiedInMillis); // a bit of black magic.
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
