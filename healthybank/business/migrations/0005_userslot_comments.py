# Generated by Django 3.0.5 on 2020-05-05 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_auto_20200414_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='userslot',
            name='comments',
            field=models.TextField(max_length=10000, null=True),
        ),
    ]
