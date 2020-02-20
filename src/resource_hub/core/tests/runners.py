from django.conf import settings
from django.test.runner import DiscoverRunner as DjangoTestSuiteRunner


class MyTestSuiteRunner(DjangoTestSuiteRunner):
    def __init__(self, *args, **kwargs):
        settings.TESTING = True
        super(MyTestSuiteRunner, self).__init__(*args, **kwargs)
