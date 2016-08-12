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

$("#responsible").keypress(function (e) {
    if(e.which === 13){
        postPayload()
    }
});

$("#description").keypress(function (e) {
    if(e.which === 13){
        postPayload()
    }
});


function postPayload() {
    payload = $('#claimForm').serialize() + '&pipelineName=' + pipelineName + '&pipelineCounter=' + pipelineCounter;
    ajaxPostClaim(payload);
}


$('#postClaim').on('keypress click', postPayload);

$(function () {
    $(".pipeline-alert").fadeIn(1000);
    shouldReload = true;
});