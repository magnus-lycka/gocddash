$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

var sec = 0;
setInterval(function () {
    if (++sec < 10) {
        $("#seconds").html("0" + sec);
    } else {
        $("#seconds").html(sec);
    }
}, 1000);

function reload_in_a_minute() {
    window.setTimeout(function () {
        if (shouldReload) {
            document.location.reload(true);
        }
    }, 60000);
}

$('#myModal').on('hide.bs.modal', function () {
    console.log("More reloads!");
    shouldReload = true;
    reload_in_a_minute();
});


function ajaxPostClaim(payload) {
    if ($('#responsible').val() === "") {
        $('#responsibleHelpBlock').removeClass('hidden');
        $('#responsibleFormGroup').addClass('has-error');
        return false;
    }
    else {
        $.post(applicationRoot + "/claim", payload).done(function () {
            $('#myModal').modal('hide');
            document.location.reload(true);
        }).fail(function () {
            console.log("Something went wrong")
        })
    }
}