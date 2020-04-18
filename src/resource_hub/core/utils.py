import re
from contextlib import contextmanager
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.db.models import Q
from django.utils import translation
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


@contextmanager
def language(lng):
    _lng = translation.get_language()
    translation.activate(lng)
    try:
        yield
    finally:
        translation.activate(_lng)


def round_decimal(dec, currency=None, places_dict=settings.CURRENCY_PLACES):
    if currency:
        places = places_dict.get(currency, 2)
        return Decimal(dec).quantize(
            Decimal('1') / 10 ** places, ROUND_HALF_UP
        )
    return Decimal(dec).quantize(Decimal('0.01'), ROUND_HALF_UP)


def money_filter(dec, currency='EUR'):
    return '{} {}'.format(round_decimal(dec, currency), currency)
