# Generated by Django 3.2.12 on 2022-02-09 15:39

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('channel', models.CharField(max_length=250)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('os', models.CharField(choices=[('android', 'Android'), ('ios', 'iOS')], default='android', max_length=10)),
                ('impressions', models.BigIntegerField()),
                ('clicks', models.IntegerField()),
                ('installs', models.IntegerField()),
                ('spend', models.FloatField()),
                ('revenue', models.FloatField()),
            ],
        ),
    ]
