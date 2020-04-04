# Generated by Django 3.0.5 on 2020-04-04 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='business_type',
            field=models.CharField(choices=[('UNKNOWN', 'UNKNOWN'), ('BANKE', 'bank'), ('GROCERY', 'grocery_store'), ('PHARMACY', 'pharmacy')], default='UNKNOWN', max_length=20),
        ),
    ]
