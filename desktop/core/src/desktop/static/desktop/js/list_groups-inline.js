$(document).ready(function () {
    var listGroupsOptionsElement = document.getElementById('listGroupsOptions');
    var listGroupsOptions = JSON.parse(listGroupsOptionsElement.textContent);

    var $groupsComponents = $('#groupsComponents');
    $(document).off('click', '#groupsComponents .groupCheck');

    var viewModel = {
        availableGroups: ko.observableArray(JSON.parse(listGroupsOptions.groups_json)),
        chosenGroups: ko.observableArray([])
    };

    ko.applyBindings(viewModel, $groupsComponents[0]);
    var aoColumns = [
        { "sWidth": "20%" },
        { "sWidth": "20%" },
        null
    ];

    if (window.USER_IS_ADMIN) {
        aoColumns.unshift({ "bSortable": false }); 
    } else {
        aoColumns.unshift({});
    }
    
    var dt = $groupsComponents.find('.datatables').dataTable({
        "sPaginationType": "bootstrap",
        "iDisplayLength": 100,
        "bLengthChange": false,
        "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
        "bInfo": false,
        "bFilter": true,
        "bAutoWidth": false,
        "aoColumns": aoColumns,
        "oLanguage": {
            "sEmptyTable": "No data available",
            "sZeroRecords": "No matching records",
        }
    });

    $groupsComponents.find('.delete-group form').ajaxForm({
        dataType: 'json',
        success: function (data) {
            $groupsComponents.find(".delete-group").modal("hide");
            huePubSub.publish('hue.global.info', {
                message: "The groups were deleted."
            });
            if (data && data.url) {
                huePubSub.publish('open.link', data.url);
            }
        }
    });

    $groupsComponents.find(".filter-input").jHueDelayedInput(function () {
        if (dt) {
            dt.fnFilter($groupsComponents.find(".filter-input").val().toLowerCase());
        }
    });

    $groupsComponents.find('[data-rel="tooltip"]').tooltip({
        placement: 'right'
    });

    $groupsComponents.find(".dataTables_wrapper").css("min-height", "0");
    $groupsComponents.find(".dataTables_filter").hide();

    $groupsComponents.find(".select-all").click(function () {
        if ($(this).attr("checked")) {
            $(this).removeAttr("checked").removeClass("fa-check");
            $groupsComponents.find(".groupCheck").removeClass("fa-check").removeAttr("checked");
        }
        else {
            $(this).attr("checked", "checked").addClass("fa-check");
            $groupsComponents.find(".groupCheck").addClass("fa-check").attr("checked", "checked");
        }
        toggleActions();
    });

    $(document).on('click', '#groupsComponents .groupCheck', function () {
        if ($(this).attr("checked")) {
            $(this).removeClass("fa-check").removeAttr("checked");
        }
        else {
            $(this).addClass("fa-check").attr("checked", "checked");
        }
        toggleActions();
    });

    function toggleActions() {
        if ($groupsComponents.find(".groupCheck[checked='checked']").length > 0) {
            $groupsComponents.find(".delete-group-btn").removeAttr("disabled");
        }
        else {
            $groupsComponents.find(".delete-group-btn").attr("disabled", "disabled");
        }
    }

    $groupsComponents.find(".delete-group-btn").click(function () {
        viewModel.chosenGroups.removeAll();

        $groupsComponents.find(".hue-checkbox[checked='checked']").each(function (index) {
            viewModel.chosenGroups.push($(this).data("name").toString()); // needed for numeric group names
        });

        $groupsComponents.find(".delete-group").modal("show");
    });

    $groupsComponents.find("a[data-row-selector='true']").jHueRowSelector();
});