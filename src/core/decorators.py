from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from core.models import User, OrganizationMember


def organization_admin_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        organization_id = kwargs['organization_id']
        member = get_object_or_404(
            OrganizationMember, organization__id=organization_id, user=user)

        if member.is_admin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
