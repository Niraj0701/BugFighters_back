# Generated by Django 3.0.5 on 2020-04-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(default='India', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='country_code',
            field=models.CharField(default='91', max_length=4),
        ),
        migrations.AlterField(
            model_name='user',
            name='verification_state',
            field=models.CharField(choices=[('UNVERIFIED', 'UNVERIFIED'), ('VERIFIED', 'VERIFIED')], default='UNVERIFIED', max_length=20),
        ),
    ]
