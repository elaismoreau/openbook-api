# Generated by Django 2.1.2 on 2018-10-10 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='name',
            field=models.CharField(max_length=50, verbose_name='name'),
        ),
    ]
