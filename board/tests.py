
from django.test import TestCase
from .models import Ad
from django.core.exceptions import ValidationError


class AdModelTest(TestCase):
    def test_negative_price_raises_error(self) -> None:
        ad = Ad(title="Test", price=-100)
        with self.assertRaises(ValidationError):
            ad.full_clean()
