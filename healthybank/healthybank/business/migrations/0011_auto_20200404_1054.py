# Generated by Django 3.0.5 on 2020-04-04 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0010_auto_20200404_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userslot',
            name='mobile',
            field=models.CharField(blank=True, default='9766818825', max_length=10, null=True),
        ),
    ]
