from django.db.models import Q

from .models import OrganizationMember


def get_associated_objects(actor, model):
    query = Q(owner=actor.pk)
    sub_condition = Q(owner__organization__members=actor)
    sub_condition.add(
        Q(owner__organization__organizationmember__role__gte=OrganizationMember.ADMIN), Q.AND)
    query.add(sub_condition, Q.OR)
    return model.objects.select_related('owner').filter(query)
