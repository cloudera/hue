$(document).ready(function(){
 var currentStep = "step1";
  var $editUserComponents = $('#editUserComponents');
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
});
