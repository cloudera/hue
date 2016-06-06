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
 * jHue generic autocomplete plugin
 * augment a textbox into an generic hive/solr autocomplete
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueGenericAutocomplete",
      defaults = {
        serverType: "HIVE",
        home: "/",
        skipColumns: false,
        onEnter: function () {
        },
        onBlur: function () {
        },
        onPathChange: function () {
        },
        smartTooltip: "",
        smartTooltipThreshold: 10, // needs 10 up/down or click actions and no tab to activate the smart tooltip
        showOnFocus: false,
        startingPath: '',
        rewriteVal: false,
        searchEverywhere: false
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

    // creates autocomplete popover
    if ($("#jHueGenericAutocomplete").length == 0) {
      $("<div>").attr("id", "jHueGenericAutocomplete").addClass("jHueAutocomplete popover")
          .attr("style", "position:absolute;display:none;max-width:1000px;z-index:33000")
          .html('<div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><ul class="unstyled"></ul></div></div>')
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
      _pauseBlur = false;
    });

    _el.keydown(function (e) {
      if (e.keyCode == 9) {
        e.preventDefault();
        showAutocomplete(function () {
          var path = _el.val();
          if (path.indexOf(".") > -1) {
            path = path.substr(path.lastIndexOf(".") + 1);
          }
          guessHivePath(path);
        });
      }
    });

    function smartTooltipMaker() {
      if (_this.options.smartTooltip != "" && typeof $.totalStorage != "undefined" && $.totalStorage("jHueGenericAutocompleteTooltip") != -1) {
        var cnt = 0;
        if ($.totalStorage("jHueGenericAutocompleteTooltip") != null) {
          cnt = $.totalStorage("jHueGenericAutocompleteTooltip") + 1;
        }
        $.totalStorage("jHueGenericAutocompleteTooltip", cnt);
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
          $.totalStorage("jHueGenericAutocompleteTooltip", -1);
        }
      }
    }

    $(window).on("scroll", function(){
      $("#jHueGenericAutocomplete").css("top", _el.offset().top + _el.outerHeight() - 1).css("left", _el.offset().left).width(_el.outerWidth() - 4);
    });

    var _hiveAutocompleteSelectedIndex = -1;
    var _filterTimeout = -1;
    _el.keyup(function (e) {
      window.clearTimeout(_filterTimeout);
      if ($.inArray(e.keyCode, [17, 38, 40, 13, 32, 191]) == -1) {
        _hiveAutocompleteSelectedIndex = -1;
        _filterTimeout = window.setTimeout(function () {
          var path = _el.val();
          if (path.indexOf(".") > -1) {
            path = path.substr(path.lastIndexOf(".") + 1);
          }
          $("#jHueGenericAutocomplete ul li").show();
          if (path != ""){
            $("#jHueGenericAutocomplete ul li").each(function () {
              if (_this.options.searchEverywhere){
                if ($(this).text().trim().toLowerCase().indexOf(path.toLowerCase()) == -1) {
                  $(this).hide();
                }
              }
              else {
                if ($(this).text().trim().indexOf(path) != 0) {
                  $(this).hide();
                }
              }
            });
          }
        }, 500);
      }
      if (e.keyCode == 38) {
        if (_hiveAutocompleteSelectedIndex <= 0) {
          _hiveAutocompleteSelectedIndex = $("#jHueGenericAutocomplete ul li:visible").length - 1;
        }
        else {
          _hiveAutocompleteSelectedIndex--;
        }
      }
      if (e.keyCode == 40) {
        if (_hiveAutocompleteSelectedIndex == $("#jHueGenericAutocomplete ul li:visible").length - 1) {
          _hiveAutocompleteSelectedIndex = 0;
        }
        else {
          _hiveAutocompleteSelectedIndex++;
        }
      }
      if (e.keyCode == 38 || e.keyCode == 40) {
        smartTooltipMaker();
        $("#jHueGenericAutocomplete ul li").removeClass("active");
        $("#jHueGenericAutocomplete ul li:visible").eq(_hiveAutocompleteSelectedIndex).addClass("active");
        $("#jHueGenericAutocomplete .popover-content").scrollTop($("#jHueGenericAutocomplete ul li:visible").eq(_hiveAutocompleteSelectedIndex).prevAll().length * $("#jHueGenericAutocomplete ul li:visible").eq(_hiveAutocompleteSelectedIndex).outerHeight());
      }
      if ((e.keyCode == 32 && e.ctrlKey) || e.keyCode == 191) {
        smartTooltipMaker();
        showAutocomplete();
      }
      if (e.keyCode == 13) {
        _pauseBlur = true;
        if (_hiveAutocompleteSelectedIndex > -1) {
          $("#jHueGenericAutocomplete ul li:visible").eq(_hiveAutocompleteSelectedIndex).click();
        }
        else {
          _this.options.onEnter($(this));
        }
        $("#jHueGenericAutocomplete").hide();
        _hiveAutocompleteSelectedIndex = -1;
      }
    });

    if (_this.options.showOnFocus){
      _el.on("focus", function(){
        showAutocomplete();
      });
    }

    var _pauseBlur = false;

    _el.blur(function () {
      if (!_pauseBlur) {
        $(document.body).off("contextmenu");
        $("#jHueGenericAutocomplete").hide();
        _this.options.onBlur();
      }
    });

    var BASE_PATH = "/beeswax/api/autocomplete/";
    if (_this.options.serverType == "IMPALA"){
      BASE_PATH = "/impala/api/autocomplete/";
    }
    if (_this.options.serverType == "SOLR"){
      BASE_PATH = "/indexer/api/autocomplete/";
    }
    var _currentFiles = [];

    function showAutocomplete(callback) {
      var path = _el.val();
      if (_this.options.startingPath != ''){
        path = _this.options.startingPath + path;
      }
      var autocompleteUrl = BASE_PATH;

      if (path != "" && path.indexOf(".") == -1) {
        path = "";
      }

      if (path != "" && path.lastIndexOf(".") != path.length - 1) {
        path = path.substring(0, (_this.options.startingPath + _el.val()).lastIndexOf("."));
      }

      if (_this.options.serverType != "SOLR") {
        autocompleteUrl += path.replace(/\./g, "/");
      }

      $.getJSON(autocompleteUrl, function (data) {
        if (data.error == null) {
          _currentFiles = [];

          var _ico = "";
          var _iterable = [];
          var _isSkipColumns = false;

          if (_this.options.serverType == "SOLR") {
            _iterable = data.collections;
            _ico = "fa-search";
          }
          else {
            if (data.databases != null) { // it's a db
              _iterable = data.databases;
              _ico = "fa-database";
            }
            else if (data.tables_meta != null) { // it's a table
              _iterable = $.map(data.tables_meta, function (tablesMeta) {
                return tablesMeta.name;
              });
              _ico = "fa-table";
            }
            else {
              if (!_this.options.skipColumns) {
                _iterable = data.columns;
                _ico = "fa-columns";
              }
              else {
                _isSkipColumns = true;
              }
            }
          }

          var firstSolrCollection = false;
          var firstSolrConfig = false;

          if (!_isSkipColumns) {
            $(_iterable).each(function (cnt, item) {
              if (_this.options.serverType == "SOLR") {
                if (item.isCollection && !firstSolrCollection) {
                  _currentFiles.push('<li class="hiveAutocompleteItem" data-value="collections.*" title="collections.*"><i class="fa fa-search-plus"></i> collections.*</li>');
                  firstSolrCollection = true;
                }
                if (item.isConfig) {
                  _ico = 'fa-cog';
                  if (!firstSolrConfig) {
                    _currentFiles.push('<li class="hiveAutocompleteItem" data-value="configs.*" title="configs.*"><i class="fa fa-cogs"></i> configs.*</li>');
                    firstSolrConfig = true;
                  }
                }
                _currentFiles.push('<li class="hiveAutocompleteItem" data-value="' + item.name + '" title="' + item.name + '"><i class="fa ' + _ico + '"></i> ' + item.name + '</li>');
              }
              else {
                _currentFiles.push('<li class="hiveAutocompleteItem" data-value="' + item + '" title="' + item + '"><i class="fa ' + _ico + '"></i> ' + item + '</li>');
              }
            });

            $("#jHueGenericAutocomplete").css("top", _el.offset().top + _el.outerHeight() - 1).css("left", _el.offset().left).width(_el.outerWidth() - 4);
            $("#jHueGenericAutocomplete").find("ul").empty().html(_currentFiles.join(""));
            $("#jHueGenericAutocomplete").find("li").on("click", function (e) {
              smartTooltipMaker();
              e.preventDefault();
              var item = $(this).text().trim();
              var path = autocompleteUrl.substring(BASE_PATH.length);

              if ($(this).html().indexOf("search") > -1 || $(this).html().indexOf("cog") > -1) {
                if ($(this).html().indexOf("search") > -1 && $(this).html().indexOf("search-plus") == -1) {
                  _el.val("collections." + item);
                }
                else if ($(this).html().indexOf("cog") > -1 && $(this).html().indexOf("cogs") == -1) {
                  _el.val("configs." + item);
                }
                else {
                  _el.val(item);
                }
                _this.options.onPathChange(_el.val());
                $("#jHueGenericAutocomplete").hide();
                _hiveAutocompleteSelectedIndex = -1;
                _this.options.onEnter(_el);
              }

              if ($(this).html().indexOf("database") > -1) {
                _el.val(item + ".");
                _this.options.onPathChange(_el.val());
                showAutocomplete();
              }

              if ($(this).html().indexOf("table") > -1){
                if (_el.val().indexOf(".") > -1){
                  if (_el.val().match(/\./gi).length == 1){
                    _el.val(_el.val().substring(0, _el.val().lastIndexOf(".") + 1) + item);
                  }
                  else {
                    _el.val(_el.val().substring(0, _el.val().indexOf(".") + 1) + item);
                  }
                }
                else {
                  if (_this.options.rewriteVal) {
                    _el.val(item);
                  }
                  else {
                    _el.val(_el.val() + item);
                  }
                }
                if (! _this.options.skipColumns){
                  _el.val(_el.val() + ".");
                }
                _this.options.onPathChange(_el.val());
                if (! _this.options.skipColumns) {
                  showAutocomplete();
                }
                else {
                  _this.options.onEnter(_el);
                  $("#jHueGenericAutocomplete").hide();
                  _hiveAutocompleteSelectedIndex = -1;
                }
              }

              if ($(this).html().indexOf("columns") > -1){
                if (_el.val().match(/\./gi).length > 1){
                  _el.val(_el.val().substring(0, _el.val().lastIndexOf(".") + 1) + item);
                }
                else {
                  _el.val(_el.val() + "." + item);
                }
                $("#jHueGenericAutocomplete").hide();
                _hiveAutocompleteSelectedIndex = -1;
                _this.options.onEnter(_el);
              }

            });
            $("#jHueGenericAutocomplete").show();
            window.setTimeout(function(){
              setHueBreadcrumbCaretAtEnd(_this.element);
            }, 100)
            if ("undefined" != typeof callback) {
              callback();
            }
          }
        }
      });
    }

    $(document).on("mouseenter", ".hiveAutocompleteItem", function () {
      _pauseBlur = true;
    });

    $(document).on("mouseout", ".hiveAutocompleteItem", function () {
      _pauseBlur = false;
    })

    function guessHivePath(lastChars) {
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
          showAutocomplete();
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
      console.warn("$(elem).jHueGenericAutocomplete() is a preferred call method.");
    }
    $(options.element).jHueGenericAutocomplete(options);
  };

})(jQuery, window, document);
