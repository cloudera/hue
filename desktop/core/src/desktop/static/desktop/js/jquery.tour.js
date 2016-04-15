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
 * jHue tour plugin
 * Optionally depends on $.totalstorage for progress checking and $.jHueNotify for error notification
 * Can be instantiated with
 $.jHueTour({
        tours: [  <-- array, the tours available for this page
          {
            name: "xxxx", <-- unique tour name  (location.pathname scope)
            desc: "Desc yyyy", <-- the label shown on the question mark
            path: "beeswax/*", <-- string for the path to show this tour on
            steps: [ <-- array, steps of the tour
              {
                arrowOn: "a[href='/beeswax']", <-- the element relative to the popover is positioned
                expose: ".navbar-fixed-top", <-- optional, the exposed object. if not present, arrowOn will be exposed
                title: "Welcome to Beeswax!", <-- popover title
                content: "This is a tour of the Beeswax app. <br/><b>HTML</b> is supported <em>too!</em>", <-- popover content, html enable
                placement: "bottom", <-- popover placement
                left: "100px", <-- popover absolute position (css string)
                top: -20 <-- popover relative position (it adds that amount of pixels to the popover calculated position)
                visitUrl: "blabla?tour=hello" <-- overrides everything, redirects to specific url
              },
              {
                arrowOn: ".subnav-fixed",
                title: "Beeswax sections",
                content: "There are several sections in the Beeswax app",
                placement: "bottom",
                left: "100px"
              }, ...
            ],
            video: "http://player.vimeo.com/xxxxx", <-- instead of the steps you can specify a video and it will be displayed in a modal
            blog: "http://gethue.com/yyyyy" <-- if specified, a link to this with a "Read more about it..." label will be placed under the video in the modal. if video is empty, the link will be automagically opened
          }, ...
        ]
      });

  Calling $.jHueTour({tours: [...]}) more than once will merge the tour data, so you can keep adding tours dynamically to the same page

  You can interact with:
  - $.jHueTour("start") / $.jHueTour("show") / $.jHueTour("play") : starts the first available tour
  - $.jHueTour("stop") / $.jHueTour("close") / $.jHueTour("hide") / $.jHueTour("stop") : starts the first available tour
  - $.jHueTour("reset") : removes stored tours and history
  - $.jHueTour("clear") : removes current tours
  - $.jHueTour("http://remote/hue/tour.hue") : loads a remote tour
  - $.jHueTour("tourName", 1) : loads tour name and start at step 1
  - $.jHueTour() : returns the available tours
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueTour",
    defaults = {
      labels: {
        AVAILABLE_TOURS: "Available tours",
        NO_AVAILABLE_TOURS: "None for this page",
        MORE_INFO: "Read more about it...",
        TOOLTIP_TITLE: "Demo tutorials"
      },
      tours: [],
      showRemote: false,
      hideIfNoneAvailable: true
    };

  function Plugin(element, options) {
    this.element = element;
    if (typeof jHueTourGlobals !== undefined) {
      var extendedDefaults = $.extend({}, defaults, jHueTourGlobals);
      extendedDefaults.labels = $.extend({}, defaults.labels, jHueTourGlobals.labels);
      this.options = $.extend({}, extendedDefaults, options);
      this.options = $.extend({}, defaults, this.options);
    }
    else {
      this.options = $.extend({}, defaults, options);
    }
    this._defaults = defaults;
    this._name = pluginName;
    this.currentTour = {
      name: "",
      path: "",
      desc: "",
      remote: false,
      steps: [],
      shownStep: 0,
      video: "",
      blog: ""
    };
    this.init();
  }

  Plugin.prototype.init = function () {
    var _this = this;
    _this.initQuestionMark();
    var _tourMask = $("<div>").attr("id", "jHueTourMask");
    _tourMask.width($(document).width()).height($(document).height())
    _tourMask.click(function () {
      _this.closeCurtains();
    });
    _tourMask.appendTo($("body"));

    $(document).on("keyup", function (e) {
      var _code = (e.keyCode ? e.keyCode : e.which);
      if ($("#jHueTourMask").is(":visible") && _code == 27) {
        _this.performOperation("close");
      }
    });
  };

  Plugin.prototype.initQuestionMark = function () {
    var _this = this;
    $("#jHueTourFlag").remove();
    var _questionMark = $("<a>").attr("id", "jHueTourFlag").addClass("pointer").html('<i class="fa fa-flag-checkered" style=""></i>');
    _questionMark.tooltip({
      placement: "bottom",
      title: _this.options.labels.TOOLTIP_TITLE
    });
    if ($.totalStorage("jHueTourExtras") != null) {
      var _newTours = [];
      $.each(_this.options.tours, function (cnt, tour) {
        if (tour.remote == undefined || !tour.remote) {
          _newTours.push(tour);
        }
      });
      _this.options.tours = _newTours.concat($.totalStorage("jHueTourExtras"));
    }

    var _toursHtml = '<ul class="nav nav-pills nav-stacked" style="margin-bottom: 0">'
      var _added = 0;
      $.each(_this.options.tours, function (ctn, tour) {
        if (tour.path === undefined || RegExp(tour.path).test(location.pathname)) {
          var _tourDone = '';
          var _removeTour = '';
          var _extraIcon = '<i class="fa fa-flag"></i> ';
          if ($.totalStorage !== undefined) {
            var _key = location.pathname;
            if (tour.path !== undefined && tour.path != "") {
              _key = tour.path;
            }
            _key += "_" + tour.name;
            if ($.totalStorage("jHueTourHistory") != null && $.totalStorage("jHueTourHistory")[_key] == true) {
              _tourDone = '<div style="color:green;float:right;margin:4px"><i class="fa fa-check-circle"></i></div>';
            }
          }
          if (tour.remote) {
            _removeTour = '<div style="color:red;float:right;margin:4px;cursor: pointer" onclick="javascript:$.jHueTour(\'remove_' + tour.name + '\')"><i class="fa fa-times-circle"></i></div>';
          }

          var _link = '<a href="javascript:$.jHueTour(\'' + tour.name + '\', 1)" style="padding:2px">';

          if (typeof tour.video != "undefined" && tour.video != null && tour.video != ""){
            _extraIcon = '<i class="fa fa-youtube-play"></i> ';
          }
          else if (typeof tour.blog != "undefined" && tour.blog != null && tour.blog != ""){
            _extraIcon = '<i class="fa fa-external-link"></i> ';
            _link = '<a href="' + tour.blog + '" target="_blank" style="padding:2px">';
          }
          _toursHtml += '<li>' + _removeTour + _tourDone + _link + _extraIcon + tour.desc + '</a></li>';
          _added++;
        }
      });

      if (_added == 0) {
        if (_this.options.hideIfNoneAvailable){
          _questionMark.css("display", "none");
        }
        else {
          _toursHtml += '<li>' + _this.options.labels.NO_AVAILABLE_TOURS + '</li>';
        }
      }

      if (_this.options.showRemote){
        _toursHtml += '<li>' +
          ' <div class="input-append" style="margin-top: 10px">' +
          '  <input id="jHueTourRemoteTutorial" style="width:70%" type="text" placeholder="URL">' +
          '  <button id="jHueTourRemoteTutorialBtn" class="btn" type="button" onclick="javascript:$.jHueTour($(\'#jHueTourRemoteTutorial\').val())">' +
          '  <i class="fa fa-cloud-download"></i></button>' +
          ' </div>' +
          '</li>';
      }
    _toursHtml += '</ul>';

    _questionMark.click(function () {

      var _closeBtn = $("<a>");
      _closeBtn.html('<i class="fa fa-times"></i>').css("cursor", "pointer").css("padding", "5px").css("padding-left", "17px").css("padding-right", "7px").css("float", "right").css("margin-top", "-4px").css("margin-right", "-6px");
      _closeBtn.click(function () {
        $(".popover").remove();
        $(document).off("keyup");
        $(document).off("click");
      });

      _questionMark.popover("destroy").popover({
        title: _this.options.labels.AVAILABLE_TOURS,
        content: _toursHtml,
        html: true,
        trigger: "click",
        placement: "bottomRight"
      }).popover("show");
      if ($(".popover").position().top <= 0) {
        $(".popover").css("top", "10px");
      }

      _closeBtn.prependTo($(".popover-title"));

      $(document).on("keyup", function (e) {
        if (e.keyCode == 27) {
          _closeBtn.click();
        }
      });
      $(document).on("click", function (e) {
        if ($(e.target).parents('.popover').length == 0 && !($(e.target).hasClass("fa-flag-checkered"))) {
          _closeBtn.click();
        }
      });
    });
    _questionMark.appendTo($("#jHueTourFlagPlaceholder"));
  };

  Plugin.prototype.addTours = function (options) {
    var _this = this;
    var _addableTours = [];
    if (options.tours != null) {
      $.each(options.tours, function (cnt, tour) {
        var _add = true;
        if (_this.options.tours != null) {
          $.each(_this.options.tours, function (icnt, itour) {
            if (itour.name == tour.name) {
              _add = false;
            }
          });
        }
        if (_add) {
          _addableTours.push(tour);
        }
      });
    }
    _this.options.tours = _this.options.tours.concat(_addableTours);
  };

  Plugin.prototype.availableTours = function () {
    return this.options.tours;
  };

  Plugin.prototype.performOperation = function (operation) {
    var _this = this;
    var _op = operation.toLowerCase();
    if (_op.indexOf("http:") == 0 || _op.indexOf("https:") == 0) {
      $("#jHueTourRemoteTutorial").attr("disabled", "disabled");
      $("#jHueTourRemoteTutorialBtn").attr("disabled", "disabled");
      $.ajax({
        type: "GET",
        url: operation + "?callback=?",
        async: false,
        jsonpCallback: "jHueRemoteTour",
        contentType: "application/json",
        dataType: "jsonp",
        success: function (json) {
          if ($.totalStorage !== undefined) {
            if ($.totalStorage("jHueTourExtras") == null) {
              $.totalStorage("jHueTourExtras", []);
            }
            var _newStoredArray = [];
            if (json.tours != null) {
              _newStoredArray = json.tours;
              $.each($.totalStorage("jHueTourExtras"), function (cnt, tour) {
                var _found = false;
                $.each(json.tours, function (icnt, itour) {
                  if (itour.name == tour.name) {
                    _found = true;
                  }
                });
                if (!_found) {
                  _newStoredArray.push(tour);
                }
              });
            }
            $.totalStorage("jHueTourExtras", _newStoredArray);
          }
          $("#jHueTourFlag").popover("destroy");
          _this.initQuestionMark();
          $("#jHueTourFlag").click();
        },
        error: function (e) {
          $(document).trigger("error", e.message);
          $("#jHueTourRemoteTutorial").removeAttr("disabled");
          $("#jHueTourRemoteTutorialBtn").removeAttr("disabled");
        }
      });
    }

    if (_op.indexOf("remove_") == 0) {
      var _tourName = _op.substr(7);
      if ($.totalStorage !== undefined) {
        var _newStoredArray = [];
        $.each($.totalStorage("jHueTourExtras"), function (cnt, tour) {
          if (tour.name != _tourName) {
            _newStoredArray.push(tour);
          }
        });
        $.totalStorage("jHueTourExtras", _newStoredArray);
        $("#jHueTourFlag").popover("destroy");
        _this.initQuestionMark();
        $("#jHueTourFlag").click();
      }
    }

    if (_op == "start" || _op == "show" || _op == "play") {
      if (_this.options.tours.length > 0 && _this.currentTour.name == "") {
        _this.currentTour.name = _this.options.tours[0].name;
        _this.currentTour.path = _this.options.tours[0].path;
        _this.currentTour.steps = _this.options.tours[0].steps;
        _this.currentTour.desc = _this.options.tours[0].desc;
        _this.currentTour.video = _this.options.tours[0].video;
        _this.currentTour.blog = _this.options.tours[0].blog;
      }
      this.showStep(1);
    }

    if (_op == "reset") {
      if ($.totalStorage !== undefined) {
        $.totalStorage("jHueTourHistory", null);
        $.totalStorage("jHueTourExtras", null);
      }
    }

    if (_op == "clear") {
      _this.options.tours = [];
    }

    if (_op == "end" || _op == "hide" || _op == "close" || _op == "stop") {
      _this.closeCurtains();
    }
  };

  Plugin.prototype.closeCurtains = function () {
    $(".popover").remove();
    $(".jHueTourExposed").removeClass("jHueTourExposed");
    $("#jHueTourMask").hide();
  };

  Plugin.prototype.showTour = function (tourName, stepNo) {
    var _this = this;
    if (_this.options.tours != null) {
      $.each(_this.options.tours, function (cnt, tour) {
        if (tour.name == tourName && (tour.path === undefined || RegExp(tour.path).test(location.pathname))) {
          _this.currentTour.name = tour.name;
          _this.currentTour.path = tour.path;
          _this.currentTour.steps = tour.steps;
          _this.currentTour.desc = tour.desc;
          _this.currentTour.video = tour.video;
          _this.currentTour.blog = tour.blog;
          if (stepNo === undefined) {
            _this.showStep(1);
          }
          else {
            _this.showStep(stepNo);
          }
          return;
        }
      });
    }
  };

  Plugin.prototype.showStep = function (stepNo) {
    var _this = this;
    if (typeof _this.currentTour.video != "undefined" && _this.currentTour.video != null && _this.currentTour.video != "") {
      if ($("#jHueTourVideoPlayer").length == 0) {
        var _playerHTML = '<div class="modal-header">' +
            '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
            '<h3>' + _this.currentTour.desc + '</h3>' +
            '</div>' +
            '<div class="modal-body">' +
            '<iframe id="jHueTourVideoFrame" src="' + _this.currentTour.video + '?autoplay=1" width="700" height="350" frameborder="0" webkitallowfullscreen="" mozallowfullscreen="" allowfullscreen="" style="height:360px;width:640px"></iframe><div class="moreInfo">' +
            (typeof _this.currentTour.blog != "undefined" && _this.currentTour.blog != "" ? '<br/><a href="' + _this.currentTour.blog + '" target="_blank"><i class="fa fa-external-link"></i> ' + _this.options.labels.MORE_INFO + '</a>' : '') +
            '</div></div>';
        var _player = $("<div>").attr("id", "jHueTourVideoPlayer").addClass("modal").addClass("hide").addClass("fade");
        _player.html(_playerHTML);
        _player.appendTo($("body"));
      }
      else {
        $("#jHueTourVideoPlayer").find("h3").html(_this.currentTour.desc);
        $("#jHueTourVideoPlayer").find(".moreInfo").html(typeof _this.currentTour.blog != "undefined" && _this.currentTour.blog != "" ? '<a href="' + _this.currentTour.blog + '" target="_blank"><i class="fa fa-external-link"></i> ' + _this.options.labels.MORE_INFO + '</a>' : '');
        $("#jHueTourVideoFrame").attr("src", _this.currentTour.video + "?autoplay=1");
      }
      $("#jHueTourVideoPlayer").modal().modal("show");
      $("#jHueTourVideoPlayer").on("hidden", function () {
        $("#jHueTourVideoFrame").attr("src", "about:blank");
      });
    }
    else {
      if (_this.currentTour.steps[stepNo - 1] != null) {
        var _step = _this.currentTour.steps[stepNo - 1];
        _this.currentTour.shownStep = stepNo;
        var _navigation = "";

        if (_step.visitUrl != undefined) {
          location.href = _step.visitUrl;
        }

        if (_step.onShown != undefined) {
          window.setTimeout(_step.onShown, 10);
        }

        $(".popover").remove();
        $(".jHueTourExposed").removeClass("jHueTourExposed");
        if ($(".jHueTourExposed").css("position") == "relative") {
          $(".jHueTourExposed").css("position", "relative");
        }
        $("#jHueTourMask").width($(document).width()).height($(document).height()).show();

        var _closeBtn = $("<a>");
        _closeBtn.addClass("btn").addClass("btn-mini").html('<i class="fa fa-times"></i>').css("float", "right").css("margin-top", "-4px").css("margin-right", "-6px");
        _closeBtn.click(function () {
          _this.performOperation("close");
        });

        var _nextBtn = $("<a>");
        _nextBtn.addClass("btn").addClass("btn-mini").html('<i class="fa fa-chevron-circle-right"></i>').css("margin-top", "10px");
        _nextBtn.click(function () {
          _this.showStep(_this.currentTour.shownStep + 1);
        });

        var _prevBtn = $("<a>");
        _prevBtn.addClass("btn").addClass("btn-mini").html('<i class="fa fa-chevron-circle-left"></i>').css("margin-top", "10px").css("margin-right", "10px");
        _prevBtn.click(function () {
          _this.showStep(_this.currentTour.shownStep - 1);
        });

        var _arrowOn = _step.arrowOn;
        var _additionalContent = "";
        if ($(_arrowOn).length == 0 || !($(_arrowOn).is(":visible"))) {
          _arrowOn = "body";
          _additionalContent = "<b>MISSING POINTER OF STEP " + _this.currentTour.shownStep + "</b> ";
        }
        $(_arrowOn).popover('destroy').popover({
          title: _step.title,
          content: _additionalContent + _step.content + "<br/>",
          html: true,
          trigger: 'manual',
          placement: (_step.placement != "" && _step.placement != undefined) ? _step.placement : "left"
        }).popover('show');

        if (_step.top != undefined) {
          if ($.isNumeric(_step.top)) {
            $(".popover").css("top", ($(".popover").position().top + _step.top) + "px");
          }
          else {
            $(".popover").css("top", _step.top);
          }
        }

        if (_step.left != undefined) {
          if ($.isNumeric(_step.left)) {
            $(".popover").css("left", ($(".popover").position().left + _step.left) + "px");
          }
          else {
            $(".popover").css("left", _step.left);
          }
        }
        $(".popover-title").html(_step.title);
        _closeBtn.prependTo($(".popover-title"));

        if (_this.currentTour.shownStep > 1) {
          _prevBtn.appendTo($(".popover-content p"));
        }
        if (_this.currentTour.shownStep < _this.currentTour.steps.length && (_step.waitForAction == undefined || _step.waitForAction == false)) {
          _nextBtn.appendTo($(".popover-content p"));
        }

        // last step, mark tour/tutorial as done
        if ($.totalStorage !== undefined && _this.currentTour.shownStep == _this.currentTour.steps.length) {
          var _key = location.pathname;
          if (_this.currentTour.path !== undefined && _this.currentTour.path != "") {
            _key = _this.currentTour.path;
          }
          _key += "_" + _this.currentTour.name;
          var _history = $.totalStorage("jHueTourHistory");
          if (_history == null) {
            _history = {}
          }
          _history[_key] = true;
          $.totalStorage("jHueTourHistory", _history);
        }

        var _exposedElement = $((_step.expose != undefined && _step.expose != "" ? _step.expose : _arrowOn));
        if (_exposedElement.css("position") === undefined || _exposedElement.css("position") != "fixed") {
          _exposedElement.css("position", "relative");
        }
        _exposedElement.addClass("jHueTourExposed");
      }
    }
  };

  $[pluginName] = function (options, stepNo) {
    var _el = $("body");
    if (!$("body").data('plugin_' + pluginName)) {
      $("body").data('plugin_' + pluginName, new Plugin(_el, options));
    }

    if (options === undefined) {
      return $("body").data('plugin_' + pluginName).availableTours();
    }

    if (typeof options == "string") {
      if (stepNo === undefined) {
        $("body").data('plugin_' + pluginName).performOperation(options);
      }
      else if ($.isNumeric(stepNo)) {
        $("body").data('plugin_' + pluginName).showTour(options, stepNo);
      }
    }
    else if ($.isNumeric(options)) {
      $("body").data('plugin_' + pluginName).showStep(options);
    }
    else {
      $("body").data('plugin_' + pluginName).addTours(options);
    }
  };

})(jQuery, window, document);
