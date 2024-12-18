

$(document).ready(function () {
    var listUsersOptionsElement = document.getElementById('listUsersOptions');
    listUsersOptions = JSON.parse(listUsersOptionsElement.textContent);
    var $usersComponents = $('#usersComponents');
    $(document).off('click', '#usersComponents .userCheck');
    var viewModel = {
        availableUsers: ko.observableArray(JSON.parse(listUsersOptions.users_json)),
        chosenUsers: ko.observableArray([])
    };

    ko.applyBindings(viewModel, $usersComponents[0]);

    var dt = $usersComponents.find('.datatables').dataTable({
        "sPaginationType": "bootstrap",
        "iDisplayLength": 100,
        "bLengthChange": false,
        "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
        "bInfo": false,
        "bFilter": true,
        "aoColumns": [
            { "bSortable": false },
            null,
            null,
            null,
            null,
            null,
            null,
            null,
            { "sType": "date" },
        ],
        "oLanguage": {
            "sEmptyTable": "No data available",
            "sZeroRecords": "No matching records",
        }
    });

    $usersComponents.find(".filter-input").jHueDelayedInput(function () {
        if (dt) {
            dt.fnFilter($usersComponents.find(".filter-input").val().toLowerCase());
        }
    });

    $usersComponents.find('[data-rel="tooltip"]').tooltip({
        placement: 'right'
    });

    $usersComponents.find('.delete-user form').ajaxForm({
        dataType: 'json',
        success: function (data) {
            $usersComponents.find(".delete-user").modal("hide");
            huePubSub.publish('hue.global.info', {
                message: "The users were deleted."
            });
            if (data && data.url) {
                huePubSub.publish('open.link', data.url);
            }
        },
        error: function (response, status, err) {
            $usersComponents.find(".delete-user").modal("hide");
            if (response.responseJSON && response.responseJSON.message && response.status == 401) {
                huePubSub.publish('hue.global.error', {
                    message: response.responseJSON.message
                });
            }
            else {
                huePubSub.publish('hue.global.error', {
                    message: "An unknown error has occurred while deleting the user. Please try again."
                });
            }
        }
    });

    $usersComponents.find(".dataTables_wrapper").css("min-height", "0");
    $usersComponents.find(".dataTables_filter").hide();

    $usersComponents.find(".confirmationModal").click(function () {
        var _this = $(this);
        $.ajax({
            url: _this.data("confirmation-url"),
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function (data) {
                $usersComponents.find(".sync-ldap").html(data);
                $usersComponents.find('.sync-ldap form').ajaxForm({
                    dataType: 'json',
                    beforeSend: function (xhr) {
                        $usersComponents.find('input[type="submit"]').attr('disabled', 'disabled');
                    },
                    success: function (data) {
                        $usersComponents.find('input[type="submit"]').removeAttr("disabled");
                        if (data && data.status == -1) {
                            renderUseradminErrors(data.errors);
                        }
                        else if (data && data.url) {
                            $usersComponents.find(".sync-ldap").modal("hide");
                            huePubSub.publish('hue.global.info', {
                                message: "The users and groups were updated correctly."
                            });
                            huePubSub.publish('open.link', data.url);
                        }
                    },
                    error: function (data) {
                        $usersComponents.find('input[type="submit"]').removeAttr("disabled");
                        $usersComponents.find(".sync-ldap").modal("hide");
                        huePubSub.publish('hue.global.error', {
                            message: data.responseJSON['message']
                        });
                        huePubSub.publish('open.link', data.url);
                    }
                });
                $usersComponents.find(".sync-ldap").modal("show");
            }
        });
    });

    $usersComponents.find(".select-all").click(function () {
        if ($(this).attr("checked")) {
            $(this).removeAttr("checked").removeClass("fa-check");;
            $usersComponents.find(".userCheck").removeClass("fa-check").removeAttr("checked");
        }
        else {
            $(this).attr("checked", "checked").addClass("fa-check");
            $usersComponents.find(".userCheck").addClass("fa-check").attr("checked", "checked");
        }
        toggleActions();
    });

    $(document).on('click', '#usersComponents .userCheck', function () {
        if ($(this).attr("checked")) {
            $(this).removeClass("fa-check").removeAttr("checked");
        }
        else {
            $(this).addClass("fa-check").attr("checked", "checked");
        }
        toggleActions();
    });

    function toggleActions() {
        if ($usersComponents.find(".userCheck[checked='checked']").length >= 1) {
            $usersComponents.find(".delete-user-btn").removeAttr("disabled");
        }
        else {
            $usersComponents.find(".delete-user-btn").attr("disabled", "disabled");
        }
    }

    $usersComponents.find(".delete-user-btn").click(function () {
        viewModel.chosenUsers.removeAll();

        $usersComponents.find(".hue-checkbox[checked='checked']").each(function (index) {
            viewModel.chosenUsers.push($(this).data("id"));
        });

        $usersComponents.find(".delete-user").modal("show");
    });

    $usersComponents.find("a[data-row-selector='true']").jHueRowSelector();
});