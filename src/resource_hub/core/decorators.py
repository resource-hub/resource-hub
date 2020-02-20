from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from resource_hub.core.models import OrganizationMember, User


def organization_admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        organization_id = kwargs['organization_id']
        member = get_object_or_404(
            OrganizationMember, organization__id=organization_id, user=user)

        if member.is_admin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
