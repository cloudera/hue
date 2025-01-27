$(document).ready(function () {
  var $editPermissionsComponents = $('#editPermissionsComponents');
  $("#id_groups").jHueSelector({
    selectAllLabel: "Select all",
    searchPlaceholder: "Search",
    noChoicesFound: "No groups found.",
    width: 600,
    height: 500
  });
  $editPermissionsComponents.find('#editForm').ajaxForm({
    dataType: 'json',
    success: function (data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.url) {
        huePubSub.publish('open.link', data.url);
        huePubSub.publish('hue.global.info', {
          message: "Permission information updated correctly"
        });
      }
    }
  });
});
