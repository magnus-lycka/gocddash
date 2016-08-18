var shouldReload = true;

reload_in_a_minute();


$('#myModal').on('show.bs.modal', function () {
    console.log("No more reloads!");
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
    var payload = $('#claimForm').serialize() + '&pipelineName=' + current_stage.pipeline_name + '&pipelineCounter=' + current_stage.pipeline_counter;
    ajaxPostClaim(payload);
}

$('#postClaim').on('keypress click', postPayload);



var rerunUrl = go_server_url + "run/" + current_stage.pipeline_name + "/" + current_stage.pipeline_counter + "/" + current_stage.stage_name;
$('#rerun-button').click(function () {
    $('#rerun-button').addClass('disabled');
    shouldReload = false;
    var encodedToken = encodeURIComponent(rerun_token);
    var payload = {authenticity_token: encodedToken};
    $.ajax({
        type: "POST",
        url: rerunUrl,
        data: payload,
        username: go_username,
        password: go_password,
        crossDomain: true,
        headers: {'Confirm': true}
    })
        .done(function () {
            document.location.reload(true);
        }).fail(function (data) {
        console.log(data)
    });
});