$(document).ready(function () {
    $('.message .close')
        .on('click', function () {
            $(this)
                .closest('.message')
                .transition('fade');
        });

    $('.ui.dropdown').dropdown();

    $('.back-button').click(function () {
        parent.history.back();
        return false;
    });
});
