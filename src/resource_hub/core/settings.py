from django.utils.translation import ugettext_lazy as _

COUNTRIES_WITH_STATE_IN_ADDRESS = {
    # Source: http://www.bitboost.com/ref/international-address-formats.html
    # This is not a list of countries that *have* states, this is a list of countries where states
    # are actually *used* in postal addresses. This is obviously not complete and opinionated.
    # Country: [(List of subdivision types as defined by pycountry), (short or long form to be used)]
    'AU': (['State', 'Territory'], 'short'),
    'BR': (['State'], 'short'),
    'CA': (['Province', 'Territory'], 'short'),
    'CN': (['Province', 'Autonomous region', 'Munincipality'], 'long'),
    'MY': (['State'], 'long'),
    'MX': (['State', 'Federal District'], 'short'),
    'US': (['State', 'Outlying area', 'District'], 'short'),
}
