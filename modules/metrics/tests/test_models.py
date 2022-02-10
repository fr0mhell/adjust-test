from ..models import Metric
from django.test import TestCase
from django.core.exceptions import FieldError


class MetricTestCase(TestCase):

    SUPPORTED_DISPLAY_FIELDS = [
        'impressions',
        'clicks',
        'installs',
        'spend',
        'revenue',
        'cpi',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(date='2017-05-17',channel='adcolony',country='US',os='android',impressions=1,clicks=9,installs=1,spend=5,revenue=6,),
            Metric(date='2017-05-17',channel='adcolony',country='US',os='ios',impressions=2,clicks=8,installs=2,spend=5,revenue=8,),
            Metric(date='2017-05-18',channel='adcolony',country='CA',os='ios',impressions=3,clicks=7,installs=4,spend=11,revenue=11,),
            Metric(date='2017-05-17',channel='apple_search_ads',country='GB',os='android',impressions=4,clicks=6,installs=4,spend=3,revenue=12,),
            Metric(date='2017-05-17',channel='apple_search_ads',country='GB',os='ios',impressions=5,clicks=4,installs=5,spend=4,revenue=14,),
            Metric(date='2017-05-17',channel='apple_search_ads',country='GB',os='android',impressions=6,clicks=5,installs=6,spend=6,revenue=16,),
            Metric(date='2017-05-17',channel='chartboost',country='FR',os='ios',impressions=7,clicks=3,installs=7,spend=4,revenue=18,),
            Metric(date='2017-05-17',channel='chartboost',country='GB',os='android',impressions=8,clicks=2,installs=8,spend=8,revenue=20,),
            Metric(date='2017-05-17',channel='chartboost',country='US',os='ios',impressions=9,clicks=1,installs=9,spend=10,revenue=22,),
        ])

        cls.not_supported_by_aggregation = [
            field.name for field in Metric._meta.fields
            if field.name not in cls.SUPPORTED_DISPLAY_FIELDS
        ]

    def test_cpi(self):
        qs = Metric.objects.with_cpi()
        for metric in qs:
            expected = metric.spend / metric.installs
            actual = metric.cpi
            with self.subTest(expected=expected, actual=actual):
                self.assertEqual(expected, actual)

    def test_aggregation_performed_for_supported_fields(self):
        group_by = ['channel']

        for field in self.SUPPORTED_DISPLAY_FIELDS:
            with self.subTest(supported_field=field):
                result = []
                self.assertIsInstance(result[0], dict)

    def test_aggregation_performed_for_not_supported_fields(self):
        group_by = ['channel']

        for field in self.SUPPORTED_DISPLAY_FIELDS:
            with self.subTest(supported_field=field):
                with self.assertRaises(FieldError):
                    result = []

    def test_aggregation_one_field(self):
        group_by = ['channel']
        display_fields = ['impressions']
        expected_impressions = [
            sum(m.impressions for m in self.metrics[0:3]),
            sum(m.impressions for m in self.metrics[3:6]),
            sum(m.impressions for m in self.metrics[6:9]),
        ]
        expected_data = [
            dict(channel='adcolony', impressions=expected_impressions[0]),
            dict(channel='apple_search_ads', impressions=expected_impressions[1]),
            dict(channel='chartboost', impressions=expected_impressions[2]),
        ]

        result = []  # order by channel

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_one_field_cpi(self):
        group_by = ['channel']
        display_fields = ['cpi']
        expected_cpis = [
            sum(m.spend for m in self.metrics[0:3]) / sum(m.installs for m in self.metrics[0:3]),
            sum(m.spend for m in self.metrics[3:6]) / sum(m.installs for m in self.metrics[3:6]),
            sum(m.spend for m in self.metrics[6:9]) / sum(m.installs for m in self.metrics[6:9]),
        ]
        expected_data = [
            dict(channel='adcolony', cpi=expected_cpis[0]),
            dict(channel='apple_search_ads', cpi=expected_cpis[1]),
            dict(channel='chartboost', cpi=expected_cpis[2]),
        ]

        result = []  # order by channel

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_two_fields(self):
        group_by = ['channel', 'country']
        display_fields = ['impressions']
        expected_clicks = [
            sum(m.clicks for m in self.metrics[0:2]),
            self.metrics[2].clicks,
            sum(m.clicks for m in self.metrics[3:6]),
            self.metrics[6].clicks,
            self.metrics[7].clicks,
            self.metrics[8].clicks,
        ]
        expected_data = [
            dict(channel='adcolony', country='US', clicks=expected_clicks[0]),
            dict(channel='adcolony', country='CA', clicks=expected_clicks[1]),
            dict(channel='apple_search_ads', country='GB', clicks=expected_clicks[2]),
            dict(channel='chartboost', country='FR', clicks=expected_clicks[3]),
            dict(channel='chartboost', country='GB', clicks=expected_clicks[4]),
            dict(channel='chartboost', country='US', clicks=expected_clicks[5]),
        ]

        result = []  # order by channel

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_two_fields_cpi(self):
        group_by = ['channel', 'country']
        display_fields = ['cpi']
        expected_cpi = [
            sum(m.spend for m in self.metrics[0:2]) / sum(m.installs for m in self.metrics[0:2]),
            self.metrics[2].spend / self.metrics[2].installs,
            sum(m.spend for m in self.metrics[3:6]) / sum(m.installs for m in self.metrics[3:6]),
            self.metrics[6].spend / self.metrics[6].installs,
            self.metrics[7].spend / self.metrics[7].installs,
            self.metrics[8].spend / self.metrics[8].installs,
        ]
        expected_data = [
            dict(channel='adcolony', country='US', cpi=expected_cpi[0]),
            dict(channel='adcolony', country='CA', cpi=expected_cpi[1]),
            dict(channel='apple_search_ads', country='GB', cpi=expected_cpi[2]),
            dict(channel='chartboost', country='FR', cpi=expected_cpi[3]),
            dict(channel='chartboost', country='GB', cpi=expected_cpi[4]),
            dict(channel='chartboost', country='US', cpi=expected_cpi[5]),
        ]

        result = []  # order by channel

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])


