from django.core.exceptions import FieldError
from django.test import TestCase

from ..models import Metric, MetricQuerySet
from ..services import MetricAggregator
from .data import metric_data


class MetricTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(**data) for data in metric_data
        ])
        cls.aggregator = MetricAggregator()
        cls.queryset = Metric.objects.all()

        cls.supported_display_fields = cls.aggregator.supported_display_fields
        cls.not_supported_display_fields = [
            field.name for field in Metric._meta.fields
            if field.name not in cls.supported_display_fields
        ]

    def test_aggregation_performed_for_supported_fields(self):
        group_by = ['channel']

        for field in self.supported_display_fields:
            with self.subTest(supported_field=field):
                result = self.aggregator.aggregate(self.queryset, group_by, [field])
                self.assertIsInstance(result[0], dict)

    def test_aggregation_performed_for_not_supported_fields(self):
        group_by = ['channel']

        for field in self.not_supported_display_fields:
            with self.subTest(supported_field=field):
                with self.assertRaises(FieldError):
                    self.aggregator.aggregate(self.queryset, group_by, [field])

    def test_aggregation_one_field(self):
        group_by = ['channel']
        display_columns = ['impressions']
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

        result = self.aggregator.aggregate(
            queryset=self.queryset,
            group_by_columns=group_by,
            display_columns=display_columns,
        ).order_by(*group_by)

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_one_field_cpi(self):
        group_by = ['channel']
        display_columns = ['cpi']
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

        result = self.aggregator.aggregate(
            queryset=self.queryset,
            group_by_columns=group_by,
            display_columns=display_columns,
        ).order_by(*group_by)

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_two_fields(self):
        group_by = ['channel', 'country']
        display_columns = ['clicks']
        expected_clicks = [
            sum(m.clicks for m in self.metrics[0:2]),
            self.metrics[2].clicks,
            sum(m.clicks for m in self.metrics[3:6]),
            self.metrics[6].clicks,
            self.metrics[7].clicks,
            self.metrics[8].clicks,
        ]
        expected_data = [
            dict(channel='adcolony', country='CA', clicks=expected_clicks[1]),
            dict(channel='adcolony', country='US', clicks=expected_clicks[0]),
            dict(channel='apple_search_ads', country='GB', clicks=expected_clicks[2]),
            dict(channel='chartboost', country='FR', clicks=expected_clicks[3]),
            dict(channel='chartboost', country='GB', clicks=expected_clicks[4]),
            dict(channel='chartboost', country='US', clicks=expected_clicks[5]),
        ]

        result = self.aggregator.aggregate(
            queryset=self.queryset,
            group_by_columns=group_by,
            display_columns=display_columns,
        ).order_by(*group_by)

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])

    def test_aggregation_two_fields_cpi(self):
        group_by = ['channel', 'country']
        display_columns = ['cpi']
        expected_cpi = [
            sum(m.spend for m in self.metrics[0:2]) / sum(m.installs for m in self.metrics[0:2]),
            self.metrics[2].spend / self.metrics[2].installs,
            sum(m.spend for m in self.metrics[3:6]) / sum(m.installs for m in self.metrics[3:6]),
            self.metrics[6].spend / self.metrics[6].installs,
            self.metrics[7].spend / self.metrics[7].installs,
            self.metrics[8].spend / self.metrics[8].installs,
        ]
        expected_data = [
            dict(channel='adcolony', country='CA', cpi=expected_cpi[1]),
            dict(channel='adcolony', country='US', cpi=expected_cpi[0]),
            dict(channel='apple_search_ads', country='GB', cpi=expected_cpi[2]),
            dict(channel='chartboost', country='FR', cpi=expected_cpi[3]),
            dict(channel='chartboost', country='GB', cpi=expected_cpi[4]),
            dict(channel='chartboost', country='US', cpi=expected_cpi[5]),
        ]

        result = self.aggregator.aggregate(
            queryset=self.queryset,
            group_by_columns=group_by,
            display_columns=display_columns,
        ).order_by(*group_by)

        self.assertEqual(len(expected_data), len(result))

        for i in range(len(expected_data)):
            with self.subTest(expected=expected_data[i], actual=result[i]):
                self.assertDictEqual(expected_data[i], result[i])


