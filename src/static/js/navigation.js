function remove_loader(name) {
    $(name).removeClass('active').addClass('disabled');
}

$(document).ready(function () {
    $('#secondary-menu').children('.ui .item').on('click', function () {
        $('#secondary-menu').children('.ui .item').removeClass('active');
        $(this).addClass('active');

        var id = $(this).attr('tab-id');
        var path = window.location.pathname.replace(/\/$/, '')
        path = path.substr(0, path.lastIndexOf('/') + 1) + id + '/';
        window.history.pushState(null, null, path);

        id = '#' + id;
        $('.tab-content').children('.tab').removeClass('active');
        $(id).addClass('active');

        function update_url() {
            return (window.location.href.replace(/(\d+)(\.html)$/, function (str, p1, p2) {
                return ((Number(p1) + 1) + p2);
            }));
        }
    });
    // allow system messages to be closed
    $('.message .close')
        .on('click', function () {
            $(this)
                .closest('.message')
                .transition('fade');
        });

    $('.ui.dropdown').dropdown();

    // toggle language
    $('.lang').on('click', function () {
        var val = $(this).val();
        $('#language').val(val);
        $('#language-form').submit();
    });


    // display role selection modal and get list of roles
    $('#role').on('click', function (e) {
        e.preventDefault();
        $('#select-roles')
            .modal('show');
        $.ajax({
            url: "{% url 'api:change_role' %}",
            type: "GET",
            dataType: "JSON"
        }).done(function (list) {
            remove_loader('#role-loader');
            $('#role-form').removeClass('hidden');
            var list_items = '';
            if (list.length > 0) {
                $.each(list, function (key, actor) {
                    list_items += '<option value="' + actor.id + '">' + actor.name + '</option>';
                });
            }
            $('#role-list').html(list_items);
        });
    });
});
