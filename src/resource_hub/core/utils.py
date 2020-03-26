import re

from django.db.models import Q
from django.utils.text import slugify


def get_associated_objects(actor, model):
    query = Q(owner=actor.pk)
    return model.objects.select_related('owner').filter(query)


def get_valid_slug(obj, string, condition=None):
    def create_query(slug, condition):
        query = Q(slug=slug)
        if condition:
            query.add(condition, Q.AND)
        return query
    slug = slugify(string)
    invalid_slug = True
    klass = obj.__class__
    count = 0
    while invalid_slug:
        try:
            klass.objects.get(create_query(slug, condition))
            if count == 0:
                slug = '{}-{}'.format(slug, str(count))
            else:
                slug = re.sub(r'-[^-]*$', '-{}'.format(str(count)), slug)

        except klass.DoesNotExist:
            invalid_slug = False
        count += 1
    return slug
