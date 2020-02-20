$(document).ready(function () {
    $("#back-up").click(function () {
        overlay.scroll({
            top: 0,
            behavior: 'smooth'
        });
    });

    (function () {
        overlay = document.documentElement;
        window.onscroll = function () { scrollFunction() };
    })();

    function scrollFunction() {
        if (overlay.scrollTop > 200) {
            document.getElementById("back-up").style.opacity = "1";
            document.getElementById("back-up").style.visibility = "visible";
            document.getElementById("back-up").style.transitionDelay = "0s";

        } else {
            document.getElementById("back-up").style.opacity = "0";
            document.getElementById("back-up").style.visibility = "hidden";
            document.getElementById("back-up").style.transitionDelay = "";
        }
    }
})