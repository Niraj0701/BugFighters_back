# Generated by Django 3.0.5 on 2020-04-13 14:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200413_1435'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 13, 14, 44, 59, 653705), verbose_name='date joined'),
        ),
        migrations.AlterModelTable(
            name='user',
            table=None,
        ),
    ]
