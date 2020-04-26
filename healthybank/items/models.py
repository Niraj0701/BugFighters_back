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
    description = models.CharField(max_length=200, null=True,blank=True)
    url = models.ImageField(upload_to='items', null=True, blank=True)
    size = models.IntegerField()
    unit = models.CharField(max_length=10,choices=UNIT_CHOICES,null=True)
    price = models.FloatField()

    def __str__(self):
        return "%s %s%s" % (self.name, self.size, self.unit)

from django.contrib import admin

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['name']
