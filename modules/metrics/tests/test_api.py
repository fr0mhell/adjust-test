from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Metric
from .data import metric_data
from ..api.serializers import MetricSerializer


class MetricApiTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(**data) for data in metric_data
        ])
        cls.url = reverse('metric-list')

    def test_no_aggregation_all_columns_presented(self):
        response = self.client.get(self.url, format='json')
        actual_data = response.data['results'][0]
        expected_fields = set(MetricSerializer().fields.keys())
        actual_fields = set(actual_data.keys())
        self.assertSetEqual(expected_fields, actual_fields)

    def test_aggregation_only_specified_columns_presented(self):
        data = {'group_by': 'channel', 'display_columns': 'installs,cpi'}
        response = self.client.get(self.url, data, format='json')
        actual_data = response.data['results'][0]
        expected_fields = {'channel', 'installs', 'cpi'}
        actual_fields = set(actual_data.keys())
        self.assertSetEqual(expected_fields, actual_fields)

    def test_group_by_one_field(self):
        data = {'group_by': 'channel', 'display_columns': 'impressions'}
        response = self.client.get(self.url, data, format='json')
        actual_data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(actual_data), 3)

    def test_group_by_one_field_display_cpi(self):
        data = {'group_by': 'channel', 'display_columns': 'installs,cpi'}
        response = self.client.get(self.url, data, format='json')
        actual_data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(actual_data), 3)

    def test_group_by_two_fields(self):
        data = {'group_by': 'channel,country', 'display_columns': 'clicks'}
        response = self.client.get(self.url, data, format='json')
        actual_data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(actual_data), 6)

    def test_group_by_two_fields_display_cpi(self):
        data = {'group_by': 'channel,country', 'display_columns': 'cpi'}
        response = self.client.get(self.url, data, format='json')
        actual_data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(actual_data), 6)
