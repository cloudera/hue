(function () {
    var secureOptionsElement = document.getElementById('secureOptions');
    var secureOptions = JSON.parse(secureOptionsElement.textContent);
    if (ko.options) {
        ko.options.deferUpdates = true;
    }

    huePubSub.subscribe('show.delete.privilege.modal', function () {
        $('#deletePrivilegeModal').modal('show');
    });

    var viewModel = new HiveViewModel(secureOptions);
    ko.cleanNode($('#securityHiveComponents')[0]);
    ko.applyBindings(viewModel, $('#securityHiveComponents')[0]);

    $(document).ready(function () {
        var _initialPath = viewModel.getPathHash();
        viewModel.init(_initialPath);
        $("#path").val(_initialPath);

        $(".help").popover({
            'title': "Looking for edit permissions?",
            'content': $("#help-content").html(),
            'trigger': 'click',
            'placement': 'left',
            'html': true
        });

        function setPathFromAutocomplete(path) {
            if (path.lastIndexOf(".") == path.length - 1) {
                path = path.substring(0, path.length - 1);
            }
            viewModel.assist.path(path);
            viewModel.assist.updatePathProperty(viewModel.assist.growingTree(), path, "isExpanded", true);
            viewModel.assist.fetchHivePath();
        }

        $("#path").jHueGenericAutocomplete({
            skipColumns: true,
            apiHelperUser: window.LOGGED_USERNAME,
            apiHelperType: 'hive',
            home: viewModel.assist.path(),
            onPathChange: function (path) {
                setPathFromAutocomplete(path);
            },
            onEnter: function (el) {
                setPathFromAutocomplete(el.val());
            },
            smartTooltip: "Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names"
        });

        function resizeComponents() {
            $("#path").width($(".tree-toolbar").width() - 64);
            $("#expandableTree").height($(window).height() - 260);
            $(".acl-panel-content").height($(window).height() - 240);
        }

        resizeComponents();

        $(document).on("renderedTree", function () {
            var _path = viewModel.assist.path();
            if (_path[_path.length - 1] == "/") {
                _path = _path.substr(0, _path.length - 1);
            }
            if ($("a.anchor[href^='" + _path + "']").length > 0) {
                $("#expandableTree").animate({
                    scrollTop: ($("a.anchor[href^='" + _path + "']:first").position().top + $("#expandableTree").scrollTop() - $("#expandableTree").position().top - 4) + "px"
                });
            }
        });

        $(document).on("createdRole", function () {
            $("#createRoleModal").modal("hide");
            $("#grantPrivilegeModal").modal("hide");
            $("#deletePrivilegeModal").modal("hide");
            viewModel.clearTempRoles();
            window.setTimeout(function () {
                viewModel.refreshExpandedRoles();
            }, 500);
        });

        $(document).on("deletedRole", function () {
            $("#deleteRoleModal").modal("hide");
        });

        $(document).on("changedPath", function () {
            if ($("#path").val() != viewModel.assist.path()) {
                $("#path").val(viewModel.assist.path());
            }
        });

        function showMainSection(mainSection) {
            if ($("#" + mainSection).is(":hidden")) {
                $(".mainSection").hide();
                $("#" + mainSection).show();
                highlightMainMenu(mainSection);
                viewModel.updateSectionHash(mainSection);
            }
            hueAnalytics.log('security/hive', mainSection);
        }

        function highlightMainMenu(mainSection) {
            $(".nav.nav-list li").removeClass("active");
            $("a[data-toggleSection='" + mainSection + "']").parent().addClass("active");
        }

        $("[data-toggleSection]").on("click", function () {
            showMainSection($(this).attr("data-toggleSection"));
        });

        showMainSection(viewModel.getSectionHash());

        $(document).on("showMainSection", function () {
            showMainSection(viewModel.getSectionHash());
        });

        $(document).on("showRole", function (e, role) {
            if (typeof role != "undefined" && role.name != null) {
                $("#bulkActionsModal").modal("hide");
                showMainSection("roles");
                $("html, body").animate({
                    scrollTop: ($("a[href='" + role.name() + "']").position().top - 90) + "px"
                });
            }
        });

        var _resizeTimeout = -1;
        $(window).resize(function () {
            window.clearTimeout(_resizeTimeout);
            _resizeTimeout = window.setTimeout(resizeComponents, 100);
        });

        window.onhashchange = function () {
            if (window.location.pathname.indexOf('/security/hive') > -1) {
                viewModel.assist.path(viewModel.getPathHash());
            }
        };

        $("#createRoleModal").modal({
            show: false
        });

        $("#grantPrivilegeModal").modal({
            show: false
        });

        $("#createRoleModal").on("show", function () {
            $(document).trigger("create.typeahead");
        });

        $("#createRoleModal").on("hide", function () {
            $('#jHueGenericAutocomplete').hide();
            viewModel.resetCreateRole();
        });

        $("#grantPrivilegeModal").on("hide", function () {
            viewModel.clearTempRoles();
        });

        $("#deleteRoleModal").modal({
            show: false
        });

        $("#selectedGroup").select2("val", "");
        $("#selectedGroup").change(function () {
            viewModel.list_sentry_privileges_by_authorizable();
            viewModel.list_sentry_roles_by_group();
        });

        $(document).on("addedBulkPrivileges", function () {
            huePubSub.publish('hue.global.info', { message: "The current privileges have been successfully added to the checked items." });
            $("#bulkActionsModal").modal("hide");
        });

        $(document).on("deletedBulkPrivileges", function () {
            huePubSub.publish('hue.global.info', { message: "All the privileges have been successfully removed from the checked items." });
            $("#bulkActionsModal").modal("hide");
        });

        $(document).on("syncdBulkPrivileges", function () {
            huePubSub.publish('hue.global.info', { message: "All the privileges for the checked items have been replaced with the current selection." });
            $("#bulkActionsModal").modal("hide");
        });

        $("#bulkActionsModal").modal({
            show: false
        });

        $("#bulkActionsModal").on("hidden", function () {
            viewModel.isApplyingBulk(false);
        });

        $(document).on("createTypeahead", function () {
            $("#createRoleName").typeahead({
                source: function (query) {
                    var _options = [];
                    viewModel.selectableRoles().forEach(function (item) {
                        if (item.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                            _options.push(item);
                        }
                    });
                    return _options;
                },
                minLength: 0,
                'updater': function (item) {
                    return item;
                }
            });
        });
        $(document).on('focus', '#createRoleName', function () {
            if ($("#createRoleName").data('typeahead')) {
                $("#createRoleName").data('typeahead').lookup();
            }
        });
        $(document).on("destroyTypeahead", function () {
            $('.typeahead').unbind();
            $("ul.typeahead").hide();
        });

        $(document).trigger("createTypeahead");

        $("#deletePrivilegeModal").modal({
            show: false
        });

        huePubSub.subscribe('app.gained.focus', function (app) {
            if (app === 'security_hive') {
                window.setTimeout(function () {
                    window.location.hash = viewModel.lastHash;
                    showMainSection(viewModel.getSectionHash());
                }, 0);
            }
        }, 'security_hive');
    });
})();