from django.db import models
from django.utils import timezone
from datetime import datetime, date, time
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Container(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    is_repair_organization = models.BooleanField(default=False, blank=False, null=False)
    in_container = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return str(self.pk)+" "+str(self.owner)+" "+self.title

class Equipment_sizename(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False, verbose_name="Наименование")

    sizename_type_choices = (
                ('pump', "Насос"),
                ('compressor', "Компрессор"),
                ('bench', "Станок"),
                ('e-engine', "Электродвигатель"),
                ('engine', "ДВС"),
                ('turbine', "Турбина"),
                ('crane', "ГПМ"),
                ('air-handling-unit', "Вент. установка"),
                ('air-cooling-unit', "АВО"),
                ('heat-exchanger', "Теплообменник"),
                ('furnace', "Печь"),
                ('safe-valve', "Клапан предохр."),
                ('check-valve', "Клапан обратный"),
                ('control-valve', "Задвижка, клапан реглирующий"),
                ('other', "Прочее оборудование"),
                )
    type = models.CharField(max_length=25,choices=sizename_type_choices,default='other', verbose_name="Тип оборудования")
    manufacturer = models.CharField(max_length=100, blank=False, null=False, default='н/д', verbose_name="Производитель")
    supply_provider = models.CharField(max_length=100, blank=False, null=False, default='н/д', verbose_name="Поставщик")
    def __str__(self):
        return self.title

class Equipment(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    sizename = models.ForeignKey(Equipment_sizename, on_delete=models.CASCADE, blank=False, null=False)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    in_container = models.ForeignKey(Container, on_delete=models.CASCADE, blank=False, null=False)
    def __str__(self):
        return str(self.sizename.title)+" № "+str(self.serial_number)+'  ['+self.in_container.title+']'

    def set_correct_places(self):
        # функция корректной проставки used_in_container
        # НЕ ЗАБЫТЬ  - расход может применяться на оборудование. при этом не очень понятно что будет делать данная функция с такими расходами
        actions = Action.objects.filter(used_in_equipment=self).order_by("action_start_date")
        new_container = None
        for action in actions:
            action.used_in_container.clear()
            if new_container:
                action.used_in_container.add(new_container)
            if action.new_container:
                new_container = action.new_container
                action.used_in_container.add(new_container)
        if new_container:
            self.in_container = new_container
            self.save()


class Spare_part(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    unit_name = models.CharField(max_length=10, blank=False, null=False)
    in_container = models.ForeignKey(Container, on_delete=models.SET_NULL, blank=True, null=True)
    used_in_equipment = models.ManyToManyField(Equipment_sizename)
    manufacturer = models.CharField(max_length=100, blank=False, null=False, default='н/д')
    suply_provider = models.CharField(max_length=100, blank=False, null=False, default='н/д')
    def __str__(self):
        return self.title

class Action(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    action_type_choices_equipment = (
                ('equipment,repair,TO', "ТО"),
                ('equipment,repair,TR', "ТР"),
                ('equipment,repair,KR', "КР"),
                ('equipment,repair,KTS', "КТС"),
                ('equipment,repair,DEFF', "ремонт"),
                ('equipment,INFO', "информация"),
                ('equipment,FAILURE', "отказ"),
                ('equipment,REPAIR_EXPORT', "вывоз в ремонт"),
                ('equipment,REPAIR_IMPORT', "завоз с ремонта"),
                ('equipment,MOUNT', "монтаж"),
                ('equipment,UNMOUNT', "демонтаж"),
                ('equipment,MOVE', "перемещение")
                )
    action_type_choices_spare_parts = (
                ('action,INFO', "информация"),
                ('action,MOVE', "перемещение")
                )
    action_type_choices_childs = (
                ('child,OUTGO', "расход"),
                )
    action_type_choices_all = action_type_choices_equipment + action_type_choices_spare_parts + action_type_choices_childs
    type = models.CharField(max_length=25,choices=action_type_choices_all,default='equipment,INFO')
    action_start_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    action_end_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    scheduled = models.NullBooleanField(default=None)
    description = models.TextField(blank=True, null=True)
    used_in_equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True)
    used_in_action = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    used_in_spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE, blank=True, null=True)
    used_in_container = models.ManyToManyField(Container, blank=True, related_name='used_in_container')
    quantity_delta = models.FloatField(default=None, blank=True, null=True)
    new_container = models.ForeignKey(Container, on_delete=models.CASCADE, blank=True, null=True, related_name='new_container')

    def __str__(self):
        return self.get_type_display()+' '+ str(self.used_in_equipment)
