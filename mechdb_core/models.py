from django.db import models
from django.utils import timezone

# Create your models here.

class Action_type(models.Model):
    title = models.CharField(max_length=20, blank=False, null=False)
    def __str__(self):
        return self.title

class Manufacturer(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    descripton = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.title

class Supply_provider(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    descripton = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.title

class Container(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    descripton = models.TextField(blank=True, null=True)
    is_repair_organization = models.BooleanField(default=False, blank=False, null=False)
    in_container_id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.pk)+" "+self.title

class Equipment_sizename(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False, default='Enter product name...')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, blank=True, null=True)
    supply_provider = models.ForeignKey(Supply_provider, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.title

class Equipment(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    sizename = models.ForeignKey(Equipment_sizename, on_delete=models.CASCADE, blank=False, null=False)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    in_container = models.ForeignKey(Container, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return_str = self.sizename.title+" s/n "+self.serial_number
        return return_str

class Spare_part(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    quantity = models.FloatField(default=0, blank=False, null=False)
    unit_name = models.CharField(max_length=10, blank=False, null=False)
    in_container = models.ForeignKey(Container, on_delete=models.SET_NULL, blank=True, null=True)
    used_in_equipment = models.ManyToManyField(Equipment_sizename)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, blank=True, null=True)
    supply_provider = models.ForeignKey(Supply_provider, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return self.title

class Action(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    type = models.ForeignKey(Action_type, on_delete=models.PROTECT, blank=False, null=False)
    action_start_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    action_end_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    scheduled = models.BooleanField(default=False, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    used_in_equipment = models.ManyToManyField(Equipment)
    def __str__(self):
        return str(self.action_start_date)

class Movement_action(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    action_date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    used_spare_part = models.ForeignKey(Spare_part, on_delete=models.CASCADE, blank=False, null=False)
    quantity = models.FloatField(default=0, blank=False, null=False)
    used_in_action = models.ForeignKey(Action, on_delete=models.SET_NULL, blank=True, null=True)
    new_container = models.ForeignKey(Container, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return str(self.action_date)
