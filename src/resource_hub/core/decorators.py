from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from resource_hub.core.models import OrganizationMember


def organization_admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        organization_id = kwargs['organization_id']
        member = get_object_or_404(
            OrganizationMember, organization__id=organization_id, user=user)

        if member.is_admin():
            return function(request, *args, **kwargs)
        raise PermissionDenied()
    return wrap


def owner_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is None:
            raise PermissionDenied()
        resource = request.resolver_match.func.view_class.get_resource()
        try:
            resource = resource.objects.get(pk=pk)
        except resource.DoesNotExist:
            raise PermissionDenied()
        if resource.owner.pk != request.actor.pk:
            raise PermissionDenied(
                'You need to be owner of this resource to access it')
        return function(request, *args, **kwargs)
    return wrap
