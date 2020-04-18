from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..fields import PercentField


class TestPercentField(TestCase):
    def test_invalid_values(self):
        percent_field = PercentField()
        invalid_values = [
            Decimal(-0.1),
            Decimal(101),
        ]
        for value in invalid_values:
            with self.assertRaises(ValidationError):
                percent_field.run_validators(value)
