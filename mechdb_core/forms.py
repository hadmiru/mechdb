from django import forms
from .models import Container, Equipment, Equipment_sizename, Action, Action_type
from .my_defs import tree_parse
from django.utils import timezone

class In_container_choicefield(forms.ChoiceField):
    # Класс для проверки на зацикленность поля in_container_id объектов Container
    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        return int(value)

    def validate(self, value):
        super(In_container_choicefield, self).validate(value)

        saved_list=[]
        recycle_flag=True
        checked_pk=value

        while recycle_flag == True:

            recycle_flag = False
            if checked_pk in saved_list:
                raise forms.ValidationError("Нельзя положить контейнер сам в себя")
            saved_list.append(checked_pk)
            print(checked_pk)
            if checked_pk>0:
                checked_container = Container.objects.get(pk=checked_pk)
                if checked_container.in_container:
                    recycle_flag = True
                    checked_pk = checked_container.in_container.pk

class ContainerForm(forms.Form):

    title = forms.CharField(max_length=200, required=True, label='Название')
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea, label='Описание')
    is_repair_organization = forms.BooleanField(required=False, label='Ремонтная организация?')
    in_container_id = In_container_choicefield(label='Расположение')

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user)

class EquipmentForm(forms.Form):

    sizename = forms.ModelChoiceField(queryset=Equipment_sizename.objects.filter(owner=0), empty_label=None, required=True, label='Модель')
    serial_number = forms.CharField(max_length=50, required=False, label='Заводской номер')
    registration_number = forms.CharField(max_length=50, required=False, label='Регистрационный номер')
    in_container_id = forms.ChoiceField(required=True, label='Расположение')

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user, False)
        self.fields['sizename'].queryset=Equipment_sizename.objects.filter(owner=user).order_by('title')

class SizenameForm(forms.ModelForm):
    class Meta:
        model = Equipment_sizename
        fields = ('title', 'manufacturer', 'supply_provider')

class ActionForm(forms.Form):

    type = forms.ModelChoiceField(queryset=Action_type.objects.all(), empty_label=None, required=True, label='Тип воздействия')
    used_in_equipment = forms.ModelChoiceField(queryset=Equipment.objects.filter(owner=0), empty_label=None, required=True, label='Оборудование')
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea, label='Описание')
    action_start_date = forms.DateTimeField(initial=timezone.now(), required=True, label='Начало')
    action_end_date = forms.DateTimeField(required=False, label='Окончание')
    scheduled = forms.BooleanField(required=False, label='Плановое?')


    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['used_in_equipment'].queryset=Equipment.objects.filter(owner=user).order_by('created_date')
