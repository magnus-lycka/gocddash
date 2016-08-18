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

var shouldReload = true;
reload_in_a_minute();



$(function () {
    $(".pipeline-alert").fadeIn(1000);
    shouldReload = true;
});