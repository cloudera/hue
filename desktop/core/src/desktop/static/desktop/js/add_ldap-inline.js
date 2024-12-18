$(document).ready(function () {
  var $addLdapUsersComponents = $('#addLdapUsersComponents');
  $addLdapUsersComponents.find("#id_groups").jHueSelector({
    selectAllLabel: "Select all",
    searchPlaceholder: "Search",
    noChoicesFound: "No groups found. <a href='/useradmin/groups/new'>Create a new group now &raquo;</a>",
    width: 618,
    height: 240
  });
  $addLdapUsersComponents.find('#syncForm').ajaxForm({
    dataType: 'json',
    success: function (data) {
      if (data && data.status == -1) {
        renderUseradminErrors(data.errors);
      }
      else if (data && data.status === 0) {
        huePubSub.publish('open.link', '/useradmin/users');
        huePubSub.publish('hue.global.info', {
          message: "User added/synced correctly"
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
