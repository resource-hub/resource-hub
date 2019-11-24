def actor(request):
    if hasattr(request, 'actor'):
        return {'actor': request.actor}
    else:
        return {'actor': None}
