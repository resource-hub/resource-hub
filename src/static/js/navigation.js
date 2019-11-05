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

    $('#language').on('change', function () {
        console.log($(this).serialize());
        //$(this).submit();

    });
    $('.lang').on('click', function () {
        var val = $(this).val();
        $('#language').val(val);
        $('#language-form').submit();
    });
});
