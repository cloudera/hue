var LiveDebugging = function () {
  var self = this;

  self.forcedDebug = ko.observable();
  self.forcedDebug.subscribe(function (oldValue) {
    if (oldValue != null) {
      self.setLogLevel(!oldValue);
    }
  }, this, "beforeChange");

  self.getDebugLevel = function () {
    $.get("/desktop/get_debug_level", function (data) { self.forcedDebug(data.debug_all); });
  };

  self.setLogLevel = function (set_debug) {
    var _url = "";
    if (set_debug) {
      _url = "/desktop/set_all_debug";
    } else {
      _url = "/desktop/reset_all_debug";
    }

    $.post(_url, {}, function (data) {
      if (data, status != 0) {
        huePubSub.publish('hue.global.error', { message: data.message });
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      huePubSub.publish('hue.global.error', { message: xhr.responseText });
    });
  };
}

$(document).ready(function () {
  var viewModel = new LiveDebugging();
  ko.applyBindings(viewModel, $("#logsComponents")[0]);

  viewModel.getDebugLevel();

  resizeScrollingLogs();

  var resizeTimeout = -1;
  $(window).resize(function () {
    window.clearTimeout(resizeTimeout);
    resizeTimeout = window.setTimeout(function () {
      resizeScrollingLogs();
    }, 200);
  });

  $("#hue-logs-search-query").jHueDelayedInput(function () {
    filterLogs($("#hue-logs-search-query").val());
  }, 500);

  if ("" != "") {
    filterLogs("");
  }

  function resizeScrollingLogs() {
    var _el = $("#hue-logs");
    if (_el.length > 0) {
      if (!$.browser.msie) {
        _el.css("overflow-y", "").css("height", "");
      }
      var heightAfter = 0;
      _el.nextAll(":visible").each(function () {
        heightAfter += $(this).outerHeight(true);
      });
      if (_el.height() > ($(window).height() - _el.offset().top - heightAfter)) {
        _el.css("overflow-y", "auto").height($(window).height() - _el.offset().top - heightAfter - 30);
      }
    }
  }

  function filterLogs(query) {
    $("#hue-logs-search-query").removeClass("notFound");
    if ($.trim(query) == "") {
      $("#hue-logs").scrollTop(0);
      return false;
    }
    $("pre.highlighted").removeClass("highlighted");
    var found = false;
    $("#hue-logs pre").each(function () {
      var _el = $(this);
      if (_el.text().toLowerCase().replace(/\s/g, "").indexOf(query.toLowerCase().replace(/\s/g, "")) > -1) {
        _el.addClass("highlighted");
        $("#hue-logs").scrollTop(_el.offset().top - $("#hue-logs").position().top - 100);
        found = true;
        return false;
      }
    });
    if (!found) {
      $("#hue-logs-search-query").addClass("notFound");
      $("#hue-logs").scrollTop(0);
    }
  }

  $("#wrapLogs").on("change", function () {
    if ($(this).is(":checked")) {
      $("pre").removeClass("nowrap");
    }
    else {
      $("pre").addClass("nowrap");
    }
  });
});