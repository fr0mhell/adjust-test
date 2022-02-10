from rest_framework import mixins, viewsets
from ..models import Metric
from .serializers import MetricSerializer


class MetricViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
