# Generated by Django 2.1.3 on 2018-12-07 12:11

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ('openbook_circles', '0004_circle_connections'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='created',
            field=models.DateTimeField(default=timezone.now(), editable=False),
            preserve_default=False,
        ),
    ]
