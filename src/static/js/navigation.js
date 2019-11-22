$(document).ready(function () {
    // allow system messages to be closed
    $('.message .close')
        .on('click', function () {
            $(this)
                .closest('.message')
                .transition('fade');
        });

    $('.ui.dropdown').dropdown();

    // temporary back button
    $('.back-button').click(function () {
        parent.history.back();
        return false;
    });

    // toggle language
    $('.lang').on('click', function () {
        var val = $(this).val();
        $('#language').val(val);
        $('#language-form').submit();
    });

    // display role selection modal and get list of roles
    $('#role').on('click', function (e) {
        var url = window.location.origin + '/api/user/roles/';

        e.preventDefault();
        $('#select-roles')
            .modal('show');
        $.ajax({
            url: url,
            type: "GET",
            dataType: "JSON"
        }).done(function (list) {
            $('#role-loader').removeClass('active').addClass('disabled');
            var list_items = '';
            if (list.length > 0) {
                $.each(list, function (key, organization) {
                    list_items += '<option value="' + organization.id + '">' + organization.name + '</option>';
                });
            } else {
                list_items += '<option>No organizations found</option>';
            }
            $('#role-list').html(list_items);
        });
    });
});
