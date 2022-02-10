from django_countries import countries
from django_filters.rest_framework import (
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter,
)

from ..models import Metric


class MetricFilter(FilterSet):
    """Filter for `Metric` model."""
    date = DateFromToRangeFilter()
    country = MultipleChoiceFilter(choices=countries)

    class Meta:
        model = Metric
        fields = {
            'channel': ['exact', 'in'],
            'os': ['exact', 'in'],
        }
