$(document).ready(function () {
  var $editGroupComponents = $('#editGroupComponents');

  $("#id_members").jHueSelector({
    selectAllLabel: "Select all",
    searchPlaceholder: "Search",
    noChoicesFound: "No users found. <a href='/useradmin/users/new'>Create a new user now &raquo;</a>",
    width: 600,
    height: 240
  });
  $("#id_permissions").jHueSelector({
    selectAllLabel: "Select all",
    searchPlaceholder: "Search",
    noChoicesFound: "No permissions found.",
    width: 600,
    height: 240
  });
  $editGroupComponents.find('#editForm').ajaxForm({
    dataType: 'json',
    success: function (data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.url) {
        huePubSub.publish('open.link', data.url);
        huePubSub.publish('hue.global.info', {
          message: "Group information updated correctly"
        });
      }
    },
    error: function (data) {
      huePubSub.publish('hue.global.error', {
        message: data.responseJSON['message']
      });
    }
  });
});
