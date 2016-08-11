var shouldReload = true;

reload_in_a_minute();

function reload_in_a_minute() {
    window.setTimeout(function () {
        if (shouldReload) {
            document.location.reload(true);
        }
    }, 60000);
}

$('#myModal').on('show.bs.modal', function (e) {
    console.log("No more reloads!");
    shouldReload = false;
});

$('#myModal').on('hide.bs.modal', function (e) {
    console.log("More reloads!");
    shouldReload = true;
    reload_in_a_minute();
});

$('#postClaim').click(function () {
    if ($('#responsible').val() === "") {
        $('#responsibleHelpBlock').removeClass('hidden');
        $('#responsibleFormGroup').addClass('has-error');
        return false;
    }
    else {
        payload = $('#claimForm').serialize() + '&pipelineName=' + current_stage.pipeline_name + '&pipelineCounter=' + current_stage.pipeline_counter;
        $.post(applicationRoot + "/claim", payload).done(function () {
            $('#myModal').modal('hide');
            document.location.reload(true);
        }).fail(function () {
            console.log("Something went wrong")
        })
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