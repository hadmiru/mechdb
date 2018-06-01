from django import forms
from .models import Container, Equipment, Equipment_sizename
from .my_defs import tree_parse

class ContainerForm(forms.ModelForm):

    in_container_id = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user)

    class Meta:
        model = Container
        fields = ('title', 'description', 'in_container_id')

class EquipmentForm(forms.ModelForm):

    in_container_id = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user, False)
        #Проверяем наличие instance. Если есть - вытягиваем значение по умолчанию для поля in_container_id
        instance = getattr(self, 'instance', None)
        if instance.pk:
            self.fields['in_container_id'].initial=instance.in_container.pk


    class Meta:
        model = Equipment
        fields = ('sizename', 'serial_number', 'registration_number')

class SizenameForm(forms.ModelForm):
    class Meta:
        model = Equipment_sizename
        fields = ('title', 'manufacturer', 'supply_provider')
