from typing import Callable, Dict, List, Set, Tuple

from ..models import Metric


class MetricAggregationQueryParamsValidator:
    """"""
    valid_fields: Tuple[str] = tuple(field.name for field in Metric._meta.fields) + ('cpi', )

