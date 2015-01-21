// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
 * jHue HDFS tree plugin
 * shows a tree HDFS picker, if initialPath is set it pre-populates the path
 * if home is specified a home link will appear
 * use attached to an element, ie:
 * $("#el").jHueHdfsTree({
 *    initialPath: "/user",
 *    home: "/user/hue"
 *    onPathChange: function (path) {
 *      console.log(path);
 *    }
 * });
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueHdfsTree",
      defaults = {
        home: "",
        initialPath: "/",
        onPathChange: function () {
        },
        createFolder: true,
        labels: {
          CREATE_FOLDER: "Create folder",
          FOLDER_NAME: "Folder name",
          CANCEL: "Cancel",
          HOME: "Home"
        }
      },
      STORAGE_PREFIX = "hueFileBrowserLastPathForUser_";

  function Plugin(element, options) {
    this.element = element;
    if (typeof jHueHdfsTreeGlobals != 'undefined') {
      var extendedDefaults = $.extend({}, defaults, jHueHdfsTreeGlobals);
      extendedDefaults.labels = $.extend({}, defaults.labels, jHueHdfsTreeGlobals.labels);
      this.options = $.extend({}, extendedDefaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, extendedDefaults.labels, options.labels);
      }
    }
    else {
      this.options = $.extend({}, defaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, defaults.labels, options.labels);
      }
    }
    this._defaults = defaults;
    this._name = pluginName;
    this.lastPath = "";
    this.previousPath = "";
    this.init();
  }

  Plugin.prototype.init = function (optionalPath) {
    var _this = this;

    if (typeof optionalPath != "undefined") {
      _this.options.initialPath = optionalPath;
    }
    var _el = $(_this.element);
    _el.empty();
    _el.addClass("jHueHdfsTree");

    if (_this.options.home != ""){
      var _homeLink = $("<a>").html('<i class="fa fa-home"></i> ' + _this.options.labels.HOME).click(function () {
        var _path = _this.options.home;
        _this.options.onPathChange(_path);
        _this.lastPath = _path;
        _tree.find("a").removeClass("selected");
        var _paths = [];
        var _re = /\//g;
        while ((match = _re.exec(_path)) != null) {
          _paths.push(_path.substr(0, match.index));
        }
        _paths.push(_path);
        
        showHdfsLeaf({
          paths: _paths,
          scroll: true
        });
      });
      _homeLink.css({
        "cursor": "pointer",
        "position": "fixed",
        "margin-top": "-10px",
        "margin-left": "12px",
        "font-size": "16px",
        "background-color": "#FFF",
        "width": "560px"
      })
    }
    
    var _tree = $("<ul>").addClass("content unstyled").html('<li><a class="pointer"><i class="fa fa-folder-open-o"></i> /</a></li>');
    _tree.css("padding-top", "30px");
    
    if (_this.options.home != ""){
      _homeLink.appendTo(_el);
    }
    _tree.appendTo(_el);



    _tree.find("a").on("click", function () {
      _this.options.onPathChange("/");
      _tree.find("a").removeClass("selected");
      _tree.find("a:eq(0)").addClass("selected");
    });

    var _root = $("<ul>").addClass("content unstyled").attr("data-path", "__JHUEHDFSTREE__ROOT__").attr("data-loaded", "true");
    _root.appendTo(_tree.find("li"));

    var BASE_PATH = "/filebrowser/view";
    var _currentFiles = [];

    function showHdfsLeaf(options) {
      var autocompleteUrl = BASE_PATH,
          currentPath = "";

      if (options.paths != null && options.paths.length > 0) {
        currentPath = options.paths.shift();
      }
      else {
        currentPath = (options.leaf != null ? options.leaf : "");
      }
      autocompleteUrl += currentPath;
      $.getJSON(autocompleteUrl + "?pagesize=1000&format=json", function (data) {
        _currentFiles = [];
        if (data.error == null) {
          var _dataPathForCurrent = currentPath != "" ? currentPath : "__JHUEHDFSTREE__ROOT__";
          _el.find("[data-path='" + _dataPathForCurrent + "']").attr("data-loaded", true);
          _el.find("[data-path='" + _dataPathForCurrent + "']").siblings("a").find(".fa-folder-o").removeClass("fa-folder-o").addClass("fa-folder-open-o");
          _tree.find("a").removeClass("selected");
          _el.find("[data-path='" + _dataPathForCurrent + "']").siblings("a").addClass("selected");
          
          if (options.scroll) {
            _el.parent().scrollTop(_el.find("[data-path='" + _dataPathForCurrent + "']").siblings("a").position().top + _el.parent().scrollTop() - 30);
          }
          $(data.files).each(function (cnt, item) {
            if (item.name != "." && item.name != ".." && item.type == "dir") {
              var _path = item.path;
              if (_el.find("[data-path='" + _path + "']").length == 0){
                var _li = $("<li>").html('<a class="pointer"><i class="fa fa-folder-o"></i> ' + item.name + '</a><ul class="content unstyled" data-path="' + _path + '" data-loaded="false"></ul>');
                var _destination = _path.substr(0, _path.lastIndexOf("/"));
                if (_destination == ""){
                  _destination = "__JHUEHDFSTREE__ROOT__";
                }
                _li.appendTo(_el.find("[data-path='" + _destination + "']"));
                _li.find("a").on("click", function () {
                  _this.options.onPathChange(_path);
                  _this.lastPath = _path;
                  _tree.find("a").removeClass("selected");
                  _li.find("a:eq(0)").addClass("selected");
                  if (_li.find(".content").attr("data-loaded") == "false") {
                    showHdfsLeaf({
                      leaf: _path,
                      scroll: false
                    });
                  }
                  else {
                    if (_li.find(".content").is(":visible")) {
                      _li.find(".content").hide();
                    }
                    else {
                      _li.find(".content").show();
                    }
                  }
                });
              }
            }
          });
          if (_this.options.createFolder) {
            var _createFolderLi = $("<li>").html('<a class="pointer"><i class="fa fa-plus-square-o"></i> ' + _this.options.labels.CREATE_FOLDER + '</a>');
            _createFolderLi.appendTo(_el.find("[data-path='" + currentPath + "']"));

            var _createFolderDetails = $("<form>").css("margin-top", "10px").addClass("form-inline");
            _createFolderDetails.hide();
            var _folderName = $("<input>").attr("type", "text").attr("placeholder", _this.options.labels.FOLDER_NAME).appendTo(_createFolderDetails);
            $("<span> </span>").appendTo(_createFolderDetails);
            var _folderBtn = $("<input>").attr("type", "button").attr("value", _this.options.labels.CREATE_FOLDER).addClass("btn primary").appendTo(_createFolderDetails);
            $("<span> </span>").appendTo(_createFolderDetails);
            var _folderCancel = $("<input>").attr("type", "button").attr("value", _this.options.labels.CANCEL).addClass("btn").appendTo(_createFolderDetails);
            _folderCancel.click(function () {
              _createFolderDetails.slideUp();
            });
            _folderBtn.click(function () {
              $.ajax({
                type: "POST",
                url: "/filebrowser/mkdir",
                data: {
                  name: _folderName.val(),
                  path: currentPath
                },
                beforeSend: function (xhr) {
                  xhr.setRequestHeader("X-Requested-With", "Hue"); // need to override the default one because otherwise Django returns HTTP 500
                },
                success: function (xhr, status) {
                  if (status == "success") {
                    _createFolderDetails.slideUp();
                    var _newFolder = currentPath + "/" + _folderName.val();
                    _this.init(_newFolder);
                    _this.options.onPathChange(_newFolder);
                  }
                }
              });

            });
            _createFolderDetails.appendTo(_el.find("[data-path='" + currentPath + "']"));

            _createFolderLi.find("a").on("click", function () {
              _createFolderDetails.slideDown();
            });
          }
          if (options.paths != null && options.paths.length > 0) {
            showHdfsLeaf({
              paths: options.paths,
              scroll: options.scroll
            });
          }
        }
      });
    }

    Plugin.prototype.showHdfsLeaf = showHdfsLeaf;

    var _paths = [];
    if (_this.options.initialPath != "/") {
      var _re = /\//g;
      while ((match = _re.exec(_this.options.initialPath)) != null) {
        _paths.push(_this.options.initialPath.substr(0, match.index));
      }
      _paths.push(_this.options.initialPath);
    }

    showHdfsLeaf({
      paths: _paths
    });

  };

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
      }
    });
  }

  $[pluginName] = function (options) {
    if (typeof console != "undefined") {
      console.warn("$(elem).jHueHdfsTree() is a preferred call method.");
    }
    $(options.element).jHueHdfsTree(options);
  };

})(jQuery, window, document);
