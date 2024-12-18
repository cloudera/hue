$(document).ready(function(){
  var $editUserComponents = $('#editUserComponents');

  $editUserComponents.find("#id_groups").jHueSelector({
    selectAllLabel: "Select all",
    searchPlaceholder: "Search",
    noChoicesFound: "No groups found. <a href='/useradmin/groups/new'>Create a new group now &raquo;</a>",
    width:618,
    height:240
  });


  $editUserComponents.find('#editForm').attr('action', window.location.pathname.substr((window.HUE_BASE_URL + '/hue').length).replace(/\/$/, ''));
  $editUserComponents.find('#editForm').ajaxForm({
    dataType:  'json',
    success: function(data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.url) {
        huePubSub.publish('open.link', data.url);
        huePubSub.publish('hue.global.info', {
          message: "User information updated correctly"
        });
      }
    }
  });

 var currentStep = "step1";

  function showStep(step) {
    currentStep = step;
    if (step != "step1") {
      $editUserComponents.find(".backBtn").removeClass("disabled");
    } else {
      $editUserComponents.find(".backBtn").addClass("disabled");
    }

    if (step != $editUserComponents.find(".stepDetails:last").attr("id")) {
      $editUserComponents.find(".nextBtn").removeClass("disabled");
    } else {
      $editUserComponents.find(".nextBtn").addClass("disabled");
    }

    $editUserComponents.find("a.step").parent().removeClass("active");
    $editUserComponents.find("a.step[data-step=" + step + "]").parent().addClass("active");
    $editUserComponents.find(".stepDetails").hide();
    $editUserComponents.find("#" + step).show();
  }

  function validateStep(step) {
    var proceed = true;
    $editUserComponents.find("#" + step).find("[validate=true]").each(function () {
      if ($(this).val().trim() == "") {
        proceed = false;
        router(step);
        $(this).parents(".control-group").addClass("error");
        $(this).parent().find(".help-inline").remove();
        $(this).after("<span class=\"help-inline\"><strong>This field is required.</strong></span>");
      }
    });
    return proceed;
  }

  function router(step) {
    switch (step) {
      case 'step1':
        showStep('step1');
        break;
      case 'step2':
        if (validateStep('step1')){
          showStep('step2');
        }
        break;
      case 'step3':
        if (validateStep('step1') && validateStep('step2')){
          showStep('step3');
        }
        break;
    }
  }

  $editUserComponents.find(".step").on('click', function () {
    router($(this).data('step'));
  });

  $editUserComponents.find(".backBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 - 1);
    if (nextStep >= 1) {
      router('step' + nextStep);
    }
  });

  $editUserComponents.find(".nextBtn").click(function () {
    var nextStep = (currentStep.substr(4) * 1 + 1);
    if (nextStep <= $(".step").length) {
      router('step' + nextStep);
    }
  });

  $editUserComponents.find("[validate=true]").change(function () {
    $(this).parents(".control-group").removeClass("error");
    $(this).parent().find(".help-inline").remove();
  });

});
