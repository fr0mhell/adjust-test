from django.db.utils import NotSupportedError
from django.test import TestCase

from ..aggregations import MetricAggregator
from ..exceptions import AggregationError
from ..models import Metric
from .data import metric_data


class MetricAggregatorTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(**data) for data in metric_data
        ])
        cls.aggregator = MetricAggregator()
        cls.queryset = Metric.objects.all()

        cls.model_fields = tuple(field.name for field in Metric._meta.fields) + ('cpi',)

    def test_aggregation_performed_supported_group_by_columns(self):
        display_fields = ['spend']
        for field in self.aggregator.supported_group_by_columns:
            with self.subTest(supported_group_by_column=field):
                result = self.aggregator.aggregate(self.queryset, [field], display_fields)
                self.assertIsInstance(result[0], dict)

    def test_aggregation_error_not_supported_group_by_columns(self):
        display_fields = ['spend']
        not_supported = [
            field for field in self.model_fields
            if field not in self.aggregator.supported_group_by_columns
        ]
        for field in not_supported:
            with self.subTest(supported_group_by_column=field):
                with self.assertRaises(AggregationError):
                    self.aggregator.aggregate(self.queryset, [field], display_fields)

    def test_aggregation_error_same_field_in_group_by_and_display(self):
        group_by_fields = ['country']
        display_fields = ['country']
        with self.assertRaises(AggregationError):
            self.aggregator.aggregate(self.queryset, group_by_fields, display_fields)

    def test_aggregation_error_not_supported_display_column_error(self):
        display_fields = ['date']
        for field in self.aggregator.not_supported_display_columns:
            with self.subTest(not_supported_field=field):
                with self.assertRaises(AggregationError):
                    self.aggregator.aggregate(self.queryset, [field], display_fields)

    def test_sum_aggregation(self):
        """Sum aggregation performed correctly when explicitly defined."""
        group_by = ['channel']
        display_columns = ['impressions__sum']
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

    def test_not_supported_aggregation(self):
        """Raise error when unsupported aggregation used."""
        group_by = ['channel']
        display_columns = ['impressions__rnd']

        with self.assertRaises(AggregationError):
            self.aggregator.aggregate(
                queryset=self.queryset,
                group_by_columns=group_by,
                display_columns=display_columns,
            ).order_by(*group_by)

    def test_group_by_one_field(self):
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

    def test_group_by_one_field_display_cpi(self):
        group_by = ['channel']
        display_columns = ['installs', 'cpi']
        expected_installs = [
            sum(m.installs for m in self.metrics[0:3]),
            sum(m.installs for m in self.metrics[3:6]),
            sum(m.installs for m in self.metrics[6:9]),
        ]
        expected_cpis = [
            sum(m.spend for m in self.metrics[0:3]) / expected_installs[0],
            sum(m.spend for m in self.metrics[3:6]) / expected_installs[1],
            sum(m.spend for m in self.metrics[6:9]) / expected_installs[2],
        ]
        expected_data = [
            dict(channel='adcolony', installs=expected_installs[0], cpi=expected_cpis[0]),
            dict(channel='apple_search_ads', installs=expected_installs[1], cpi=expected_cpis[1]),
            dict(channel='chartboost', installs=expected_installs[2], cpi=expected_cpis[2]),
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

    def test_group_by_two_fields(self):
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

    def test_group_by_two_fields_display_cpi(self):
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


