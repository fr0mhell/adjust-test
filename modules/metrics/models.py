from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField


class MetricQuerySet(models.QuerySet):
    def with_cpi(self):
        """Compute CPI (cost per install) = spend / installs for every Metric."""
        return self.annotate(cpi=models.F('spend') / models.F('installs'))


class Metric(models.Model):

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
