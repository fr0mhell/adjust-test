from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from typing import List
from django.core.exceptions import FieldError

CPI = 'cpi'


class MetricQuerySet(models.QuerySet):
    SUPPORTED_DISPLAY_FIELDS = {
        'impressions',
        'clicks',
        'installs',
        'spend',
        'revenue',
        'cpi',
    }

    def with_cpi(self):
        return self.annotate(cpi=models.Sum('spend') / models.Sum('installs'))

    def with_aggregation(
            self,
            group_by_columns: List[str],
            display_columns: List[str],
    ) -> models.QuerySet:
        """Apply aggregation.

        * GROUP BY columns from `group_by_columns`;
        * SELECT SUM of every column in `columns`.

        """
        if any(col not in self.SUPPORTED_DISPLAY_FIELDS for col in display_columns):
            raise FieldError

        if display_cpi := CPI in display_columns:
            display_columns.remove(CPI)

        sum_aggregation = {col: models.Sum(col) for col in display_columns}
        queryset = self.values(*group_by_columns).annotate(**sum_aggregation)

        if display_cpi:
            queryset = queryset.with_cpi()

        return queryset


class Metric(models.Model):
    """Store metrics data."""
    class OSChoices(models.TextChoices):
        ANDROID = 'android', _('Android')
        IOS = 'ios', _('iOS')

    date = models.DateField()
    channel = models.CharField(
        max_length=250,
    )
    country = CountryField()
    os = models.CharField(
        max_length=10,
        choices=OSChoices.choices,
        default=OSChoices.ANDROID,
    )
    impressions = models.BigIntegerField()
    clicks = models.IntegerField()
    installs = models.IntegerField()
    spend = models.FloatField()
    revenue = models.FloatField()

    objects = MetricQuerySet.as_manager()


# cases
# 1
Metric.objects.values("channel", "country").filter(date__lte="2017-06-01").annotate(
    impressions=models.Sum("impressions"),
    clicks=models.Sum("clicks"),
).with_cpi().order_by("-clicks")

# 2
Metric.objects.values("date").filter(
    date__lte="2017-05-31",
    date__gte="2017-05-01",
).annotate(installs=models.Sum("installs")).order_by("-date")

# 3
Metric.objects.values('os').filter(
    date="2017-06-01",
).annotate(revenue=models.Sum('revenue')).order_by('-revenue')

# 4
Metric.objects.values("channel").filter(
    country='CA',
).annotate(
    cpi=models.Sum('spend') / models.Sum('installs'),
).order_by('-cpi')
