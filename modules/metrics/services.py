from .models import Metric
from typing import Set, Callable, Dict, List, Tuple
from django.db.models import Sum, QuerySet, Aggregate
from django.core.exceptions import FieldError

CPI = 'cpi'


class MetricAggregator:
    """"""
    supported_display_fields: Set[str] = {
        'impressions',
        'clicks',
        'installs',
        'spend',
        'revenue',
        'cpi',
    }
    supported_aggregations: Dict[str, Callable] = {
        'sum': Sum,
    }
    default_aggregation: Callable = Sum
    model_fields: Tuple[str] = tuple(field.name for field in Metric._meta.fields) + ('cpi', )

    def aggregate(
            self,
            queryset: QuerySet,
            group_by_columns: List[str],
            display_columns: List[str],
    ) -> QuerySet:
        """"""
        aggregations = self._get_column_aggregations(display_columns)
        queryset = queryset.values(*group_by_columns).annotate(**aggregations)

        if CPI in display_columns:
            queryset = queryset.with_cpi()

        return queryset

    def _get_column_aggregations(self, display_columns: List[str]) -> Dict['str', Aggregate]:
        """"""
        column_aggregations = dict()

        for column_with_function in display_columns:
            column, *any_func = column_with_function.split('__')

            if column == CPI:
                continue

            if column not in self.supported_display_fields:
                raise FieldError(f'Aggregation is not supported for the "{column}" field')

            func = any_func[0] if any_func else None
            aggregation = self.supported_aggregations.get(func, self.default_aggregation)
            column_aggregations[column] = aggregation(column)

        return column_aggregations
