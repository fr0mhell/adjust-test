from django.contrib import admin

from .models import Metric


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date',
        'channel',
        'country',
        'os',
        'impressions',
        'clicks',
        'installs',
        'spend',
        'revenue',
    )
    list_filter = (
        'channel',
        'os',
        'country',
    )
