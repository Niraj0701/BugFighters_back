from django.contrib import admin

# Register your models here.


from django.contrib import admin

# Register your models here.
from items.models import Item,ItemAdmin
admin.site.register(Item, ItemAdmin)
