from django.db.models import Q

from .models import OrganizationMember


def get_associated_objects(actor, model):
    query = Q(owner=actor.pk)
    return model.objects.select_related('owner').filter(query)
