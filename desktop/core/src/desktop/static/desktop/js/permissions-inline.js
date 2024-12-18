
$(document).ready(function () {
  var $permissionsComponents = $('#permissionsComponents');
  var dt = $permissionsComponents.find(".datatables").dataTable({
    "bPaginate": false,
    "bLengthChange": false,
    "bInfo": false,
    "bFilter": true,
    "aoColumns": [
      null,
      null,
      null
    ],
    "oLanguage": {
      "sEmptyTable": "No data available",
      "sZeroRecords": "No matching records",
    }
  });

  $permissionsComponents.find(".filter-input").jHueDelayedInput(function () {
    if (dt) {
      dt.fnFilter($permissionsComponents.find(".filter-input").val().toLowerCase());
    }
  });

  $permissionsComponents.find('[data-rel="tooltip"]').tooltip({
    placement: 'right'
  });

  $permissionsComponents.find(".dataTables_wrapper").css("min-height", "0");
  $permissionsComponents.find(".dataTables_filter").hide();

  $permissionsComponents.find("a[data-row-selector='true']").jHueRowSelector();
});
