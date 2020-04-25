from django.db import models

# Create your models here.


class Item(models.Model):
    UNIT_CHOICES = (
        ("liters", "liters"),
        ("ml", "ml"),
        ("dozen", "dozen"),
        ("kg", "kg"),
        ("g", "g"),
    )
    name = models.CharField(max_length=100,null=False)
    description = models.CharField(max_length=200, null=True)
    url = models.ImageField(upload_to='items', null=True)
    size = models.IntegerField()
    unit = models.CharField(max_length=10,choices=UNIT_CHOICES,null=True)
    price = models.FloatField()

