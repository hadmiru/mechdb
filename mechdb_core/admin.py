from django.contrib import admin
from .models import Action_type, Manufacturer, Supply_provider, Container, Equipment_sizename, Equipment, Spare_part, Action, Movement_action

# Register your models here.
admin.site.register(Action_type)
admin.site.register(Manufacturer)
admin.site.register(Supply_provider)
admin.site.register(Container)
admin.site.register(Equipment_sizename)
admin.site.register(Equipment)
admin.site.register(Spare_part)
admin.site.register(Action)
admin.site.register(Movement_action)
