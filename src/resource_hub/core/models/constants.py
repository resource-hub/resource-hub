from django.utils.translation import gettext_lazy as _


class LEVEL:
    '''
    the level of a message is the basis for user
    notification preferences
    '''
    LOW = 0  # info
    MEDIUM = 1  # action required, mail
    HIGH = 2  # warning
    CRITICAL = 3  # mandatory information


LEVELS = [
    (LEVEL.LOW, _('low')),
    (LEVEL.MEDIUM, _('medium')),
    (LEVEL.HIGH, _('high')),
    (LEVEL.CRITICAL, _('critical')),
]
