var shouldReload = true;

reload_in_a_minute();


$('#myModal').on('show.bs.modal', function (e) {
    console.log("No more reloads!");
    shouldReload = false;
});



$('#postClaim').on('keypress click', function (e) {
    console.log(e);
    if (e.which === 13 || e.type === 'click'){
        payload = $('#claimForm').serialize() + '&pipelineName=' + current_stage.pipeline_name + '&pipelineCounter=' + current_stage.pipeline_counter;
        ajaxPostClaim(payload);
    }
});



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
        crossDomain: true
    })
        .done(function () {
            document.location.reload(true);
        }).fail(function (data) {
        console.log(data)
    });
});