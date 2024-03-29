from typing import Callable, Dict, List

from django.db.models import Aggregate, F, QuerySet, Sum

from .exceptions import AggregationError
from .models import Metric

CPI = 'cpi'


class MetricAggregator:
    """Aggregate Metric data using GROUP BY functionality.

    The current solution is limited and support only SUM aggregation.

    """
    model = Metric
    supported_group_by_columns = (
        'date',
        'channel',
        'country',
        'os',
    )
    not_supported_display_columns = (
        'date',
    )
    supported_aggregations: Dict[str, Callable] = {
        'sum': Sum,
    }
    default_aggregation: Callable = Sum

    def aggregate(
            self,
            queryset: QuerySet,
            group_by_columns: List[str],
            display_columns: List[str],
    ) -> QuerySet:
        """Aggregate the data using SELECT ... GROUP BY query under the hood."""
        self._validate_group_by_columns(group_by_columns)
        aggregations = self._get_column_aggregations(group_by_columns, display_columns)
        queryset = queryset.values(*group_by_columns).annotate(**aggregations)
        return queryset

    def _validate_group_by_columns(self, group_by_columns: List[str]):
        unsupported_columns = []
        for column in group_by_columns:
            if column not in self.supported_group_by_columns:
                unsupported_columns.append(column)

        if unsupported_columns:
            error_line = ', '.join(unsupported_columns)
            raise AggregationError(
                f'The following values are not supported in the `group_by_columns`: {error_line}'
            )

    def _get_column_aggregations(
            self,
            group_by_columns: List[str],
            display_columns: List[str],
    ) -> Dict['str', Aggregate]:
        """Get proper aggregation functions from parameters.

        Apply correct CPI computation.
        Apply SUM aggregation for other columns.

        """
        column_aggregations = dict()
        has_cpi = False

        for column_with_function in display_columns:
            column, *any_func = column_with_function.split('__')

            if column in self.not_supported_display_columns:
                raise AggregationError(
                    f'The "{column}" in `display_columns` not supported. '
                    f'The DB does not support aggregation for the data type'
                )

            if column in group_by_columns:
                raise AggregationError(
                    f'The "{column}" in `display_columns` means aggregation that conflicts with'
                    f'"{column}" in `group_by_columns`'
                )

            # Skip `cpi` column and implement aggregation below
            if column == CPI:
                has_cpi = True
                continue

            func = any_func[0] if any_func else None
            if func and func not in self.supported_aggregations:
                raise AggregationError(f'Aggregation function {func} not supported')

            aggregation = self.supported_aggregations.get(func) or self.default_aggregation
            column_aggregations[column] = aggregation(column)

        if has_cpi:
            # Use aggregated value of `spend` or `installs` when already aggregated
            spend_agg = F('spend') if 'spend' in display_columns else Sum('spend')
            installs_agg = F('installs') if 'installs' in display_columns else Sum('installs')
            column_aggregations.update({
                'cpi': spend_agg / installs_agg,
            })

        return column_aggregations
