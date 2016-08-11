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