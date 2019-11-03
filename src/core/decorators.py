from django.core.exceptions import PermissionDenied

from core.models import User, OrganizationMember


def organization_admin_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        organization_id = kwargs['id']

        if OrganizationMember.is_admin(user, organization_id):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
