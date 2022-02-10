from django.test import TestCase

from ..models import Metric
from .data import metric_data


class MetricTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(**data) for data in metric_data
        ])

    def test_cpi(self):
        qs = Metric.objects.with_cpi()
        for metric in qs:
            expected = metric.spend / metric.installs
            actual = metric.cpi
            with self.subTest(expected=expected, actual=actual):
                self.assertEqual(expected, actual)
