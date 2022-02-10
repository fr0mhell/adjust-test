from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Metric
from .data import metric_data


class AccountTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.metrics = Metric.objects.bulk_create([
            Metric(**data) for data in metric_data
        ])

    def test_aggregation_one_field(self):
        """
        """
        url = reverse('metric-list')
        data = {'group_by': 'channel', 'display_columns': 'impressions'}
        response = self.client.get(url, data, format='json')
        actual_data = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(actual_data), 3)
