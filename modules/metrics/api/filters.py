from django_filters.rest_framework import FilterSet, DateFromToRangeFilter, MultipleChoiceFilter

from ..models import Metric
from django_countries import countries


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
