from django.template.loader import render_to_string


def admin_sidebar(context, *args, **kwargs):
    return render_to_string(
        template_name='rooms/hooks/admin_sidebar.html',
    )
