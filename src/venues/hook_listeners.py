from django.template.loader import render_to_string


def control_sidebar(context, *args, **kwargs):
    return render_to_string(
        template_name='venues/hooks/control_sidebar.html', request=context.request,
    )


def navigation_bar(context, *args, **kwargs):
    return render_to_string(template_name='venues/hooks/navigation_bar.html', request=context.request)


def location_profile(context, *args, **kwargs):
    print(context)
    from venues.models import Venue
    location_id = context.request.resolver_match.kwargs['location_id']
    if not Venue.objects.filter(location=location_id):
        return ""
    return render_to_string(template_name='venues/hooks/location_profile.html', context=context.flatten(), request=context.request)
