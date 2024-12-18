$(document).ready(function () {
  $("#saveAsBtn").click(function () {
    $("#saveAsModal").modal({
      backdrop: "static",
      keyboard: true,
      show: true
    })
  });

  $("#cancelSaveAsBtn").click(function () {
    $("#saveAsModal").modal("hide");
  });

  $('#saveForm').ajaxForm({
    dataType: 'json',
    success: function (data) {
      if (data && data.exists) {
        resetPrimaryButtonsStatus();
        huePubSub.publish('hue.global.info', {
          message: data.path + " saved correctly"
        });
      }
    }
  });

  $('#saveAsForm').ajaxForm({
    dataType: 'json',
    beforeSubmit: function (data) {
      if ($.trim($("#saveAsForm").find("input[name='path']").val()) == "") {
        $("#saveAsForm").find("input[name='path']").addClass("fieldError");
        $("#saveAsNameRequiredAlert").show();
        resetPrimaryButtonsStatus(); //globally available
        return false;
      }
      // Contents of SaveAs form is not updated. Need to do it manually
      data.forEach(dataUnit => {
        if (dataUnit.name.toLowerCase() === 'contents') {
          dataUnit.value = $('#saveForm textarea').val();
        }
      });
      return true;
    },
    success: function (data) {
      if (data && data.exists) {
        resetPrimaryButtonsStatus();
        $("#saveAsModal").modal("hide");
        huePubSub.publish('hue.global.info', {
          message: data.path + " saved correctly"
        });
      }
    }
  });

  $("#saveAsForm").find("input[name='path']").focus(function () {
    $(this).removeClass("fieldError");
    $("#saveAsNameRequiredAlert").hide();
  });

  function getBrowseButton() {
    var self = $('.pathChooser');
    return $('<a>').addClass('btn').addClass('fileChooserBtn').text('..').click(function (e) {
      e.preventDefault();
      $('#fileChooserSaveModal').jHueFileChooser({
        initialPath: $(self).val(),
        onFileChoose: function (filePath) {
          $(self).val(filePath);
        },
        onFolderChange: function (folderPath) {
          $(self).val(folderPath);
        },
        createFolder: false,
        uploadFile: false
      });
      $('#fileChooserSaveModal').slideDown();
    });

  }

  $('.pathChooser').after(getBrowseButton());


  function resizeTextarea() {
    var RESIZE_CORRECTION = 246;
    $("textarea[name='contents']").height($(window).height() - RESIZE_CORRECTION);
  }

  var _resizeTimeout = -1;
  $(window).on("resize", function () {
    window.clearTimeout(_resizeTimeout);
    _resizeTimeout = window.setTimeout(function () {
      resizeTextarea();
    }, 100);
  });

  resizeTextarea();

});
