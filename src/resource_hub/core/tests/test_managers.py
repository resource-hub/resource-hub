from django.test import TestCase

from ..models import Address


class TestCombinedManager(TestCase):
    def setUp(self):
        self.address = Address.objects.create()

    def test_soft_deletion(self):
        Address.objects.filter(pk=self.address.pk).soft_delete()
        self.assertEqual(len(Address.objects.all()), 0)
