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
 * shows a tree HDFS picker, if home is set it pre-populates the path
 * use attached to an element, ie:
 * $("#el").jHueHdfsTree({
 *    home: "/user",
 *    onPathChange: function (path) {
 *      console.log(path);
 *    }
 * });
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueHdfsTree",
      defaults = {
        home: "/",
        onPathChange: function () {
        }
      };

  function Plugin(element, options) {
    this.element = element;
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.init();
  }

  Plugin.prototype.init = function () {
    var _this = this;
    var _el = $(_this.element);
    _el.empty();
    _el.addClass("jHueHdfsTree");
    var _tree = $("<ul>").addClass("content unstyled").html('<li><a class="pointer"><i class="fa fa-folder-open-o"></i> /</a></li>');
    _tree.appendTo(_el);

    _tree.find("a").on("click", function () {
      _this.options.onPathChange("/");
      _tree.find("a").removeClass("selected");
      _tree.find("a:eq(0)").addClass("selected");
    });

    var _root = $("<ul>").addClass("content unstyled").attr("data-path", "").attr("data-loaded", "true");
    _root.appendTo(_tree.find("li"));

    var BASE_PATH = "/filebrowser/view";
    var _currentFiles = [];

    function showHdfsLeaf(options) {
      var autocompleteUrl = BASE_PATH;
      if (options.paths != null) {
        autocompleteUrl += options.paths.shift();
      }
      else {
        autocompleteUrl += (options.leaf != null ? options.leaf : "");
      }
      $.getJSON(autocompleteUrl + "?pagesize=1000&format=json", function (data) {
        _currentFiles = [];
        if (data.error == null) {
          if (options.leaf != null) {
            _el.find("[data-path='" + options.leaf + "']").attr("data-loaded", true);
          }
          $(data.files).each(function (cnt, item) {
            if (item.name != "." && item.name != ".." && item.type == "dir") {
              var _path = item.path;
              var _li = $("<li>").html('<a class="pointer"><i class="fa fa-folder-o"></i> ' + item.name + '</a><ul class="content unstyled" data-path="' + _path + '" data-loaded="false"></ul>');
              var _destination = _path.substr(0, _path.lastIndexOf("/"));
              _li.appendTo(_el.find("[data-path='" + _destination + "']"));
              _li.find("a").on("click", function () {
                _this.options.onPathChange(_path);
                _tree.find("a").removeClass("selected");
                _li.find("a:eq(0)").addClass("selected");
                if (_li.find(".content").attr("data-loaded") == "false") {
                  _li.find(".fa-folder-o").removeClass("fa-folder-o").addClass("fa-folder-open-o");
                  showHdfsLeaf({
                    leaf: _path
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
          });
          if (options.paths.length > 0) {
            showHdfsLeaf({
              paths: options.paths
            });
          }
        }
      });
    }

    var _paths = [];
    if (_this.options.home != "/") {
      var _re = /\//g;
      while ((match = _re.exec(_this.options.home)) != null) {
        _paths.push(_this.options.home.substr(0, match.index));
      }
      _paths.push(_this.options.home);
      console.log(_paths)
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
