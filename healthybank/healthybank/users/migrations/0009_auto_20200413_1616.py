# Generated by Django 3.0.5 on 2020-04-13 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.CharField(choices=[('Consumer', 'Consumer'), ('ServiceProvider', 'ServiceProvider')], max_length=20),
        ),
    ]
