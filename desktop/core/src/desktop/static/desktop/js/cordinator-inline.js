var coordinatorOptionsElement = document.getElementById('coordinatorOptions');
coordinatorOptions = JSON.parse(coordinatorOptionsElement.textContent);

var viewModel = new CoordinatorEditorViewModel(
    JSON.parse(coordinatorOptions.coordinator_json), JSON.parse(coordinatorOptions.credentials_json), JSON.parse(coordinatorOptions.workflows_json), coordinatorOptions.can_edit_json);

ko.applyBindings(viewModel, $("#oozie_coordinatorComponents")[0]);

viewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
viewModel.coordinator.tracker().markCurrentStateAsClean();
viewModel.coordinator.refreshParameters();

shareViewModel.setDocUuid('');

function showChooseWorkflow() {
    $("#chooseWorkflowDemiModal").removeAttr("disabled");
    $("#chooseWorkflowDemiModal")[0].style.display = "block";
    $("#chooseWorkflowDemiModal").modal("show");
}

function selectWorkflow(wf) {
    viewModel.coordinator.properties.workflow(wf.uuid());
    $("#chooseWorkflowDemiModal").attr('disabled', 'disabled');
    $("#chooseWorkflowDemiModal")[0].style.display = "none";
    $("#chooseWorkflowDemiModal").modal("hide");
}

var firstToggled = true;
$(document).on("editingToggled", function () {
    if (firstToggled && window.location.pathname.indexOf('/oozie/editor/coordinator') > -1) {
        firstToggled = false;
        viewModel.coordinator.tracker().markCurrentStateAsClean();
    }
});

$(document).ready(function () {
    renderJqCron();
    $("#chooseWorkflowDemiModal").modal({
        show: false
    });
    $("#chooseWorkflowDemiModal").attr('disabled', 'disabled');
    $("#chooseWorkflowDemiModal")[0].style.display = "none";

    $(window).bind("keydown", "esc", function () {
        if ($(".demi-modal.fade.in").length > 0) {
            $(".demi-modal.fade.in .demi-modal-chevron").click();
        }
    });

    huePubSub.subscribe('submit.popup.return', function (data) {
        if (data.type == 'schedule') {
            huePubSub.publish('hue.global.info', {
                message: "Schedule submitted."
            });
            huePubSub.publish('open.link', '/jobbrowser/#!id=' + data.job_id);
            huePubSub.publish('browser.job.open.link', data.job_id);
            $('.submit-modal').modal('hide');
            $('.modal-backdrop').hide();
        }
    }, 'oozie');
});
