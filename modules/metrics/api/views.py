from typing import List

from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from django_filters.rest_framework import DjangoFilterBackend

from ..aggregations import MetricAggregator
from ..models import Metric
from .filters import MetricFilter
from ..exceptions import AggregationError
from .serializers import MetricSerializer
from rest_framework.exceptions import APIException

from rest_framework.permissions import AllowAny

GROUP_BY = 'group_by'
DISPLAY_COLUMNS = 'display_columns'


class AggregationAPIError(APIException):
    status_code = 400


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
    permission_classes = (
        AllowAny,
    )
    filter_class = MetricFilter
    ordering_fields = (
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
    aggregator = MetricAggregator()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.is_aggregation:
            return queryset.with_cpi().order_by('date')

        group_by = self._get_group_by_columns()
        display_columns = self._get_display_columns()
        queryset = self.aggregator.aggregate(queryset, group_by, display_columns)
        return queryset

    def _get_group_by_columns(self) -> List[str]:
        return self.request.query_params.get(GROUP_BY).split(',')

    def _get_display_columns(self) -> List[str]:
        return self.request.query_params.get(DISPLAY_COLUMNS).split(',')

    @property
    def is_aggregation(self):
        """Check if aggregation required.

        Aggregation is required when both `group_by` and `display_columns` query parameters passed.

        """
        group_by = self.request.query_params.get(GROUP_BY, '')
        display_columns = self.request.query_params.get(DISPLAY_COLUMNS, '')
        return bool(group_by and display_columns)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except AggregationError as error:
            return Response(
                data={'error': f'Aggregation error: {error}'},
                status=HTTP_400_BAD_REQUEST,
            )

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
