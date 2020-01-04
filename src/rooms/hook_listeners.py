from django.template.loader import render_to_string


def admin_sidebar(context, *args, **kwargs):
    return render_to_string(
        template_name='rooms/hooks/admin_sidebar.html', request=context.request,
    )


def navigation_bar(context, *args, **kwargs):
    return render_to_string(template_name='rooms/hooks/navigation_bar.html', request=context.request)
