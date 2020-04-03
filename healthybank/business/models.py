# from django.db import models
#
# Create your models here.
from django.contrib.gis.db import models

class Business(models.Model):
    name = models.CharField(max_length=100)
    loc = models.PointField()
    users_allowed=models.IntegerField()
    slot_size_min=models.IntegerField()




