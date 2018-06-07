from django.db import models
from django.utils import timezone
from datetime import datetime, date, time
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Action_type(models.Model):
    title = models.CharField(max_length=20, blank=False, null=False)
    only_repair_containers = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return self.title

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
    title = models.CharField(max_length=200, blank=False, null=False)
    manufacturer = models.CharField(max_length=100, blank=False, null=False, default='н/д')
    supply_provider = models.CharField(max_length=100, blank=False, null=False, default='н/д')
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
    def get_place_on_date(self,date):
        last_move_action = Action.objects.filter(used_in_equipment=self, new_container__isnull=False, action_start_date__lt=date).order_by("action_end_date").last()
        if last_move_action:
            return last_move_action.new_container
        else:
            return False

    def set_current_container(self):
        # функция расчитывает и записывает текущее местоположение
        last_move_action = Action.objects.filter(used_in_equipment=self, new_container__isnull=False).order_by("-action_end_date")[0]
        if last_move_action:
            self.in_container=last_move_action.new_container
            self.save()
        else:
            return False


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
    type = models.ForeignKey(Action_type, on_delete=models.PROTECT, blank=False, null=False)
    action_start_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    action_end_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    scheduled = models.NullBooleanField(default=None)
    description = models.TextField(blank=True, null=True)
    used_in_equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True)
    used_in_action = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    used_in_spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE, blank=True, null=True)
    quantity_delta = models.FloatField(default=None, blank=True, null=True)
    new_container = models.ForeignKey(Container, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.action_start_date.strftime("%d.%m.%Y %H:%M")+' '+self.type.title+' ['+ str(self.used_in_equipment)+']'


#class Movement_action(models.Model):
#    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#    action_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
#    description = models.TextField(blank=True, null=True)
#    type = models.ForeignKey(Action_type, on_delete=models.PROTECT, blank=True, null=True)
#    used_in_action = models.ForeignKey(Action, on_delete=models.SET_NULL, blank=True, null=True)
#    used_in_equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, blank=True, null=True)
#    used_in_spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE, blank=True, null=True)
#    quantity_delta = models.FloatField(default=0, blank=True, null=True)
#    new_container = models.ForeignKey(Container, on_delete=models.SET_NULL, blank=True, null=True)
#    def __str__(self):
#        return str(self.action_date)
