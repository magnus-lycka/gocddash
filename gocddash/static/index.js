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

var pipelineName = null;
var pipelineCounter = null;
var shouldReload = true;
reload_in_a_minute();


$('#myModal').on('show.bs.modal', function (event) {
    console.log("No more reloads!");
    var icon = $(event.relatedTarget);
    pipelineName = icon.data('pipeline_name');
    pipelineCounter = icon.data('pipeline_counter');
    shouldReload = false;
});


$('#postClaim').click(function () {
    payload = $('#claimForm').serialize() + '&pipelineName=' + pipelineName + '&pipelineCounter=' + pipelineCounter;
    ajaxPostClaim(payload);
});


$(function () {
    $(".pipeline-alert").fadeIn(1000);
    shouldReload = true;
});