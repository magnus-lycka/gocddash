
$(function () {
    if (window.localStorage.getItem("show-mgmt-bar") === "true") {
        $('#mgmt-bar').removeClass("hidden")
    }

});

$(function () {
    if (window.localStorage.getItem("show-status-popups") === "true") {
        $('#status-popup').removeClass("hidden")
    }
});

var stageid = null;
var pipelineName = null;
var pipelineCounter = null;
var shouldReload = true;
reload_in_a_minute();

function reload_in_a_minute() {
    window.setTimeout(function () {
        if (shouldReload) {
            document.location.reload(true);
        }
    }, 60000);
}
$('#myModal').on('show.bs.modal', function (event) {
    console.log("No more reloads!");
    var icon = $(event.relatedTarget);
    pipelineName = icon.data('pipeline_name');
    pipelineCounter = icon.data('pipeline_counter');
    shouldReload = false;
});

$('#myModal').on('hide.bs.modal', function (e) {
    console.log("More reloads!");
    shouldReload = true;
    reload_in_a_minute();
});

$('#postClaim').click(function () {
    console.log($('#responsible').val());
    if ($('#responsible').val() === "") {
        $('#responsibleHelpBlock').removeClass('hidden');
        $('#responsibleFormGroup').addClass('has-error');
        return false;
    }
    else {
        payload = $('#claimForm').serialize() + '&pipelineName=' + pipelineName + '&pipelineCounter=' + pipelineCounter;
        $.post(applicationRoot + "/claim", payload).done(function () {
            $('#myModal').modal('hide');
            document.location.reload(true);
        }).fail(function () {
            console.log("Something went wrong")
        })
    }
});

$(function () {
    $(".pipeline-alert").fadeIn(1000);
    shouldReload = true;
});