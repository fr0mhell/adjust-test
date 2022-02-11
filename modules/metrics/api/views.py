from typing import List

from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from ..aggregations import MetricAggregator
from ..models import Metric
from .filters import MetricFilter
from .serializers import MetricSerializer


class MetricViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )
    filter_class = MetricFilter
    ordering_fields = '__all__'
    aggregator = MetricAggregator()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.is_aggregation:
            return queryset.with_cpi()

        group_by = self._get_group_by_columns()
        display_columns = self._get_display_columns()
        queryset = self.aggregator.aggregate(queryset, group_by, display_columns)
        return queryset

    def _get_group_by_columns(self) -> List[str]:
        return self.request.query_params.get('group_by').split(',')

    def _get_display_columns(self) -> List[str]:
        return self.request.query_params.get('display_columns').split(',')

    @property
    def is_aggregation(self):
        group_by = self.request.query_params.get('group_by', '')
        display_columns = self.request.query_params.get('display_columns', '')
        return bool(group_by and display_columns)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page:
            data = self.serialize_data(page)
            return self.get_paginated_response(data)

        data = self.serialize_data(queryset)
        return Response(data)

    def serialize_data(self, queryset):
        """Serialize data for response."""
        if self.is_aggregation:
            return queryset

        serializer = self.get_serializer(queryset, many=True)
        return serializer.data


"""
+ 1. Add standard DRF pagination, filtering, ordering
+ 2. Add CPI computation to QuerySet
+ 3. Add tests for CPI computation

+ 4. Figure out cases I need to implement to retrieve the data:
    + group by
    + filter
    + order
    + CPI computation
+ 5. Cover cases with tests

+ 6. Figure out how to implement st.4 in API
+ 7 Update API and tests with new Aggregator
8. Add tests for API
  + 8.1 Fix issue with cpi, spend and installs
9. Code style: doc strings, imports
10. Update readme

"""
