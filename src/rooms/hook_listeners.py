from django.template.loader import render_to_string


def admin_sidebar(context, *args, **kwargs):
    return render_to_string(
        template_name='rooms/hooks/admin_sidebar.html', request=context.request,
    )


def navigation_bar(context, *args, **kwargs):
    return render_to_string(template_name='rooms/hooks/navigation_bar.html', request=context.request)


def location_profile(context, *args, **kwargs):
    print(context)
    from rooms.models import Room
    location_id = context.request.resolver_match.kwargs['location_id']
    if not Room.objects.filter(location=location_id):
        return ""
    return render_to_string(template_name='rooms/hooks/location_profile.html', context=context.flatten(), request=context.request)
