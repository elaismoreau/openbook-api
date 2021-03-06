# Generated by Django 2.1.5 on 2019-01-06 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_invitations', '0006_userinvite_created_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinvite',
            name='email',
            field=models.EmailField(error_messages={'unique': 'The specified email has already been invited.'}, max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
