from rest_framework import serializers

from ..models import Metric


class MetricSerializer(serializers.ModelSerializer):
    cpi = serializers.ReadOnlyField()

    class Meta:
        model = Metric
        fields = (
            'date',
            'channel',
            'country',
            'os',
            'impressions',
            'clicks',
            'installs',
            'spend',
            'revenue',
            'cpi',
        )
