routie.setPathname('/about');
var AdminWizardViewModel = function () {
  var self = this;

  self.connectors = ko.observableArray();
  self.isInstallingSample = ko.observable(false);

  self.installConnectorDataExample = function (connector, event) {
    self.isInstallingSample(true);
    $.post("/notebook/install_examples", {
      connector: connector.id
    }, function (data) {
      if (data.message) {
        huePubSub.publish('hue.global.info', { message: data.message });
      }
      if (data.errorMessage) {
        huePubSub.publish('hue.global.error', { message: data.errorMessage });
      }
      if (data.status == 0 && $(event.target).data("is-connector")) {
        huePubSub.publish('cluster.config.refresh.config');
      }
    }).always(function (data) {
      self.isInstallingSample(false);
    });
  }
};

function installConnectorExample() {
  var button = $(this);
  $(button).button('loading');
  $.post(button.data("sample-url"), function (data) {
    if (data.status == 0) {
      if (data.message) {
        huePubSub.publish('hue.global.info', { message: data.message });
      } else {
        huePubSub.publish('hue.global.info', { message: 'Examples refreshed' });
      }
      if ($(button).data("is-connector")) {
        huePubSub.publish('cluster.config.refresh.config');
      }
    } else {
      huePubSub.publish('hue.global.error', { message: data.message });
    }
  })
    .always(function (data) {
      $(button).button('reset');
    });
}

$(document).ready(function () {

  var adminWizardViewModel = new AdminWizardViewModel();
  ko.applyBindings(adminWizardViewModel, $('#adminWizardComponents')[0]);

  function checkConfig() {
    $.get("/desktop/debug/check_config", function (response) {
      $("#check-config-section .spinner").css({
        'position': 'absolute',
        'top': '-100px'
      });
      $("#check-config-section .info").html(response);
      $("#check-config-section .info").removeClass('hide');
    })
      .fail(function () {
        huePubSub.publish('hue.global.error', { message: 'Check config failed: ' });
      });
  }

  $("[rel='popover']").popover();


  $(".installBtn").click(installConnectorExample);

  $(".installAllBtn").click(function () {
    var button = $(this);
    $(button).button('loading');
    var calls = jQuery.map($(button).data("sample-data"), function (app) {
      return $.post($(button).data("sample-url"), { data: app }, function (data) {
        if (data.status != 0) {
          huePubSub.publish('hue.global.error', { message: data.message });
        }
      });
    });
    $.when.apply(this, calls)
      .then(function () {
        huePubSub.publish('hue.global.info', { message: 'Examples refreshed' });
      })
      .always(function (data) {
        $(button).button('reset');
      });
  });

  var currentStep = "step1";

  routie({
    "step1": function () {
      showStep("step1");
    },
    "step2": function () {
      showStep("step2");
    },
    "step3": function () {
      showStep("step3");
    },
    "step4": function () {
      showStep("step4");
    }
  });

  if (window.location.hash === '') {
    checkConfig();
  }

  function showStep(step) {
    if (window.location.hash === '#step1') {
      checkConfig();
    }

    currentStep = step;
    if (step != "step1") {
      $("#backBtn").removeClass("disabled");
    } else {
      $("#backBtn").addClass("disabled");
    }

    if (step != $(".stepDetails:last").attr("id")) {
      $("#nextBtn").removeClass("hide");
      $("#doneBtn").addClass("hide");
    } else {
      $("#nextBtn").addClass("hide");
      $("#doneBtn").removeClass("hide");
    }

    $("a.step").parent().removeClass("active");
    $("a.step[href='#" + step + "']").parent().addClass("active");
    if (step == "step4") {
      $("#lastStep").parent().addClass("active");
    }
    $(".stepDetails").hide();
    $("#" + step).show();
  }

  $("#backBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 - 1);
    if (nextStep >= 1) {
      routie("step" + nextStep);
    }
  });

  $("#nextBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 + 1);
    if (nextStep <= $(".step").length) {
      routie("step" + nextStep);
    }
  });

  $("#doneBtn").click(function () {
    huePubSub.publish('open.link', "/");
  });

  $(".updatePreferences").click(function () {
    $.post("/about/update_preferences", $("input").serialize(), function (data) {
      if (data.status == 0) {
        huePubSub.publish('hue.global.info', { message: 'Configuration updated' });
      } else {
        huePubSub.publish('hue.global.error', { message: data.data });
      }
    });
  });

  $("#updateSkipWizard").prop('checked', $.cookie("hueLandingPage", { path: "/" }) == "home");

  $("#updateSkipWizard").change(function () {
    $.cookie("hueLandingPage", this.checked ? "home" : "wizard", {
      path: "/",
      secure: window.location.protocol.indexOf('https') > -1
    });
  });
});