from django.contrib import admin
from .models import Action_type, Container, Equipment_sizename, Equipment, Spare_part, Action

# Register your models here.
admin.site.register(Action_type)
admin.site.register(Container)
admin.site.register(Equipment_sizename)
admin.site.register(Equipment)
admin.site.register(Spare_part)
admin.site.register(Action)
