from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField


class MetricQuerySet(models.QuerySet):
    """"""
    def with_cpi(self):
        """"""
        return self.annotate(cpi=models.Sum('spend') / models.Sum('installs'))


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
