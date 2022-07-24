# Generated by Django 3.0.6 on 2021-01-18 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visit', '0004_auto_20210118_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='information',
            name='cel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test', to=settings.AUTH_USER_MODEL),
        ),
    ]
