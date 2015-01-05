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
 * jHue HDFS autocomplete plugin
 * augment a textbox into an HDFS autocomplete
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueHdfsAutocomplete",
      defaults = {
        home: "/",
        onEnter: function () {
        },
        onBlur: function () {
        },
        onPathChange: function () {
        },
        smartTooltip: "",
        smartTooltipThreshold: 10, // needs 10 up/down or click actions and no tab to activate the smart tooltip
        showOnFocus: false
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
    _el.attr("autocomplete", "off"); // prevents default browser behavior

    // creates autocomplete popover
    if ($("#jHueHdfsAutocomplete").length == 0) {
      $("<div>").attr("id", "jHueHdfsAutocomplete").addClass("jHueAutocomplete popover")
          .attr("style", "position:absolute;display:none;max-width:1000px;z-index:33000")
          .html('<div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p><ul class="unstyled"></ul></p></div></div>')
          .appendTo($("body"));
    }

    function setHueBreadcrumbCaretAtEnd(element) {
      var elemLength = element.value.length;
      if (document.selection) {
        element.focus();
        var _oSel = document.selection.createRange();
        _oSel.moveStart('character', -elemLength);
        _oSel.moveStart('character', elemLength);
        _oSel.moveEnd('character', 0);
        _oSel.select();
      }
      else if (element.selectionStart || element.selectionStart == '0') {
        element.selectionStart = elemLength;
        element.selectionEnd = elemLength;
        element.focus();
      }
    }


    _el.focus(function () {
      $(document.body).on("contextmenu", function (e) {
        e.preventDefault(); // prevents native menu on FF for Mac from being shown
      });
      setHueBreadcrumbCaretAtEnd(_this.element);
    });

    _el.keydown(function (e) {
      if (e.keyCode == 9) {
        e.preventDefault();
        showHdfsAutocomplete(function () {
          var path = _el.val();
          if (path.indexOf("/") > -1) {
            path = path.substr(path.lastIndexOf("/") + 1);
          }
          guessHdfsPath(path);
        });
      }
    });

    function smartTooltipMaker() {
      if (_this.options.smartTooltip != "" && typeof $.totalStorage != "undefined" && $.totalStorage("jHueHdfsAutocompleteTooltip") != -1) {
        var cnt = 0;
        if ($.totalStorage("jHueHdfsAutocompleteTooltip") != null) {
          cnt = $.totalStorage("jHueHdfsAutocompleteTooltip") + 1;
        }
        $.totalStorage("jHueHdfsAutocompleteTooltip", cnt);
        if (cnt >= _this.options.smartTooltipThreshold) {
          _el.tooltip({
            animation: true,
            title: _this.options.smartTooltip,
            trigger: "manual",
            placement: "top"
          }).tooltip("show");
          window.setTimeout(function () {
            _el.tooltip("hide");
          }, 10000);
          $.totalStorage("jHueHdfsAutocompleteTooltip", -1);
        }
      }
    }

    $(window).on("scroll", function(){
      $("#jHueHdfsAutocomplete").css("top", _el.offset().top + _el.outerHeight() - 1).css("left", _el.offset().left).width(_el.outerWidth() - 4);
    });

    $(window).on("keydown", function(e){
      if ((e.keyCode==32 && e.ctrlKey) || e.keyCode == 191){
        e.preventDefault();
      }
    });


    var _hdfsAutocompleteSelectedIndex = -1;
    var _filterTimeout = -1;
    _el.keyup(function (e) {
      window.clearTimeout(_filterTimeout);
      if ($.inArray(e.keyCode, [38, 40, 13, 32, 191]) == -1) {
        _hdfsAutocompleteSelectedIndex = -1;
        _filterTimeout = window.setTimeout(function () {
          var path = _el.val();
          if (path.indexOf("/") > -1) {
            path = path.substr(path.lastIndexOf("/") + 1);
          }
          $("#jHueHdfsAutocomplete ul li").show();
          $("#jHueHdfsAutocomplete ul li").each(function () {
            if ($(this).text().trim().indexOf(path) != 0) {
              $(this).hide();
            }
          });
        }, 500);
      }
      if (e.keyCode == 38) {
        if (_hdfsAutocompleteSelectedIndex <= 0) {
          _hdfsAutocompleteSelectedIndex = $("#jHueHdfsAutocomplete ul li:visible").length - 1;
        }
        else {
          _hdfsAutocompleteSelectedIndex--;
        }
      }
      if (e.keyCode == 40) {
        if (_hdfsAutocompleteSelectedIndex == $("#jHueHdfsAutocomplete ul li:visible").length - 1) {
          _hdfsAutocompleteSelectedIndex = 0;
        }
        else {
          _hdfsAutocompleteSelectedIndex++;
        }
      }
      if (e.keyCode == 38 || e.keyCode == 40) {
        smartTooltipMaker();
        $("#jHueHdfsAutocomplete ul li").removeClass("active");
        $("#jHueHdfsAutocomplete ul li:visible").eq(_hdfsAutocompleteSelectedIndex).addClass("active");
        $("#jHueHdfsAutocomplete .popover-content").scrollTop($("#jHueHdfsAutocomplete ul li:visible").eq(_hdfsAutocompleteSelectedIndex).prevAll().length * $("#jHueHdfsAutocomplete ul li:visible").eq(_hdfsAutocompleteSelectedIndex).outerHeight());
      }
      if ((e.keyCode == 32 && e.ctrlKey) || e.keyCode == 191) {
        smartTooltipMaker();
        showHdfsAutocomplete();
      }
      if (e.keyCode == 13) {
        if (_hdfsAutocompleteSelectedIndex > -1) {
          $("#jHueHdfsAutocomplete ul li:visible").eq(_hdfsAutocompleteSelectedIndex).click();
        }
        else {
          _this.options.onEnter($(this));
        }
        $("#jHueHdfsAutocomplete").hide();
        _hdfsAutocompleteSelectedIndex = -1;
      }
    });

    if (_this.options.showOnFocus){
      _el.on("focus", function(){
        showHdfsAutocomplete();
      });
    }

    var _pauseBlur = false;

    _el.blur(function () {
      if (!_pauseBlur) {
        $(document.body).off("contextmenu");
        $("#jHueHdfsAutocomplete").hide();
        _this.options.onBlur();
      }
    });

    var BASE_PATH = "/filebrowser/view";
    var _currentFiles = [];

    function showHdfsAutocomplete(callback) {
      var path = _el.val();
      var autocompleteUrl = BASE_PATH;
      if (path.indexOf("/") == 0) {
        autocompleteUrl += path.substr(0, path.lastIndexOf("/"));
      }
      else if (path.indexOf("/") > 0) {
        autocompleteUrl += _this.options.home + path.substr(0, path.lastIndexOf("/"));
      }
      else {
        autocompleteUrl += _this.options.home;
      }
      $.getJSON(autocompleteUrl + "?pagesize=1000&format=json", function (data) {
        _currentFiles = [];
        if (data.error == null) {
          $(data.files).each(function (cnt, item) {
            if (item.name != ".") {
              var ico = "fa-file-o";
              if (item.type == "dir") {
                ico = "fa-folder";
              }
              _currentFiles.push('<li class="hdfsAutocompleteItem" data-value="' + item.name + '"><i class="fa ' + ico + '"></i> ' + item.name + '</li>');
            }
          });
          window.setTimeout(function () {
            $("#jHueHdfsAutocomplete").css("top", _el.offset().top + _el.outerHeight() - 1).css("left", _el.offset().left).width(_el.outerWidth() - 4);
            $("#jHueHdfsAutocomplete").find("ul").empty().html(_currentFiles.join(""));
            $("#jHueHdfsAutocomplete").find("li").on("click", function (e) {
              smartTooltipMaker();
              e.preventDefault();
              var item = $(this).text().trim();
              var path = autocompleteUrl.substring(BASE_PATH.length);
              if (item == "..") { // one folder up
                _el.val(path.substring(0, path.lastIndexOf("/")));
              }
              else {
                _el.val(path + "/" + item);
              }
              if ($(this).html().indexOf("folder") > -1) {
                _el.val(_el.val() + "/");
                _this.options.onPathChange(_el.val());
                showHdfsAutocomplete();
              }
              else {
                _this.options.onEnter(_el);
              }
            });
            $("#jHueHdfsAutocomplete").show();
            setHueBreadcrumbCaretAtEnd(_this.element);
            if ("undefined" != typeof callback) {
              callback();
            }
          }, 100);  // timeout for IE8
        }
      });
    }

    $(document).on("mouseenter", ".hdfsAutocompleteItem", function () {
      _pauseBlur = true;
    });

    $(document).on("mouseout", ".hdfsAutocompleteItem", function () {
      _pauseBlur = false;
    })

    function guessHdfsPath(lastChars) {
      var possibleMatches = [];
      for (var i = 0; i < _currentFiles.length; i++) {
        if (($(_currentFiles[i]).text().trim().indexOf(lastChars) == 0 || lastChars == "") && $(_currentFiles[i]).text().trim() != "..") {
          possibleMatches.push(_currentFiles[i]);
        }
      }
      if (possibleMatches.length == 1) {
        _el.val(_el.val() + $(possibleMatches[0]).text().trim().substr(lastChars.length));
        if ($(possibleMatches[0]).html().indexOf("folder") > -1) {
          _el.val(_el.val() + "/");
          showHdfsAutocomplete();
        }
      }
      else if (possibleMatches.length > 1) {
        // finds the longest common prefix
        var possibleMatchesPlain = [];
        for (var z = 0; z < possibleMatches.length; z++) {
          possibleMatchesPlain.push($(possibleMatches[z]).text().trim());
        }
        var arr = possibleMatchesPlain.slice(0).sort(),
            word1 = arr[0], word2 = arr[arr.length - 1],
            j = 0;
        while (word1.charAt(j) == word2.charAt(j))++j;
        var match = word1.substring(0, j);
        _el.val(_el.val() + match.substr(lastChars.length));
      }
    }
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
      console.warn("$(elem).jHueHdfsAutocomplete() is a preferred call method.");
    }
    $(options.element).jHueHdfsAutocomplete(options);
  };

})(jQuery, window, document);
