from rest_framework import mixins, viewsets
from rest_framework.response import Response
from typing import Set
from ..models import Metric
from .serializers import MetricSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum


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
    filterset_fields = (
        'channel',
        'country',
        'os',
        'impressions',
    )
    # date filter
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        group_by_values = self.get_group_by_values(queryset)
        if group_by_values:
            queryset = queryset.values(*group_by_values)

        queryset = self.filter_queryset(queryset)

        columns = self.get_columns()
        if columns:
            queryset = queryset.annotate(**columns)

        page = self.paginate_queryset(queryset)

        if page:
            if group_by_values:
                data = page
            else:
                serializer = self.get_serializer(page, many=True)
                data = serializer.data
            return self.get_paginated_response(data)

        if group_by_values:
            data = queryset
        else:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        return Response(data)

    def get_group_by_values(self, queryset):
        raw_columns = self.request.query_params.get('group_by', '')
        if not raw_columns:
            return

        columns = raw_columns.split(',')
        return columns

    def get_columns(self):
        fields = self.request.query_params.get('columns', '')
        if not fields:
            return

        columns = {column: Sum(column) for column in fields.split(',')}
        return columns


"""
1. Add standard DRF pagination, filtering, ordering
2. Add CPI computation to QuerySet
3. Add tests for CPI computation

4. Figure out cases I need to implement to retrieve the data:
    + group by
    + filter
    + order
    - CPI computation
5. Cover cases with tests

6. Figure out how to implement st.4 in API
7. Add tests for API

8.
"""
