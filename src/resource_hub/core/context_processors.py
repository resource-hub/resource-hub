from django.conf import settings

from resource_hub.core.models import Contract


def actor(request):
    if hasattr(request, 'actor'):
        return {'actor': request.actor}
    else:
        return {'actor': None}


def map_api_token(request):
    return {
        'MAP_API_TOKEN': settings.MAP_API_TOKEN,
    }


def contract_states(request):
    return {'CONTRACT_STATE': Contract.STATE}
